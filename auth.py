"""
Autenticação OAuth 2.0 com Google.

Fluxo:
  /login          → tela de login
  /login/google   → redireciona para consent screen do Google
  /oauth/callback → recebe token, salva sessão → redireciona para /
  /logout         → limpa sessão → redireciona para /login

Proteção de rotas:
  @login_required  → decorator aplicado em todas as rotas do app.py

Configuração necessária no .env:
  GOOGLE_CLIENT_ID=...
  GOOGLE_CLIENT_SECRET=...
  FLASK_SECRET_KEY=...   (string aleatória, ex: python -c "import secrets; print(secrets.token_hex())")
"""

import os
import functools

from flask import Blueprint, session, redirect, request, url_for, render_template, jsonify
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Permite HTTP em localhost (apenas desenvolvimento local)
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
# Evita erro quando o Google retorna escopos em ordem diferente da solicitada
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")

bp = Blueprint("auth", __name__)

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive",
]


# ─── Helpers de credencial ───────────────────────────────────────────────────

def _client_config():
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET precisam estar no .env"
        )
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


def _make_flow():
    flow = Flow.from_client_config(_client_config(), scopes=SCOPES)
    flow.redirect_uri = url_for("auth.callback", _external=True)
    return flow


def _save_creds(creds):
    session["token"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or SCOPES),
    }
    session.modified = True


def get_credentials():
    t = session.get("token")
    if not t:
        return None
    return Credentials(
        token=t["token"],
        refresh_token=t.get("refresh_token"),
        token_uri=t["token_uri"],
        client_id=t["client_id"],
        client_secret=t["client_secret"],
        scopes=t["scopes"],
    )


def get_service():
    """Retorna Google Drive service autenticado com o usuário da sessão atual."""
    creds = get_credentials()
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_creds(creds)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def current_user():
    return session.get("user", {})


def is_oauth_configured():
    return bool(
        os.environ.get("GOOGLE_CLIENT_ID")
        and os.environ.get("GOOGLE_CLIENT_SECRET")
    )


# ─── Decorator ───────────────────────────────────────────────────────────────

def login_required(f):
    """
    Protege rotas. Redireciona para /login se não autenticado.
    Rotas /api/* retornam JSON 401 em vez de redirect.
    Se OAuth não estiver configurado (.env), passa sem autenticação (modo local).
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not is_oauth_configured():
            return f(*args, **kwargs)
        if not session.get("token"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Não autenticado", "login_url": "/login"}), 401
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ─── Rotas OAuth ─────────────────────────────────────────────────────────────

@bp.route("/login")
def login():
    if session.get("token"):
        return redirect(url_for("index"))
    return render_template("login.html", oauth_configured=is_oauth_configured())


@bp.route("/login/google")
def login_google():
    flow = _make_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    session["oauth_state"] = state
    # Persiste o code_verifier (PKCE) gerado automaticamente pela lib
    session["code_verifier"] = getattr(flow, "code_verifier", None)
    return redirect(auth_url)


@bp.route("/oauth/callback")
def callback():
    flow = _make_flow()
    # Restaura o code_verifier para que o fetch_token funcione corretamente
    code_verifier = session.pop("code_verifier", None)
    if code_verifier:
        flow.code_verifier = code_verifier
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    _save_creds(creds)

    # Busca nome, e-mail e foto do usuário
    svc = build("oauth2", "v2", credentials=creds)
    info = svc.userinfo().get().execute()
    session["user"] = {
        "email": info.get("email", ""),
        "name": info.get("name", ""),
        "picture": info.get("picture", ""),
    }
    return redirect(url_for("index"))


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/api/me")
@login_required
def api_me():
    return jsonify(current_user())

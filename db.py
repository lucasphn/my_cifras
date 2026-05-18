"""
Camada de acesso ao Supabase via REST API (httpx).
Usado em vez de arquivos JSON no Google Drive para dados por usuário.
"""
import json
import logging
import os
from datetime import datetime, timezone

import httpx

log = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

_ENABLED = bool(SUPABASE_URL and SUPABASE_KEY)


def enabled() -> bool:
    return _ENABLED


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def _h(prefer: str = "") -> dict:
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _raise(r) -> None:
    if not r.is_success:
        raise httpx.HTTPStatusError(
            f"{r.status_code} {r.reason_phrase} — {r.text}",
            request=r.request, response=r,
        )


def _get(table: str, **params) -> list:
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h(),
        params={k: v for k, v in params.items() if v is not None},
        timeout=10,
    )
    _raise(r)
    return r.json()


def _post(table: str, body, upsert: bool = False) -> list:
    prefer = "resolution=merge-duplicates,return=representation" if upsert else "return=representation"
    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h(prefer),
        json=body,
        timeout=10,
    )
    _raise(r)
    return r.json()


def _patch(table: str, body: dict, **params) -> list:
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h("return=representation"),
        json=body,
        params={k: v for k, v in params.items()},
        timeout=10,
    )
    _raise(r)
    return r.json()


def _delete(table: str, **params) -> None:
    r = httpx.delete(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h(),
        params={k: v for k, v in params.items()},
        timeout=10,
    )
    _raise(r)


# ─── Users ────────────────────────────────────────────────────────────────────

_uid_cache: dict = {}  # email → uuid


def get_or_create_user(email: str, google_id: str, name: str = "",
                        avatar: str = "", is_owner: bool = False) -> str | None:
    if email in _uid_cache:
        return _uid_cache[email]
    try:
        # Busca por email primeiro — garante que dados seedados (google_id=email)
        # sejam encontrados mesmo quando o sub real do Google é diferente.
        rows = _get("users", select="id,google_id", email=f"eq.{email}")
        if rows:
            uid = rows[0]["id"]
            real_gid = google_id or email
            # Atualiza google_id se ainda era o placeholder (email), e atualiza perfil.
            patch: dict = {"name": name, "avatar_url": avatar, "last_seen_at": "now()"}
            if rows[0].get("google_id") != real_gid:
                patch["google_id"] = real_gid
            _patch("users", patch, id=f"eq.{uid}")
            _uid_cache[email] = uid
            return uid
        # Não existe → cria
        rows = _post("users", {
            "google_id": google_id or email,
            "email": email,
            "name": name,
            "avatar_url": avatar,
            "is_owner": is_owner,
        }, upsert=True)
        uid = rows[0]["id"] if rows else None
        if uid:
            _uid_cache[email] = uid
        return uid
    except Exception as e:
        log.error("[db.users] Erro ao criar/obter usuário %s: %s", email, e)
        return None


def get_user_id(email: str) -> str | None:
    if email in _uid_cache:
        return _uid_cache[email]
    try:
        rows = _get("users", select="id", email=f"eq.{email}")
        if rows:
            _uid_cache[email] = rows[0]["id"]
            return rows[0]["id"]
    except Exception as e:
        log.error("[db.users] Erro ao buscar user_id %s: %s", email, e)
    return None


# ─── Views ────────────────────────────────────────────────────────────────────

def load_views(user_id: str) -> dict:
    """Retorna {file_id: view_count} para o usuário."""
    rows = _get("song_views", select="file_id,view_count", user_id=f"eq.{user_id}")
    return {r["file_id"]: r["view_count"] for r in rows}


def increment_view(user_id: str, file_id: str) -> int:
    rows = _get("song_views", select="view_count",
                user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
    if rows:
        new_count = rows[0]["view_count"] + 1
        _patch("song_views", {"view_count": new_count},
               user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
        return new_count
    _post("song_views", {"user_id": user_id, "file_id": file_id, "view_count": 1})
    return 1


# ─── Tones / Preferences ─────────────────────────────────────────────────────

_TONE_COLS = ("my_key", "original_key", "alt_key", "my_capo")


def load_tones(user_id: str) -> dict:
    """Retorna {file_id: {slot: value, ...}} para o usuário."""
    rows = _get("user_tones",
                select="file_id,my_key,original_key,alt_key,my_capo",
                user_id=f"eq.{user_id}")
    result = {}
    for r in rows:
        d = {k: v for k in _TONE_COLS if (v := r.get(k)) is not None}
        if d:
            result[r["file_id"]] = d
    return result


def upsert_tone(user_id: str, file_id: str, slot: str, value) -> dict:
    """Grava/atualiza um slot de tom. Retorna todos os slots da música."""
    rows = _get("user_tones", select=",".join(_TONE_COLS),
                user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
    current = {k: v for k in _TONE_COLS if (v := (rows[0] if rows else {}).get(k)) is not None}
    if not value or (slot == "my_capo" and str(value) in ("0", "")):
        current.pop(slot, None)
    else:
        current[slot] = value
    current.update({"user_id": user_id, "file_id": file_id})
    result = _post("user_tones", current, upsert=True)
    row = result[0] if result else current
    return {k: v for k in _TONE_COLS if (v := row.get(k)) is not None}


def delete_tone(user_id: str, file_id: str, slot: str = "") -> dict:
    """Remove um slot ou todos os slots de um arquivo."""
    if slot and slot in _TONE_COLS:
        rows = _patch("user_tones", {slot: None},
                      user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
        row = rows[0] if rows else {}
        return {k: v for k in _TONE_COLS if (v := row.get(k)) is not None}
    _delete("user_tones", user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
    return {}


# ─── Repertórios ──────────────────────────────────────────────────────────────

def _rep_to_dict(r: dict) -> dict:
    songs = r.get("songs") or []
    if isinstance(songs, str):
        try:
            songs = json.loads(songs)
        except Exception:
            songs = []
    return {
        "id": r["id"],
        "name": r["name"],
        "songs": songs,
        "created_at": r.get("created_at", ""),
        "updated_at": r.get("updated_at", ""),
    }


def load_reps(user_id: str) -> dict:
    rows = _get("repertories",
                select="id,name,songs,created_at,updated_at",
                user_id=f"eq.{user_id}")
    return {r["id"]: _rep_to_dict(r) for r in rows}


def create_rep(user_id: str, name: str, songs: list) -> dict:
    rows = _post("repertories", {"user_id": user_id, "name": name, "songs": songs})
    return _rep_to_dict(rows[0])


def update_rep(rep_id: str, patch: dict) -> dict:
    rows = _patch("repertories", patch, id=f"eq.{rep_id}")
    return _rep_to_dict(rows[0]) if rows else {}


def delete_rep(rep_id: str) -> None:
    _delete("repertories", id=f"eq.{rep_id}")


# ─── Shares ───────────────────────────────────────────────────────────────────

def _share_to_dict(r: dict) -> dict:
    d = dict(r)
    for field in ("seen_by", "dismissed_by", "songs"):
        val = d.get(field)
        if isinstance(val, str):
            try:
                d[field] = json.loads(val)
            except Exception:
                d[field] = []
        elif val is None:
            d[field] = []
    return d


def load_all_shares() -> dict:
    rows = _get("shares", select="*")
    return {r["id"]: _share_to_dict(r) for r in rows}


_SHARE_LOCAL_ONLY = {"rep_id"}  # campos in-memory sem coluna no Supabase


def create_share(data: dict) -> dict:
    payload = {k: v for k, v in data.items() if k not in _SHARE_LOCAL_ONLY}
    rows = _post("shares", payload, upsert=True)
    return _share_to_dict(rows[0]) if rows else data


def update_share(share_id: str, data: dict) -> dict:
    payload = {k: v for k, v in data.items() if k not in {"id"} | _SHARE_LOCAL_ONLY}
    rows = _patch("shares", payload, id=f"eq.{share_id}")
    return _share_to_dict(rows[0]) if rows else {}


def delete_share(share_id: str) -> None:
    _delete("shares", id=f"eq.{share_id}")


def delete_shares_by_rep(rep_id: str, from_email: str) -> None:
    _delete("shares", repertory_id=f"eq.{rep_id}", from_email=f"eq.{from_email}")


# ─── Groups ───────────────────────────────────────────────────────────────────

def _group_to_dict(r: dict) -> dict:
    members = r.get("members") or []
    if isinstance(members, str):
        try:
            members = json.loads(members)
        except Exception:
            members = []
    return {
        "id": r["id"],
        "name": r["name"],
        "members": members,
        "created_at": r.get("created_at", ""),
    }


def load_groups(user_id: str) -> dict:
    rows = _get("groups", select="id,name,members,created_at",
                owner_id=f"eq.{user_id}")
    return {r["id"]: _group_to_dict(r) for r in rows}


def create_group(user_id: str, name: str, members: list) -> dict:
    rows = _post("groups", {"owner_id": user_id, "name": name, "members": members})
    return _group_to_dict(rows[0])


def update_group(group_id: str, data: dict) -> dict:
    rows = _patch("groups", data, id=f"eq.{group_id}")
    return _group_to_dict(rows[0]) if rows else {}


def delete_group(group_id: str) -> None:
    _delete("groups", id=f"eq.{group_id}")


# ─── Songs Meta ───────────────────────────────────────────────────────────────

_META_COLS = ("artist", "key", "capo", "youtube")


def load_songs_meta() -> dict:
    """Retorna {file_id: {artist, key, capo, youtube}} — global, não por usuário."""
    rows = _get("songs_meta", select="file_id,artist,key,capo,youtube")
    result = {}
    for r in rows:
        d = {k: r[k] for k in _META_COLS if r.get(k) is not None}
        result[r["file_id"]] = d
    return result


def upsert_song_meta(file_id: str, meta: dict) -> None:
    payload = {"file_id": file_id}
    for k in _META_COLS:
        payload[k] = meta.get(k) or None
    _post("songs_meta", payload, upsert=True)


def upsert_songs_meta_batch(records: list) -> None:
    """Upsert em lote. Cada record deve ter 'file_id' + campos opcionais."""
    if records:
        _post("songs_meta", records, upsert=True)


# ─── User status ──────────────────────────────────────────────────────────────

def get_user_status(user_id: str) -> str:
    rows = _get("users", select="status", id=f"eq.{user_id}")
    return rows[0]["status"] if rows else "pending"


def activate_user(user_id: str, coupon_code: str) -> None:
    _patch("users", {
        "status": "active",
        "activated_via": coupon_code,
        "activated_at": "now()",
    }, id=f"eq.{user_id}")


# ─── Coupons ──────────────────────────────────────────────────────────────────

def get_coupon(code: str) -> dict | None:
    rows = _get("coupons", select="*", code=f"eq.{code.upper().strip()}")
    return rows[0] if rows else None


def redeem_coupon(user_id: str, code: str) -> dict:
    """Valida e resgata um cupom. Retorna {"ok": True} ou {"error": "..."}."""
    coupon = get_coupon(code)
    if not coupon:
        return {"error": "Cupom inválido"}

    exp = coupon.get("expires_at")
    if exp:
        try:
            exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
            if exp_dt < datetime.now(timezone.utc):
                return {"error": "Cupom expirado"}
        except Exception:
            pass

    max_uses = coupon.get("max_uses")
    if max_uses is not None and coupon.get("uses_count", 0) >= max_uses:
        return {"error": "Cupom esgotado"}

    coupon_id = coupon["id"]

    existing = _get("coupon_uses", select="user_id",
                    user_id=f"eq.{user_id}", coupon_id=f"eq.{coupon_id}")
    if existing:
        return {"error": "Cupom já utilizado por esta conta"}

    _post("coupon_uses", {"coupon_id": coupon_id, "user_id": user_id})
    _patch("coupons", {"uses_count": coupon.get("uses_count", 0) + 1},
           code=f"eq.{code.upper().strip()}")
    activate_user(user_id, code.upper().strip())
    return {"ok": True}


def create_coupon(code: str, max_uses: int | None = 1,
                  expires_at: str | None = None, note: str = "") -> dict:
    rows = _post("coupons", {
        "code":       code.upper().strip(),
        "max_uses":   max_uses,
        "expires_at": expires_at,
        "note":       note,
    })
    return rows[0] if rows else {}


def list_coupons() -> list:
    return _get("coupons", select="*", order="created_at.desc")

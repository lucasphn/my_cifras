"""
Compartilha todos os arquivos da pasta de cifras com a Service Account como "writer".
Roda localmente uma vez. Abre o browser para autenticar com sua conta Google.

Uso:
  python grant_sa_writer.py
"""

import json
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json as _json

# Lê configurações do .env local
def _load_env(path=".env"):
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env

_env = _load_env()

FOLDER_ID     = _env.get("CIFRAS_FOLDER_ID", "")
CLIENT_ID     = _env.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = _env.get("GOOGLE_CLIENT_SECRET", "")

# E-mail da Service Account (extraído do JSON do .env)
_sa_json_raw = _env.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
SA_EMAIL = _json.loads(_sa_json_raw).get("client_email", "")

SCOPES = ["https://www.googleapis.com/auth/drive"]

CLIENT_CONFIG = {
    "installed": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
    }
}


def list_all_files(svc, folder_id):
    """Lista recursivamente todos os arquivos (não pastas) dentro de folder_id."""
    items = []
    page_token = None
    while True:
        resp = svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        for f in resp.get("files", []):
            if f["mimeType"] == "application/vnd.google-apps.folder":
                items.extend(list_all_files(svc, f["id"]))
            else:
                items.append(f)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return items


def sa_already_writer(svc, file_id):
    """Retorna True se a SA já tem permissão de writer no arquivo."""
    try:
        perms = svc.permissions().list(
            fileId=file_id,
            fields="permissions(emailAddress,role)",
            supportsAllDrives=True,
        ).execute().get("permissions", [])
        for p in perms:
            if p.get("emailAddress", "").lower() == SA_EMAIL.lower():
                return p.get("role") in ("writer", "owner", "organizer", "fileOrganizer")
    except HttpError:
        pass
    return False


def grant_writer(svc, file_id, name):
    try:
        svc.permissions().create(
            fileId=file_id,
            body={"type": "user", "role": "writer", "emailAddress": SA_EMAIL},
            fields="id",
            supportsAllDrives=True,
            sendNotificationEmail=False,
        ).execute()
        print(f"  [OK] {name}")
    except HttpError as e:
        print(f"  [ERRO] {name}: {e}")


def main():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=8080, open_browser=True)
    svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    print(f"\nListando arquivos em {FOLDER_ID}...")
    files = list_all_files(svc, FOLDER_ID)
    print(f"Encontrados {len(files)} arquivos.\n")

    granted = 0
    skipped = 0
    for f in files:
        if sa_already_writer(svc, f["id"]):
            skipped += 1
        else:
            grant_writer(svc, f["id"], f["name"])
            granted += 1

    print(f"\nConcluído: {granted} compartilhados, {skipped} já tinham acesso.")


if __name__ == "__main__":
    main()

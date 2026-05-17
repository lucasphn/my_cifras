"""
Migra _songs_meta.json do Google Drive para a tabela songs_meta no Supabase.

Uso:
    python seed_songs_meta.py           # migração real
    python seed_songs_meta.py --dry-run # mostra o que faria, sem gravar
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import db

CIFRAS_FOLDER_ID = os.environ.get("CIFRAS_FOLDER_ID", "")

_TOKEN_FILE   = Path(__file__).parent / "_script_token.json"
_SECRETS_FILE = Path(__file__).parent / "client_secrets.json"
_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_svc():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GRequest
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    if not _SECRETS_FILE.exists():
        print("[ERRO] client_secrets.json não encontrado.")
        sys.exit(1)

    creds = None
    if _TOKEN_FILE.exists():
        t = json.loads(_TOKEN_FILE.read_text())
        creds = Credentials(
            token=t.get("token"),
            refresh_token=t.get("refresh_token"),
            token_uri=t.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=t.get("client_id", os.environ.get("GOOGLE_CLIENT_ID", "")),
            client_secret=t.get("client_secret", os.environ.get("GOOGLE_CLIENT_SECRET", "")),
            scopes=t.get("scopes", _SCOPES),
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GRequest())
        else:
            print("Abrindo browser para autorizar acesso ao Google Drive...")
            flow = InstalledAppFlow.from_client_secrets_file(str(_SECRETS_FILE), scopes=_SCOPES)
            creds = flow.run_local_server(port=0)
        _TOKEN_FILE.write_text(json.dumps({
            "token":         creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri":     creds.token_uri,
            "client_id":     creds.client_id,
            "client_secret": creds.client_secret,
            "scopes":        list(creds.scopes or _SCOPES),
        }))

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def seed(dry_run: bool):
    if not db.enabled():
        print("[ERRO] SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar no .env")
        sys.exit(1)
    if not CIFRAS_FOLDER_ID:
        print("[ERRO] CIFRAS_FOLDER_ID deve estar no .env")
        sys.exit(1)

    print("Conectando ao Google Drive...")
    svc = _get_drive_svc()

    import drive as drv
    print("Carregando _songs_meta.json do Drive...")
    meta_data, _ = drv.load_songs_meta(svc, CIFRAS_FOLDER_ID)
    print(f"  {len(meta_data)} entradas encontradas.\n")

    if not meta_data:
        print("Nada a migrar.")
        return

    records = []
    for file_id, m in meta_data.items():
        rec = {
            "file_id": file_id,
            "artist":  m.get("artist") or None,
            "key":     m.get("key") or None,
            "capo":    m.get("capo") or None,
            "youtube": m.get("youtube") or None,
        }
        records.append(rec)
        has_yt = "✓" if rec["youtube"] else " "
        print(f"  [{has_yt}] {file_id}  {rec['artist'] or '—'}  {rec['youtube'] or ''}")

    print(f"\n{'─'*50}")
    if dry_run:
        print(f"[DRY RUN] {len(records)} registros seriam inseridos no Supabase.")
        return

    print(f"Inserindo {len(records)} registros no Supabase (upsert)...")
    db.upsert_songs_meta_batch(records)
    print("Concluído.")
    with_yt = sum(1 for r in records if r["youtube"])
    print(f"  Total     : {len(records)}")
    print(f"  Com YouTube: {with_yt}")
    print(f"  Sem YouTube: {len(records) - with_yt}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migra _songs_meta.json do Drive para o Supabase.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que faria sem gravar")
    args = parser.parse_args()
    seed(dry_run=args.dry_run)

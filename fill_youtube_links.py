"""
Busca links do YouTube para músicas da seção 'ministração' (exceto 'missa')
e salva nos metadados do app (songs_meta no Drive).

Uso:
    python fill_youtube_links.py                  # pula músicas que já têm link
    python fill_youtube_links.py --overwrite       # sobrescreve links existentes
    python fill_youtube_links.py --dry-run         # mostra o que faria, sem salvar

Dependência extra:
    pip install youtube-search-python
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

CIFRAS_FOLDER_ID = os.environ.get("CIFRAS_FOLDER_ID", "")
SECTION_TARGET   = "ministração"
SKIP_CATS        = {"missa"}   # categorias a ignorar (case-insensitive, sem acento)
DELAY_BETWEEN    = 2.5         # segundos entre buscas (evita bloqueio)


# ─── Autenticação ─────────────────────────────────────────────────────────────
# Token salvo localmente para não depender da sessão Flask.
# Na primeira execução abre o browser para autorizar; depois reutiliza o refresh_token.

_TOKEN_FILE = Path(__file__).parent / "_script_token.json"
_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_svc():
    import json
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GRequest
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    client_id     = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    _SECRETS_FILE = Path(__file__).parent / "client_secrets.json"
    if not _SECRETS_FILE.exists():
        print("[ERRO] Arquivo client_secrets.json não encontrado.")
        print("  Crie um OAuth Client ID do tipo 'Desktop app' no Google Cloud Console,")
        print("  baixe o JSON e salve como client_secrets.json na pasta do projeto.")
        sys.exit(1)

    creds = None
    if _TOKEN_FILE.exists():
        t = json.loads(_TOKEN_FILE.read_text())
        creds = Credentials(
            token=t.get("token"),
            refresh_token=t.get("refresh_token"),
            token_uri=t.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=t.get("client_id", client_id),
            client_secret=t.get("client_secret", client_secret),
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


# ─── Normalização ─────────────────────────────────────────────────────────────

import unicodedata

def _strip_accents(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def _skip_cat(cat: str) -> bool:
    c = _strip_accents(cat.split(" > ")[0])
    return c in {_strip_accents(s) for s in SKIP_CATS}


# ─── Biblioteca ───────────────────────────────────────────────────────────────

def load_songs(svc):
    import drive as drv
    library = drv.scan_library(svc, CIFRAS_FOLDER_ID)

    songs = []
    section_data = None
    for sec_name, cats in library.items():
        if _strip_accents(sec_name) == _strip_accents(SECTION_TARGET):
            section_data = cats
            break

    if not section_data:
        print(f"[ERRO] Seção '{SECTION_TARGET}' não encontrada no Drive.")
        sys.exit(1)

    for cat, items in section_data.items():
        if _skip_cat(cat):
            print(f"  ↷ Pulando categoria: {cat}")
            continue
        for song in items:
            if song.get("fileId"):
                songs.append(song)

    return songs


# ─── YouTube search ───────────────────────────────────────────────────────────

def _yt_search(query: str) -> str | None:
    try:
        from youtubesearchpython import VideosSearch
        res = VideosSearch(query, limit=1)
        items = res.result().get("result", [])
        if items:
            return "https://www.youtube.com/watch?v=" + items[0]["id"]
    except Exception as e:
        print(f"  [WARN] Erro na busca YT: {e}")
    return None


def _build_query(song: dict, meta: dict) -> str:
    name   = song.get("name", "")
    artist = meta.get("artist") or song.get("artist") or ""
    if artist:
        return f"{name} {artist} letra"
    return f"{name} música católica cifra"


# ─── Main ─────────────────────────────────────────────────────────────────────

def run(overwrite: bool, dry_run: bool):
    if not CIFRAS_FOLDER_ID:
        print("[ERRO] CIFRAS_FOLDER_ID não definido no .env")
        sys.exit(1)

    print(f"Conectando ao Google Drive...")
    svc = _get_svc()

    import drive as drv

    print(f"Carregando biblioteca — seção '{SECTION_TARGET}'...")
    songs = load_songs(svc)
    print(f"  {len(songs)} músicas encontradas.\n")

    print("Carregando metadados existentes...")
    meta_data, meta_fid = drv.load_songs_meta(svc, CIFRAS_FOLDER_ID)
    print(f"  {len(meta_data)} entradas no songs_meta.\n")

    updated = 0
    skipped = 0
    failed  = 0

    for i, song in enumerate(songs, 1):
        fid    = song["fileId"]
        name   = song.get("name", "?")
        meta   = meta_data.get(fid, {})
        artist = meta.get("artist") or song.get("artist") or ""
        cat    = song.get("category", "")

        has_link = bool(meta.get("youtube"))
        prefix   = f"[{i:03}/{len(songs):03}]"

        if has_link and not overwrite:
            print(f"{prefix} ⏩ {name}  (já tem link, pulando)")
            skipped += 1
            continue

        query = _build_query(song, meta)
        print(f"{prefix} 🔍 {name}  ({artist or 'sem artista'})  |  cat: {cat}")
        print(f"         query: {query!r}")

        if dry_run:
            print("         [dry-run] não buscando")
            continue

        url = _yt_search(query)
        if url:
            print(f"         ✓ {url}")
            if not dry_run:
                meta_data.setdefault(fid, {})
                meta_data[fid] = {
                    "artist":  meta.get("artist", ""),
                    "key":     meta.get("key", ""),
                    "capo":    meta.get("capo", ""),
                    "tags":    meta.get("tags", []),
                    "youtube": url,
                }
            updated += 1
        else:
            print(f"         ✗ nenhum resultado")
            failed += 1

        time.sleep(DELAY_BETWEEN)

    print(f"\n{'─'*50}")
    print(f"  Atualizadas : {updated}")
    print(f"  Puladas     : {skipped}")
    print(f"  Sem resultado: {failed}")

    if not dry_run and updated > 0:
        print(f"\nSalvando metadados no Drive...")
        drv.save_songs_meta(svc, meta_fid, meta_data)
        print("  ✓ Salvo com sucesso.")
    elif dry_run:
        print("\n[dry-run] Nada foi salvo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preenche links do YouTube nos metadados.")
    parser.add_argument("--overwrite", action="store_true",
                        help="Sobrescreve links já existentes")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que faria sem salvar nada")
    args = parser.parse_args()
    run(overwrite=args.overwrite, dry_run=args.dry_run)

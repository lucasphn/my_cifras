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
    """Carrega músicas da seção SECTION_TARGET (exceto SKIP_CATS)."""
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


def load_all_songs(svc):
    """Carrega todas as músicas de todas as seções (para sync global)."""
    import drive as drv
    library = drv.scan_library(svc, CIFRAS_FOLDER_ID)
    songs = []
    for cats in library.values():
        for items in cats.values():
            for song in items:
                if song.get("fileId"):
                    songs.append(song)
    return songs


# ─── YouTube search ───────────────────────────────────────────────────────────

_YT_RETRIES   = 3        # tentativas por música
_YT_RETRY_WAIT = 8.0    # segundos entre tentativas (back-off: *2 a cada falha)

def _yt_search(query: str) -> str | None:
    import yt_dlp
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "socket_timeout": 20,
        "retries": 3,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        },
    }
    wait = _YT_RETRY_WAIT
    for attempt in range(1, _YT_RETRIES + 1):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                result = ydl.extract_info(f"ytsearch1:{query}", download=False)
                entries = (result or {}).get("entries", [])
                if entries:
                    vid_id = entries[0].get("id")
                    if vid_id:
                        return f"https://www.youtube.com/watch?v={vid_id}"
            return None  # busca OK mas sem resultado
        except Exception as e:
            msg = str(e)
            print(f"  [WARN] Tentativa {attempt}/{_YT_RETRIES} falhou: {msg[:120]}")
            if attempt < _YT_RETRIES:
                print(f"         Aguardando {wait:.0f}s antes de tentar novamente...")
                time.sleep(wait)
                wait *= 2
    return None


_MD_MIMES = {"text/markdown", "text/plain"}

def _patch_youtube_in_frontmatter(raw: str, url: str) -> str:
    """Injeta/substitui o campo youtube no frontmatter YAML do .md, preservando o resto."""
    if not raw.startswith("---"):
        return f"---\nyoutube: {url}\n---\n\n{raw}"
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return raw  # frontmatter malformado — não toca
    fm_lines = parts[1].splitlines(keepends=True)
    new_lines = []
    replaced = False
    for line in fm_lines:
        if line.startswith("youtube:"):
            new_lines.append(f"youtube: {url}\n")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f"youtube: {url}\n")
    return "---" + "".join(new_lines) + "---\n\n" + parts[2].lstrip("\n")


def _ensure_frontmatter_youtube(svc, fid: str, mime: str, url: str, drv) -> str:
    """Garante que o frontmatter do .md tem o youtube informado.
    Retorna: 'synced' (atualizou), 'ok' (já estava correto), 'skipped' (não é .md / erro).
    """
    if mime not in _MD_MIMES and not mime.endswith("markdown"):
        return "skipped"
    try:
        raw = drv.download_bytes(svc, fid).decode("utf-8", errors="replace")
        # Checa se o frontmatter já tem a URL exata — evita upload desnecessário
        if f"youtube: {url}" in raw:
            return "ok"
        patched = _patch_youtube_in_frontmatter(raw, url)
        drv.update_md_content(svc, fid, patched)
        return "synced"
    except Exception as e:
        print(f"         [WARN] Não foi possível verificar/atualizar frontmatter: {e}")
        return "skipped"


def _build_query(song: dict, meta: dict) -> str:
    name   = song.get("name", "")
    artist = meta.get("artist") or song.get("artist") or ""
    if artist:
        return f"{name} {artist} letra"
    return f"{name} música católica cifra"


# ─── Main ─────────────────────────────────────────────────────────────────────

def run(overwrite: bool, dry_run: bool, save_every: int = 20):
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

    updated          = 0
    skipped          = 0
    failed           = 0
    pending_save     = 0  # atualizações desde o último save

    def _checkpoint(force: bool = False):
        nonlocal pending_save
        if dry_run or pending_save == 0:
            return
        if force or pending_save >= save_every:
            print(f"\n  💾 Checkpoint — salvando {pending_save} atualização(ões) no Drive...")
            drv.save_songs_meta(svc, meta_fid, meta_data)
            print(f"  ✓ Salvo.\n")
            pending_save = 0

    for i, song in enumerate(songs, 1):
        fid    = song["fileId"]
        name   = song.get("name", "?")
        meta   = meta_data.get(fid, {})
        artist = meta.get("artist") or song.get("artist") or ""
        cat    = song.get("category", "")

        existing_url = meta.get("youtube", "")
        has_link     = bool(existing_url)
        mime         = song.get("mimeType", "")
        prefix       = f"[{i:03}/{len(songs):03}]"

        if has_link and not overwrite:
            # Link já existe no _songs_meta.json — garante que o frontmatter também tem
            fm_status = _ensure_frontmatter_youtube(svc, fid, mime, existing_url, drv)
            if fm_status == "synced":
                print(f"{prefix} 🔄 {name}  (frontmatter sincronizado com link existente)")
            else:
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
            # Atualiza frontmatter do arquivo .md no Drive (fonte da verdade)
            fm_status = _ensure_frontmatter_youtube(svc, fid, mime, url, drv)
            if fm_status in ("synced", "ok"):
                print(f"         ✓ frontmatter {'atualizado' if fm_status == 'synced' else 'já correto'}")
            # Atualiza _songs_meta.json (cache de listagem)
            meta_data.setdefault(fid, {})
            meta_data[fid] = {
                "artist":  meta.get("artist", ""),
                "key":     meta.get("key", ""),
                "capo":    meta.get("capo", ""),
                "tags":    meta.get("tags", []),
                "youtube": url,
            }
            updated      += 1
            pending_save += 1
        else:
            print(f"         ✗ nenhum resultado")
            failed += 1

        time.sleep(DELAY_BETWEEN)
        _checkpoint()

    print(f"\n{'─'*50}")
    print(f"  Atualizadas : {updated}")
    print(f"  Puladas     : {skipped}")
    print(f"  Sem resultado: {failed}")

    _checkpoint(force=True)  # salva o restante (< save_every)
    if dry_run:
        print("\n[dry-run] Nada foi salvo.")


def _read_frontmatter_youtube(raw: str) -> str:
    """Extrai o campo youtube do frontmatter YAML de um .md. Retorna '' se não encontrado."""
    if not raw.startswith("---"):
        return ""
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return ""
    for line in parts[1].splitlines():
        if line.startswith("youtube:"):
            return line.partition(":")[2].strip()
    return ""


def sync_from_md(dry_run: bool, save_every: int = 20):
    """Lê o frontmatter de TODOS os .md do Drive e sincroniza o _songs_meta.json.

    Útil quando o youtube foi adicionado manualmente ao arquivo mas o cache
    _songs_meta.json ainda não reflete isso — sem fazer nenhuma busca no YouTube.
    """
    if not CIFRAS_FOLDER_ID:
        print("[ERRO] CIFRAS_FOLDER_ID não definido no .env")
        sys.exit(1)

    print("Conectando ao Google Drive...")
    svc = _get_svc()

    import drive as drv

    print("Carregando biblioteca completa (todas as seções)...")
    songs = load_all_songs(svc)
    md_songs = [s for s in songs if s.get("mimeType") in _MD_MIMES
                or (s.get("mimeType") or "").endswith("markdown")]
    print(f"  {len(md_songs)} arquivos .md encontrados.\n")

    print("Carregando _songs_meta.json...")
    meta_data, meta_fid = drv.load_songs_meta(svc, CIFRAS_FOLDER_ID)
    print(f"  {len(meta_data)} entradas no cache.\n")

    synced       = 0
    already_ok   = 0
    no_link      = 0
    pending_save = 0

    def _checkpoint(force: bool = False):
        nonlocal pending_save
        if dry_run or pending_save == 0:
            return
        if force or pending_save >= save_every:
            print(f"\n  💾 Checkpoint — salvando {pending_save} entrada(s) no Drive...")
            drv.save_songs_meta(svc, meta_fid, meta_data)
            print("  ✓ Salvo.\n")
            pending_save = 0

    for i, song in enumerate(md_songs, 1):
        fid  = song["fileId"]
        name = song.get("name", "?")
        prefix = f"[{i:03}/{len(md_songs):03}]"

        try:
            raw = drv.download_bytes(svc, fid).decode("utf-8", errors="replace")
        except Exception as e:
            print(f"{prefix} ⚠ {name}  — erro ao baixar: {e}")
            continue

        fm_url   = _read_frontmatter_youtube(raw)
        meta_url = (meta_data.get(fid) or {}).get("youtube", "")

        if not fm_url:
            print(f"{prefix} —  {name}  (sem youtube no frontmatter)")
            no_link += 1
            continue

        if meta_url == fm_url:
            print(f"{prefix} ✓  {name}  (já sincronizado)")
            already_ok += 1
            continue

        print(f"{prefix} 🔄 {name}")
        print(f"         frontmatter : {fm_url}")
        print(f"         songs_meta  : {meta_url or '(vazio)'}")

        if not dry_run:
            existing = meta_data.get(fid, {})
            meta_data[fid] = {
                "artist":  existing.get("artist", ""),
                "key":     existing.get("key", ""),
                "capo":    existing.get("capo", ""),
                "tags":    existing.get("tags", []),
                "youtube": fm_url,
            }
            pending_save += 1
        synced += 1
        _checkpoint()

    print(f"\n{'─'*50}")
    print(f"  Sincronizados : {synced}")
    print(f"  Já corretos   : {already_ok}")
    print(f"  Sem link      : {no_link}")

    _checkpoint(force=True)
    if dry_run:
        print("\n[dry-run] Nada foi salvo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preenche links do YouTube nos metadados.")
    parser.add_argument("--overwrite", action="store_true",
                        help="Sobrescreve links já existentes")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que faria sem salvar nada")
    parser.add_argument("--save-every", type=int, default=20, metavar="N",
                        help="Salva no Drive a cada N músicas atualizadas (padrão: 20)")
    parser.add_argument("--sync-from-md", action="store_true",
                        help="Lê o youtube do frontmatter de todos os .md e sincroniza o "
                             "_songs_meta.json (sem buscar YouTube). Útil quando o link foi "
                             "adicionado manualmente ao arquivo.")
    args = parser.parse_args()

    if args.sync_from_md:
        sync_from_md(dry_run=args.dry_run, save_every=args.save_every)
    else:
        run(overwrite=args.overwrite, dry_run=args.dry_run, save_every=args.save_every)

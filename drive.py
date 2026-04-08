"""
Operações com Google Drive.

Todas as funções recebem `service` como primeiro parâmetro.
Obtenha o service via auth.get_service() nas rotas do app.py.

Configuração necessária no .env:
  CIFRAS_FOLDER_ID=<id-da-pasta-raiz-no-drive>
"""

import io
import os
from pathlib import Path

FOLDER_MIME = "application/vnd.google-apps.folder"
GDOCS_MIME = "application/vnd.google-apps.document"

SUPPORTED_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "application/pdf",
    "text/plain",
    "text/markdown",
}
SUPPORTED_EXTENSIONS = {".docx", ".doc", ".pdf", ".txt", ".md"}


# ─── Listagem ────────────────────────────────────────────────────────────────

def list_folder(service, folder_id):
    """Retorna lista de {id, name, mimeType} de todos os itens na pasta."""
    results = []
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
                orderBy="name",
            )
            .execute()
        )
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


# ─── Download ────────────────────────────────────────────────────────────────

def download_bytes(service, file_id):
    from googleapiclient.http import MediaIoBaseDownload

    buf = io.BytesIO()
    req = service.files().get_media(fileId=file_id)
    dl = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    buf.seek(0)
    return buf.read()


def export_gdoc_as_text(service, file_id):
    """Exporta Google Docs nativos como texto simples."""
    content = (
        service.files()
        .export(fileId=file_id, mimeType="text/plain")
        .execute()
    )
    return content.decode("utf-8", errors="replace") if isinstance(content, bytes) else content


# ─── Upload ──────────────────────────────────────────────────────────────────

def upload_md(service, name, content, folder_id):
    """Cria um arquivo .md na pasta especificada. Retorna o file_id."""
    from googleapiclient.http import MediaIoBaseUpload

    if not name.endswith(".md"):
        name += ".md"
    metadata = {"name": name, "parents": [folder_id]}
    media = MediaIoBaseUpload(
        io.BytesIO(content.encode("utf-8")), mimetype="text/markdown"
    )
    f = (
        service.files()
        .create(body=metadata, media_body=media, fields="id")
        .execute()
    )
    return f.get("id")


# ─── Pastas ──────────────────────────────────────────────────────────────────

def get_or_create_folder(service, name, parent_id):
    """Retorna ID da pasta existente ou cria uma nova."""
    resp = (
        service.files()
        .list(
            q=(
                f"name='{name}' and '{parent_id}' in parents "
                f"and mimeType='{FOLDER_MIME}' and trashed=false"
            ),
            fields="files(id)",
        )
        .execute()
    )
    files = resp.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]}
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder.get("id")


def resolve_folder(service, section, category, root_folder_id):
    """
    Retorna folder_id correto para seção + categoria.
    Cria as pastas se não existirem.
    """
    section_id = get_or_create_folder(service, section, root_folder_id)
    if not category or category == "_raiz":
        return section_id
    return get_or_create_folder(service, category, section_id)


# ─── Scan biblioteca ─────────────────────────────────────────────────────────

def _is_supported(f):
    mime = f.get("mimeType", "")
    ext = Path(f.get("name", "")).suffix.lower()
    return mime in SUPPORTED_MIMES or ext in SUPPORTED_EXTENSIONS or mime == GDOCS_MIME


def _collect_songs(service, folder_id, section, category):
    return [
        {
            "name": Path(f["name"]).stem,
            "fileId": f["id"],
            "mimeType": f["mimeType"],
            "section": section,
            "category": category,
        }
        for f in list_folder(service, folder_id)
        if f["mimeType"] != FOLDER_MIME and _is_supported(f)
    ]


def scan_library(service, root_folder_id):
    """Escaneia a estrutura de pastas no Drive e retorna a biblioteca."""
    library = {}
    for section in list_folder(service, root_folder_id):
        if section["mimeType"] != FOLDER_MIME:
            continue
        sname = section["name"]
        library[sname] = {}
        for item in list_folder(service, section["id"]):
            if item["mimeType"] == FOLDER_MIME:
                songs = _collect_songs(service, item["id"], sname, item["name"])
                if songs:
                    library[sname][item["name"]] = songs
            elif _is_supported(item):
                library[sname].setdefault("_raiz", [])
                library[sname]["_raiz"].append(
                    {
                        "name": Path(item["name"]).stem,
                        "fileId": item["id"],
                        "mimeType": item["mimeType"],
                        "section": sname,
                        "category": "_raiz",
                    }
                )
    return library

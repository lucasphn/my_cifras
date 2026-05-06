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

FOLDER_MIME    = "application/vnd.google-apps.folder"
SHORTCUT_MIME  = "application/vnd.google-apps.shortcut"
_USERDATA_FOLDER = "_mycifras_data"
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
    """Retorna lista de {id, name, mimeType, modifiedTime, shortcutDetails?} de todos os itens na pasta."""
    results = []
    page_token = None
    while True:
        resp = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, shortcutDetails)",
                pageToken=page_token,
                orderBy="folder,name_natural",
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


# ─── JSON genérico no Drive ──────────────────────────────────────────────────

REPERTORIOS_FILENAME  = "_repertorios.json"
VIEWS_FILENAME        = "_views.json"
PREFERENCES_FILENAME  = "_preferences.json"
GROUPS_FILENAME       = "_groups.json"

def _get_or_create_json_file(service, name, parent_id):
    """Retorna file_id de um arquivo JSON, criando-o vazio se não existir."""
    from googleapiclient.http import MediaIoBaseUpload
    resp = (
        service.files()
        .list(
            q=f"name='{name}' and '{parent_id}' in parents and trashed=false",
            fields="files(id)",
        )
        .execute()
    )
    files = resp.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {"name": name, "parents": [parent_id]}
    media = MediaIoBaseUpload(io.BytesIO(b"{}"), mimetype="application/json")
    f = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return f.get("id")


def load_repertorios(service, root_folder_id):
    """Carrega o dict de repertórios do Drive. Retorna (data, file_id)."""
    import json
    file_id = _get_or_create_json_file(service, REPERTORIOS_FILENAME, root_folder_id)
    try:
        content = download_bytes(service, file_id)
        return json.loads(content.decode("utf-8") or "{}"), file_id
    except Exception:
        return {}, file_id


def save_repertorios(service, file_id, data):
    """Salva o dict de repertórios no Drive."""
    import json
    from googleapiclient.http import MediaIoBaseUpload
    content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/json")
    service.files().update(fileId=file_id, media_body=media).execute()


# ─── Groups (JSON no Drive) ──────────────────────────────────────────────────

def load_groups(service, root_folder_id):
    """Carrega o dict de grupos do Drive. Retorna (data, file_id)."""
    import json
    file_id = _get_or_create_json_file(service, GROUPS_FILENAME, root_folder_id)
    try:
        content = download_bytes(service, file_id)
        return json.loads(content.decode("utf-8") or "{}"), file_id
    except Exception:
        return {}, file_id


def save_groups(service, file_id, data):
    """Salva o dict de grupos no Drive."""
    import json
    from googleapiclient.http import MediaIoBaseUpload
    content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/json")
    service.files().update(fileId=file_id, media_body=media).execute()


# ─── Views (JSON no Drive) ───────────────────────────────────────────────────

def load_views(service, root_folder_id):
    """Carrega o dict de views do Drive. Retorna (data, file_id)."""
    import json
    file_id = _get_or_create_json_file(service, VIEWS_FILENAME, root_folder_id)
    try:
        content = download_bytes(service, file_id)
        return json.loads(content.decode("utf-8") or "{}"), file_id
    except Exception:
        return {}, file_id


def save_views(service, file_id, data):
    """Salva o dict de views no Drive."""
    import json
    from googleapiclient.http import MediaIoBaseUpload
    content = json.dumps(data, ensure_ascii=False).encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/json")
    service.files().update(fileId=file_id, media_body=media).execute()


# ─── Preferences (tons salvos por música) ───────────────────────────────────

def load_preferences(service, root_folder_id):
    """Carrega preferências de tons do Drive. Retorna (data, file_id).
    Estrutura: { "<fileId>": { "my_key": "G", "original_key": "A", "alt_key": null } }
    """
    import json
    file_id = _get_or_create_json_file(service, PREFERENCES_FILENAME, root_folder_id)
    try:
        content = download_bytes(service, file_id)
        return json.loads(content.decode("utf-8") or "{}"), file_id
    except Exception:
        return {}, file_id


def save_preferences(service, file_id, data):
    """Salva preferências de tons no Drive."""
    import json
    from googleapiclient.http import MediaIoBaseUpload
    content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/json")
    service.files().update(fileId=file_id, media_body=media).execute()


# ─── Compartilhamento de repertórios ────────────────────────────────────────

SHARES_FILENAME = "_shares.json"

def _find_json_file(service, name, parent_id):
    """Retorna file_id se o arquivo existir, ou None. Nunca cria."""
    resp = (
        service.files()
        .list(
            q=f"name='{name}' and '{parent_id}' in parents and trashed=false",
            fields="files(id)",
        )
        .execute()
    )
    files = resp.get("files", [])
    return files[0]["id"] if files else None


def load_shares(service, root_folder_id):
    """Carrega dict de shares do Drive. Retorna (data, file_id).
    Usa find-only (sem create) para funcionar com credenciais read-only."""
    import json
    file_id = _find_json_file(service, SHARES_FILENAME, root_folder_id)
    if not file_id:
        return {}, None
    try:
        content = download_bytes(service, file_id)
        return json.loads(content.decode("utf-8") or "{}"), file_id
    except Exception:
        return {}, file_id


def save_shares(service, file_id, data):
    """Salva dict de shares no Drive."""
    import json
    from googleapiclient.http import MediaIoBaseUpload
    content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/json")
    service.files().update(fileId=file_id, media_body=media).execute()


# ─── Metadados globais de músicas ───────────────────────────────────────────

SONGS_META_FILENAME = "_songs_meta.json"

def load_songs_meta(service, root_folder_id):
    """Carrega dict de metadados globais do Drive. Retorna (data, file_id).
    Estrutura: { "<fileId>": { "artist": "", "key": "", "capo": "", "youtube": "" } }
    """
    import json
    file_id = _get_or_create_json_file(service, SONGS_META_FILENAME, root_folder_id)
    try:
        content = download_bytes(service, file_id)
        return json.loads(content.decode("utf-8") or "{}"), file_id
    except Exception:
        return {}, file_id


def save_songs_meta(service, file_id, data):
    """Salva dict de metadados globais no Drive."""
    import json
    from googleapiclient.http import MediaIoBaseUpload
    content = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype="application/json")
    service.files().update(fileId=file_id, media_body=media).execute()


# ─── Upload ──────────────────────────────────────────────────────────────────

def update_md_content(service, file_id, content):
    """Atualiza o conteúdo de um arquivo .md existente no Drive."""
    from googleapiclient.http import MediaIoBaseUpload

    media = MediaIoBaseUpload(
        io.BytesIO(content.encode("utf-8")), mimetype="text/markdown"
    )
    service.files().update(fileId=file_id, media_body=media).execute()


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

def get_file_name(service, file_id):
    """Retorna o nome real (com extensão) do arquivo no Drive."""
    f = service.files().get(fileId=file_id, fields="name").execute()
    return f.get("name", "")


def trash_file(service, file_id):
    """Move arquivo para a lixeira do Drive."""
    service.files().update(fileId=file_id, body={"trashed": True}).execute()


def rename_file(service, file_id, new_name_with_ext):
    """Renomeia arquivo no Drive."""
    service.files().update(fileId=file_id, body={"name": new_name_with_ext}).execute()


def copy_file(service, file_id, new_name, target_folder_id):
    """Copia arquivo para outra pasta no Drive."""
    body = {"name": new_name, "parents": [target_folder_id]}
    return service.files().copy(fileId=file_id, body=body, fields="id").execute()


def create_shortcut(service, name, target_id, target_folder_id):
    """Cria um atalho do Drive apontando para target_id dentro de target_folder_id."""
    body = {
        "name": name,
        "mimeType": SHORTCUT_MIME,
        "shortcutDetails": {"targetId": target_id},
        "parents": [target_folder_id],
    }
    return service.files().create(body=body, fields="id").execute()


def find_shortcuts_to(service, target_id):
    """Retorna lista de IDs de atalhos que apontam para target_id."""
    results = []
    page_token = None
    q = f"mimeType='{SHORTCUT_MIME}' and shortcutDetails.targetId='{target_id}' and trashed=false"
    while True:
        resp = service.files().list(
            q=q,
            fields="nextPageToken, files(id)",
            pageToken=page_token,
        ).execute()
        results.extend(f["id"] for f in resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


def move_file(service, file_id, source_folder_id, target_folder_id):
    """Move arquivo entre pastas no Drive."""
    service.files().update(
        fileId=file_id,
        addParents=target_folder_id,
        removeParents=source_folder_id,
        fields="id",
    ).execute()


def find_folder_by_name(service, name, parent_id):
    """Retorna file_id de uma pasta pelo nome dentro do parent, ou None."""
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
    return files[0]["id"] if files else None


def create_folder(service, name, parent_id):
    """Cria nova pasta. Retorna {id, name}."""
    metadata = {"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]}
    return service.files().create(body=metadata, fields="id,name").execute()


def rename_folder(service, folder_id, new_name):
    """Renomeia pasta."""
    service.files().update(fileId=folder_id, body={"name": new_name}).execute()


def is_folder_empty(service, folder_id):
    """Retorna True se a pasta não tiver nenhum item não-trashado."""
    resp = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id)",
            pageSize=1,
        )
        .execute()
    )
    return len(resp.get("files", [])) == 0


def delete_folder(service, folder_id):
    """Move pasta para a lixeira do Drive."""
    service.files().update(fileId=folder_id, body={"trashed": True}).execute()


def get_user_data_folder(service):
    """Retorna/cria pasta _mycifras_data na raiz do Drive do usuário logado."""
    resp = (
        service.files()
        .list(
            q=(
                f"name='{_USERDATA_FOLDER}' and 'root' in parents "
                f"and mimeType='{FOLDER_MIME}' and trashed=false"
            ),
            fields="files(id)",
        )
        .execute()
    )
    files = resp.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {"name": _USERDATA_FOLDER, "mimeType": FOLDER_MIME, "parents": ["root"]}
    f = service.files().create(body=metadata, fields="id").execute()
    return f.get("id")


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
    Suporta categoria composta "Cat > SubCat" para estrutura de 3 níveis.
    """
    section_id = get_or_create_folder(service, section, root_folder_id)
    if not category or category == "_raiz":
        return section_id
    if " > " in category:
        cat_name, subcat_name = category.split(" > ", 1)
        cat_id = get_or_create_folder(service, cat_name, section_id)
        return get_or_create_folder(service, subcat_name, cat_id)
    return get_or_create_folder(service, category, section_id)


# ─── Busca full-text ─────────────────────────────────────────────────────────

def search_content(service, query, root_folder_id, max_results=50):
    """Busca arquivos dentro da pasta raiz cujo conteúdo contém `query`.
    Retorna lista de { fileId, name, mimeType, excerpt }.
    """
    # Drive fullText contains busca no conteúdo indexado dos arquivos
    safe_q = query.replace("'", "\\'")
    q = (
        f"fullText contains '{safe_q}' "
        f"and '{root_folder_id}' in parents "
        f"and trashed=false"
    )
    # A fullText contains não funciona com hierarquia profunda via 'in parents'.
    # Precisamos buscar em todo o Drive limitando ao domínio da pasta raiz via
    # uma query mais ampla e depois filtrar. Mas a API não suporta "ancestors in".
    # Alternativa: buscar sem o filtro de parent e filtrar pelos IDs que aparecem
    # na biblioteca já carregada no caller. Aqui fazemos a busca ampla.
    q_broad = f"fullText contains '{safe_q}' and trashed=false and mimeType != '{FOLDER_MIME}'"
    results = []
    page_token = None
    while len(results) < max_results:
        resp = (
            service.files()
            .list(
                q=q_broad,
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
                pageSize=min(max_results - len(results), 100),
            )
            .execute()
        )
        for f in resp.get("files", []):
            if not _is_supported(f):
                continue
            results.append({
                "fileId": f["id"],
                "name": Path(f["name"]).stem,
                "mimeType": f["mimeType"],
                "excerpt": "",
            })
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


# ─── Scan biblioteca ─────────────────────────────────────────────────────────

def _is_supported(f):
    mime = f.get("mimeType", "")
    if mime == SHORTCUT_MIME:
        # atalhos são suportados se o alvo for um formato suportado
        target_mime = (f.get("shortcutDetails") or {}).get("targetMimeType", "")
        ext = Path(f.get("name", "")).suffix.lower()
        return target_mime in SUPPORTED_MIMES or ext in SUPPORTED_EXTENSIONS or target_mime == GDOCS_MIME
    ext = Path(f.get("name", "")).suffix.lower()
    return mime in SUPPORTED_MIMES or ext in SUPPORTED_EXTENSIONS or mime == GDOCS_MIME


def _resolve_file_entry(f, section, category):
    """Converte um item do Drive num dicionário de música, resolvendo atalhos."""
    if f["mimeType"] == SHORTCUT_MIME:
        details = f.get("shortcutDetails") or {}
        return {
            "name": Path(f["name"]).stem,
            "fileId": details.get("targetId", f["id"]),
            "mimeType": details.get("targetMimeType", ""),
            "modifiedTime": f.get("modifiedTime", ""),
            "section": section,
            "category": category,
            "isShortcut": True,
            "shortcutFileId": f["id"],
        }
    return {
        "name": Path(f["name"]).stem,
        "fileId": f["id"],
        "mimeType": f["mimeType"],
        "modifiedTime": f.get("modifiedTime", ""),
        "section": section,
        "category": category,
    }


def _collect_songs(service, folder_id, section, category):
    return [
        _resolve_file_entry(f, section, category)
        for f in list_folder(service, folder_id)
        if f["mimeType"] != FOLDER_MIME and _is_supported(f)
    ]


def scan_library(service, root_folder_id):
    """Escaneia a estrutura de pastas no Drive e retorna a biblioteca.

    Suporta até 3 níveis: seção → categoria → subcategoria.
    Quando uma categoria contém sub-pastas, as chaves do dict usam o separador
    ' > ', ex: 'Tempo Comum > Entrada'. Músicas diretamente na pasta da categoria
    ficam sob a chave simples 'Tempo Comum'.
    """
    library = {}
    for section in list_folder(service, root_folder_id):
        if section["mimeType"] != FOLDER_MIME:
            continue
        sname = section["name"]
        library[sname] = {}
        for item in list_folder(service, section["id"]):
            if item["mimeType"] == FOLDER_MIME:
                cat_name = item["name"]
                cat_items = list_folder(service, item["id"])
                direct_songs = [
                    _resolve_file_entry(f, sname, cat_name)
                    for f in cat_items
                    if f["mimeType"] != FOLDER_MIME and _is_supported(f)
                ]
                sub_folders = [f for f in cat_items if f["mimeType"] == FOLDER_MIME]
                library[sname][cat_name] = direct_songs
                for sub in sub_folders:
                    sub_key = cat_name + " > " + sub["name"]
                    library[sname][sub_key] = _collect_songs(service, sub["id"], sname, sub_key)
            elif _is_supported(item):
                library[sname].setdefault("_raiz", [])
                library[sname]["_raiz"].append(_resolve_file_entry(item, sname, "_raiz"))
    return library

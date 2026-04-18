import json
import os
import re
import tempfile
import threading
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, Response, session

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-insecure-key-troque-no-env")

# Confia nos headers X-Forwarded-Proto/Host do ngrok/proxy reverso
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

CIFRAS_ROOT = os.environ.get("CIFRAS_ROOT", str(Path.home() / "OneDrive" / "Cifras"))
CIFRAS_FOLDER_ID = os.environ.get("CIFRAS_FOLDER_ID", "")
SUPPORTED_EXTENSIONS = {".docx", ".doc", ".pdf", ".txt", ".md"}

# Registra blueprint de autenticação
from auth import bp as auth_bp, login_required, get_service, current_user, is_oauth_configured
app.register_blueprint(auth_bp)


# ---------------------------------------------------------------------------
# Modo de operação
# ---------------------------------------------------------------------------

def _use_drive():
    """Drive ativo se OAuth configurado E CIFRAS_FOLDER_ID definido."""
    return is_oauth_configured() and bool(CIFRAS_FOLDER_ID)


_AUTH_ERROR_SIGNALS = (
    "invalid_grant", "token has been expired", "token has been revoked",
    "unauthorized", "401", "revoked", "invalid_token",
)

def _is_auth_error(e):
    full = (str(e) + " " + str(getattr(e, "__cause__", "") or "")).lower()
    return any(s in full for s in _AUTH_ERROR_SIGNALS)

def _auth_error_response():
    session.clear()
    return jsonify({"error": "Sessão expirada", "login_url": "/login"}), 401


# ---------------------------------------------------------------------------
# Extração de texto — por bytes
# ---------------------------------------------------------------------------

def extract_text_from_bytes(content_bytes, extension):
    ext = extension.lower()
    if ext in (".docx", ".doc"):
        return _docx_from_bytes(content_bytes)
    elif ext == ".pdf":
        return _pdf_from_bytes(content_bytes)
    elif ext in (".txt", ".md"):
        text = content_bytes.decode("utf-8", errors="replace")
        return _strip_frontmatter(text)
    return "[Formato não suportado]"


def _docx_from_bytes(content_bytes):
    try:
        import io as _io
        from docx import Document
        from docx.oxml.ns import qn

        doc = Document(_io.BytesIO(content_bytes))
        lines = []

        for element in doc.element.body:
            tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

            if tag == "p":
                # Parágrafo normal
                text = "".join(n.text or "" for n in element.iter() if n.tag.endswith("}t"))
                lines.append(text)

            elif tag == "tbl":
                # Tabela — lê cada linha juntando células com espaço
                for row in element.findall(".//" + qn("w:tr")):
                    cells = []
                    for cell in row.findall(".//" + qn("w:tc")):
                        cell_text = "".join(
                            n.text or "" for n in cell.iter() if n.tag.endswith("}t")
                        )
                        if cell_text.strip():
                            cells.append(cell_text.strip())
                    if cells:
                        lines.append("   ".join(cells))

        return "\n".join(lines)
    except Exception:
        return _docx_via_com(content_bytes)


def _docx_via_com(content_bytes):
    tmp_path = None
    try:
        import win32com.client
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as tmp:
            tmp.write(content_bytes)
            tmp_path = tmp.name
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        doc = word.Documents.Open(str(Path(tmp_path).resolve()), ReadOnly=True)
        text = doc.Content.Text
        doc.Close(False)
        word.Quit()
        return text
    except ImportError:
        return "[Erro: .doc binário não suportado. Instale pywin32.]"
    except Exception as e:
        return f"[Erro ao ler via Word COM: {e}]"
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def _pdf_from_bytes(content_bytes):
    try:
        import io as _io
        import fitz
        doc = fitz.open(stream=_io.BytesIO(content_bytes), filetype="pdf")
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages)
    except Exception as e:
        return f"[Erro ao ler .pdf: {e}]"


def _strip_frontmatter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text


def _parse_frontmatter(text):
    """Retorna (body, meta_dict) extraindo YAML frontmatter simples."""
    meta = {"artist": "", "key": "", "title": "", "tags": []}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    key = k.strip().lower()
                    val = v.strip().strip('"').strip("'")
                    if key == "tags":
                        # Parse simple YAML list: [a, b, c] or a, b, c
                        val = val.strip("[]")
                        meta["tags"] = [t.strip() for t in val.split(",") if t.strip()] if val else []
                    else:
                        meta[key] = val
            return parts[2].strip(), meta
    return text, meta


# ---------------------------------------------------------------------------
# Extração de texto — por caminho local
# ---------------------------------------------------------------------------

def extract_text(path):
    try:
        content_bytes = Path(path).read_bytes()
        return extract_text_from_bytes(content_bytes, Path(path).suffix)
    except Exception as e:
        return f"[Erro ao ler arquivo: {e}]"


# ---------------------------------------------------------------------------
# Biblioteca local
# ---------------------------------------------------------------------------

def _md_meta(path):
    """Lê apenas o frontmatter de um .md sem carregar o corpo inteiro."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(1024)
        _, meta = _parse_frontmatter(head)
        return meta
    except Exception:
        return {"artist": "", "key": "", "title": ""}


def _song_entry(f, section, category, read_meta=False):
    entry = {"name": f.stem, "path": str(f), "section": section, "category": category,
             "artist": "", "key": ""}
    if read_meta and f.suffix.lower() == ".md":
        meta = _md_meta(f)
        entry["artist"] = meta.get("artist", "")
        entry["key"] = meta.get("key", "")
        if meta.get("title"):
            entry["name"] = meta["title"]
    return entry


def scan_library_local():
    root = Path(CIFRAS_ROOT)
    library = {}
    if not root.exists():
        return library
    for section_dir in sorted(root.iterdir()):
        if not section_dir.is_dir():
            continue
        sname = section_dir.name
        library[sname] = {}
        for item in sorted(section_dir.iterdir()):
            if item.is_dir():
                songs = _collect_local(item, sname, item.name)
                if songs:
                    library[sname][item.name] = songs
            elif item.suffix.lower() in SUPPORTED_EXTENSIONS:
                library[sname].setdefault("_raiz", [])
                library[sname]["_raiz"].append(_song_entry(item, sname, "_raiz", read_meta=False))
    return library


def _collect_local(folder, section, category):
    return [
        _song_entry(f, section, category, read_meta=False)
        for f in sorted(folder.iterdir())
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def flatten_songs(library):
    return [song for cats in library.values() for songs in cats.values() for song in songs]


# ---------------------------------------------------------------------------
# Repertórios (persistidos em arquivo JSON)
# ---------------------------------------------------------------------------

REPERTORIOS_LOCAL = Path(__file__).parent / "_repertorios.json"
_rep_lock = threading.Lock()

def _load_reps_local():
    try:
        return json.loads(REPERTORIOS_LOCAL.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_reps_local(data):
    REPERTORIOS_LOCAL.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _load_reps():
    if _use_drive():
        import drive as drv
        data, _ = drv.load_repertorios(get_service(), CIFRAS_FOLDER_ID)
        return data
    return _load_reps_local()

def _save_reps(data):
    if _use_drive():
        import drive as drv
        svc = get_service()
        _, file_id = drv.load_repertorios(svc, CIFRAS_FOLDER_ID)
        drv.save_repertorios(svc, file_id, data)
    else:
        _save_reps_local(data)


@app.route("/api/repertorios", methods=["GET"])
@login_required
def api_reps_list():
    try:
        return jsonify(_load_reps())
    except Exception as e:
        if _is_auth_error(e):
            return _auth_error_response()
        return jsonify({"error": str(e)}), 500


@app.route("/api/repertorios", methods=["POST"])
@login_required
def api_reps_create():
    from datetime import datetime
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    songs = data.get("songs", [])
    if not name:
        return jsonify({"error": "Nome obrigatório"}), 400
    rep_id = "rpt_" + os.urandom(6).hex()
    now = datetime.utcnow().isoformat()
    rep = {"id": rep_id, "name": name, "songs": songs, "created_at": now, "updated_at": now}
    with _rep_lock:
        reps = _load_reps()
        reps[rep_id] = rep
        _save_reps(reps)
    return jsonify(rep), 201


@app.route("/api/repertorios/<rep_id>", methods=["PUT"])
@login_required
def api_reps_update(rep_id):
    from datetime import datetime
    data = request.get_json(force=True)
    with _rep_lock:
        reps = _load_reps()
        if rep_id not in reps:
            return jsonify({"error": "Não encontrado"}), 404
        if "name" in data:
            reps[rep_id]["name"] = data["name"].strip() or reps[rep_id]["name"]
        if "songs" in data:
            reps[rep_id]["songs"] = data["songs"]
        reps[rep_id]["updated_at"] = datetime.utcnow().isoformat()
        _save_reps(reps)
    return jsonify(reps[rep_id])


@app.route("/api/repertorios/<rep_id>", methods=["DELETE"])
@login_required
def api_reps_delete(rep_id):
    with _rep_lock:
        reps = _load_reps()
        if rep_id not in reps:
            return jsonify({"error": "Não encontrado"}), 404
        del reps[rep_id]
        _save_reps(reps)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Views tracking (persistido em views.json com lock para concorrência)
# ---------------------------------------------------------------------------

_views_lock = threading.Lock()   # protege contra escrita simultânea
_views_cache = {"data": None, "file_id": None}  # cache em memória para evitar leitura a cada request

def _load_views():
    """Carrega views do Drive (com cache em memória). Thread-safe para leitura."""
    if _views_cache["data"] is not None:
        return _views_cache["data"]
    if _use_drive():
        try:
            import drive as _drive
            data, file_id = _drive.load_views(get_service(), CIFRAS_FOLDER_ID)
            _views_cache["data"] = data
            _views_cache["file_id"] = file_id
            return data
        except Exception:
            return {}
    # fallback local (modo dev sem Drive)
    try:
        p = Path(__file__).parent / "views.json"
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _increment_view(key: str) -> int:
    """Incrementa o contador de uma música e persiste no Drive. Retorna o novo valor."""
    with _views_lock:
        if _use_drive():
            try:
                import drive as _drive
                svc = get_service()
                # Garante que temos o file_id
                if _views_cache["file_id"] is None:
                    data, file_id = _drive.load_views(svc, CIFRAS_FOLDER_ID)
                    _views_cache["data"] = data
                    _views_cache["file_id"] = file_id
                views = _views_cache["data"] if _views_cache["data"] is not None else {}
                views[key] = views.get(key, 0) + 1
                _views_cache["data"] = views
                _drive.save_views(svc, _views_cache["file_id"], views)
                return views[key]
            except Exception as e:
                app.logger.error("Erro ao salvar view no Drive: %s", e)
                return 0
        else:
            # fallback local
            p = Path(__file__).parent / "views.json"
            try:
                views = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                views = {}
            views[key] = views.get(key, 0) + 1
            p.write_text(json.dumps(views, ensure_ascii=False), encoding="utf-8")
            return views[key]

def _song_key(data):
    return data.get("fileId") or data.get("path", "")


# ---------------------------------------------------------------------------
# Preferências de tons (persistido em _preferences.json no Drive)
# ---------------------------------------------------------------------------

_prefs_lock = threading.Lock()
_prefs_cache = {"data": None, "file_id": None}

VALID_SLOTS = {"my_key", "original_key", "alt_key"}


def _load_prefs():
    if _prefs_cache["data"] is not None:
        return _prefs_cache["data"]
    if _use_drive():
        try:
            import drive as _drive
            data, file_id = _drive.load_preferences(get_service(), CIFRAS_FOLDER_ID)
            _prefs_cache["data"] = data
            _prefs_cache["file_id"] = file_id
            return data
        except Exception:
            pass
    return {}


def _save_prefs(data):
    import drive as _drive
    with _prefs_lock:
        if _use_drive():
            svc = get_service()
            if _prefs_cache["file_id"] is None:
                _, file_id = _drive.load_preferences(svc, CIFRAS_FOLDER_ID)
                _prefs_cache["file_id"] = file_id
            _drive.save_preferences(svc, _prefs_cache["file_id"], data)
        _prefs_cache["data"] = data


@app.route("/api/preferences")
@login_required
def api_get_preferences():
    """Retorna todas as preferências de tons ou as de uma música específica."""
    file_id = request.args.get("fileId", "")
    try:
        prefs = _load_prefs()
        if file_id:
            return jsonify(prefs.get(file_id, {}))
        return jsonify(prefs)
    except Exception as e:
        if _is_auth_error(e):
            return _auth_error_response()
        return jsonify({"error": str(e)}), 500


@app.route("/api/preferences", methods=["POST"])
@login_required
def api_save_preference():
    """Salva/atualiza um tom em um slot. Body: { fileId, slot, key }"""
    data = request.get_json() or {}
    file_id = data.get("fileId", "").strip()
    slot = data.get("slot", "").strip()
    key = data.get("key", "").strip()
    if not file_id or slot not in VALID_SLOTS or not key:
        return jsonify({"error": "fileId, slot e key são obrigatórios"}), 400
    try:
        prefs = dict(_load_prefs())
        song_prefs = dict(prefs.get(file_id, {}))
        song_prefs[slot] = key
        prefs[file_id] = song_prefs
        _save_prefs(prefs)
        return jsonify(song_prefs)
    except Exception as e:
        if _is_auth_error(e):
            return _auth_error_response()
        return jsonify({"error": str(e)}), 500


@app.route("/api/preferences", methods=["DELETE"])
@login_required
def api_delete_preference():
    """Remove um slot de tom. Body: { fileId, slot } ou { fileId } para remover tudo."""
    data = request.get_json() or {}
    file_id = data.get("fileId", "").strip()
    slot = data.get("slot", "").strip()
    if not file_id:
        return jsonify({"error": "fileId é obrigatório"}), 400
    try:
        prefs = dict(_load_prefs())
        if file_id not in prefs:
            return jsonify({})
        song_prefs = dict(prefs[file_id])
        if slot and slot in VALID_SLOTS:
            song_prefs.pop(slot, None)
        else:
            song_prefs = {}
        if song_prefs:
            prefs[file_id] = song_prefs
        else:
            prefs.pop(file_id, None)
        _save_prefs(prefs)
        return jsonify(song_prefs)
    except Exception as e:
        if _is_auth_error(e):
            return _auth_error_response()
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Cache de biblioteca (evita re-scan a cada request)
# ---------------------------------------------------------------------------

_library_cache = {"data": None, "ts": 0}
_cache_lock = threading.Lock()
CACHE_TTL = 120  # segundos — re-escaneia se a última leitura foi há mais de 2 min

def _get_library():
    """Retorna a biblioteca escaneada, usando cache quando possível."""
    now = time.monotonic()
    with _cache_lock:
        if _library_cache["data"] is None or (now - _library_cache["ts"]) > CACHE_TTL:
            try:
                if _use_drive():
                    import drive
                    data = drive.scan_library(get_service(), CIFRAS_FOLDER_ID)
                else:
                    data = scan_library_local()
                _library_cache["data"] = data
                _library_cache["ts"] = now
            except Exception as e:
                app.logger.error("Erro ao escanear biblioteca: %s", e)
                # Se já tinha cache antigo, retorna ele em vez de falhar
                if _library_cache["data"] is not None:
                    return _library_cache["data"]
                raise
        return _library_cache["data"]

def invalidate_library_cache():
    with _cache_lock:
        _library_cache["data"] = None


# ---------------------------------------------------------------------------
# Pastas (criar, renomear, excluir categorias)
# ---------------------------------------------------------------------------

@app.route("/api/folders", methods=["POST"])
@login_required
def api_folder_create():
    """Cria nova categoria dentro de uma seção."""
    data = request.get_json(force=True)
    section = (data.get("section") or "").strip()
    name = (data.get("name") or "").strip()
    if not section or not name:
        return jsonify({"error": "section e name obrigatórios"}), 400

    if _use_drive():
        import drive as drv
        svc = get_service()
        section_id = drv.find_folder_by_name(svc, section, CIFRAS_FOLDER_ID)
        if not section_id:
            return jsonify({"error": f"Seção '{section}' não encontrada"}), 404
        if drv.find_folder_by_name(svc, name, section_id):
            return jsonify({"error": "Categoria já existe"}), 409
        drv.create_folder(svc, name, section_id)
    else:
        folder_path = Path(CIFRAS_ROOT) / section / name
        if not (Path(CIFRAS_ROOT) / section).exists():
            return jsonify({"error": f"Seção '{section}' não encontrada"}), 404
        if folder_path.exists():
            return jsonify({"error": "Categoria já existe"}), 409
        folder_path.mkdir(parents=False)

    invalidate_library_cache()
    return jsonify({"ok": True, "section": section, "name": name}), 201


@app.route("/api/folders/<path:section>/<path:category>", methods=["PUT"])
@login_required
def api_folder_rename(section, category):
    """Renomeia uma categoria."""
    data = request.get_json(force=True)
    new_name = (data.get("newName") or "").strip()
    if not new_name:
        return jsonify({"error": "newName obrigatório"}), 400

    if _use_drive():
        import drive as drv
        svc = get_service()
        section_id = drv.find_folder_by_name(svc, section, CIFRAS_FOLDER_ID)
        if not section_id:
            return jsonify({"error": "Seção não encontrada"}), 404
        folder_id = drv.find_folder_by_name(svc, category, section_id)
        if not folder_id:
            return jsonify({"error": "Categoria não encontrada"}), 404
        if drv.find_folder_by_name(svc, new_name, section_id):
            return jsonify({"error": "Já existe categoria com esse nome"}), 409
        drv.rename_folder(svc, folder_id, new_name)
    else:
        old_path = Path(CIFRAS_ROOT) / section / category
        new_path = Path(CIFRAS_ROOT) / section / new_name
        if not old_path.exists():
            return jsonify({"error": "Categoria não encontrada"}), 404
        if new_path.exists():
            return jsonify({"error": "Já existe categoria com esse nome"}), 409
        old_path.rename(new_path)

    invalidate_library_cache()
    return jsonify({"ok": True, "newName": new_name})


@app.route("/api/folders/<path:section>/<path:category>", methods=["DELETE"])
@login_required
def api_folder_delete(section, category):
    """Exclui uma categoria — apenas se estiver vazia."""
    if _use_drive():
        import drive as drv
        svc = get_service()
        section_id = drv.find_folder_by_name(svc, section, CIFRAS_FOLDER_ID)
        if not section_id:
            return jsonify({"error": "Seção não encontrada"}), 404
        folder_id = drv.find_folder_by_name(svc, category, section_id)
        if not folder_id:
            return jsonify({"error": "Categoria não encontrada"}), 404
        if not drv.is_folder_empty(svc, folder_id):
            return jsonify({"error": "A pasta não está vazia"}), 409
        drv.delete_folder(svc, folder_id)
    else:
        folder_path = Path(CIFRAS_ROOT) / section / category
        if not folder_path.exists():
            return jsonify({"error": "Categoria não encontrada"}), 404
        if any(folder_path.iterdir()):
            return jsonify({"error": "A pasta não está vazia"}), 409
        folder_path.rmdir()

    invalidate_library_cache()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Operações em arquivos de cifra (renomear, excluir, copiar, mover)
# ---------------------------------------------------------------------------

@app.route("/api/songs/delete", methods=["POST"])
@login_required
def api_song_delete():
    data = request.get_json(force=True)
    file_id = (data.get("fileId") or "").strip()
    path = (data.get("path") or "").strip()
    if file_id:
        import drive as drv
        drv.trash_file(get_service(), file_id)
    elif path:
        if not is_safe_path(path):
            return jsonify({"error": "Caminho não permitido"}), 403
        p = Path(path)
        if not p.exists():
            return jsonify({"error": "Arquivo não encontrado"}), 404
        p.unlink()
    else:
        return jsonify({"error": "fileId ou path obrigatório"}), 400
    invalidate_library_cache()
    return jsonify({"ok": True})


@app.route("/api/songs/rename", methods=["POST"])
@login_required
def api_song_rename():
    data = request.get_json(force=True)
    file_id = (data.get("fileId") or "").strip()
    path = (data.get("path") or "").strip()
    new_name = (data.get("newName") or "").strip()
    if not new_name:
        return jsonify({"error": "newName obrigatório"}), 400
    if file_id:
        import drive as drv
        svc = get_service()
        current = drv.get_file_name(svc, file_id)
        ext = Path(current).suffix or ".md"
        drv.rename_file(svc, file_id, new_name + ext)
    elif path:
        if not is_safe_path(path):
            return jsonify({"error": "Caminho não permitido"}), 403
        p = Path(path)
        if not p.exists():
            return jsonify({"error": "Arquivo não encontrado"}), 404
        new_path = p.parent / (new_name + p.suffix)
        if new_path.exists():
            return jsonify({"error": "Já existe arquivo com esse nome"}), 409
        p.rename(new_path)
    else:
        return jsonify({"error": "fileId ou path obrigatório"}), 400
    invalidate_library_cache()
    return jsonify({"ok": True})


@app.route("/api/songs/copy", methods=["POST"])
@login_required
def api_song_copy():
    import shutil
    data = request.get_json(force=True)
    file_id = (data.get("fileId") or "").strip()
    path = (data.get("path") or "").strip()
    target_section = (data.get("targetSection") or "").strip()
    target_category = (data.get("targetCategory") or "").strip()
    if not target_section:
        return jsonify({"error": "targetSection obrigatório"}), 400
    if file_id:
        import drive as drv
        svc = get_service()
        target_id = drv.resolve_folder(svc, target_section, target_category or None, CIFRAS_FOLDER_ID)
        fname = drv.get_file_name(svc, file_id)
        drv.copy_file(svc, file_id, fname, target_id)
    elif path:
        if not is_safe_path(path):
            return jsonify({"error": "Caminho não permitido"}), 403
        src = Path(path)
        if not src.exists():
            return jsonify({"error": "Arquivo não encontrado"}), 404
        dest_dir = Path(CIFRAS_ROOT) / target_section / target_category if target_category else Path(CIFRAS_ROOT) / target_section
        if not dest_dir.exists():
            return jsonify({"error": "Pasta destino não encontrada"}), 404
        dest = dest_dir / src.name
        if dest.exists():
            return jsonify({"error": "Já existe arquivo com esse nome no destino"}), 409
        shutil.copy2(str(src), str(dest))
    else:
        return jsonify({"error": "fileId ou path obrigatório"}), 400
    invalidate_library_cache()
    return jsonify({"ok": True})


@app.route("/api/songs/move", methods=["POST"])
@login_required
def api_song_move():
    import shutil
    data = request.get_json(force=True)
    file_id = (data.get("fileId") or "").strip()
    path = (data.get("path") or "").strip()
    source_section = (data.get("sourceSection") or "").strip()
    source_category = (data.get("sourceCategory") or "").strip()
    target_section = (data.get("targetSection") or "").strip()
    target_category = (data.get("targetCategory") or "").strip()
    if not target_section:
        return jsonify({"error": "targetSection obrigatório"}), 400
    if file_id:
        import drive as drv
        svc = get_service()
        source_id = drv.resolve_folder(svc, source_section, source_category or None, CIFRAS_FOLDER_ID)
        target_id = drv.resolve_folder(svc, target_section, target_category or None, CIFRAS_FOLDER_ID)
        drv.move_file(svc, file_id, source_id, target_id)
    elif path:
        if not is_safe_path(path):
            return jsonify({"error": "Caminho não permitido"}), 403
        src = Path(path)
        if not src.exists():
            return jsonify({"error": "Arquivo não encontrado"}), 404
        dest_dir = Path(CIFRAS_ROOT) / target_section / target_category if target_category else Path(CIFRAS_ROOT) / target_section
        if not dest_dir.exists():
            return jsonify({"error": "Pasta destino não encontrada"}), 404
        dest = dest_dir / src.name
        if dest.exists():
            return jsonify({"error": "Já existe arquivo com esse nome no destino"}), 409
        shutil.move(str(src), str(dest))
    else:
        return jsonify({"error": "fileId ou path obrigatório"}), 400
    invalidate_library_cache()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------

def is_safe_path(path_str):
    try:
        return Path(path_str).resolve().is_relative_to(Path(CIFRAS_ROOT).resolve())
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_CHORD_WORD_RE = re.compile(r'^[A-G][b#]?(?:m|maj|min|dim|aug|sus|add|[0-9]|/[A-G][b#]?)*$')

def _is_chord_line(line: str) -> bool:
    words = line.strip().split()
    if not words:
        return False
    matches = sum(1 for w in words if _CHORD_WORD_RE.match(re.sub(r'[()[\]]', '', w)))
    return matches / len(words) >= 0.5


def _render_cifra_html(text: str) -> str:
    """Converte texto de cifra em HTML com linhas de acordes coloridas."""
    lines = []
    for line in text.split("\n"):
        if _is_chord_line(line):
            lines.append('<span class="chord-line">' + _esc(line) + '</span>')
        else:
            lines.append(_esc(line))
    return "\n".join(lines)


def _mime_to_ext(mime):
    return {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/msword": ".doc",
        "application/pdf": ".pdf",
        "text/plain": ".txt",
        "text/markdown": ".md",
    }.get(mime, ".txt")


# ---------------------------------------------------------------------------
# Keep-alive — evita spin-down do Render free tier (idle após 15 min)
# ---------------------------------------------------------------------------

@app.route("/ping")
def ping():
    return "ok", 200


def _start_keep_alive():
    external_url = os.environ.get("EXTERNAL_URL", "").rstrip("/")
    if not external_url:
        return

    import requests as _req

    def _loop():
        while True:
            time.sleep(14 * 60)
            try:
                _req.get(external_url + "/ping", timeout=10)
            except Exception:
                pass

    threading.Thread(target=_loop, daemon=True).start()


_start_keep_alive()


# ---------------------------------------------------------------------------
# Rotas principais
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    # Modo local (sem OAuth): vai direto para o app
    if not is_oauth_configured():
        return render_template("index.html", user={})
    # OAuth configurado: se autenticado vai para o app, senão mostra landing
    if session.get("token"):
        user = current_user()
        return render_template("index.html", user=user)
    return render_template("landing.html")


@app.route("/api/library")
@login_required
def api_library():
    try:
        return jsonify(_get_library())
    except Exception as e:
        err = str(e)
        cause = str(e.__cause__) if getattr(e, "__cause__", None) else ""
        full = (err + " " + cause).lower()
        app.logger.error("api_library falhou: %s | causa: %s", err, cause)
        _AUTH_SIGNALS = ("invalid_grant", "token has been expired", "sessão expirada",
                         "unauthorized", "401", "revoked", "invalid_token")
        if any(s in full for s in _AUTH_SIGNALS):
            session.clear()
            return jsonify({"error": "Sessão expirada", "login_url": "/login"}), 401
        return jsonify({"error": f"Erro ao carregar biblioteca: {err}"}), 500


@app.route("/api/songs")
@login_required
def api_songs():
    views = _load_views()
    songs = []
    for s in flatten_songs(_get_library()):
        # Lê frontmatter lazy: só para .md locais sem metadados ainda
        if not s.get("artist") and not s.get("key") and s.get("path","").endswith(".md"):
            meta = _md_meta(s["path"])
            s["artist"] = meta.get("artist", "")
            s["key"] = meta.get("key", "")
            if meta.get("title"):
                s["name"] = meta["title"]
        s["views"] = views.get(_song_key(s), 0)
        songs.append(s)
    return jsonify(songs)


@app.route("/api/track_view", methods=["POST"])
@login_required
def api_track_view():
    data = request.get_json(force=True)
    key = _song_key(data)
    if not key:
        return jsonify({"error": "fileId ou path obrigatório"}), 400
    new_count = _increment_view(key)
    return jsonify({"views": new_count})


@app.route("/api/save_content", methods=["POST"])
@login_required
def api_save_content():
    """Salva o conteúdo editado (com ou sem transposição), preservando frontmatter."""
    data = request.get_json(force=True)
    new_body = data.get("text", "").strip()
    file_id = data.get("fileId", "").strip()
    path = data.get("path", "").strip()

    if not new_body:
        return jsonify({"error": "Texto vazio"}), 400

    if file_id:
        import drive
        svc = get_service()
        try:
            raw = drive.download_bytes(svc, file_id).decode("utf-8", errors="replace")
        except Exception:
            raw = ""
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            frontmatter = "---" + parts[1] + "---\n\n" if len(parts) >= 3 else ""
        else:
            frontmatter = ""
        try:
            drive.update_md_content(svc, file_id, frontmatter + new_body)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"ok": True})

    if path:
        try:
            abs_path = Path(path).resolve()
            root = Path(CIFRAS_ROOT).resolve()
            if root not in abs_path.parents and abs_path != root:
                return jsonify({"error": "Caminho não permitido"}), 403
        except Exception:
            return jsonify({"error": "Caminho inválido"}), 400
        if not abs_path.exists() or abs_path.suffix.lower() != ".md":
            return jsonify({"error": "Arquivo não encontrado ou não é .md"}), 404
        original = abs_path.read_text(encoding="utf-8")
        if original.startswith("---"):
            parts = original.split("---", 2)
            frontmatter = "---" + parts[1] + "---\n\n" if len(parts) >= 3 else ""
        else:
            frontmatter = ""
        abs_path.write_text(frontmatter + new_body, encoding="utf-8")
        return jsonify({"ok": True})

    return jsonify({"error": "Informe fileId ou path"}), 400


@app.route("/api/cifra")
@login_required
def api_cifra():
    file_id = request.args.get("fileId", "")
    path = request.args.get("path", "")

    if file_id:
        import drive
        mime = request.args.get("mimeType", "")
        try:
            if mime == drive.GDOCS_MIME:
                text = drive.export_gdoc_as_text(get_service(), file_id)
            else:
                content_bytes = drive.download_bytes(get_service(), file_id)
                text = extract_text_from_bytes(content_bytes, _mime_to_ext(mime))
        except Exception as e:
            if _is_auth_error(e):
                return _auth_error_response()
            return jsonify({"error": str(e)}), 500
        return jsonify({"text": text})

    if not path:
        return jsonify({"error": "path ou fileId é obrigatório"}), 400
    if not is_safe_path(path):
        return jsonify({"error": "Acesso negado"}), 403
    if not Path(path).exists():
        return jsonify({"error": "Arquivo não encontrado"}), 404

    p = Path(path)
    if p.suffix.lower() == ".md":
        raw = p.read_text(encoding="utf-8", errors="replace")
        body, meta = _parse_frontmatter(raw)
        return jsonify({"text": body, "artist": meta.get("artist",""), "key": meta.get("key",""),
                        "title": meta.get("title",""), "tags": meta.get("tags",[])})
    return jsonify({"text": extract_text(path), "artist": "", "key": "", "title": "", "tags": []})


@app.route("/api/upload", methods=["POST"])
@login_required
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    file = request.files["file"]
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return jsonify({"error": "Formato não suportado"}), 400
    text = extract_text_from_bytes(file.read(), suffix)
    return jsonify({"text": text, "name": Path(file.filename).stem})


@app.route("/api/export", methods=["POST"])
@login_required
def api_export():
    data = request.get_json(force=True)
    songs = data.get("songs", [])
    title = data.get("title", "Repertório")
    auto_print = data.get("print", False)
    today = date.today().strftime("%d/%m/%Y")

    # Inline logo SVG
    logo_path = Path(__file__).parent / "static" / "brand" / "logo-mono-dark.svg"
    try:
        logo_svg = logo_path.read_text(encoding="utf-8")
        # Remove XML comments to keep it clean inline
        import re as _re
        logo_svg = _re.sub(r'<!--.*?-->', '', logo_svg, flags=_re.DOTALL).strip()
    except Exception:
        logo_svg = ""

    def _song_card(idx, s):
        num     = idx + 1
        name    = _esc(s.get("name", ""))
        artist  = _esc((s.get("artist") or "").strip())
        category = s.get("category", "")
        key     = s.get("key", "")
        meta_parts = []
        if artist:
            meta_parts.append(f'<span class="meta-artist">{artist}</span>')
        if category:
            meta_parts.append(f'<span class="badge badge-cat">{_esc(category)}</span>')
        if key:
            meta_parts.append(f'<span class="badge badge-key">&#9835; {_esc(key)}</span>')
        meta_row = f'<div class="song-meta">{" ".join(meta_parts)}</div>' if meta_parts else ""
        cifra_html = _render_cifra_html(s.get("text", ""))
        return (
            f'<div class="song">'
            f'  <div class="song-header">'
            f'    <h2><span class="song-num">{num}.</span> {name}</h2>'
            f'  </div>'
            f'  {meta_row}'
            f'  <pre>{cifra_html}</pre>'
            f'</div>\n'
        )

    n = len(songs)
    song_word = "música" if n == 1 else "músicas"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', system-ui, sans-serif;
    background: #f4f2fa;
    color: #1a1d2e;
    max-width: 860px;
    margin: 0 auto;
    padding: 0 0 80px;
  }}

  /* ── Cabeçalho com fundo roxo ── */
  .doc-banner {{
    background: #5b4b8a;
    padding: 28px 40px 24px;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
  }}
  .doc-banner .logo svg {{ height: 32px; width: auto; filter: brightness(10); opacity: .9; }}
  .doc-banner-right {{ text-align: right; }}
  .doc-title {{
    font-size: 1.6em;
    font-weight: 800;
    letter-spacing: -.03em;
    color: #fff;
    line-height: 1.15;
  }}
  .doc-subtitle {{
    font-size: .8em;
    color: rgba(255,255,255,.65);
    margin-top: 4px;
  }}

  .doc-body {{ padding: 32px 40px 0; }}

  /* ── Song card ── */
  .song {{
    background: #fff;
    border: 1px solid #e4e0f4;
    border-radius: 12px;
    padding: 20px 24px 24px;
    margin-bottom: 24px;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  .song-header {{
    margin-bottom: 8px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ede9fa;
  }}
  .song h2 {{
    font-size: 1.05em;
    font-weight: 700;
    color: #5b4b8a;
    letter-spacing: -.015em;
    display: flex;
    align-items: baseline;
    gap: 6px;
  }}
  .song-num {{
    color: #d4af37;
    font-size: .9em;
    font-weight: 800;
    flex-shrink: 0;
  }}
  .song-meta {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }}
  .meta-artist {{
    font-size: .78em;
    font-style: italic;
    color: #7a6fa8;
  }}
  .badge {{
    font-size: .72em;
    font-weight: 600;
    padding: 2px 9px;
    border-radius: 99px;
    white-space: nowrap;
  }}
  .badge-cat {{
    background: rgba(91,75,138,.1);
    color: #5b4b8a;
    border: 1px solid rgba(91,75,138,.2);
  }}
  .badge-key {{
    background: rgba(212,175,55,.12);
    color: #9a7a10;
    border: 1px solid rgba(212,175,55,.3);
    font-weight: 700;
  }}

  /* ── Cifra ── */
  pre {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: .8em;
    line-height: 1.75;
    white-space: pre-wrap;
    word-break: break-word;
    color: #2e2645;
  }}
  .chord-line {{ color: #5b4b8a; font-weight: 700; }}

  /* ── Footer ── */
  .doc-footer {{
    margin: 40px 40px 0;
    padding-top: 14px;
    border-top: 1px solid #e2dff5;
    font-size: .73em;
    color: #b0a8cc;
    text-align: center;
  }}

  /* ── Botão voltar (mobile) ── */
  .btn-back {{
    display: none;
    position: fixed; bottom: 24px; right: 20px;
    background: #5b4b8a; color: #fff;
    border: none; border-radius: 50px;
    padding: .65rem 1.2rem;
    font-family: 'Inter', system-ui, sans-serif;
    font-size: .85rem; font-weight: 700;
    box-shadow: 0 4px 16px rgba(91,75,138,.4);
    cursor: pointer; z-index: 999;
    text-decoration: none;
    touch-action: manipulation;
  }}
  @media (max-width: 768px) {{
    .doc-banner {{ padding: 20px; }}
    .doc-body {{ padding: 20px 16px 0; }}
    .doc-footer {{ margin: 32px 16px 0; }}
    .btn-back {{ display: inline-flex; align-items: center; gap: .4rem; }}
  }}

  /* ── Print ── */
  @media print {{
    body {{ background: #fff; }}
    .doc-banner {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .badge {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .song {{ border: 1px solid #ddd; margin-bottom: 16px; }}
    .btn-back {{ display: none !important; }}
  }}
</style>
</head>
<body>

<header class="doc-banner">
  <div>
    <div class="logo">{logo_svg}</div>
  </div>
  <div class="doc-banner-right">
    <div class="doc-title">{_esc(title)}</div>
    <div class="doc-subtitle">{n} {song_word} · {_esc(today)}</div>
  </div>
</header>

<div class="doc-body">
{"".join(_song_card(i, s) for i, s in enumerate(songs))}
</div>

<footer class="doc-footer">My Cifras · gerado em {_esc(today)}</footer>

<a class="btn-back" onclick="window.close(); history.back(); return false;" href="#">← Voltar</a>

{'<script>window.onload=function(){window.print();}</script>' if auto_print else ''}
</body>
</html>"""

    return Response(html, mimetype="text/html; charset=utf-8")


# ---------------------------------------------------------------------------
# Rotas de importação
# ---------------------------------------------------------------------------

@app.route("/api/import/preview", methods=["POST"])
@login_required
def api_import_preview():
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    text = data.get("text", "").strip()

    if url:
        try:
            from scraper import fetch_cifra
            return jsonify(fetch_cifra(url))
        except Exception as e:
            return jsonify({"error": f"Não foi possível buscar a URL: {e}"}), 400

    if text:
        return jsonify({"title": "", "artist": "", "key": "", "text": text})

    return jsonify({"error": "Envie url ou text"}), 400


@app.route("/api/import/save", methods=["POST"])
@login_required
def api_import_save():
    data = request.get_json(force=True)
    title = data.get("title", "").strip()
    artist = data.get("artist", "").strip()
    key = data.get("key", "").strip()
    section = data.get("section", "").strip()
    category = data.get("category", "").strip()
    text = data.get("text", "").strip()

    if not title:
        return jsonify({"error": "Título é obrigatório"}), 400
    if not section:
        return jsonify({"error": "Seção é obrigatória"}), 400

    cat_display = category if category and category != "_raiz" else ""
    content = (
        "---\n"
        f"title: {title}\n"
        f"artist: {artist}\n"
        f"key: {key}\n"
        f"section: {section}\n"
        f"category: {cat_display}\n"
        "tags: []\n"
        "---\n\n"
        + text
    )

    if _use_drive():
        import drive
        svc = get_service()
        folder_id = drive.resolve_folder(svc, section, category or "_raiz", CIFRAS_FOLDER_ID)
        file_id = drive.upload_md(svc, title, content, folder_id)
        return jsonify({"ok": True, "fileId": file_id})
    else:
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", title).strip()
        dest_dir = Path(CIFRAS_ROOT) / section / (category if category and category != "_raiz" else "")
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / (safe_name + ".md")
        dest_file.write_text(content, encoding="utf-8")
        return jsonify({"ok": True, "path": str(dest_file)})


@app.route("/api/export/docx", methods=["POST"])
@login_required
def api_export_docx():
    """Gera um arquivo .docx estilizado com as cifras do repertório."""
    import io
    import re as _re
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from flask import send_file

    # ── Paleta de cores do app ──────────────────────────────────────────────
    PURPLE = RGBColor(0x5b, 0x4b, 0x8a)   # primary
    GOLD   = RGBColor(0xd4, 0xaf, 0x37)   # accent
    DARK   = RGBColor(0x1a, 0x1d, 0x2e)   # texto principal
    MUTED  = RGBColor(0x88, 0x88, 0x99)   # texto secundário
    LIGHT  = RGBColor(0xec, 0xe9, 0xf5)   # fundo suave roxo

    # ── Detecta linha de acordes (mesmo critério do frontend) ───────────────
    _CHORD_TOKEN = _re.compile(
        r'^[A-G][b#]?(?:m|maj|min|dim|aug|sus|add|[0-9]|/[A-G][b#]?)*$'
    )
    def _is_chord_line(line):
        tokens = line.strip().split()
        return bool(tokens) and all(_CHORD_TOKEN.match(t) for t in tokens)

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _tight(p, before=0, after=0):
        fmt = p.paragraph_format
        fmt.space_before = Pt(before)
        fmt.space_after  = Pt(after)
        return p

    def _shade_paragraph(p, hex_fill="ece9f5"):
        """Aplica cor de fundo a um parágrafo via XML."""
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hex_fill)
        pPr.append(shd)

    def _bottom_border(p, color="5b4b8a", size=6):
        """Adiciona borda inferior a um parágrafo."""
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), str(size))
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), color)
        pBdr.append(bottom)
        pPr.append(pBdr)

    # ── Documento ────────────────────────────────────────────────────────────
    data = request.get_json(force=True)
    songs = data.get("songs", [])
    title = data.get("title", "Repertório")

    doc = Document()

    # Remove estilos padrão do Word para herdar só o que definimos
    for sec in doc.sections:
        sec.top_margin    = Inches(0.9)
        sec.bottom_margin = Inches(0.9)
        sec.left_margin   = Inches(1.1)
        sec.right_margin  = Inches(1.1)

    # ── Cabeçalho do documento ──────────────────────────────────────────────
    header_p = doc.add_paragraph()
    _shade_paragraph(header_p, "5b4b8a")
    _tight(header_p, before=4, after=4)
    header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header_p.add_run(title)
    run.font.bold = True
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0xff, 0xff, 0xff)
    run.font.name = "Inter"

    # Subtítulo com data e contagem
    from datetime import date as _date
    sub_p = doc.add_paragraph()
    _shade_paragraph(sub_p, "4a3a78")
    _tight(sub_p, before=0, after=6)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run(
        f"{len(songs)} música{'s' if len(songs) != 1 else ''}  ·  {_date.today().strftime('%d/%m/%Y')}"
    )
    sub_run.font.size = Pt(9)
    sub_run.font.color.rgb = RGBColor(0xcc, 0xc4, 0xee)
    sub_run.font.name = "Inter"

    # ── Músicas ──────────────────────────────────────────────────────────────
    for i, song in enumerate(songs):
        if i > 0:
            doc.add_page_break()

        # Número + nome da música
        title_p = doc.add_paragraph()
        _shade_paragraph(title_p, "ece9f5")
        _tight(title_p, before=6, after=2)
        num_run = title_p.add_run(f"{i + 1}.  ")
        num_run.font.color.rgb = GOLD
        num_run.font.size = Pt(14)
        num_run.font.bold = True
        name_run = title_p.add_run(song.get("name", ""))
        name_run.font.color.rgb = PURPLE
        name_run.font.size = Pt(14)
        name_run.font.bold = True
        name_run.font.name = "Inter"
        _bottom_border(title_p, "5b4b8a", 4)

        # Artista · Categoria
        artist   = (song.get("artist")   or "").strip()
        category = (song.get("category") or song.get("section") or "").strip()
        meta_parts = [p for p in [artist, category] if p]
        if meta_parts:
            mp = doc.add_paragraph()
            _tight(mp, before=3, after=1)
            mr = mp.add_run("  " + "  ·  ".join(meta_parts))
            mr.font.size = Pt(9)
            mr.font.italic = True
            mr.font.color.rgb = MUTED

        # Tom
        key = (song.get("key") or "").strip()
        if key:
            kp = doc.add_paragraph()
            _tight(kp, before=1, after=4)
            kp.add_run("  Tom: ").font.size = Pt(9)
            kr = kp.add_run(key)
            kr.font.size = Pt(10)
            kr.font.bold = True
            kr.font.color.rgb = GOLD

        # Cifra linha a linha
        text = (song.get("text") or "").strip()
        for line in text.split("\n"):
            lp = doc.add_paragraph()
            _tight(lp, before=0, after=0)
            if not line.strip():
                _tight(lp, before=0, after=3)
                continue
            run = lp.add_run(line)
            run.font.name = "Courier New"
            if _is_chord_line(line):
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = PURPLE
            else:
                run.font.size = Pt(8.5)
                run.font.color.rgb = DARK

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    safe_name = _re.sub(r'[<>:"/\\|?*]', "_", title).strip() or "repertorio"
    return send_file(
        buf,
        as_attachment=True,
        download_name=safe_name + ".docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.route("/api/songs/update_meta", methods=["POST"])
@login_required
def api_update_meta():
    """Atualiza apenas o frontmatter YAML de um arquivo .md."""
    data = request.get_json(force=True)
    file_id = (data.get("fileId") or "").strip()
    path    = (data.get("path") or "").strip()
    new_meta = {
        "title":  (data.get("title")  or "").strip(),
        "artist": (data.get("artist") or "").strip(),
        "key":    (data.get("key")    or "").strip(),
        "tags":   data.get("tags", []),
    }

    def _patch_frontmatter(raw, new_meta):
        """Substitui os campos de metadados no frontmatter, preserva o corpo."""
        body = raw
        existing = {"section": "", "category": ""}
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].splitlines():
                    if ":" in line:
                        k, _, v = line.partition(":")
                        existing[k.strip().lower()] = v.strip().strip('"').strip("'")
                body = parts[2].strip()

        tags_str = ", ".join(new_meta["tags"]) if isinstance(new_meta["tags"], list) else new_meta["tags"]
        # Normaliza tags para lista YAML
        tags_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        tags_yaml = "[" + ", ".join(tags_list) + "]"

        fm = (
            "---\n"
            f"title: {new_meta['title']}\n"
            f"artist: {new_meta['artist']}\n"
            f"key: {new_meta['key']}\n"
            f"section: {existing.get('section','')}\n"
            f"category: {existing.get('category','')}\n"
            f"tags: {tags_yaml}\n"
            "---\n\n"
        )
        return fm + body

    if file_id:
        import drive
        svc = get_service()
        try:
            raw = drive.download_bytes(svc, file_id).decode("utf-8", errors="replace")
        except Exception as e:
            if _is_auth_error(e):
                return _auth_error_response()
            return jsonify({"error": f"Erro ao ler arquivo: {e}"}), 500
        patched = _patch_frontmatter(raw, new_meta)
        try:
            drive.update_md_content(svc, file_id, patched)
            # Se o título mudou, renomeia o arquivo .md para corresponder
            if new_meta["title"]:
                current_name = drive.get_file_name(svc, file_id)
                if Path(current_name).stem != new_meta["title"]:
                    drive.rename_file(svc, file_id, new_meta["title"] + ".md")
        except Exception as e:
            if _is_auth_error(e):
                return _auth_error_response()
            return jsonify({"error": str(e)}), 500
        invalidate_library_cache()
        return jsonify({"ok": True})

    if path:
        if not is_safe_path(path):
            return jsonify({"error": "Caminho não permitido"}), 403
        p = Path(path)
        if not p.exists() or p.suffix.lower() != ".md":
            return jsonify({"error": "Arquivo não encontrado ou não é .md"}), 404
        raw = p.read_text(encoding="utf-8")
        patched = _patch_frontmatter(raw, new_meta)
        p.write_text(patched, encoding="utf-8")
        invalidate_library_cache()
        return jsonify({"ok": True})

    return jsonify({"error": "fileId ou path obrigatório"}), 400


@app.route("/api/save_tone", methods=["POST"])
@login_required
def api_save_tone():
    data = request.get_json(force=True)
    new_text = data.get("text", "").strip()
    file_id = data.get("fileId", "").strip()
    path = data.get("path", "").strip()

    if not new_text:
        return jsonify({"error": "Texto vazio"}), 400

    if file_id:
        # Drive: baixa o arquivo original para preservar frontmatter
        import drive
        svc = get_service()
        try:
            raw = drive.download_bytes(svc, file_id)
            original = raw.decode("utf-8", errors="replace")
        except Exception:
            original = ""

        # Preserva o bloco frontmatter se existir
        if original.startswith("---"):
            parts = original.split("---", 2)
            frontmatter = "---" + parts[1] + "---\n\n" if len(parts) >= 3 else ""
        else:
            frontmatter = ""

        content = frontmatter + new_text
        try:
            drive.update_md_content(svc, file_id, content)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"ok": True})

    elif path:
        # Local: valida path dentro de CIFRAS_ROOT
        try:
            abs_path = Path(path).resolve()
            root = Path(CIFRAS_ROOT).resolve()
            if root not in abs_path.parents and abs_path != root:
                return jsonify({"error": "Caminho não permitido"}), 403
        except Exception:
            return jsonify({"error": "Caminho inválido"}), 400

        if not abs_path.exists() or abs_path.suffix.lower() != ".md":
            return jsonify({"error": "Arquivo não encontrado ou não é .md"}), 404

        original = abs_path.read_text(encoding="utf-8")
        if original.startswith("---"):
            parts = original.split("---", 2)
            frontmatter = "---" + parts[1] + "---\n\n" if len(parts) >= 3 else ""
        else:
            frontmatter = ""

        abs_path.write_text(frontmatter + new_text, encoding="utf-8")
        return jsonify({"ok": True})

    return jsonify({"error": "Informe fileId ou path"}), 400


@app.route("/api/search/content")
@login_required
def api_search_content():
    """Busca full-text nas letras/conteúdo das cifras.
    Drive: usa fullText contains via API.
    Local: lê os arquivos .md e procura no conteúdo.
    Retorna lista de { name, section, category, fileId/path, mimeType?, excerpt }.
    """
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify({"error": "Consulta muito curta (mín. 2 caracteres)"}), 400

    results = []

    if _use_drive():
        import drive as drv
        svc = get_service()
        try:
            items = drv.search_content(svc, q, CIFRAS_FOLDER_ID)
            views = _load_views()
            # Enriquece com section/category a partir da biblioteca cacheada
            lib = _get_library()
            # Monta índice fileId → {section, category, name, key}
            fid_index = {}
            for sec, cats in lib.items():
                for cat, songs in cats.items():
                    for s in songs:
                        if s.get("fileId"):
                            fid_index[s["fileId"]] = {
                                "section": sec,
                                "category": cat,
                                "name": s.get("name", ""),
                                "key": s.get("key", ""),
                                "artist": s.get("artist", ""),
                            }
            for item in items:
                fid = item.get("fileId", "")
                meta = fid_index.get(fid, {})
                results.append({
                    "fileId": fid,
                    "name": meta.get("name") or item.get("name", ""),
                    "section": meta.get("section", ""),
                    "category": meta.get("category", ""),
                    "key": meta.get("key", ""),
                    "artist": meta.get("artist", ""),
                    "mimeType": item.get("mimeType", ""),
                    "excerpt": item.get("excerpt", ""),
                    "views": views.get(fid, 0),
                })
        except Exception as e:
            return jsonify({"error": f"Erro na busca: {e}"}), 500
    else:
        # Busca local: percorre os .md dentro de CIFRAS_ROOT
        root = Path(CIFRAS_ROOT)
        if not root.exists():
            return jsonify([])
        ql = q.lower()
        views = _load_views()
        for section_dir in sorted(root.iterdir()):
            if not section_dir.is_dir():
                continue
            section = section_dir.name
            for item in sorted(section_dir.rglob("*")):
                if not item.is_file() or item.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue
                rel = item.relative_to(section_dir)
                category = rel.parts[0] if len(rel.parts) > 1 else "_raiz"
                try:
                    raw = item.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                body, meta = _parse_frontmatter(raw)
                searchable = (body + " " + meta.get("artist", "") + " " + meta.get("title", "")).lower()
                if ql not in searchable:
                    continue
                # Gera excerpt: linha que contém o termo
                excerpt = ""
                for line in body.splitlines():
                    if ql in line.lower():
                        excerpt = line.strip()[:120]
                        break
                path_str = str(item)
                results.append({
                    "path": path_str,
                    "name": meta.get("title") or item.stem,
                    "section": section,
                    "category": category,
                    "key": meta.get("key", ""),
                    "artist": meta.get("artist", ""),
                    "excerpt": excerpt,
                    "views": views.get(path_str, 0),
                })

    return jsonify(results)


@app.route("/api/sections")
@login_required
def api_sections():
    if _use_drive():
        import drive
        library = drive.scan_library(get_service(), CIFRAS_FOLDER_ID)
    else:
        library = scan_library_local()
    return jsonify({sec: list(cats.keys()) for sec, cats in library.items()})


# ---------------------------------------------------------------------------
# Liturgia diária
# ---------------------------------------------------------------------------

_liturgia_cache = {}   # { "YYYY-MM-DD": { data, liturgia, cor, leituras } }

_COR_MAP = {
    "branco": "#f0ede6",
    "verde":  "#3d7a52",
    "roxo":   "#6b3fa0",
    "violeta":"#6b3fa0",
    "vermelho":"#b92b2b",
    "rosa":   "#d4608a",
    "preto":  "#2c2c2c",
}

def _cor_hex(cor_str):
    return _COR_MAP.get((cor_str or "").lower().strip(), "#9b97b0")


@app.route("/api/liturgia")
@login_required
def api_liturgia():
    from datetime import datetime, date as _date
    import requests as _req

    date_str = request.args.get("date", "")
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else _date.today()
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    cache_key = d.isoformat()
    if cache_key in _liturgia_cache:
        return jsonify(_liturgia_cache[cache_key])

    try:
        resp = _req.get(
            "https://liturgia.up.railway.app/v2/",
            params={"dia": d.day, "mes": d.month, "ano": d.year},
            timeout=8,
        )
        resp.raise_for_status()
        raw = resp.json()
    except Exception as e:
        return jsonify({"error": f"Não foi possível carregar a liturgia: {e}"}), 502

    leituras = raw.get("leituras", {})

    def _reading(key):
        items = leituras.get(key) or []
        if not items:
            return None
        item = items[0]
        return {
            "referencia": item.get("referencia", ""),
            "titulo":     item.get("titulo", ""),
            "texto":      item.get("texto", ""),
            "refrao":     item.get("refrao", ""),   # salmo
        }

    cor = raw.get("cor", "")
    result = {
        "data":          raw.get("data", cache_key),
        "liturgia":      raw.get("liturgia", ""),
        "cor":           cor,
        "corHex":        _cor_hex(cor),
        "primeiraLeitura": _reading("primeiraLeitura"),
        "salmo":           _reading("salmo"),
        "segundaLeitura":  _reading("segundaLeitura"),
        "evangelho":       _reading("evangelho"),
    }

    _liturgia_cache[cache_key] = result
    return jsonify(result)


# ---------------------------------------------------------------------------
# Google Calendar
# ---------------------------------------------------------------------------

CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")

# Palavras-chave para filtrar eventos do calendário (case-insensitive, sem acento)
def _calendar_keywords():
    raw = os.environ.get("CALENDAR_KEYWORDS", "").strip()
    if not raw:
        return []
    import unicodedata
    def _norm(s):
        return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    return [_norm(k.strip()) for k in raw.split(",") if k.strip()]

def _event_matches_keywords(title, keywords):
    """Retorna True se o título contém ao menos uma palavra-chave (ou se não há filtro)."""
    if not keywords:
        return True
    import unicodedata
    def _norm(s):
        return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    t = _norm(title)
    return any(kw in t for kw in keywords)

def _format_event(item):
    start = item.get("start", {})
    end   = item.get("end", {})
    all_day = "dateTime" not in start
    return {
        "id":          item.get("id", ""),
        "title":       item.get("summary", "(sem título)"),
        "description": item.get("description", ""),
        "location":    item.get("location", ""),
        "start":       start.get("dateTime") or start.get("date") or "",
        "end":         end.get("dateTime")   or end.get("date")   or "",
        "allDay":      all_day,
        "htmlLink":    item.get("htmlLink", ""),
    }

@app.route("/api/calendar")
@login_required
def api_calendar():
    from datetime import datetime, timezone, timedelta
    try:
        from auth import get_calendar_service
        svc = get_calendar_service()

        # Aceita range customizado (FullCalendar envia start/end ao buscar eventos)
        start_param = request.args.get("start")
        end_param   = request.args.get("end")
        if start_param and end_param:
            time_min = start_param if start_param.endswith("Z") else start_param + "T00:00:00Z"
            time_max = end_param   if end_param.endswith("Z")   else end_param   + "T00:00:00Z"
        else:
            dt_now = datetime.now(timezone.utc)
            time_min = dt_now.isoformat()
            time_max = (dt_now + timedelta(days=30)).isoformat()

        result = svc.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=250,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        keywords = _calendar_keywords()
        events = [
            _format_event(item) for item in result.get("items", [])
            if _event_matches_keywords(item.get("summary", ""), keywords)
        ]
        return jsonify({"events": events})

    except Exception as e:
        app.logger.error("Erro ao carregar calendário: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/calendar/events", methods=["POST"])
@login_required
def api_calendar_create():
    from auth import get_calendar_service
    data = request.get_json(force=True)
    try:
        svc = get_calendar_service()
        body = {"summary": data.get("title", "").strip()}
        if data.get("description"): body["description"] = data["description"]
        if data.get("location"):    body["location"]    = data["location"]
        if data.get("allDay"):
            body["start"] = {"date": data["start"][:10]}
            body["end"]   = {"date": data["end"][:10]}
        else:
            body["start"] = {"dateTime": data["start"], "timeZone": data.get("timeZone", "America/Sao_Paulo")}
            body["end"]   = {"dateTime": data["end"],   "timeZone": data.get("timeZone", "America/Sao_Paulo")}
        event = svc.events().insert(calendarId=CALENDAR_ID, body=body).execute()
        return jsonify(_format_event(event))
    except Exception as e:
        app.logger.error("Erro ao criar evento: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/calendar/events/<event_id>", methods=["PUT"])
@login_required
def api_calendar_update(event_id):
    from auth import get_calendar_service
    data = request.get_json(force=True)
    try:
        svc = get_calendar_service()
        body = {"summary": data.get("title", "").strip()}
        if data.get("description"): body["description"] = data["description"]
        if data.get("location"):    body["location"]    = data["location"]
        if data.get("allDay"):
            body["start"] = {"date": data["start"][:10]}
            body["end"]   = {"date": data["end"][:10]}
        else:
            body["start"] = {"dateTime": data["start"], "timeZone": data.get("timeZone", "America/Sao_Paulo")}
            body["end"]   = {"dateTime": data["end"],   "timeZone": data.get("timeZone", "America/Sao_Paulo")}
        event = svc.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=body).execute()
        return jsonify(_format_event(event))
    except Exception as e:
        app.logger.error("Erro ao atualizar evento: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/calendar/events/<event_id>", methods=["DELETE"])
@login_required
def api_calendar_delete(event_id):
    from auth import get_calendar_service
    try:
        svc = get_calendar_service()
        svc.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return jsonify({"ok": True})
    except Exception as e:
        app.logger.error("Erro ao excluir evento: %s", e)
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mode = "Google Drive + OAuth" if _use_drive() else f"Local ({CIFRAS_ROOT})"
    auth = "OAuth ativo" if is_oauth_configured() else "sem autenticação"
    print(f"Modo  : {mode}")
    print(f"Auth  : {auth}")
    app.run(host="0.0.0.0", port=5000, debug=True)

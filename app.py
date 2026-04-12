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
    meta = {"artist": "", "key": "", "title": ""}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip().lower()] = v.strip().strip('"').strip("'")
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

VIEWS_FILE = Path(__file__).parent / "views.json"
_views_lock = threading.Lock()   # protege contra threads simultâneas no mesmo processo

def _load_views():
    """Leitura simples, sem lock (usada apenas para popular a listagem)."""
    try:
        return json.loads(VIEWS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _increment_view(key: str) -> int:
    """Incrementa atomicamente o contador de uma música. Retorna o novo valor."""
    with _views_lock:
        views = _load_views()
        views[key] = views.get(key, 0) + 1
        VIEWS_FILE.write_text(json.dumps(views, ensure_ascii=False), encoding="utf-8")
        return views[key]

def _song_key(data):
    return data.get("fileId") or data.get("path", "")


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
        return jsonify({"text": body, "artist": meta.get("artist",""), "key": meta.get("key","")})
    return jsonify({"text": extract_text(path), "artist": "", "key": ""})


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

    def _song_card(s):
        name = _esc(s.get("name", ""))
        category = s.get("category", "")
        key = s.get("key", "")
        badges = ""
        if category:
            badges += f'<span class="badge badge-cat">{_esc(category)}</span>'
        if key:
            badges += f'<span class="badge badge-key">{_esc(key)}</span>'
        header_right = f'<div class="song-badges">{badges}</div>' if badges else ""
        cifra_html = _render_cifra_html(s.get("text", ""))
        return (
            f'<div class="song">'
            f'  <div class="song-header">'
            f'    <h2>{name}</h2>'
            f'    {header_right}'
            f'  </div>'
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
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Sora', system-ui, sans-serif;
    background: #f7f6fc;
    color: #1a1528;
    max-width: 860px;
    margin: 0 auto;
    padding: 48px 32px 80px;
  }}

  /* ── Header ── */
  .doc-header {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    border-bottom: 2px solid #e2dff5;
    padding-bottom: 20px;
    margin-bottom: 10px;
  }}
  .doc-header .logo {{ display: flex; align-items: center; }}
  .doc-header .logo svg {{ height: 36px; width: auto; }}
  .doc-meta {{
    text-align: right;
    font-size: .8em;
    color: #7a6fa8;
    line-height: 1.6;
  }}
  .doc-title {{
    font-size: 1.5em;
    font-weight: 800;
    letter-spacing: -.03em;
    color: #1a1528;
    margin: 18px 0 4px;
  }}
  .doc-subtitle {{
    font-size: .82em;
    color: #9186b8;
    margin-bottom: 40px;
  }}

  /* ── Song card ── */
  .song {{
    background: #fff;
    border: 1px solid #e4e0f4;
    border-radius: 12px;
    padding: 22px 26px 26px;
    margin-bottom: 28px;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  .song-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ede9fa;
  }}
  .song h2 {{
    font-size: 1em;
    font-weight: 700;
    color: #1a1528;
    letter-spacing: -.01em;
    padding-left: 10px;
    border-left: 3px solid #5b4b8a;
  }}
  .song-badges {{ display: flex; gap: 6px; flex-shrink: 0; }}
  .badge {{
    font-size: .72em;
    font-weight: 600;
    padding: 2px 9px;
    border-radius: 99px;
    white-space: nowrap;
  }}
  .badge-cat {{
    background: rgba(91, 75, 138, .1);
    color: #5b4b8a;
    border: 1px solid rgba(91, 75, 138, .2);
  }}
  .badge-key {{
    background: rgba(212, 175, 55, .12);
    color: #9a7a10;
    border: 1px solid rgba(212, 175, 55, .3);
  }}

  /* ── Cifra body ── */
  pre {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: .82em;
    line-height: 1.8;
    white-space: pre-wrap;
    word-break: break-word;
    color: #2e2645;
  }}
  .chord-line {{
    color: #5b4b8a;
    font-weight: 700;
  }}

  /* ── Footer ── */
  .doc-footer {{
    margin-top: 56px;
    padding-top: 16px;
    border-top: 1px solid #e2dff5;
    font-size: .75em;
    color: #b0a8cc;
    text-align: center;
  }}

  /* ── Print ── */
  @media print {{
    body {{ background: #fff; padding: 24px 20px; }}
    .song {{ border: 1px solid #ddd; box-shadow: none; margin-bottom: 20px; }}
    .doc-footer {{ margin-top: 32px; }}
  }}
</style>
</head>
<body>

<header class="doc-header">
  <div class="logo">{logo_svg}</div>
  <div class="doc-meta">
    {_esc(today)}<br>
    {n} {song_word}
  </div>
</header>

<h1 class="doc-title">{_esc(title)}</h1>
<p class="doc-subtitle">Repertório gerado pelo My Cifras</p>

{"".join(_song_card(s) for s in songs)}

<footer class="doc-footer">My Cifras · mycifras.app</footer>

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
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mode = "Google Drive + OAuth" if _use_drive() else f"Local ({CIFRAS_ROOT})"
    auth = "OAuth ativo" if is_oauth_configured() else "sem autenticação"
    print(f"Modo  : {mode}")
    print(f"Auth  : {auth}")
    app.run(host="0.0.0.0", port=5000, debug=True)

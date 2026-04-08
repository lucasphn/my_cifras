import os
import re
import tempfile
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, Response, session

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-insecure-key-troque-no-env")

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
                library[sname]["_raiz"].append(
                    {"name": item.stem, "path": str(item), "section": sname, "category": "_raiz"}
                )
    return library


def _collect_local(folder, section, category):
    return [
        {"name": f.stem, "path": str(f), "section": section, "category": category}
        for f in sorted(folder.iterdir())
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def flatten_songs(library):
    return [song for cats in library.values() for songs in cats.values() for song in songs]


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
@login_required
def index():
    user = current_user()
    return render_template("index.html", user=user)


@app.route("/api/library")
@login_required
def api_library():
    if _use_drive():
        import drive
        library = drive.scan_library(get_service(), CIFRAS_FOLDER_ID)
    else:
        library = scan_library_local()
    return jsonify(library)


@app.route("/api/songs")
@login_required
def api_songs():
    if _use_drive():
        import drive
        library = drive.scan_library(get_service(), CIFRAS_FOLDER_ID)
    else:
        library = scan_library_local()
    return jsonify(flatten_songs(library))


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

    return jsonify({"text": extract_text(path)})


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

    parts = [
        f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{_esc(title)}</title>
<style>
  body {{ font-family: monospace; max-width: 900px; margin: 40px auto; padding: 0 20px; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
  .meta {{ color: #666; font-size: .85em; margin-bottom: 40px; }}
  .song {{ page-break-inside: avoid; margin-bottom: 48px; }}
  .song h2 {{ font-size: 1.1em; border-left: 4px solid #555; padding-left: 10px; }}
  pre {{ white-space: pre-wrap; word-break: break-word; font-size: .9em; line-height: 1.6; }}
  @media print {{ .song {{ page-break-inside: avoid; }} }}
</style>
</head>
<body>
<h1>{_esc(title)}</h1>
<p class="meta">Gerado em {today} · {len(songs)} música(s)</p>
"""
    ]
    for s in songs:
        parts.append(
            f'<div class="song"><h2>{_esc(s.get("name",""))}</h2>'
            f'<pre>{_esc(s.get("text",""))}</pre></div>\n'
        )
    parts.append("</body></html>")
    return Response("".join(parts), mimetype="text/html; charset=utf-8")


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

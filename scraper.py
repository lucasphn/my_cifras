"""
Extrai cifra e metadados de URLs de sites de cifras.
Suporte: CifraClub, Cifras.com.br, BananaCifras, genérico.
"""

import json as _json
import re
import requests
from urllib.parse import urlparse, urljoin

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 12


def fetch_cifra(url):
    """
    Busca e parseia uma cifra a partir de uma URL.
    Retorna dict: { title, artist, key, text }
    Lança requests.HTTPError ou ValueError em caso de falha.
    """
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")

    domain = urlparse(url).netloc.lower()

    if "cifraclub" in domain:
        return _parse_cifraclub(soup)
    if "bananacifras" in domain:
        return _parse_bananacifras(soup, url)
    if "cifras.com.br" in domain:
        return _parse_cifras_com_br(soup)

    return _parse_generic(soup)


# ─── Parsers ─────────────────────────────────────────────────────────────────

def _parse_cifraclub(soup):
    title = _text(soup.find("h1")) or _meta(soup, "og:title")
    artist = _text(soup.find("h2")) or ""

    key = ""
    for tag in soup.find_all(string=re.compile(r"Tom[:\s]+[A-G]", re.I)):
        m = re.search(r"[A-G][b#]?m?", tag)
        if m:
            key = m.group()
            break

    text = ""
    pre = soup.find("pre")
    if pre:
        text = pre.get_text()
    else:
        for cls in ["cifra_cnt", "cifra", "chord-sheet", "js-tab-content"]:
            el = soup.find(class_=re.compile(cls, re.I))
            if el:
                text = el.get_text("\n")
                break

    return {
        "title": _clean(title),
        "artist": _clean(artist),
        "key": key,
        "text": _clean_text(text),
    }


def _parse_cifras_com_br(soup):
    # Título: <h1 class="...song-show-header__song-title...">
    h1 = soup.find("h1", class_=re.compile(r"song-show-header__song-title", re.I))
    title = _text(h1) or _meta(soup, "og:title")

    # Artista: <h2 class="...song-show-header__artist..."><a>Nome</a>
    h2 = soup.find("h2", class_=re.compile(r"song-show-header__artist", re.I))
    artist = _text(h2.find("a")) if h2 else ""

    # Tom: atributo original-key no web component <song-change-key original-key="C">
    key = ""
    key_el = soup.find("song-change-key")
    if key_el:
        key = key_el.get("original-key", "")

    # Cifra: <div class="...song-show-chord-content..."><pre>...
    text = ""
    content_div = soup.find("div", class_=re.compile(r"song-show-chord-content", re.I))
    if content_div:
        pre = content_div.find("pre")
        if pre:
            text = pre.get_text()
    if not text:
        pre = soup.find("pre")
        if pre:
            text = pre.get_text()

    return {
        "title": _clean(title),
        "artist": _clean(artist),
        "key": key,
        "text": _clean_text(text),
    }


def _parse_bananacifras(soup, url):
    title = ""
    artist = ""

    # Metadados embutidos como JS inline: songdata={"track_name":"...","artist_name":"..."}
    for script in soup.find_all("script"):
        src = script.string or ""
        m = re.search(r'songdata\s*=\s*(\{.+?\});', src, re.S)
        if m:
            try:
                sd = _json.loads(m.group(1))
                title = sd.get("track_name", "")
                artist = sd.get("artist_name", "")
            except Exception:
                pass
            break

    if not title:
        title = _text(soup.find("h1")) or _meta(soup, "og:title")

    # Conteúdo carregado via endpoint JSON:
    # bananajs.push(["init_tab", {"json":"/json/tab.js?id=123&v=abc..."}])
    key = ""
    text = ""
    for script in soup.find_all("script"):
        src = script.string or ""
        m = re.search(r'bananajs\.push\(\["init_tab"\s*,\s*(\{[^}]+\})\]', src)
        if m:
            try:
                tab_info = _json.loads(m.group(1))
                json_path = tab_info.get("json", "")
                if json_path:
                    json_url = urljoin(url, json_path)
                    tab_resp = requests.get(json_url, headers=HEADERS, timeout=TIMEOUT)
                    if tab_resp.ok:
                        tab_data = tab_resp.json()
                        # Tentativa por campos comuns de tom e conteúdo
                        key = (
                            tab_data.get("key") or tab_data.get("tom") or
                            tab_data.get("tone") or tab_data.get("original_key") or ""
                        )
                        text = (
                            tab_data.get("content") or tab_data.get("text") or
                            tab_data.get("tab") or tab_data.get("cifra") or ""
                        )
                        # Caso o conteúdo venha com HTML, converte para texto
                        if text and "<" in text:
                            from bs4 import BeautifulSoup as _BS
                            text = _BS(text, "html.parser").get_text()
            except Exception:
                pass
            break

    return {
        "title": _clean(title),
        "artist": _clean(artist),
        "key": key,
        "text": _clean_text(text),
    }


def _parse_generic(soup):
    title = _text(soup.find("h1")) or _meta(soup, "og:title") or ""
    artist = ""

    pre = soup.find("pre")
    text = pre.get_text() if pre else ""

    return {
        "title": _clean(title),
        "artist": _clean(artist),
        "key": "",
        "text": _clean_text(text),
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _text(el):
    return el.get_text(strip=True) if el else ""


def _meta(soup, prop):
    tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
    return tag.get("content", "").strip() if tag else ""


def _clean(s):
    """Remove sufixos de título como ' | CifraClub', ' - Cifras.com.br', etc."""
    return re.split(
        r"\s*[|\-–]\s*(?:cifraclub|cifra\s*club|bananacifras|cifras(?:\.com\.br)?)",
        s, flags=re.I
    )[0].strip()


def _clean_text(text):
    """Remove espaços em fim de linha e comprime linhas em branco excessivas."""
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

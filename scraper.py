"""
Extrai cifra e metadados de URLs de sites de cifras (CifraClub e genérico).
"""

import re
import requests
from urllib.parse import urlparse

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

    return _parse_generic(soup)


# ─── Parsers ─────────────────────────────────────────────────────────────────

def _parse_cifraclub(soup):
    title = _text(soup.find("h1")) or _meta(soup, "og:title")
    artist = _text(soup.find("h2")) or ""

    # Tom: procura padrão "Tom: G" em qualquer lugar da página
    key = ""
    for tag in soup.find_all(string=re.compile(r"Tom[:\s]+[A-G]", re.I)):
        m = re.search(r"[A-G][b#]?m?", tag)
        if m:
            key = m.group()
            break

    # Cifra: <pre> principal
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

    # Limpa artefatos de HTML mal convertido
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return {
        "title": _clean(title),
        "artist": _clean(artist),
        "key": key,
        "text": text.strip(),
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
        "text": text.strip(),
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _text(el):
    return el.get_text(strip=True) if el else ""


def _meta(soup, prop):
    tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
    return tag.get("content", "").strip() if tag else ""


def _clean(s):
    """Remove sufixos comuns de título como ' | CifraClub'."""
    return re.split(r"\s*[|\-–]\s*(?:cifraclub|cifra club)", s, flags=re.I)[0].strip()

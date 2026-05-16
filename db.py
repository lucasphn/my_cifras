"""
Camada de acesso ao Supabase via REST API (httpx).
Usado em vez de arquivos JSON no Google Drive para dados por usuário.
"""
import json
import logging
import os

import httpx

log = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

_ENABLED = bool(SUPABASE_URL and SUPABASE_KEY)


def enabled() -> bool:
    return _ENABLED


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def _h(prefer: str = "") -> dict:
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _get(table: str, **params) -> list:
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h(),
        params={k: v for k, v in params.items() if v is not None},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def _post(table: str, body, upsert: bool = False) -> list:
    prefer = "resolution=merge-duplicates,return=representation" if upsert else "return=representation"
    r = httpx.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h(prefer),
        json=body,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def _patch(table: str, body: dict, **params) -> list:
    r = httpx.patch(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h("return=representation"),
        json=body,
        params={k: v for k, v in params.items()},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def _delete(table: str, **params) -> None:
    r = httpx.delete(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=_h(),
        params={k: v for k, v in params.items()},
        timeout=10,
    )
    r.raise_for_status()


# ─── Users ────────────────────────────────────────────────────────────────────

_uid_cache: dict = {}  # email → uuid


def get_or_create_user(email: str, google_id: str, name: str = "",
                        avatar: str = "", is_owner: bool = False) -> str | None:
    if email in _uid_cache:
        return _uid_cache[email]
    try:
        rows = _post("users", {
            "google_id": google_id or email,
            "email": email,
            "name": name,
            "avatar_url": avatar,
            "is_owner": is_owner,
        }, upsert=True)
        uid = rows[0]["id"] if rows else None
        if uid:
            _uid_cache[email] = uid
        return uid
    except Exception as e:
        log.error("[db.users] Erro ao criar/obter usuário %s: %s", email, e)
        return None


def get_user_id(email: str) -> str | None:
    if email in _uid_cache:
        return _uid_cache[email]
    try:
        rows = _get("users", select="id", email=f"eq.{email}")
        if rows:
            _uid_cache[email] = rows[0]["id"]
            return rows[0]["id"]
    except Exception as e:
        log.error("[db.users] Erro ao buscar user_id %s: %s", email, e)
    return None


# ─── Views ────────────────────────────────────────────────────────────────────

def load_views(user_id: str) -> dict:
    """Retorna {file_id: view_count} para o usuário."""
    rows = _get("song_views", select="file_id,view_count", user_id=f"eq.{user_id}")
    return {r["file_id"]: r["view_count"] for r in rows}


def increment_view(user_id: str, file_id: str) -> int:
    rows = _get("song_views", select="view_count",
                user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
    if rows:
        new_count = rows[0]["view_count"] + 1
        _patch("song_views", {"view_count": new_count},
               user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
        return new_count
    _post("song_views", {"user_id": user_id, "file_id": file_id, "view_count": 1})
    return 1


# ─── Tones / Preferences ─────────────────────────────────────────────────────

_TONE_COLS = ("my_key", "original_key", "alt_key", "my_capo")


def load_tones(user_id: str) -> dict:
    """Retorna {file_id: {slot: value, ...}} para o usuário."""
    rows = _get("user_tones",
                select="file_id,my_key,original_key,alt_key,my_capo",
                user_id=f"eq.{user_id}")
    result = {}
    for r in rows:
        d = {k: v for k in _TONE_COLS if (v := r.get(k)) is not None}
        if d:
            result[r["file_id"]] = d
    return result


def upsert_tone(user_id: str, file_id: str, slot: str, value) -> dict:
    """Grava/atualiza um slot de tom. Retorna todos os slots da música."""
    rows = _get("user_tones", select=",".join(_TONE_COLS),
                user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
    current = {k: v for k in _TONE_COLS if (v := (rows[0] if rows else {}).get(k)) is not None}
    if not value or (slot == "my_capo" and str(value) in ("0", "")):
        current.pop(slot, None)
    else:
        current[slot] = value
    current.update({"user_id": user_id, "file_id": file_id})
    result = _post("user_tones", current, upsert=True)
    row = result[0] if result else current
    return {k: v for k in _TONE_COLS if (v := row.get(k)) is not None}


def delete_tone(user_id: str, file_id: str, slot: str = "") -> dict:
    """Remove um slot ou todos os slots de um arquivo."""
    if slot and slot in _TONE_COLS:
        rows = _patch("user_tones", {slot: None},
                      user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
        row = rows[0] if rows else {}
        return {k: v for k in _TONE_COLS if (v := row.get(k)) is not None}
    _delete("user_tones", user_id=f"eq.{user_id}", file_id=f"eq.{file_id}")
    return {}


# ─── Repertórios ──────────────────────────────────────────────────────────────

def _rep_to_dict(r: dict) -> dict:
    songs = r.get("songs") or []
    if isinstance(songs, str):
        try:
            songs = json.loads(songs)
        except Exception:
            songs = []
    return {
        "id": r["id"],
        "name": r["name"],
        "songs": songs,
        "created_at": r.get("created_at", ""),
        "updated_at": r.get("updated_at", ""),
    }


def load_reps(user_id: str) -> dict:
    rows = _get("repertories",
                select="id,name,songs,created_at,updated_at",
                user_id=f"eq.{user_id}")
    return {r["id"]: _rep_to_dict(r) for r in rows}


def create_rep(user_id: str, name: str, songs: list) -> dict:
    rows = _post("repertories", {"user_id": user_id, "name": name, "songs": songs})
    return _rep_to_dict(rows[0])


def update_rep(rep_id: str, patch: dict) -> dict:
    rows = _patch("repertories", patch, id=f"eq.{rep_id}")
    return _rep_to_dict(rows[0]) if rows else {}


def delete_rep(rep_id: str) -> None:
    _delete("repertories", id=f"eq.{rep_id}")


# ─── Shares ───────────────────────────────────────────────────────────────────

def _share_to_dict(r: dict) -> dict:
    d = dict(r)
    for field in ("seen_by", "dismissed_by", "songs"):
        val = d.get(field)
        if isinstance(val, str):
            try:
                d[field] = json.loads(val)
            except Exception:
                d[field] = []
        elif val is None:
            d[field] = []
    return d


def load_all_shares() -> dict:
    rows = _get("shares", select="*")
    return {r["id"]: _share_to_dict(r) for r in rows}


def create_share(data: dict) -> dict:
    payload = {k: v for k, v in data.items() if k != "id"}
    rows = _post("shares", payload)
    return _share_to_dict(rows[0]) if rows else data


def update_share(share_id: str, data: dict) -> dict:
    payload = {k: v for k, v in data.items() if k != "id"}
    rows = _patch("shares", payload, id=f"eq.{share_id}")
    return _share_to_dict(rows[0]) if rows else {}


def delete_share(share_id: str) -> None:
    _delete("shares", id=f"eq.{share_id}")


def delete_shares_by_rep(rep_id: str, from_email: str) -> None:
    _delete("shares", repertory_id=f"eq.{rep_id}", from_email=f"eq.{from_email}")


# ─── Groups ───────────────────────────────────────────────────────────────────

def _group_to_dict(r: dict) -> dict:
    members = r.get("members") or []
    if isinstance(members, str):
        try:
            members = json.loads(members)
        except Exception:
            members = []
    return {
        "id": r["id"],
        "name": r["name"],
        "members": members,
        "created_at": r.get("created_at", ""),
    }


def load_groups(user_id: str) -> dict:
    rows = _get("groups", select="id,name,members,created_at",
                owner_id=f"eq.{user_id}")
    return {r["id"]: _group_to_dict(r) for r in rows}


def create_group(user_id: str, name: str, members: list) -> dict:
    rows = _post("groups", {"owner_id": user_id, "name": name, "members": members})
    return _group_to_dict(rows[0])


def update_group(group_id: str, data: dict) -> dict:
    rows = _patch("groups", data, id=f"eq.{group_id}")
    return _group_to_dict(rows[0]) if rows else {}


def delete_group(group_id: str) -> None:
    _delete("groups", id=f"eq.{group_id}")

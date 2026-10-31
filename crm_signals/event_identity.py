"""Stable identities for source events; independent of Frappe runtime."""

from hashlib import sha256


def build_source_event_key(source_doctype, source_name, source_event_id):
    """Return a deterministic SHA-256 key when all source identity parts exist."""
    parts = (source_doctype, source_name, source_event_id)
    if not all(str(part or "").strip() for part in parts):
        return None
    canonical = "\x1f".join(str(part).strip() for part in parts)
    return sha256(canonical.encode("utf-8")).hexdigest()

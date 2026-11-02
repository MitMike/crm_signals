"""Permission-aware, metadata-only customer activity timeline for Explorer."""

import base64
import json

import frappe
from frappe import _
from frappe.utils import get_datetime, now_datetime

MAX_PAGE_LENGTH = 50
MAX_CURSOR_LENGTH = 4096
MAX_CURSOR_OFFSET = 100000

SOURCE_ADAPTERS = (
    {
        "id": "crm_signal",
        "doctype": "CRM Signal",
        "required_fields": ("lead", "customer", "signal_type", "priority"),
    },
    {
        "id": "quotation",
        "doctype": "Quotation",
        "required_fields": ("quotation_to", "party_name", "status"),
    },
    {
        "id": "opportunity",
        "doctype": "Opportunity",
        "required_fields": ("opportunity_from", "party_name", "status"),
    },
)
SOURCE_IDS = tuple(adapter["id"] for adapter in SOURCE_ADAPTERS)


def _value(row, fieldname, default=None):
    if isinstance(row, dict):
        return row.get(fieldname, default)
    return getattr(row, fieldname, default)


def _require_readable_record(doctype, name, fields=(), extra_filters=None):
    """Load one record through permission-aware APIs without revealing inaccessible names."""
    if not frappe.db.exists("DocType", doctype) or not frappe.has_permission(
        doctype, ptype="read"
    ):
        frappe.throw(_("Timeline context is unavailable"), frappe.PermissionError)

    meta = frappe.get_meta(doctype)
    if any(not meta.has_field(fieldname) for fieldname in fields):
        frappe.throw(_("Timeline context is unavailable"), frappe.PermissionError)

    filters = {"name": name}
    filters.update(extra_filters or {})
    rows = frappe.get_list(
        doctype,
        filters=filters,
        fields=["name", *fields],
        limit_page_length=1,
    )
    if not rows or not frappe.has_permission(doctype, ptype="read", doc=name):
        frappe.throw(_("Timeline context is unavailable"), frappe.PermissionError)
    return rows[0]


def _resolve_party(context_doctype, context_name):
    """Resolve a supported context to a readable Lead or Customer."""
    if context_doctype in {"Lead", "Customer"}:
        party_doctype, party_name = context_doctype, context_name
    elif context_doctype == "Opportunity":
        row = _require_readable_record(
            "Opportunity", context_name, ("opportunity_from", "party_name")
        )
        party_doctype = _value(row, "opportunity_from")
        party_name = _value(row, "party_name")
    elif context_doctype in {"CRM Signal", "Highlight"}:
        filters = {"signal_type": "High-Value Quote"} if context_doctype == "Highlight" else None
        row = _require_readable_record(
            "CRM Signal", context_name, ("lead", "customer"), filters
        )
        party_doctype = "Lead" if _value(row, "lead") else "Customer"
        party_name = _value(row, "lead") or _value(row, "customer")
    else:
        frappe.throw(_("Unsupported timeline context"), frappe.ValidationError)

    if party_doctype not in {"Lead", "Customer"} or not party_name:
        frappe.throw(_("The selected record is not linked to a Lead or Customer"), frappe.ValidationError)

    _require_readable_record(party_doctype, party_name)
    return party_doctype, party_name


def _decode_cursor(cursor, page_length):
    if not cursor:
        return {
            "as_of": str(now_datetime()),
            "offsets": {source_id: 0 for source_id in SOURCE_IDS},
        }
    if not isinstance(cursor, str) or len(cursor) > MAX_CURSOR_LENGTH:
        frappe.throw(_("Invalid timeline cursor"), frappe.ValidationError)

    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4))
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        frappe.throw(_("Invalid timeline cursor"), frappe.ValidationError)

    if not isinstance(payload, dict):
        frappe.throw(_("Invalid timeline cursor"), frappe.ValidationError)

    offsets = payload.get("offsets")
    as_of = payload.get("as_of")
    try:
        get_datetime(as_of)
    except (TypeError, ValueError):
        frappe.throw(_("Invalid timeline cursor"), frappe.ValidationError)

    if (
        payload.get("version") != 1
        or payload.get("page_length") != page_length
        or not isinstance(as_of, str)
        or not as_of
        or len(as_of) > 40
        or not isinstance(offsets, dict)
        or set(offsets) != set(SOURCE_IDS)
    ):
        frappe.throw(_("Invalid timeline cursor"), frappe.ValidationError)

    if any(
        isinstance(offset, bool)
        or not isinstance(offset, int)
        or offset < 0
        or offset > MAX_CURSOR_OFFSET
        for offset in offsets.values()
    ):
        frappe.throw(_("Invalid timeline cursor"), frappe.ValidationError)

    return {"as_of": as_of, "offsets": offsets}


def _encode_cursor(as_of, offsets, page_length):
    payload = {
        "version": 1,
        "as_of": as_of,
        "page_length": page_length,
        "offsets": offsets,
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _source_filters(source_id, party_doctype, party_name, as_of):
    filters = {"creation": ["<=", as_of]}
    if source_id == "crm_signal":
        filters["lead" if party_doctype == "Lead" else "customer"] = party_name
    elif source_id == "quotation":
        filters.update({"quotation_to": party_doctype, "party_name": party_name})
    else:
        filters.update({"opportunity_from": party_doctype, "party_name": party_name})
    return filters


def _normalize_event(adapter, row, party_doctype, party_name):
    source_id = adapter["id"]
    doctype = adapter["doctype"]
    name = _value(row, "name")
    if source_id == "crm_signal":
        event_type = _value(row, "signal_type") or "CRM Signal"
        summary = f"{event_type} · {_value(row, 'priority') or 'Priority unavailable'}"
        status = None
    else:
        event_type = doctype
        status = _value(row, "status")
        summary = f"{doctype} · {status or 'Status unavailable'}"

    return {
        "source_id": source_id,
        "source_doctype": doctype,
        "source_event_id": name,
        "event_type": event_type,
        "timestamp": _value(row, "creation"),
        "related_doctype": party_doctype,
        "related_name": party_name,
        "summary": summary,
        "source_status": status,
        "source_route": f"/app/{doctype.lower().replace(' ', '-')}/{name}",
    }


def _fetch_source_page(adapter, party_doctype, party_name, as_of, offset, page_length):
    """Read one bounded source page and re-check every returned source record."""
    source_id = adapter["id"]
    doctype = adapter["doctype"]
    if not frappe.db.exists("DocType", doctype):
        return {"status": "not_connected", "rows": [], "raw_count": 0, "leading_skipped": 0}
    if not frappe.has_permission(doctype, ptype="read"):
        return {"status": "unavailable", "rows": [], "raw_count": 0, "leading_skipped": 0}

    meta = frappe.get_meta(doctype)
    if any(not meta.has_field(fieldname) for fieldname in adapter["required_fields"]):
        return {"status": "unavailable", "rows": [], "raw_count": 0, "leading_skipped": 0}

    fields = ["name", "creation", *adapter["required_fields"]]
    try:
        raw_rows = frappe.get_list(
            doctype,
            filters=_source_filters(source_id, party_doctype, party_name, as_of),
            fields=fields,
            order_by="creation desc, name desc",
            start=offset,
            limit_page_length=page_length + 1,
        )
    except frappe.PermissionError:
        return {"status": "unavailable", "rows": [], "raw_count": 0, "leading_skipped": 0}

    visible_rows = []
    leading_skipped = 0
    found_visible = False
    for position, row in enumerate(raw_rows):
        name = _value(row, "name")
        if not name or not frappe.has_permission(doctype, ptype="read", doc=name):
            if not found_visible:
                leading_skipped += 1
            continue
        found_visible = True
        visible_rows.append(
            {
                "item": _normalize_event(adapter, row, party_doctype, party_name),
                "position": position,
            }
        )

    if visible_rows:
        status = "available"
    elif raw_rows:
        status = "unavailable"
    else:
        status = "empty" if offset == 0 else "available"

    return {
        "status": status,
        "rows": visible_rows,
        "raw_count": len(raw_rows),
        "leading_skipped": leading_skipped,
    }


def _merge_source_pages(source_pages, offsets, page_length):
    """Merge pages while advancing each source only past rows consumed by this page."""
    candidates = [
        entry["item"]
        for page in source_pages.values()
        for entry in page["rows"]
    ]
    unique = {
        (item["source_id"], item["source_event_id"]): item
        for item in candidates
    }
    ordered = sorted(
        unique.values(),
        key=lambda item: (
            str(item["timestamp"] or ""),
            item["source_id"],
            str(item["source_event_id"] or ""),
        ),
        reverse=True,
    )
    items = ordered[:page_length]
    selected_ids = {
        (item["source_id"], item["source_event_id"])
        for item in items
    }

    next_offsets = dict(offsets)
    has_more = False
    for source_id, page in source_pages.items():
        positions = [
            entry["position"]
            for entry in page["rows"]
            if (source_id, entry["item"]["source_event_id"]) in selected_ids
        ]
        consumed = max(positions) + 1 if positions else page["leading_skipped"]
        next_offsets[source_id] = offsets[source_id] + consumed
        has_more = has_more or page["raw_count"] > consumed
        has_more = has_more or page["raw_count"] == page_length + 1

    return items, next_offsets, has_more


@frappe.whitelist()
def get_explorer_timeline(context_doctype, context_name, page_length=20, cursor=None):
    """Return a permission-aware metadata timeline for a Lead or Customer relationship.

    The initial release includes CRM Signal, Quotation and Opportunity only.
    Optional Communication/Event/call/WhatsApp sources require target-site discovery.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication is required"), frappe.AuthenticationError)

    context_doctype = str(context_doctype or "").strip()
    context_name = str(context_name or "").strip()
    if not context_name or len(context_name) > 140:
        frappe.throw(_("A valid timeline context name is required"), frappe.ValidationError)

    try:
        if isinstance(page_length, bool):
            raise ValueError
        page_length = int(page_length)
    except (TypeError, ValueError):
        frappe.throw(_("Page length must be a whole number"), frappe.ValidationError)
    if page_length < 1 or page_length > MAX_PAGE_LENGTH:
        frappe.throw(
            _("Page length must be between 1 and {0}").format(MAX_PAGE_LENGTH),
            frappe.ValidationError,
        )

    cursor_state = _decode_cursor(cursor, page_length)
    party_doctype, party_name = _resolve_party(context_doctype, context_name)

    source_pages = {}
    sources = []
    for adapter in SOURCE_ADAPTERS:
        page = _fetch_source_page(
            adapter,
            party_doctype,
            party_name,
            cursor_state["as_of"],
            cursor_state["offsets"][adapter["id"]],
            page_length,
        )
        source_pages[adapter["id"]] = page
        sources.append(
            {
                "source_id": adapter["id"],
                "source_doctype": adapter["doctype"],
                "status": page["status"],
            }
        )

    items, next_offsets, has_more = _merge_source_pages(
        source_pages,
        cursor_state["offsets"],
        page_length,
    )
    next_cursor = (
        _encode_cursor(cursor_state["as_of"], next_offsets, page_length)
        if has_more
        else None
    )
    return {
        "context": {
            "doctype": context_doctype,
            "name": context_name,
            "party_doctype": party_doctype,
            "party_name": party_name,
        },
        "sources": sources,
        "items": items,
        "next_cursor": next_cursor,
    }

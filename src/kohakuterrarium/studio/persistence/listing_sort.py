"""Ordering helpers for the saved-session listing.

Pure functions over the plain-dict index entries produced by
``store.build_session_index`` — no SessionStore, no filesystem, no shared
state — so they live in their own module and are unit-tested in isolation.
``store`` (the index builder) and the ``persistence/saved`` HTTP route both
import :func:`sort_session_entries` from here so the CLI and HTTP share one
ordering implementation.
"""

from datetime import datetime
from typing import Any

# Saved-session list sort fields exposed to the HTTP / CLI surface. The
# two timestamp fields order by parsed ISO value; the two string fields
# order case-insensitively. Anything else falls back to ``last_active``
# so a bad query param can never 500 or scramble the listing.
SORT_FIELDS = ("last_active", "created_at", "name", "config_type")


def parse_iso_ts(value: Any) -> float | None:
    """Parse an ISO-8601 timestamp into a POSIX float, or ``None``.

    Session ``last_active`` / ``created_at`` are written by
    :meth:`SessionStore.init_meta` / ``update_status`` / ``touch`` as
    ``datetime.now(timezone.utc).isoformat()``. Returns ``None`` for an
    empty, missing, or unparseable value so callers can treat "no usable
    timestamp" distinctly — sort such entries to the tail, skip them in
    stats — instead of crashing on a corrupt or absent field.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return None


def sort_session_entries(
    entries: list[dict],
    sort_by: str = "last_active",
    order: str = "desc",
) -> list[dict]:
    """Return ``entries`` ordered by ``sort_by`` / ``order``.

    Stable: callers pass the mtime-ordered index, so entries that tie on
    the sort key — or carry no usable timestamp — keep their incoming
    "last touched on disk" order as the tiebreaker.

    Timestamp fields (``last_active`` / ``created_at``): entries with no
    parseable timestamp are *always* pushed to the tail in their incoming
    order, regardless of ``order`` — a corrupt or undated session is never
    "the newest" and should not head an ascending list either.
    ``last_active`` falls back to ``created_at`` so a freshly-created
    session that has not been touched still sorts by its creation time.

    String fields (``name`` / ``config_type``): case-insensitive; missing
    values coerce to ``""``.

    Unknown ``sort_by`` falls back to ``last_active``; any ``order`` other
    than ``"asc"`` is treated as ``"desc"``.
    """
    field = sort_by if sort_by in SORT_FIELDS else "last_active"
    reverse = str(order).lower() != "asc"

    if field in ("last_active", "created_at"):
        with_ts: list[tuple[float, dict]] = []
        without_ts: list[dict] = []
        for entry in entries:
            raw = entry.get(field) or ""
            if field == "last_active" and not raw:
                raw = entry.get("created_at") or ""
            ts = parse_iso_ts(raw)
            if ts is None:
                without_ts.append(entry)
            else:
                with_ts.append((ts, entry))
        with_ts.sort(key=lambda pair: pair[0], reverse=reverse)
        return [entry for _, entry in with_ts] + without_ts

    return sorted(
        entries,
        key=lambda entry: str(entry.get(field) or "").lower(),
        reverse=reverse,
    )

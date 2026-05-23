"""Unit tests for :mod:`kohakuterrarium.studio.persistence.listing_sort`."""

from kohakuterrarium.studio.persistence import listing_sort

# ── parse_iso_ts ──────────────────────────────────────────────


class TestParseIsoTs:
    def test_none_and_empty(self):
        assert listing_sort.parse_iso_ts(None) is None
        assert listing_sort.parse_iso_ts("") is None

    def test_valid_iso(self):
        out = listing_sort.parse_iso_ts("2025-01-01T00:00:00+00:00")
        assert isinstance(out, float) and out > 0

    def test_z_suffix_accepted(self):
        # ``...Z`` is normalised to ``+00:00`` before parsing.
        assert listing_sort.parse_iso_ts("2025-01-01T00:00:00Z") is not None

    def test_unparseable_returns_none(self):
        assert listing_sort.parse_iso_ts("not-a-date") is None

    def test_non_string_returns_none(self):
        # A stray non-ISO scalar must not raise.
        assert listing_sort.parse_iso_ts(12345) is None


# ── sort_session_entries ──────────────────────────────────────


class TestSortSessionEntries:
    def _entries(self):
        # Deliberately out of order; "mid" carries only ``created_at``
        # (no ``last_active``) to exercise the fallback.
        return [
            {
                "name": "Bravo",
                "config_type": "agent",
                "last_active": "2025-06-01T00:00:00+00:00",
            },
            {
                "name": "alpha",
                "config_type": "terrarium",
                "last_active": "2026-01-01T00:00:00+00:00",
            },
            {
                "name": "mid",
                "config_type": "agent",
                "created_at": "2025-09-01T00:00:00+00:00",
            },
        ]

    def test_default_is_last_active_desc(self):
        out = listing_sort.sort_session_entries(self._entries())
        # alpha (2026) > mid (created 2025-09 via fallback) > Bravo (2025-06)
        assert [e["name"] for e in out] == ["alpha", "mid", "Bravo"]

    def test_last_active_asc(self):
        out = listing_sort.sort_session_entries(self._entries(), order="asc")
        assert [e["name"] for e in out] == ["Bravo", "mid", "alpha"]

    def test_last_active_falls_back_to_created_at(self):
        # "mid" has only created_at — it must still be sorted, not dropped
        # to the tail as undated.
        out = listing_sort.sort_session_entries(self._entries())
        assert "mid" in [e["name"] for e in out]
        assert out[1]["name"] == "mid"

    def test_undated_entries_sink_to_tail_desc(self):
        entries = [
            {"name": "dated", "last_active": "2025-01-01T00:00:00+00:00"},
            {"name": "undated"},  # no last_active, no created_at
        ]
        out = listing_sort.sort_session_entries(entries, order="desc")
        assert [e["name"] for e in out] == ["dated", "undated"]

    def test_undated_entries_sink_to_tail_asc_too(self):
        # Negative case: an undated entry must NOT lead an ascending sort
        # just because ``None`` sorts before any real timestamp. It stays
        # at the tail in both directions.
        entries = [
            {"name": "dated", "last_active": "2025-01-01T00:00:00+00:00"},
            {"name": "undated"},
        ]
        out = listing_sort.sort_session_entries(entries, order="asc")
        assert [e["name"] for e in out] == ["dated", "undated"]

    def test_created_at_sort_does_not_fall_back_to_last_active(self):
        # Negative case: sorting explicitly by ``created_at`` must use
        # only created_at. An entry with last_active but no created_at is
        # undated for this sort and sinks to the tail — it must not borrow
        # its last_active value.
        entries = [
            {"name": "has_created", "created_at": "2025-01-01T00:00:00+00:00"},
            {"name": "only_last_active", "last_active": "2030-01-01T00:00:00+00:00"},
        ]
        out = listing_sort.sort_session_entries(
            entries, sort_by="created_at", order="desc"
        )
        assert [e["name"] for e in out] == ["has_created", "only_last_active"]

    def test_sort_by_name_case_insensitive(self):
        out = listing_sort.sort_session_entries(
            self._entries(), sort_by="name", order="asc"
        )
        # Case-insensitive: alpha, Bravo, mid (not Bravo before alpha).
        assert [e["name"] for e in out] == ["alpha", "Bravo", "mid"]

    def test_sort_by_config_type(self):
        out = listing_sort.sort_session_entries(
            self._entries(), sort_by="config_type", order="asc"
        )
        assert out[-1]["config_type"] == "terrarium"

    def test_unknown_sort_field_falls_back_to_last_active(self):
        out = listing_sort.sort_session_entries(self._entries(), sort_by="bogus")
        assert [e["name"] for e in out] == ["alpha", "mid", "Bravo"]

    def test_unknown_order_is_treated_as_desc(self):
        out = listing_sort.sort_session_entries(self._entries(), order="sideways")
        assert out[0]["name"] == "alpha"

    def test_ties_keep_input_order(self):
        # Two entries with identical last_active keep their incoming order
        # (stable sort → mtime tiebreaker is preserved).
        entries = [
            {"name": "first", "last_active": "2025-01-01T00:00:00+00:00"},
            {"name": "second", "last_active": "2025-01-01T00:00:00+00:00"},
        ]
        out = listing_sort.sort_session_entries(entries)
        assert [e["name"] for e in out] == ["first", "second"]

    def test_does_not_mutate_input(self):
        entries = self._entries()
        before = [e["name"] for e in entries]
        listing_sort.sort_session_entries(entries)
        assert [e["name"] for e in entries] == before

    def test_empty(self):
        assert listing_sort.sort_session_entries([]) == []

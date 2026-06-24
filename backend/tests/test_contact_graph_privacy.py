"""Contact graph privacy — seal ACL + encrypted rosters."""
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.contact_graph import (
    COLLECTION_ROSTERS,
    COLLECTION_SEALS,
    LEGACY_COLLECTION,
    block_seal,
    decrypt_roster_blob,
    encrypt_roster_blob,
    migrate_legacy_contacts,
    mute_seal,
    pair_seal,
)
from core.contacts_graph_policy import (
    BLIND_COLLECTIONS,
    CONTACTS_GRAPH_STEPS,
    contacts_graph_privacy_complete,
)


def test_contacts_graph_steps_complete():
    assert contacts_graph_privacy_complete() is True
    assert len(CONTACTS_GRAPH_STEPS) == 5


def test_pair_seal_is_deterministic_and_sorted():
    os.environ["CONTACT_GRAPH_PEPPER"] = "test-pepper-abc"
    a = pair_seal("u_bbb", "u_aaa")
    b = pair_seal("u_aaa", "u_bbb")
    assert a == b
    assert len(a) == 64


def test_block_and_mute_seals_differ():
    os.environ["CONTACT_GRAPH_PEPPER"] = "test-pepper-abc"
    assert block_seal("u_a", "u_b") != mute_seal("u_a", "u_b")
    assert block_seal("u_a", "u_b") != pair_seal("u_a", "u_b")


def test_roster_encrypt_roundtrip():
    os.environ["CONTACT_GRAPH_PEPPER"] = "test-pepper-roster"
    entries = [{"contact_id": "u_peer", "blocked": False, "muted": True}]
    blob = encrypt_roster_blob("u_self", entries)
    out = decrypt_roster_blob("u_self", blob)
    assert out[0]["contact_id"] == "u_peer"
    assert out[0]["muted"] is True


def _memory_db():
    """In-memory Mongo stand-in for contact graph unit tests."""
    store: dict[str, list[dict]] = {
        COLLECTION_SEALS: [],
        "contact_blocks": [],
        "contact_mutes": [],
        COLLECTION_ROSTERS: [],
        LEGACY_COLLECTION: [],
    }

    def coll(name: str):
        m = MagicMock()

        async def find_one(query, projection=None):
            for row in store[name]:
                if all(row.get(k) == v for k, v in query.items()):
                    return dict(row)
            return None

        async def update_one(query, update, upsert=False):
            for row in store[name]:
                if all(row.get(k) == v for k, v in query.items()):
                    if "$set" in update:
                        row.update(update["$set"])
                    if "$setOnInsert" in update:
                        for k, v in update["$setOnInsert"].items():
                            row.setdefault(k, v)
                    return MagicMock(matched_count=1)
            if upsert:
                doc = dict(query)
                if "$setOnInsert" in update:
                    doc.update(update["$setOnInsert"])
                if "$set" in update:
                    doc.update(update["$set"])
                store[name].append(doc)
            return MagicMock(matched_count=0)

        async def delete_one(query):
            before = len(store[name])
            store[name][:] = [r for r in store[name] if not all(r.get(k) == v for k, v in query.items())]
            return MagicMock(deleted_count=before - len(store[name]))

        async def delete_many(query):
            if not query:
                n = len(store[name])
                store[name].clear()
                return MagicMock(deleted_count=n)
            before = len(store[name])
            store[name][:] = [r for r in store[name] if not all(r.get(k) == v for k, v in query.items())]
            return MagicMock(deleted_count=before - len(store[name]))

        async def insert_many(docs):
            store[name].extend(docs)

        async def count_documents(query):
            if not query:
                return len(store[name])
            return sum(1 for r in store[name] if all(r.get(k) == v for k, v in query.items()))

        class _Cursor:
            def __init__(self, rows):
                self._rows = rows

            def __aiter__(self):
                self._i = 0
                return self

            async def __anext__(self):
                if self._i >= len(self._rows):
                    raise StopAsyncIteration
                row = self._rows[self._i]
                self._i += 1
                return row

        def find(query, projection=None):
            rows = [r for r in store[name] if all(r.get(k) == v for k, v in query.items())]
            return _Cursor(rows)

        m.find_one = AsyncMock(side_effect=find_one)
        m.update_one = AsyncMock(side_effect=update_one)
        m.delete_one = AsyncMock(side_effect=delete_one)
        m.delete_many = AsyncMock(side_effect=delete_many)
        m.insert_many = AsyncMock(side_effect=insert_many)
        m.count_documents = AsyncMock(side_effect=count_documents)
        m.find = find
        return m

    db = MagicMock()
    for key in store:
        setattr(db, key, coll(key))
    db.__getitem__ = MagicMock(side_effect=lambda key: coll(key))
    return db, store


@pytest.mark.asyncio
async def test_establish_and_are_contacts():
    from unittest.mock import patch

    from core.contact_graph import are_contacts, establish_mutual_contact, remove_mutual_contact

    mem_db, store = _memory_db()
    with patch("core.contact_graph.db", mem_db):
        await establish_mutual_contact("u_one", "u_two")
        assert await are_contacts("u_one", "u_two") is True
        seal = next(r for r in store[COLLECTION_SEALS] if r["seal"] == pair_seal("u_one", "u_two"))
        assert "user_id" not in seal
        await remove_mutual_contact("u_one", "u_two")
        assert await are_contacts("u_one", "u_two") is False


@pytest.mark.asyncio
async def test_block_prevents_contact():
    from unittest.mock import patch

    from core.contact_graph import are_contacts, establish_mutual_contact, set_block

    mem_db, store = _memory_db()
    with patch("core.contact_graph.db", mem_db):
        await establish_mutual_contact("u_a", "u_b")
        await set_block("u_a", "u_b", blocked_flag=True)
        assert await are_contacts("u_a", "u_b") is False
        assert any(r["seal"] == block_seal("u_a", "u_b") for r in store["contact_blocks"])


@pytest.mark.asyncio
async def test_mute_seal_stored():
    from unittest.mock import patch

    from core.contact_graph import establish_mutual_contact, is_muted_pair, set_mute

    mem_db, _store = _memory_db()
    with patch("core.contact_graph.db", mem_db):
        await establish_mutual_contact("u_x", "u_y")
        await set_mute("u_x", "u_y", muted_flag=True)
        assert await is_muted_pair("u_x", "u_y") is True


@pytest.mark.asyncio
async def test_roster_stored_encrypted_not_plaintext():
    from unittest.mock import patch

    from core.contact_graph import establish_mutual_contact

    mem_db, store = _memory_db()
    with patch("core.contact_graph.db", mem_db):
        await establish_mutual_contact("u_r1", "u_r2")
        doc = next(r for r in store[COLLECTION_ROSTERS] if r["user_id"] == "u_r1")
        assert "ciphertext" in doc
        assert "u_r2" not in doc["ciphertext"]


@pytest.mark.asyncio
async def test_migrate_legacy_contacts():
    from unittest.mock import patch

    from core.contact_graph import are_contacts, is_muted_pair

    mem_db, store = _memory_db()
    store[LEGACY_COLLECTION].extend([
        {
            "user_id": "u_old_a",
            "contact_id": "u_old_b",
            "blocked": False,
            "muted": False,
            "created_at": "2026-06-01T00:00:00Z",
        },
        {
            "user_id": "u_old_b",
            "contact_id": "u_old_a",
            "blocked": False,
            "muted": True,
            "created_at": "2026-06-01T00:00:00Z",
        },
    ])
    with patch("core.contact_graph.db", mem_db):
        count = await migrate_legacy_contacts()
        assert count == 1
        assert len(store[LEGACY_COLLECTION]) == 0
        assert await are_contacts("u_old_a", "u_old_b") is True
        assert await is_muted_pair("u_old_b", "u_old_a") is True


def test_charter_and_router_wiring():
    repo = Path(__file__).resolve().parents[2]
    charter = (repo / "memory" / "CONTACT_GRAPH_PRIVACY_CHARTER.md").read_text(encoding="utf-8")
    assert "contact_seals" in charter
    assert "CONTACT_GRAPH_PEPPER" in charter
    contacts_router = (repo / "backend" / "routers" / "contacts.py").read_text(encoding="utf-8")
    assert "establish_mutual_contact" in contacts_router
    assert "db.contacts" not in contacts_router


def test_blind_collections_defined():
    assert "contact_seals" in BLIND_COLLECTIONS
    assert "contact_rosters" in BLIND_COLLECTIONS
    assert LEGACY_COLLECTION not in BLIND_COLLECTIONS


def test_metadata_m4_resolved():
    from core.metadata_policy import METADATA_GAPS

    m4 = next(g for g in METADATA_GAPS if g.gap_id == "M4")
    assert m4.resolved is True
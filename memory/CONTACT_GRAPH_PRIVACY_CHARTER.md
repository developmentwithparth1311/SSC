# Contact graph privacy charter

**Version:** 1.0  
**Effective:** 2026-06-24  
**Scope:** Server/staff cannot read the friend graph from database exports

---

## 1. Decision

| Before | After |
|--------|-------|
| `contacts` collection with plaintext `user_id` + `contact_id` | Seal-based edges + pepper-encrypted per-user rosters |

**Goal:** Mongo Atlas console, backups, and staff without `CONTACT_GRAPH_PEPPER` cannot reconstruct who is friends with whom.

**Residual metadata (accepted):**
- `friend_requests` pending rows name sender/recipient until TTL expires (Engine 1.3)
- Runtime ACL checks compute seals in memory during authenticated requests

---

## 2. Storage

| Collection | Contents | Staff-blind? |
|------------|----------|--------------|
| `contact_seals` | `seal = HMAC(pepper, sorted pair)` | ✅ |
| `contact_blocks` | `seal = HMAC(pepper, block:blocker:blocked)` | ✅ |
| `contact_mutes` | `seal = HMAC(pepper, mute:muter:muted)` | ✅ |
| `contact_rosters` | AES-GCM ciphertext per `user_id` | ✅ (without pepper) |

Plaintext `contacts` collection is **retired** after one-time migration.

---

## 3. API (unchanged contract)

- `GET /contacts` — roster decrypt + peer profile projection
- `POST /contacts/request` · accept/reject — unchanged UX
- Block/mute/remove — updates seals + encrypted roster

Panic wipe still preserves social graph (wife scenario).

---

## 4. Engine step

| Step | Description | Status |
|------|-------------|--------|
| CG.1 | Charter + `contact_graph.py` + policy gate | ✅ |
| CG.2 | Seal ACL replaces `are_contacts` plaintext lookup | ✅ |
| CG.3 | Legacy `contacts` migration on startup | ✅ |
| CG.4 | Push mute uses mute seals | ✅ |
| CG.5 | M4 closed in metadata policy | ✅ |

**Env:** `CONTACT_GRAPH_PEPPER` — set in production (`cloud_run.env`); never commit.
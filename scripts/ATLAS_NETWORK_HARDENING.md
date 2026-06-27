# MongoDB Atlas network hardening (TASK O.6)

**Status (2026-06-27):** GCP static egress **applied**. Atlas allowlist script ready — run after API keys are in `backend/atlas-api.env`.

## What “guide only” meant

Earlier, O.6 was only a markdown checklist because Cloud Run has **no fixed IP** by default, so you cannot safely remove Atlas `0.0.0.0/0` until GCP egress is pinned. That infra is now live.

## Applied on GCP (`super-chat-b0992`, `europe-west1`)

| Resource | Name | Value |
|----------|------|-------|
| Static NAT IP | `ssc-nat-ip` | **34.140.240.41** |
| Cloud Router | `ssc-nat-router` | default VPC |
| Cloud NAT | `ssc-cloud-nat` | MANUAL_ONLY → `ssc-nat-ip` |
| VPC connector | `ssc-vpc-connector` | `10.8.0.0/28` |
| Cloud Run | `ssc-api` | `vpc-egress=all-traffic` via connector |

Re-apply idempotently:

```powershell
.\scripts\setup_gcp_nat_egress.ps1
```

Verify API still reaches Mongo:

```powershell
Invoke-RestMethod https://api.supersecurechat.com/api/health
```

## Atlas IP allowlist (final lockdown step)

1. Copy `backend/atlas-api.env.example` → `backend/atlas-api.env`
2. Add Atlas Admin API keys (Organization → Access Manager → API Keys)
3. Set `SSC_DEV_EGRESS_IP` to your laptop public IP if you run janitor/scripts locally
4. Run:

```powershell
backend\venv\Scripts\python.exe scripts\apply_atlas_ip_allowlist.py
```

This **adds** `34.140.240.41/32` (Cloud Run) + your dev IP, then **removes** `0.0.0.0/0` and `::/0`.

Dry-run first:

```powershell
backend\venv\Scripts\python.exe scripts\apply_atlas_ip_allowlist.py --dry-run
```

## Manual fallback (Atlas UI)

1. [MongoDB Atlas](https://cloud.mongodb.com) → **Network Access**
2. **Add** `34.140.240.41/32` — comment: SSC Cloud Run NAT
3. **Add** your dev machine IP `/32` — comment: founder scripts (optional)
4. **Delete** `0.0.0.0/0` and `::/0` only after step 2 health check passes

## Cost note

- Static IP + NAT + VPC connector: low monthly GCP cost on current traffic
- Atlas Private Endpoint: paid — defer until scale requires it
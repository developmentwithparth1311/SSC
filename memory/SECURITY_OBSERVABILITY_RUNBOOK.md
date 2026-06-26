# Security Observability Runbook

## Purpose
Operational response guide for security-relevant anomaly events emitted by backend logs.

## Event format
All events are emitted as log lines beginning with:

- security-event event=<event_name> key=value ...

Primary source files:

- backend/core/security_observability.py
- backend/security.py
- backend/core/retention_janitor.py

## Event catalog

1. redis_rate_limit_fallback
- Trigger: REDIS_URL configured but Redis connection failed and app falls back to memory rate limiting.
- Risk: weaker distributed rate limits and revocation behavior across instances.
- Immediate action:
  - Validate Redis health and credentials.
  - For production, treat as SEV-1 and redeploy only after Redis connectivity restored.

2. retention_orphan_gridfs_deleted
- Trigger: janitor deleted orphan GridFS blobs.
- Risk: indicates retention drift occurred before janitor correction.
- Immediate action:
  - Run retention attestation (/api/retention/attestation).
  - Review recent file upload/delete behavior and janitor interval.

3. retention_janitor_errors
- Trigger: janitor run encountered cleanup errors.
- Risk: stale data may persist beyond retention policy.
- Immediate action:
  - Run scripts/retention_janitor.py --json.
  - Run scripts/retention_proof.py --json.
  - Check Mongo health and permissions on ssc_files bucket.

4. rate-limit reject logs
- Trigger: request denied by limiter.
- Formats include limiter names such as:
  - friend_request_burst
  - friend_request_daily
  - group_create
  - file_upload_burst
  - file_upload_sustained
- Immediate action:
  - If spike from many user_ids: potential abuse wave.
  - If spike from one user_id: targeted abuse attempt.

## Incident levels

1. SEV-1
- redis_rate_limit_fallback in production
- repeated retention_janitor_errors

2. SEV-2
- sustained retention_orphan_gridfs_deleted events
- sudden broad rate-limit spikes across multiple user_ids

3. SEV-3
- occasional isolated rate-limit rejects from single user

## Standard response sequence

1. Capture evidence
- Save relevant logs with timestamp window.
- Save current attestation outputs to test_reports.

2. Verify retention state
- backend/scripts/retention_proof.py --json
- backend/scripts/retention_janitor.py --json

3. Verify infra state
- Redis ping/connectivity
- Mongo health and index presence

4. Mitigate
- Restore Redis if degraded.
- Run janitor once manually if orphan/deletion errors appear.
- If abuse wave, tighten limiter values and redeploy.

5. Post-incident
- Add roadmap changelog entry with root cause and corrective action.
- Keep artifacts in test_reports for audit trail.

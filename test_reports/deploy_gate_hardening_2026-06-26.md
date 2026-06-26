# Deploy Gate Hardening Evidence (L.6)

Date: 2026-06-26

## 1) Gate initially blocked deploy (expected)
- Command: backend/scripts/prepare_cloud_run_deploy.py
- Result: failed with retention proof check
- Failure reason: orphan_gridfs_blobs check reported 5 orphaned blobs

## 2) Remediation executed
- Command: backend/scripts/retention_janitor.py --json (with cloud_run.env values)
- Result:
  - scanned_gridfs_blobs: 5
  - orphaned_gridfs_blobs_deleted: 5
  - errors: 0

## 3) Gate passed after remediation
- Command: backend/scripts/prepare_cloud_run_deploy.py
- Result: success, generated backend/.cloudrun/deploy_env.yaml

## 4) Enforced checks now in deploy preparation
- Security env validation:
  - JWT_SECRET >= 48 chars
  - CONTACT_GRAPH_PEPPER strong and not dev default
  - DB_NAME must be ssc
  - MONGO_URL must not point to localhost
  - REDIS_URL must use redis:// or rediss://
- Retention proof gate:
  - Runs scripts/retention_proof.py --json
  - Blocks deploy when proof fails

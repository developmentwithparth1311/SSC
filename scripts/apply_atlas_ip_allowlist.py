"""Apply MongoDB Atlas project IP allowlist for TASK O.6.

Adds Cloud Run NAT egress + optional founder/dev IPs, then removes open-world entries.

Requires backend/atlas-api.env (gitignored):
  ATLAS_PUBLIC_KEY=...
  ATLAS_PRIVATE_KEY=...
  ATLAS_PROJECT_ID=...          # 24-hex project id (optional if ATLAS_CLUSTER=ssc resolves it)
  ATLAS_CLUSTER=ssc             # optional — used to discover project id
  SSC_NAT_EGRESS_IP=34.140.240.41
  SSC_DEV_EGRESS_IP=86.166.40.195   # optional founder laptop for scripts/local dev

Usage:
  backend\\venv\\Scripts\\python.exe scripts\\apply_atlas_ip_allowlist.py
  backend\\venv\\Scripts\\python.exe scripts\\apply_atlas_ip_allowlist.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from requests.auth import HTTPDigestAuth

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
ENV_PATH = BACKEND / "atlas-api.env"
API_BASE = "https://cloud.mongodb.com/api/atlas/v2"
API_VERSION = "application/vnd.atlas.2023-01-01+json"


def _load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def _headers() -> dict[str, str]:
    return {
        "Accept": API_VERSION,
        "Content-Type": API_VERSION,
    }


def _auth(cfg: dict[str, str]) -> HTTPDigestAuth:
    public = (cfg.get("ATLAS_PUBLIC_KEY") or os.environ.get("ATLAS_PUBLIC_KEY") or "").strip()
    private = (cfg.get("ATLAS_PRIVATE_KEY") or os.environ.get("ATLAS_PRIVATE_KEY") or "").strip()
    if not public or not private:
        raise SystemExit(
            f"Missing Atlas API keys. Create {ENV_PATH} from atlas-api.env.example "
            "(Atlas UI → Organization → Access Manager → API Keys)."
        )
    return HTTPDigestAuth(public, private)


def _get(session: requests.Session, path: str, *, params: dict[str, Any] | None = None) -> Any:
    r = session.get(f"{API_BASE}{path}", params=params, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"GET {path} -> {r.status_code}: {r.text[:500]}")
    return r.json()


def _post(session: requests.Session, path: str, payload: list[dict[str, Any]] | dict[str, Any]) -> Any:
    r = session.post(f"{API_BASE}{path}", data=json.dumps(payload), timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"POST {path} -> {r.status_code}: {r.text[:500]}")
    return r.json()


def _delete(session: requests.Session, path: str) -> None:
    r = session.delete(f"{API_BASE}{path}", timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"DELETE {path} -> {r.status_code}: {r.text[:500]}")


def _discover_project_id(session: requests.Session, cluster_name: str) -> str:
    projects = _get(session, "/groups", params={"itemsPerPage": 500})
    for project in projects.get("results", []):
        group_id = project.get("id")
        if not group_id:
            continue
        try:
            clusters = _get(session, f"/groups/{group_id}/clusters", params={"itemsPerPage": 500})
        except RuntimeError:
            continue
        for cluster in clusters.get("results", []):
            if (cluster.get("name") or "").lower() == cluster_name.lower():
                return group_id
    raise SystemExit(f"Could not find Atlas project for cluster '{cluster_name}'")


def _list_access_entries(session: requests.Session, project_id: str) -> list[dict[str, Any]]:
    data = _get(session, f"/groups/{project_id}/accessList", params={"itemsPerPage": 500})
    return list(data.get("results") or [])


def _entry_key(entry: dict[str, Any]) -> str:
    return (
        entry.get("cidrBlock")
        or entry.get("ipAddress")
        or entry.get("awsSecurityGroup")
        or ""
    )


def _is_open_world(entry: dict[str, Any]) -> bool:
    cidr = (entry.get("cidrBlock") or "").strip()
    ip = (entry.get("ipAddress") or "").strip()
    return cidr in {"0.0.0.0/0", "::/0"} or ip in {"0.0.0.0", "::"}


def main() -> int:
    parser = argparse.ArgumentParser(description="SSC Atlas IP allowlist hardening (O.6)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without applying")
    args = parser.parse_args()

    cfg = _load_env(ENV_PATH)
    nat_ip = (cfg.get("SSC_NAT_EGRESS_IP") or os.environ.get("SSC_NAT_EGRESS_IP") or "34.140.240.41").strip()
    dev_ip = (cfg.get("SSC_DEV_EGRESS_IP") or os.environ.get("SSC_DEV_EGRESS_IP") or "").strip()
    project_id = (cfg.get("ATLAS_PROJECT_ID") or os.environ.get("ATLAS_PROJECT_ID") or "").strip()
    cluster_name = (cfg.get("ATLAS_CLUSTER") or os.environ.get("ATLAS_CLUSTER") or "ssc").strip()

    session = requests.Session()
    session.auth = _auth(cfg)
    session.headers.update(_headers())

    if not project_id:
        project_id = _discover_project_id(session, cluster_name)
        print(f"Discovered ATLAS_PROJECT_ID={project_id} (cluster={cluster_name})")

    desired: list[dict[str, str]] = [
        {"cidrBlock": f"{nat_ip}/32", "comment": "SSC Cloud Run NAT egress"},
    ]
    if dev_ip:
        desired.append({"cidrBlock": f"{dev_ip}/32", "comment": "SSC founder dev/scripts"})

    existing = _list_access_entries(session, project_id)
    existing_keys = {_entry_key(e) for e in existing}

    to_add = [e for e in desired if e["cidrBlock"] not in existing_keys]
    to_remove = [e for e in existing if _is_open_world(e)]

    print("Atlas IP allowlist plan:")
    for entry in to_add:
        print(f"  ADD    {entry['cidrBlock']} — {entry.get('comment', '')}")
    for entry in to_remove:
        print(f"  REMOVE {_entry_key(entry)}")
    if not to_add and not to_remove:
        print("  (no changes needed)")
        return 0

    if args.dry_run:
        print("Dry run — no Atlas changes applied.")
        return 0

    if to_add:
        _post(session, f"/groups/{project_id}/accessList", to_add)
        print(f"Added {len(to_add)} allowlist entry/entries.")

    for entry in to_remove:
        key = _entry_key(entry)
        if not key:
            continue
        encoded = quote(key, safe="")
        _delete(session, f"/groups/{project_id}/accessList/{encoded}")
        print(f"Removed open-world entry: {key}")

    print("Atlas allowlist updated. Verify: curl https://api.supersecurechat.com/api/health")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
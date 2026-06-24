#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/frontend"
echo "== Building React bundle for desktop =="
yarn build:desktop
cd desktop
echo "== Installing desktop dependencies =="
yarn install
echo "== Building Mac dmg (requires macOS) =="
export CSC_IDENTITY_AUTO_DISCOVERY=false
yarn build:mac
echo ""
echo "DONE: frontend/desktop/dist/SSC-1.0.0-*.dmg"
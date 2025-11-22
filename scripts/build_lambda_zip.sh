#!/usr/bin/env bash
set -euo pipefail

echo "=== UTC Lambda: Build Start ==="

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAMBDA_DIR="${PROJECT_ROOT}/lambda_http"
BUILD_DIR="${LAMBDA_DIR}/build"

echo "[1] Clean build directory"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

echo "[2] Install Lambda requirements (including ../requirements.txt)"
pip install -r "${LAMBDA_DIR}/requirements.txt" -t "${BUILD_DIR}"

echo "[3] Copy source code"
cp -r "${PROJECT_ROOT}/core" "${BUILD_DIR}/core"
cp -r "${PROJECT_ROOT}/backend" "${BUILD_DIR}/backend"
cp "${LAMBDA_DIR}/main.py" "${BUILD_DIR}/main.py"

echo "[4] Create deployment ZIP"
(
  cd "${BUILD_DIR}"
  zip -r ../deployment.zip .
)

echo "=== UTC Lambda: Build Completed Successfully ==="
echo "ZIP output → ${LAMBDA_DIR}/deployment.zip"


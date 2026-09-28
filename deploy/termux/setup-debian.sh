#!/usr/bin/env bash
# One-time setup INSIDE Debian (proot-distro) on the phone. Safe to re-run.
#
#   proot-distro login debian
#   cd ~/wkai && bash deploy/termux/setup-debian.sh
#
# Installs Node 20 (same major as render.yaml NODE_VERSION), python3 (for the
# backend's POST /api/run sandbox), then installs backend dependencies.
# Postgres stays on Neon and Redis on Upstash. Nothing here compiles native
# code.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND_DIR="$REPO_DIR/wkai-backend"
NODE_MAJOR=20

echo "==> apt packages"
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl git xz-utils procps nano python3

echo "==> Node.js ${NODE_MAJOR}"
current_major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
if [ "$current_major" -ge 20 ]; then
  echo "    node $(node -v) already installed, keeping it"
else
  case "$(uname -m)" in
    aarch64) arch=arm64 ;;
    armv7l)  arch=armv7l ;;
    x86_64)  arch=x64 ;;
    *) echo "Unsupported CPU: $(uname -m)" >&2; exit 1 ;;
  esac
  base="https://nodejs.org/dist/latest-v${NODE_MAJOR}.x"
  tmp="$(mktemp -d)"
  curl -fsSL "$base/SHASUMS256.txt" -o "$tmp/SHASUMS256.txt"
  tarball="$(grep -o "node-v[0-9.]*-linux-${arch}\.tar\.xz" "$tmp/SHASUMS256.txt" | head -1)"
  curl -fSL "$base/$tarball" -o "$tmp/$tarball"
  (cd "$tmp" && grep " $tarball\$" SHASUMS256.txt | sha256sum -c -)
  tar -xJf "$tmp/$tarball" -C /usr/local --strip-components=1
  rm -rf "$tmp"
  echo "    installed node $(node -v)"
fi

echo "==> npm ci (wkai-backend only)"
cd "$BACKEND_DIR"
npm ci --no-audit --no-fund

if [ ! -f .env ]; then
  cp .env.example .env
  echo
  echo "!!  Created .env from .env.example. Fill it in before starting:"
  echo "    nano $BACKEND_DIR/.env"
  echo "    (copy every value from Render > wkai-backend > Environment)"
fi

echo
echo "Done. Test in the foreground with:  bash $REPO_DIR/deploy/termux/run.sh"

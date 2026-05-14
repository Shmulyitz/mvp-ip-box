#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="/opt/smartbox"
VENV_DIR="$TARGET_DIR/venv"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo ./install.sh"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
  python3 python3-venv python3-pip python3-gi python3-gi-cairo \
  gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 \
  gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
  libgirepository1.0-dev libcairo2-dev pkg-config rsync

mkdir -p "$TARGET_DIR"
rsync -a --delete --exclude '.git' --exclude '__pycache__' "$SRC_DIR/" "$TARGET_DIR/"

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip wheel setuptools
"$VENV_DIR/bin/pip" install -r "$TARGET_DIR/requirements.txt"

mkdir -p "$TARGET_DIR/data"
"$VENV_DIR/bin/python" "$TARGET_DIR/scripts/init_db.py"

install -m 0644 "$TARGET_DIR/systemd/smartbox-api.service" /etc/systemd/system/smartbox-api.service
install -m 0644 "$TARGET_DIR/systemd/smartbox-video.service" /etc/systemd/system/smartbox-video.service

systemctl daemon-reload
systemctl enable smartbox-api
systemctl enable smartbox-video
systemctl restart smartbox-api
systemctl restart smartbox-video

echo "Install complete"
echo "Web admin: http://<device-ip>:8080"
echo "Default credentials: admin / admin"

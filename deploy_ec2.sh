#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./deploy_ec2.sh -k "C:\Users\shmuly\Downloads\mvp-ip-box.pem" -h 54.234.153.203 [-u ubuntu] [-r ~/mvp-ip-box] [-b main]

Example:
  ./deploy_ec2.sh -k ~/.ssh/my-key.pem -h 3.120.45.67
USAGE
}

KEY_PATH=""
EC2_HOST=""
SSH_USER="ubuntu"
REPO_DIR="~/mvp-ip-box"
BRANCH="main"

while getopts ":k:h:u:r:b:" opt; do
  case "$opt" in
    k) KEY_PATH="$OPTARG" ;;
    h) EC2_HOST="$OPTARG" ;;
    u) SSH_USER="$OPTARG" ;;
    r) REPO_DIR="$OPTARG" ;;
    b) BRANCH="$OPTARG" ;;
    *) usage; exit 1 ;;
  esac
done

if [[ -z "$KEY_PATH" || -z "$EC2_HOST" ]]; then
  usage
  exit 1
fi

if [[ ! -f "$KEY_PATH" ]]; then
  echo "SSH key not found: $KEY_PATH"
  exit 1
fi

echo "Deploying branch '$BRANCH' to $SSH_USER@$EC2_HOST ..."

ssh -o StrictHostKeyChecking=accept-new -i "$KEY_PATH" "$SSH_USER@$EC2_HOST" "BRANCH='$BRANCH' REPO_DIR='$REPO_DIR' bash -s" <<'REMOTE'
set -euo pipefail

cd "$REPO_DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

cd smartbox
chmod +x install.sh
sed -i 's/\r$//' install.sh
sudo bash ./install.sh

sudo systemctl daemon-reload
sudo systemctl enable --now smartbox-api smartbox-video

echo "--- smartbox-api status ---"
sudo systemctl status smartbox-api --no-pager -l || true

echo "--- smartbox-video status ---"
sudo systemctl status smartbox-video --no-pager -l || true
REMOTE

echo "Deploy complete."

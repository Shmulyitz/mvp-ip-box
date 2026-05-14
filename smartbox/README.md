# Smartbox MVP

Python MVP for HDMI RTSP camera grid rendering and local admin.

## Install on Ubuntu

```bash
git clone <repo>
cd smartbox
sudo ./install.sh
sudo systemctl enable smartbox-api
sudo systemctl enable smartbox-video
sudo reboot
```

If `install.sh` fails with permission or line-ending errors:

```bash
chmod +x install.sh
sed -i 's/\r$//' install.sh
sudo bash ./install.sh
```

## Services

- API: `http://device-ip:8080`
- Default basic auth: `admin / admin`
- API reads/writes SQLite at `/opt/smartbox/data/smartbox.db`

Set secure credentials before production use by editing:

- `/etc/systemd/system/smartbox-api.service`
- `SMARTBOX_ADMIN_PASSWORD`
- `SMARTBOX_FERNET_KEY`

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl restart smartbox-api
sudo systemctl restart smartbox-video
```

## Notes

- Supports layouts 1 / 4 / 9 / 16.
- Uses GStreamer compositor to render to local HDMI.
- No cloud, no browser playback for HDMI, no Docker requirement.

## One-command EC2 deploy

From your local machine (repo root), run:

```bash
chmod +x deploy_ec2.sh
./deploy_ec2.sh -k /path/to/key.pem -h <EC2_PUBLIC_IP>
```

This script SSHes to EC2, pulls latest `main`, runs `smartbox/install.sh`, and ensures both services are enabled and running.

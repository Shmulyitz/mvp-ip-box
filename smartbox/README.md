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

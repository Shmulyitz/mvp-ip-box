Security Requirements for MVP

- Web admin should bind to local LAN only by default.
- Add a simple admin password.
- Store camera passwords encrypted using Fernet.
- Do not log full RTSP URLs with passwords.
- Mask passwords in API responses.
- Do not expose the API publicly.
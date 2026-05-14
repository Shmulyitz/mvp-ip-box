Systemd Services

smartbox-api.service:
- Runs FastAPI on port 8080.
- Starts on boot.
- Restarts on failure.

smartbox-video.service:
- Runs Python video engine.
- Starts on boot after network is online.
- Restarts on failure.
- Reads layout config from SQLite.
- Rebuilds pipeline when /api/video/reload is called.

Reload mechanism:
MVP option:
- API writes a reload flag into SQLite settings.
- Video service checks every 2 seconds.
Better option:
- API sends SIGHUP to video process.
- Video service catches SIGHUP and rebuilds pipeline.
Project: Smart IP Box MVP

Goal:
Build a Python-based MVP for a Linux appliance that displays multiple IP camera RTSP streams on an HDMI monitor in a grid layout and provides a local web API/admin UI for configuration.

Primary MVP Target:
- Run on Ubuntu Server or Debian Linux.
- Support 1, 4, 9, and 16 camera grid layouts.
- Use RTSP camera streams.
- Use GStreamer for decoding/compositing/rendering.
- Use Python FastAPI for the local API.
- Use SQLite for local configuration.
- Use systemd services for appliance-style auto-start and recovery.
- No cloud, no master/slave, no paid licensing, no Windows.

Important Technical References:
- FastAPI is the Python API framework.
- GStreamer Python bindings use GObject Introspection.
- ONVIF discovery can be added using python-onvif-zeep, but ONVIF is optional for the first working MVP.

Core Architecture:
1. smartbox-api
   - FastAPI app.
   - Manages cameras, layouts, settings, and stream control.
   - Stores config in SQLite.
   - Exposes REST endpoints.
   - Sends commands to the video engine.

2. smartbox-video
   - Python service using GStreamer.
   - Reads active layout and camera config.
   - Builds GStreamer pipelines.
   - Outputs the final composed grid to HDMI/display.
   - Monitors stream health.
   - Reconnects failed streams.

3. smartbox-db
   - SQLite database.
   - Stores cameras, layouts, layout cells, device settings, and event logs.

4. smartbox-watchdog
   - Can be simple in MVP.
   - systemd should restart failed services.
   - Later version can detect frozen video and restart smartbox-video.

Recommended Runtime:
- OS: Ubuntu Server 24.04 LTS or Debian 12.
- Python: 3.11+
- API: FastAPI + Uvicorn.
- DB: SQLite.
- Video: GStreamer 1.22+.
- Python GStreamer: PyGObject.
- Process manager: systemd.
- Hardware decode target: Intel VAAPI / Quick Sync where available.
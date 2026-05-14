Acceptance Criteria

The MVP is accepted only if all of these pass:

1. Device boots and starts API automatically.
2. Device boots and starts video output automatically.
3. User can open web admin at:
   http://device-ip:8080
4. User can add RTSP cameras.
5. User can create a 4-camera layout.
6. User can create a 16-camera layout.
7. User can assign cameras to layout cells.
8. User can activate a layout.
9. HDMI output updates to the selected layout.
10. If one camera is disconnected, the full system continues running.
11. Disconnected camera cell shows offline/blank placeholder.
12. System retries failed stream.
13. Stream errors are visible in the web UI.
14. Rebooting the device restores the last active layout.
15. The MVP runs for 24 hours with at least 4 streams without crashing.
16. Stretch goal: 16 substreams run for 24 hours without crashing.
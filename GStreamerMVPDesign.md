GStreamer MVP Design

Use Python with PyGObject.

Preferred pipeline concept:

For each camera:
rtspsrc
→ rtph264depay
→ h264parse
→ hardware decoder if available
→ videoconvert
→ videoscale
→ capsfilter target size/framerate
→ queue
→ compositor sink

Compositor:
compositor
→ videoconvert
→ fpsdisplaysink or autovideosink

For Intel VAAPI:
Try vaapih264dec if available.
Fallback to avdec_h264.

Decoder selection logic:
1. Check if vaapih264dec exists.
2. If yes, use vaapih264dec.
3. Otherwise use avdec_h264.

MVP can first support H.264 only.

For each grid:
1-view:
- output 1920x1080
- cell 0: x=0, y=0, w=1920, h=1080

4-view:
- cell size 960x540
- positions:
  0: 0,0
  1: 960,0
  2: 0,540
  3: 960,540

9-view:
- cell size 640x360
- positions:
  row = index // 3
  col = index % 3
  x = col * 640
  y = row * 360

16-view:
- cell size 480x270
- positions:
  row = index // 4
  col = index % 4
  x = col * 480
  y = row * 270

Output resolution:
1920x1080.

RTSP settings:
- protocols=tcp by default
- latency=500
- retry reconnect outside pipeline if stream fails

Important:
The video engine should not depend on the web browser for displaying streams.
The browser only configures the system.
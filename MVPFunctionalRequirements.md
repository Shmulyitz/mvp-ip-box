MVP Functional Requirements

1. Camera Management
The system must allow users to:
- Add a camera manually.
- Edit a camera.
- Delete a camera.
- Test a camera RTSP URL.
- Store camera name.
- Store RTSP main stream URL.
- Store RTSP sub stream URL.
- Store username/password if needed.
- Enable or disable a camera.

Camera fields:
- id
- name
- ip_address
- rtsp_main_url
- rtsp_sub_url
- username
- password_encrypted
- preferred_stream: main/sub
- enabled
- created_at
- updated_at

MVP rule:
For 16-grid layout, use substreams by default.
For 1-camera layout, use main stream if available.

2. Layout Management
The system must support:
- 1-view layout
- 4-view layout
- 9-view layout
- 16-view layout

Each layout has cells.
Each cell can be assigned one camera.

Layout fields:
- id
- name
- grid_size: 1, 4, 9, 16
- is_active
- created_at
- updated_at

Layout cell fields:
- id
- layout_id
- cell_index
- camera_id
- stream_type: main/sub

3. Video Display
The video engine must:
- Read the active layout from SQLite.
- Create one RTSP input per assigned camera.
- Decode each stream.
- Scale each stream to its grid cell.
- Composite all streams into one output.
- Render the output to HDMI/local display.
- Show a placeholder for empty cells.
- Show a placeholder for failed streams.

Minimum supported target:
- 16 streams at 640x360 or 720p substream.
- 10-15 FPS target per stream.
- H.264 required.
- H.265 optional for MVP.

4. Stream Health
The system must track:
- camera online/offline
- last frame timestamp
- reconnect count
- last error message
- current FPS if easy to collect

If a stream fails:
- Do not crash the full layout.
- Show offline placeholder for that cell.
- Retry reconnect every 5 seconds.
- Log the failure.

5. API
Create these REST endpoints:

Health:
GET /api/health
Returns:
{
  "status": "ok",
  "api_version": "0.1.0",
  "video_service_status": "running"
}

Cameras:
GET /api/cameras
POST /api/cameras
GET /api/cameras/{id}
PUT /api/cameras/{id}
DELETE /api/cameras/{id}
POST /api/cameras/{id}/test

Layouts:
GET /api/layouts
POST /api/layouts
GET /api/layouts/{id}
PUT /api/layouts/{id}
DELETE /api/layouts/{id}
POST /api/layouts/{id}/activate
PUT /api/layouts/{id}/cells/{cell_index}

Video:
POST /api/video/reload
POST /api/video/restart
GET /api/video/status

Events:
GET /api/events

Settings:
GET /api/settings
PUT /api/settings

6. Simple Admin UI
Create a basic local web UI served by FastAPI.

Pages:
- Dashboard
- Cameras
- Layout Editor
- Stream Status
- Settings

Dashboard:
- Active layout
- Number of active cameras
- Stream health list
- Video service status

Cameras page:
- Add/edit/delete camera
- Test RTSP URL

Layout Editor:
- Select grid size: 1, 4, 9, 16
- Assign cameras to cells
- Save layout
- Activate layout

Stream Status:
- Camera name
- Online/offline
- Last error
- Reconnect count

Settings:
- Device name
- Network display only for MVP
- Restart video service button

UI can be plain HTML/Jinja or React.
For fastest MVP, use FastAPI + Jinja templates.
Database Schema

Use SQLite.

Table: cameras
- id INTEGER PRIMARY KEY AUTOINCREMENT
- name TEXT NOT NULL
- ip_address TEXT
- rtsp_main_url TEXT
- rtsp_sub_url TEXT
- username TEXT
- password_encrypted TEXT
- preferred_stream TEXT DEFAULT 'sub'
- enabled INTEGER DEFAULT 1
- created_at TEXT
- updated_at TEXT

Table: layouts
- id INTEGER PRIMARY KEY AUTOINCREMENT
- name TEXT NOT NULL
- grid_size INTEGER NOT NULL
- is_active INTEGER DEFAULT 0
- created_at TEXT
- updated_at TEXT

Table: layout_cells
- id INTEGER PRIMARY KEY AUTOINCREMENT
- layout_id INTEGER NOT NULL
- cell_index INTEGER NOT NULL
- camera_id INTEGER
- stream_type TEXT DEFAULT 'sub'
- FOREIGN KEY(layout_id) REFERENCES layouts(id)
- FOREIGN KEY(camera_id) REFERENCES cameras(id)

Table: stream_status
- camera_id INTEGER PRIMARY KEY
- status TEXT
- last_frame_at TEXT
- last_error TEXT
- reconnect_count INTEGER DEFAULT 0
- fps REAL
- updated_at TEXT

Table: events
- id INTEGER PRIMARY KEY AUTOINCREMENT
- level TEXT
- event_type TEXT
- camera_id INTEGER
- message TEXT
- created_at TEXT

Table: settings
- key TEXT PRIMARY KEY
- value TEXT
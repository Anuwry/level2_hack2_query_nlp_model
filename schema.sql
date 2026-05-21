-- Vehicle metadata database for the Jetson Nano CCTV pipeline.
-- Required output contract: Date,CCTV_ID,First_Seen,Last_Seen,Brand,Color,Type,Event.
-- SQLite-first design: one compact row per stable vehicle track, sparse support logs, no image blobs.

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA temp_store = MEMORY;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY,
  run_tag TEXT NOT NULL UNIQUE,
  started_at TEXT NOT NULL,
  ended_at TEXT,
  source_mode TEXT,
  model_name TEXT,
  input_size INTEGER,
  detector_skip_initial INTEGER,
  notes TEXT
);

-- WRITE_PATTERN: insert once per camera at run start; normally no updates.
CREATE TABLE IF NOT EXISTS cameras (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL,
  camera_id TEXT NOT NULL,
  source_uri TEXT,
  width INTEGER,
  height INTEGER,
  fps_hint REAL,
  UNIQUE(run_id, camera_id),
  FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE CASCADE
);

-- One row per stable vehicle UUID / track.
-- WRITE_PATTERN: insert once, update while active, final update when track exits.
-- This is the main table for final answers.
CREATE TABLE IF NOT EXISTS vehicle_tracks (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL,
  camera_id TEXT NOT NULL,
  uuid TEXT NOT NULL,
  event TEXT NOT NULL DEFAULT 'pass' CHECK (event IN ('entry', 'exit', 'pass')),

  first_seen_ts REAL NOT NULL,
  last_seen_ts REAL NOT NULL,
  first_seen_iso TEXT,
  last_seen_iso TEXT,

  vehicle_type TEXT,
  vehicle_conf REAL,

  color TEXT,
  color_conf REAL,
  color_votes_json TEXT,

  brand TEXT,
  brand_conf REAL,
  brand_model TEXT,
  brand_status TEXT NOT NULL DEFAULT 'pending',
  brand_error TEXT,

  best_crop_path TEXT,
  best_crop_quality REAL DEFAULT 0.0,
  best_bbox_x1 INTEGER,
  best_bbox_y1 INTEGER,
  best_bbox_x2 INTEGER,
  best_bbox_y2 INTEGER,

  frame_count INTEGER NOT NULL DEFAULT 0,
  observation_count INTEGER NOT NULL DEFAULT 0,
  vit_runs INTEGER NOT NULL DEFAULT 0,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE(run_id, camera_id, uuid),
  FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE CASCADE
);

-- Optional audit table. Keep it sparse on Jetson.
-- Suggested policy: write only detector frames, periodic snapshots, or best-crop updates.
-- WRITE_PATTERN: append-only, optional, never per frame.
CREATE TABLE IF NOT EXISTS vehicle_observations (
  id INTEGER PRIMARY KEY,
  track_id INTEGER NOT NULL,
  ts REAL NOT NULL,
  ts_iso TEXT,
  frame_index INTEGER,

  bbox_x1 INTEGER,
  bbox_y1 INTEGER,
  bbox_x2 INTEGER,
  bbox_y2 INTEGER,
  yolo_conf REAL,

  color TEXT,
  crop_path TEXT,
  crop_quality REAL,

  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(track_id) REFERENCES vehicle_tracks(id) ON DELETE CASCADE
);

-- ViT brand attempts, normally 1 per UUID and rarely 2.
-- WRITE_PATTERN: insert when queued, update once when finished/failed.
CREATE TABLE IF NOT EXISTS brand_attempts (
  id INTEGER PRIMARY KEY,
  track_id INTEGER NOT NULL,
  queued_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  started_at TEXT,
  finished_at TEXT,

  crop_path TEXT NOT NULL,
  crop_quality REAL,

  brand TEXT,
  brand_conf REAL,
  topk_json TEXT,
  status TEXT NOT NULL DEFAULT 'queued',
  error TEXT,
  latency_ms REAL,

  FOREIGN KEY(track_id) REFERENCES vehicle_tracks(id) ON DELETE CASCADE
);

-- Low-frequency service health/performance logs.
-- Keep interval around 1-5 seconds; do not write per frame.
-- WRITE_PATTERN: append-only every 2-5 seconds.
CREATE TABLE IF NOT EXISTS performance_samples (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL,
  ts REAL NOT NULL,
  ts_iso TEXT,

  avg_fps REAL,
  active_cameras INTEGER,
  detector_skip INTEGER,

  capture_queue_size INTEGER,
  detection_queue_size INTEGER,
  brand_queue_size INTEGER,
  brand_queue_dropped INTEGER,
  db_queue_size INTEGER,

  frame_loop_ms_ema REAL,
  yolo_ms_ema REAL,
  tracking_ms_ema REAL,
  hsv_ms_ema REAL,
  vit_ms_ema REAL,
  db_write_ms_ema REAL,

  active_tracks INTEGER,
  completed_tracks INTEGER,
  vit_jobs_done INTEGER,
  vit_jobs_skipped INTEGER,
  vit_jobs_dropped INTEGER,

  ram_used_mb REAL,
  swap_used_mb REAL,
  cpu_pct REAL,
  gpu_pct REAL,
  temp_c REAL,
  power_w REAL,

  note TEXT,
  FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE CASCADE
);

-- WATCHDOG events are sparse and useful for debugging 3-hour runs.
-- WRITE_PATTERN: append-only only when watchdog takes action.
CREATE TABLE IF NOT EXISTS watchdog_events (
  id INTEGER PRIMARY KEY,
  run_id INTEGER,
  ts REAL NOT NULL,
  ts_iso TEXT,
  event_type TEXT NOT NULL,
  command TEXT,
  reason TEXT,
  fps REAL,
  q_depth INTEGER,
  ram_used_pct REAL,
  temp_c REAL,
  restart_count INTEGER,
  FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tracks_run_time
  ON vehicle_tracks(run_id, first_seen_ts, last_seen_ts);

CREATE INDEX IF NOT EXISTS idx_tracks_lookup
  ON vehicle_tracks(run_id, camera_id, vehicle_type, color, brand);

CREATE INDEX IF NOT EXISTS idx_tracks_brand_status
  ON vehicle_tracks(run_id, brand_status, best_crop_quality);

CREATE INDEX IF NOT EXISTS idx_observations_track_time
  ON vehicle_observations(track_id, ts);

CREATE INDEX IF NOT EXISTS idx_brand_attempts_track
  ON brand_attempts(track_id, status);

CREATE INDEX IF NOT EXISTS idx_perf_run_time
  ON performance_samples(run_id, ts);

CREATE INDEX IF NOT EXISTS idx_watchdog_run_time
  ON watchdog_events(run_id, ts);

-- Common final-answer helpers.

CREATE VIEW IF NOT EXISTS vehicle_answer_view AS
SELECT
  r.run_tag,
  vt.camera_id,
  vt.uuid,
  vt.event,
  vt.first_seen_ts,
  vt.last_seen_ts,
  vt.first_seen_iso,
  vt.last_seen_iso,
  vt.vehicle_type,
  vt.vehicle_conf,
  vt.color,
  vt.color_conf,
  vt.brand,
  vt.brand_conf,
  vt.brand_status,
  vt.best_crop_path,
  vt.frame_count,
  vt.observation_count,
  vt.vit_runs
FROM vehicle_tracks vt
JOIN runs r ON r.id = vt.run_id;

-- Exact required model/answer export surface.
-- Use this for CSV export:
--   SELECT Date,CCTV_ID,First_Seen,Last_Seen,Brand,Color,Type,Event FROM required_output_view;
CREATE VIEW IF NOT EXISTS required_output_view AS
SELECT
  COALESCE(substr(vt.first_seen_iso, 1, 10), date(vt.first_seen_ts, 'unixepoch', 'localtime')) AS Date,
  vt.camera_id AS CCTV_ID,
  COALESCE(vt.first_seen_iso, datetime(vt.first_seen_ts, 'unixepoch', 'localtime')) AS First_Seen,
  COALESCE(vt.last_seen_iso, datetime(vt.last_seen_ts, 'unixepoch', 'localtime')) AS Last_Seen,
  COALESCE(vt.brand, 'Unknown') AS Brand,
  COALESCE(vt.color, 'Unknown') AS Color,
  COALESCE(vt.vehicle_type, 'Unknown') AS Type,
  COALESCE(vt.event, 'pass') AS Event
FROM vehicle_tracks vt;

CREATE VIEW IF NOT EXISTS run_health_summary AS
SELECT
  r.run_tag,
  COUNT(ps.id) AS samples,
  ROUND(AVG(ps.avg_fps), 2) AS avg_fps,
  ROUND(MIN(ps.avg_fps), 2) AS min_fps,
  ROUND(MAX(ps.brand_queue_size), 2) AS max_brand_queue,
  ROUND(MAX(ps.ram_used_mb), 2) AS max_ram_used_mb,
  ROUND(MAX(ps.swap_used_mb), 2) AS max_swap_used_mb,
  ROUND(MAX(ps.temp_c), 2) AS max_temp_c,
  SUM(COALESCE(ps.vit_jobs_dropped, 0)) AS vit_jobs_dropped
FROM runs r
LEFT JOIN performance_samples ps ON ps.run_id = r.id
GROUP BY r.id;

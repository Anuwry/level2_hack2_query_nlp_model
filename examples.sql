-- Complete example seed data for schema.sql.
-- Usage:
--   sqlite3 sample_vehicle.db < schema.sql
--   sqlite3 sample_vehicle.db < examples.sql

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

INSERT INTO runs (
  id, run_tag, started_at, ended_at, source_mode, model_name, input_size,
  detector_skip_initial, notes
) VALUES (
  1, 'ck1n_20260520_120000', '2026-05-20 12:00:00', '2026-05-20 12:15:00',
  'mock_cctv_file', 'yolov8n-vehicle+tensorrt-vit-small', 640, 2,
  'Synthetic challenge seed: 2 cameras, 18 stable tracks, sparse audit logs.'
);

INSERT INTO cameras (
  id, run_id, camera_id, source_uri, width, height, fps_hint
) VALUES
  (1, 1, 'CCTV01', 'file:///data/challenge/cctv01.mp4', 1280, 720, 25.0),
  (2, 1, 'CCTV02', 'file:///data/challenge/cctv02.mp4', 1280, 720, 25.0);

INSERT INTO vehicle_tracks (
  id, run_id, camera_id, uuid, first_seen_ts, last_seen_ts, first_seen_iso, last_seen_iso,
  vehicle_type, vehicle_conf, color, color_conf, color_votes_json,
  brand, brand_conf, brand_model, brand_status, brand_error,
  best_crop_path, best_crop_quality, best_bbox_x1, best_bbox_y1, best_bbox_x2, best_bbox_y2,
  frame_count, observation_count, vit_runs, created_at, updated_at
) VALUES
  (1, 1, 'CCTV01', 'CCTV01-TRK-001', 1779253265.0, 1779253294.0, '2026-05-20 12:01:05', '2026-05-20 12:01:34', 'car', 0.92, 'Gray', 0.86, '{"Gray":18,"Silver":3}', 'Toyota', 0.93, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-001.jpg', 0.91, 432, 214, 721, 548, 67, 3, 1, '2026-05-20 12:01:05', '2026-05-20 12:01:35'),
  (2, 1, 'CCTV01', 'CCTV01-TRK-002', 1779253330.0, 1779253362.0, '2026-05-20 12:02:10', '2026-05-20 12:02:42', 'car', 0.95, 'White', 0.91, '{"White":21,"Silver":2}', 'Toyota', 0.91, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-002.jpg', 0.94, 211, 190, 518, 526, 74, 4, 1, '2026-05-20 12:02:10', '2026-05-20 12:02:43'),
  (3, 1, 'CCTV01', 'CCTV01-TRK-003', 1779253400.0, 1779253421.0, '2026-05-20 12:03:20', '2026-05-20 12:03:41', 'motorcycle', 0.88, 'Black', 0.82, '{"Black":14,"Charcoal":4}', 'Honda', 0.89, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-003.jpg', 0.82, 606, 286, 760, 575, 51, 2, 1, '2026-05-20 12:03:20', '2026-05-20 12:03:42'),
  (4, 1, 'CCTV01', 'CCTV01-TRK-004', 1779253470.0, 1779253513.0, '2026-05-20 12:04:30', '2026-05-20 12:05:13', 'truck', 0.90, 'Silver', 0.84, '{"Silver":17,"Gray":5}', 'Isuzu', 0.87, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-004.jpg', 0.88, 118, 177, 507, 592, 89, 3, 1, '2026-05-20 12:04:30', '2026-05-20 12:05:14'),
  (5, 1, 'CCTV01', 'CCTV01-TRK-005', 1779253515.0, 1779253549.0, '2026-05-20 12:05:15', '2026-05-20 12:05:49', 'car', 0.93, 'Blue', 0.88, '{"Blue":19,"Navy Blue":2}', 'BYD', 0.90, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-005.jpg', 0.90, 515, 230, 802, 559, 71, 3, 1, '2026-05-20 12:05:15', '2026-05-20 12:05:50'),
  (6, 1, 'CCTV01', 'CCTV01-TRK-006', 1779253550.0, 1779253584.0, '2026-05-20 12:05:50', '2026-05-20 12:06:24', 'car', 0.91, 'Gray', 0.85, '{"Gray":16,"Silver":4}', 'Toyota', 0.88, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-006.jpg', 0.87, 349, 219, 642, 552, 73, 3, 1, '2026-05-20 12:05:50', '2026-05-20 12:06:25'),
  (7, 1, 'CCTV01', 'CCTV01-TRK-007', 1779253600.0, 1779253632.0, '2026-05-20 12:06:40', '2026-05-20 12:07:12', 'car', 0.89, 'Red', 0.83, '{"Red":15,"Maroon":3}', 'Mitsubishi', 0.84, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-007.jpg', 0.83, 681, 245, 941, 571, 62, 3, 1, '2026-05-20 12:06:40', '2026-05-20 12:07:13'),
  (8, 1, 'CCTV01', 'CCTV01-TRK-008', 1779253645.0, 1779253690.0, '2026-05-20 12:07:25', '2026-05-20 12:08:10', 'truck', 0.92, 'White', 0.89, '{"White":20,"Silver":2}', 'Hino', 0.86, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-008.jpg', 0.86, 95, 168, 491, 614, 96, 4, 1, '2026-05-20 12:07:25', '2026-05-20 12:08:11'),
  (9, 1, 'CCTV01', 'CCTV01-TRK-009', 1779253690.0, 1779253716.0, '2026-05-20 12:08:10', '2026-05-20 12:08:36', 'motorcycle', 0.86, 'Yellow', 0.80, '{"Yellow":12,"Gold":4}', NULL, NULL, 'vit-small-thai-vehicle-v1', 'failed', 'low crop quality after blur filter', 'logs/crops/CCTV01-TRK-009.jpg', 0.49, 742, 302, 894, 590, 44, 2, 1, '2026-05-20 12:08:10', '2026-05-20 12:08:37'),
  (10, 1, 'CCTV01', 'CCTV01-TRK-010', 1779253745.0, 1779253780.0, '2026-05-20 12:09:05', '2026-05-20 12:09:40', 'car', 0.96, 'Black', 0.90, '{"Black":22,"Charcoal":1}', 'BMW', 0.96, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-010.jpg', 0.95, 437, 202, 731, 540, 80, 4, 1, '2026-05-20 12:09:05', '2026-05-20 12:09:41'),
  (11, 1, 'CCTV01', 'CCTV01-TRK-011', 1779253785.0, 1779253818.0, '2026-05-20 12:09:45', '2026-05-20 12:10:18', 'car', 0.90, 'White', 0.87, '{"White":18,"Silver":3}', 'Honda', 0.85, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-011.jpg', 0.84, 260, 223, 552, 547, 68, 3, 1, '2026-05-20 12:09:45', '2026-05-20 12:10:19'),
  (12, 1, 'CCTV01', 'CCTV01-TRK-012', 1779253795.0, 1779253834.0, '2026-05-20 12:09:55', '2026-05-20 12:10:34', 'truck', 0.87, 'Gray', 0.81, '{"Gray":13,"Silver":5}', 'Ford', 0.82, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV01-TRK-012.jpg', 0.81, 816, 199, 1190, 602, 79, 3, 1, '2026-05-20 12:09:55', '2026-05-20 12:10:35'),
  (13, 1, 'CCTV02', 'CCTV02-TRK-001', 1779253268.0, 1779253301.0, '2026-05-20 12:01:08', '2026-05-20 12:01:41', 'car', 0.91, 'Silver', 0.85, '{"Silver":16,"Gray":4}', 'Nissan', 0.88, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV02-TRK-001.jpg', 0.87, 388, 211, 660, 545, 70, 3, 1, '2026-05-20 12:01:08', '2026-05-20 12:01:42'),
  (14, 1, 'CCTV02', 'CCTV02-TRK-002', 1779253478.0, 1779253510.0, '2026-05-20 12:04:38', '2026-05-20 12:05:10', 'bus', 0.94, 'Blue-White', 0.83, '{"Blue-White":12,"White":6}', 'Bus', 0.92, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV02-TRK-002.jpg', 0.85, 54, 142, 581, 641, 87, 3, 1, '2026-05-20 12:04:38', '2026-05-20 12:05:11'),
  (15, 1, 'CCTV02', 'CCTV02-TRK-003', 1779253635.0, 1779253668.0, '2026-05-20 12:07:15', '2026-05-20 12:07:48', 'car', 0.89, 'Green', 0.79, '{"Green":11,"Dark Green":4}', 'MG', 0.80, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV02-TRK-003.jpg', 0.78, 603, 225, 877, 553, 65, 2, 1, '2026-05-20 12:07:15', '2026-05-20 12:07:49'),
  (16, 1, 'CCTV02', 'CCTV02-TRK-004', 1779253860.0, 1779253897.0, '2026-05-20 12:11:00', '2026-05-20 12:11:37', 'car', 0.93, 'Orange', 0.84, '{"Orange":15,"Red":2}', 'Tesla', 0.94, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV02-TRK-004.jpg', 0.92, 305, 214, 600, 548, 72, 3, 1, '2026-05-20 12:11:00', '2026-05-20 12:11:38'),
  (17, 1, 'CCTV02', 'CCTV02-TRK-005', 1779253925.0, 1779253968.0, '2026-05-20 12:12:05', '2026-05-20 12:12:48', 'truck', 0.90, 'Bronze', 0.78, '{"Bronze":10,"Gold":5}', 'Chevrolet', 0.79, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV02-TRK-005.jpg', 0.77, 721, 201, 1094, 594, 82, 2, 1, '2026-05-20 12:12:05', '2026-05-20 12:12:49'),
  (18, 1, 'CCTV02', 'CCTV02-TRK-006', 1779254010.0, 1779254044.0, '2026-05-20 12:13:30', '2026-05-20 12:14:04', 'car', 0.92, 'Maroon', 0.81, '{"Maroon":13,"Red":4}', 'Mazda', 0.83, 'vit-small-thai-vehicle-v1', 'done', NULL, 'logs/crops/CCTV02-TRK-006.jpg', 0.80, 166, 232, 449, 557, 69, 2, 1, '2026-05-20 12:13:30', '2026-05-20 12:14:05');

INSERT INTO vehicle_observations (
  id, track_id, ts, ts_iso, frame_index, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
  yolo_conf, color, crop_path, crop_quality, created_at
) VALUES
  (1, 1, 1779253265.0, '2026-05-20 12:01:05', 1625, 432, 214, 721, 548, 0.92, 'Gray', 'logs/crops/CCTV01-TRK-001.jpg', 0.91, '2026-05-20 12:01:05'),
  (2, 2, 1779253330.0, '2026-05-20 12:02:10', 3250, 211, 190, 518, 526, 0.95, 'White', 'logs/crops/CCTV01-TRK-002.jpg', 0.94, '2026-05-20 12:02:10'),
  (3, 5, 1779253515.0, '2026-05-20 12:05:15', 7875, 515, 230, 802, 559, 0.93, 'Blue', 'logs/crops/CCTV01-TRK-005.jpg', 0.90, '2026-05-20 12:05:15'),
  (4, 9, 1779253690.0, '2026-05-20 12:08:10', 12250, 742, 302, 894, 590, 0.86, 'Yellow', 'logs/crops/CCTV01-TRK-009.jpg', 0.49, '2026-05-20 12:08:10'),
  (5, 10, 1779253745.0, '2026-05-20 12:09:05', 13625, 437, 202, 731, 540, 0.96, 'Black', 'logs/crops/CCTV01-TRK-010.jpg', 0.95, '2026-05-20 12:09:05'),
  (6, 14, 1779253478.0, '2026-05-20 12:04:38', 3695, 54, 142, 581, 641, 0.94, 'Blue-White', 'logs/crops/CCTV02-TRK-002.jpg', 0.85, '2026-05-20 12:04:38'),
  (7, 16, 1779253860.0, '2026-05-20 12:11:00', 16500, 305, 214, 600, 548, 0.93, 'Orange', 'logs/crops/CCTV02-TRK-004.jpg', 0.92, '2026-05-20 12:11:00'),
  (8, 18, 1779254010.0, '2026-05-20 12:13:30', 20250, 166, 232, 449, 557, 0.92, 'Maroon', 'logs/crops/CCTV02-TRK-006.jpg', 0.80, '2026-05-20 12:13:30');

INSERT INTO brand_attempts (
  id, track_id, queued_at, started_at, finished_at, crop_path, crop_quality,
  brand, brand_conf, topk_json, status, error, latency_ms
) VALUES
  (1, 1, '2026-05-20 12:01:06', '2026-05-20 12:01:06', '2026-05-20 12:01:06.185', 'logs/crops/CCTV01-TRK-001.jpg', 0.91, 'Toyota', 0.93, '{"Toyota":0.93,"Honda":0.03,"Nissan":0.02}', 'done', NULL, 185.0),
  (2, 2, '2026-05-20 12:02:11', '2026-05-20 12:02:11', '2026-05-20 12:02:11.192', 'logs/crops/CCTV01-TRK-002.jpg', 0.94, 'Toyota', 0.91, '{"Toyota":0.91,"Honda":0.04,"BYD":0.02}', 'done', NULL, 192.0),
  (3, 3, '2026-05-20 12:03:21', '2026-05-20 12:03:21', '2026-05-20 12:03:21.176', 'logs/crops/CCTV01-TRK-003.jpg', 0.82, 'Honda', 0.89, '{"Honda":0.89,"Yamaha":0.04,"Suzuki":0.03}', 'done', NULL, 176.0),
  (4, 4, '2026-05-20 12:04:31', '2026-05-20 12:04:31', '2026-05-20 12:04:31.210', 'logs/crops/CCTV01-TRK-004.jpg', 0.88, 'Isuzu', 0.87, '{"Isuzu":0.87,"Hino":0.05,"Toyota":0.03}', 'done', NULL, 210.0),
  (5, 5, '2026-05-20 12:05:16', '2026-05-20 12:05:16', '2026-05-20 12:05:16.205', 'logs/crops/CCTV01-TRK-005.jpg', 0.90, 'BYD', 0.90, '{"BYD":0.90,"Tesla":0.04,"Neta":0.03}', 'done', NULL, 205.0),
  (6, 6, '2026-05-20 12:05:51', '2026-05-20 12:05:51', '2026-05-20 12:05:51.188', 'logs/crops/CCTV01-TRK-006.jpg', 0.87, 'Toyota', 0.88, '{"Toyota":0.88,"Nissan":0.05,"Mazda":0.02}', 'done', NULL, 188.0),
  (7, 7, '2026-05-20 12:06:41', '2026-05-20 12:06:41', '2026-05-20 12:06:41.224', 'logs/crops/CCTV01-TRK-007.jpg', 0.83, 'Mitsubishi', 0.84, '{"Mitsubishi":0.84,"Mazda":0.06,"Toyota":0.03}', 'done', NULL, 224.0),
  (8, 8, '2026-05-20 12:07:26', '2026-05-20 12:07:26', '2026-05-20 12:07:26.238', 'logs/crops/CCTV01-TRK-008.jpg', 0.86, 'Hino', 0.86, '{"Hino":0.86,"Isuzu":0.07,"Truck":0.03}', 'done', NULL, 238.0),
  (9, 9, '2026-05-20 12:08:11', '2026-05-20 12:08:11', '2026-05-20 12:08:11.229', 'logs/crops/CCTV01-TRK-009.jpg', 0.49, NULL, NULL, '{"Honda":0.22,"Suzuki":0.18,"Yamaha":0.14}', 'failed', 'low crop quality after blur filter', 229.0),
  (10, 10, '2026-05-20 12:09:06', '2026-05-20 12:09:06', '2026-05-20 12:09:06.181', 'logs/crops/CCTV01-TRK-010.jpg', 0.95, 'BMW', 0.96, '{"BMW":0.96,"Mercedes-Benz":0.02,"Mini":0.01}', 'done', NULL, 181.0),
  (11, 11, '2026-05-20 12:09:46', '2026-05-20 12:09:46', '2026-05-20 12:09:46.190', 'logs/crops/CCTV01-TRK-011.jpg', 0.84, 'Honda', 0.85, '{"Honda":0.85,"Toyota":0.06,"Nissan":0.04}', 'done', NULL, 190.0),
  (12, 12, '2026-05-20 12:09:56', '2026-05-20 12:09:56', '2026-05-20 12:09:56.212', 'logs/crops/CCTV01-TRK-012.jpg', 0.81, 'Ford', 0.82, '{"Ford":0.82,"Chevrolet":0.08,"Toyota":0.03}', 'done', NULL, 212.0);

INSERT INTO performance_samples (
  id, run_id, ts, ts_iso, avg_fps, active_cameras, detector_skip,
  capture_queue_size, detection_queue_size, brand_queue_size, brand_queue_dropped, db_queue_size,
  frame_loop_ms_ema, yolo_ms_ema, tracking_ms_ema, hsv_ms_ema, vit_ms_ema, db_write_ms_ema,
  active_tracks, completed_tracks, vit_jobs_done, vit_jobs_skipped, vit_jobs_dropped,
  ram_used_mb, swap_used_mb, cpu_pct, gpu_pct, temp_c, power_w, note
) VALUES
  (1, 1, 1779253260.0, '2026-05-20 12:01:00', 14.2, 2, 2, 1, 0, 0, 0, 0, 69.8, 24.1, 5.8, 3.9, 0.0, 1.3, 2, 0, 0, 0, 0, 1378.0, 64.0, 62.0, 42.0, 65.1, 8.4, 'warmup stable'),
  (2, 1, 1779253380.0, '2026-05-20 12:03:00', 13.8, 2, 2, 1, 1, 1, 0, 0, 72.4, 25.0, 6.0, 4.1, 184.0, 1.5, 3, 2, 2, 0, 0, 1412.0, 70.0, 65.0, 45.0, 66.8, 8.7, 'normal'),
  (3, 1, 1779253500.0, '2026-05-20 12:05:00', 13.5, 2, 2, 2, 1, 1, 0, 1, 74.1, 26.2, 6.3, 4.5, 199.0, 1.8, 4, 4, 4, 0, 0, 1460.0, 82.0, 69.0, 48.0, 67.9, 9.1, 'brand queue light'),
  (4, 1, 1779253620.0, '2026-05-20 12:07:00', 12.9, 2, 3, 2, 2, 2, 0, 1, 77.5, 28.4, 6.8, 4.8, 212.0, 2.0, 5, 7, 7, 1, 0, 1518.0, 96.0, 74.0, 53.0, 69.8, 9.6, 'thermal detector skip raised'),
  (5, 1, 1779253740.0, '2026-05-20 12:09:00', 13.1, 2, 3, 1, 1, 2, 1, 1, 76.2, 27.8, 6.6, 4.7, 219.0, 1.9, 5, 10, 10, 1, 1, 1504.0, 104.0, 72.0, 50.0, 69.2, 9.4, 'one low-quality ViT job dropped'),
  (6, 1, 1779253860.0, '2026-05-20 12:11:00', 13.6, 2, 2, 1, 1, 1, 1, 0, 73.5, 25.7, 6.2, 4.4, 195.0, 1.6, 3, 13, 13, 1, 0, 1476.0, 98.0, 67.0, 47.0, 68.0, 9.0, 'recovered'),
  (7, 1, 1779253980.0, '2026-05-20 12:13:00', 14.0, 2, 2, 0, 0, 0, 1, 0, 70.6, 24.3, 5.9, 4.0, 186.0, 1.4, 2, 16, 16, 1, 0, 1438.0, 90.0, 64.0, 43.0, 66.4, 8.6, 'normal'),
  (8, 1, 1779254100.0, '2026-05-20 12:15:00', 13.7, 2, 2, 0, 0, 0, 1, 0, 71.9, 24.8, 6.1, 4.2, 188.0, 1.5, 0, 18, 17, 1, 0, 1420.0, 88.0, 63.0, 41.0, 65.9, 8.5, 'run finished');

INSERT INTO watchdog_events (
  id, run_id, ts, ts_iso, event_type, command, reason, fps, q_depth,
  ram_used_pct, temp_c, restart_count
) VALUES
  (1, 1, 1779253621.0, '2026-05-20 12:07:01', 'throttle_detector', 'set_detector_skip=3', 'temp above 69C and FPS below target', 12.9, 2, 58.0, 69.8, 0),
  (2, 1, 1779253741.0, '2026-05-20 12:09:01', 'drop_brand_job', 'drop_low_quality_crop', 'brand queue cap reached and crop quality below 0.50', 13.1, 2, 57.5, 69.2, 0);

COMMIT;

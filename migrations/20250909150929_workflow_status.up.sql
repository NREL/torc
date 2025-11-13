CREATE TABLE workflow_status (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  run_id INTGEGER NOT NULL DEFAULT 1,
  has_detected_need_to_run_completion_script INTEGER NOT NULL DEFAULT 0,
  is_canceled INTEGER NOT NULL DEFAULT 0,
  is_archived INTEGER NOT NULL DEFAULT 0
);

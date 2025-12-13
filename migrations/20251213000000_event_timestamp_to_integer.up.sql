-- Migration: Convert event.timestamp from TEXT (ISO 8601) to INTEGER (milliseconds since epoch)
-- This improves query efficiency for timestamp filtering and ensures consistency with the API.

-- SQLite doesn't support ALTER COLUMN, so we recreate the table

-- Step 1: Create new table with INTEGER timestamp
CREATE TABLE event_new (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  timestamp INTEGER NOT NULL,
  data TEXT NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- Step 2: Copy data, converting ISO 8601 timestamps to milliseconds since epoch
-- SQLite's strftime with '%s' gives seconds since epoch, multiply by 1000 for milliseconds
-- We also add milliseconds from the fractional part if present
INSERT INTO event_new (id, workflow_id, timestamp, data)
SELECT
  id,
  workflow_id,
  CAST(strftime('%s', substr(timestamp, 1, 19)) AS INTEGER) * 1000 +
  CASE
    WHEN length(timestamp) > 20 AND substr(timestamp, 20, 1) = '.'
    THEN CAST(substr(timestamp, 21, 3) AS INTEGER)
    ELSE 0
  END,
  data
FROM event;

-- Step 3: Drop old table
DROP TABLE event;

-- Step 4: Rename new table
ALTER TABLE event_new RENAME TO event;

-- Step 5: Create index on timestamp for efficient filtering
CREATE INDEX idx_event_workflow_timestamp ON event(workflow_id, timestamp);

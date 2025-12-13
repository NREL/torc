-- Revert: Convert event.timestamp from INTEGER (milliseconds) back to TEXT (ISO 8601)

-- Step 1: Create table with TEXT timestamp
CREATE TABLE event_new (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  workflow_id INTEGER NOT NULL,
  timestamp TEXT NOT NULL,
  data TEXT NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflow(id) ON DELETE CASCADE
);

-- Step 2: Copy data, converting milliseconds to ISO 8601 format
-- datetime with 'unixepoch' modifier converts seconds to datetime
INSERT INTO event_new (id, workflow_id, timestamp, data)
SELECT
  id,
  workflow_id,
  strftime('%Y-%m-%dT%H:%M:%S', timestamp / 1000, 'unixepoch') ||
  '.' || printf('%03d', timestamp % 1000) || 'Z',
  data
FROM event;

-- Step 3: Drop old table and index
DROP TABLE event;

-- Step 4: Rename new table
ALTER TABLE event_new RENAME TO event;

-- Enum for the statuses
CREATE TYPE notes_status AS ENUM ('Open', 'Completed', 'Deferred');

-- Create the notes table
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action_date TIMESTAMPTZ,
    status notes_status NOT NULL DEFAULT 'Open'
);

-- Indexes for common query patterns
CREATE INDEX idx_notes_category ON notes (category);
CREATE INDEX idx_notes_status ON notes (status);
CREATE INDEX idx_notes_created_at ON notes (created_at);
CREATE INDEX idx_notes_action_date ON notes (action_date);

-- A sample note
INSERT INTO notes (content, category)
VALUES ('Project Plan', 'Work');


-- Run this once in the Supabase SQL editor to set up the waitlist table.

CREATE TABLE IF NOT EXISTS waitlist (
  id         BIGSERIAL    PRIMARY KEY,
  email      TEXT         NOT NULL,
  source     TEXT         NOT NULL DEFAULT 'hero',
  created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  CONSTRAINT waitlist_email_unique UNIQUE (email)
);

-- Allow the Edge Function (service role) to insert rows.
-- No public SELECT — the table is write-only from the outside.
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service role full access"
  ON waitlist
  FOR ALL
  USING (auth.role() = 'service_role');

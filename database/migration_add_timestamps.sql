-- Migration: Add created_at and updated_at columns to incidents table
-- Run this if the columns don't exist

-- Add created_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'incidents' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE incidents ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Add updated_at column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'incidents' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE incidents ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Update existing rows to have timestamps
UPDATE incidents 
SET created_at = detected_at 
WHERE created_at IS NULL;

UPDATE incidents 
SET updated_at = detected_at 
WHERE updated_at IS NULL;


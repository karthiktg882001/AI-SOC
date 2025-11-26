-- Migration: Add threat_metadata column to threat_intelligence table
-- This column stores additional metadata about threats in JSON format

-- Check if column exists, if not add it
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'threat_intelligence' 
        AND column_name = 'threat_metadata'
    ) THEN
        -- Add the threat_metadata column
        ALTER TABLE threat_intelligence 
        ADD COLUMN threat_metadata JSONB;
        
        -- Migrate data from additional_info to threat_metadata if additional_info exists
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name = 'threat_intelligence' 
            AND column_name = 'additional_info'
        ) THEN
            UPDATE threat_intelligence 
            SET threat_metadata = additional_info 
            WHERE additional_info IS NOT NULL;
        END IF;
        
        RAISE NOTICE 'Column threat_metadata added successfully';
    ELSE
        RAISE NOTICE 'Column threat_metadata already exists';
    END IF;
END $$;


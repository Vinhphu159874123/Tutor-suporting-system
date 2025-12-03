-- Migration: Add file_data column to store files in database
-- Date: 2025-12-03
-- Description: Add BYTEA column to store file binary data directly in PostgreSQL

-- Add file_data column
ALTER TABLE tutor_system.sessionmaterial 
ADD COLUMN IF NOT EXISTS file_data BYTEA;

-- Make file_url nullable (now optional if file_data exists)
ALTER TABLE tutor_system.sessionmaterial 
ALTER COLUMN file_url DROP NOT NULL;

-- Add comment
COMMENT ON COLUMN tutor_system.sessionmaterial.file_data IS 'Binary file data stored directly in database (BYTEA)';
COMMENT ON COLUMN tutor_system.sessionmaterial.file_url IS 'External URL or legacy disk path (optional if file_data exists)';

-- Check migration
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_schema = 'tutor_system'
        AND table_name = 'sessionmaterial'
        AND column_name = 'file_data'
    ) THEN
        RAISE NOTICE '✅ Column file_data added successfully';
    ELSE
        RAISE EXCEPTION '❌ Failed to add file_data column';
    END IF;
END $$;

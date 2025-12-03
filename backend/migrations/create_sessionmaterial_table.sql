-- Migration: Create sessionmaterial table for file uploads
-- Date: 2025-12-03
-- Description: Create table to store session materials metadata

-- Create sessionmaterial table if it doesn't exist
CREATE TABLE IF NOT EXISTS tutor_system.sessionmaterial (
    material_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES tutor_system.session(session_id) ON DELETE CASCADE,
    uploaded_by INTEGER NOT NULL REFERENCES tutor_system."User"(user_id) ON DELETE CASCADE,
    file_name VARCHAR NOT NULL,
    file_url TEXT NOT NULL,
    file_type VARCHAR,
    file_size BIGINT,
    description TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sessionmaterial_session_id ON tutor_system.sessionmaterial(session_id);
CREATE INDEX IF NOT EXISTS idx_sessionmaterial_uploaded_by ON tutor_system.sessionmaterial(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_sessionmaterial_uploaded_at ON tutor_system.sessionmaterial(uploaded_at);

-- Add comments
COMMENT ON TABLE tutor_system.sessionmaterial IS 'Stores learning materials uploaded for sessions';
COMMENT ON COLUMN tutor_system.sessionmaterial.material_id IS 'Primary key';
COMMENT ON COLUMN tutor_system.sessionmaterial.session_id IS 'Reference to session';
COMMENT ON COLUMN tutor_system.sessionmaterial.uploaded_by IS 'User who uploaded the file';
COMMENT ON COLUMN tutor_system.sessionmaterial.file_name IS 'Original filename';
COMMENT ON COLUMN tutor_system.sessionmaterial.file_url IS 'Path to stored file';
COMMENT ON COLUMN tutor_system.sessionmaterial.file_type IS 'MIME type of file';
COMMENT ON COLUMN tutor_system.sessionmaterial.file_size IS 'File size in bytes';
COMMENT ON COLUMN tutor_system.sessionmaterial.description IS 'Optional description';

-- Check if table was created successfully
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'tutor_system' 
        AND table_name = 'sessionmaterial'
    ) THEN
        RAISE NOTICE 'Table sessionmaterial created successfully';
    ELSE
        RAISE EXCEPTION 'Failed to create table sessionmaterial';
    END IF;
END $$;

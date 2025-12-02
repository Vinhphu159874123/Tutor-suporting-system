-- Add materials JSONB column to session table for storing simple material names
ALTER TABLE tutor_system.session 
ADD COLUMN IF NOT EXISTS materials JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN tutor_system.session.materials IS 'List of material file names (JSONB array)';

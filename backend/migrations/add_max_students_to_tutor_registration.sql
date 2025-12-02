-- Add max_students column to tutorregistration table
ALTER TABLE tutor_system.tutorregistration 
ADD COLUMN IF NOT EXISTS max_students INTEGER DEFAULT 25 CHECK (max_students >= 1 AND max_students <= 35);

COMMENT ON COLUMN tutor_system.tutorregistration.max_students IS 'Maximum number of students allowed per session (1-35, default 25)';

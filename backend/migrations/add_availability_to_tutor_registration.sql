-- Add availability JSONB column to TutorRegistration table
-- Migration: add_availability_to_tutor_registration

ALTER TABLE tutor_system.tutorregistration 
ADD COLUMN IF NOT EXISTS availability JSONB;

-- Add comment
COMMENT ON COLUMN tutor_system.tutorregistration.availability IS 'Lịch rảnh theo tuần của tutor cho môn này (JSONB format: {monday: ["07:00-09:00"], tuesday: ["13:00-15:00"], ...})';

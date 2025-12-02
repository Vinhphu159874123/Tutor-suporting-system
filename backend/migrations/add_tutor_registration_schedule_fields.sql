-- Add course schedule fields to TutorRegistration table
-- Migration: add_tutor_registration_schedule_fields

ALTER TABLE tutor_system.tutorregistration 
ADD COLUMN IF NOT EXISTS total_sessions INTEGER DEFAULT 10 NOT NULL,
ADD COLUMN IF NOT EXISTS start_date DATE,
ADD COLUMN IF NOT EXISTS end_date DATE;

-- Add comment
COMMENT ON COLUMN tutor_system.tutorregistration.total_sessions IS 'Số buổi học trong khóa (mặc định 10 buổi)';
COMMENT ON COLUMN tutor_system.tutorregistration.start_date IS 'Ngày bắt đầu dạy';
COMMENT ON COLUMN tutor_system.tutorregistration.end_date IS 'Ngày kết thúc dự kiến';

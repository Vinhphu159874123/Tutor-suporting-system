-- Migration: Add selected_schedule_id to TutorRegistration
-- Purpose: Store which schedule coordinator selected when approving registration
-- Created: 2025-12-03

ALTER TABLE tutor_system.tutorregistration
ADD COLUMN IF NOT EXISTS selected_schedule_id INTEGER;

ALTER TABLE tutor_system.tutorregistration
ADD CONSTRAINT fk_tutorregistration_schedule
    FOREIGN KEY (selected_schedule_id)
    REFERENCES tutor_system.sessionschedule(schedule_id)
    ON DELETE SET NULL;

COMMENT ON COLUMN tutor_system.tutorregistration.selected_schedule_id IS 'Schedule selected by coordinator during approval';

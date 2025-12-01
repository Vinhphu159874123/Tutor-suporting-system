-- Performance optimization indexes
-- Created: 2025-12-01
-- Purpose: Add indexes for frequently queried columns to improve response time

-- Index for tutorregistration queries
CREATE INDEX IF NOT EXISTS idx_tutor_registration_tutor_status 
ON tutor_system.tutorregistration(tutor_id, status);

CREATE INDEX IF NOT EXISTS idx_tutor_registration_subject 
ON tutor_system.tutorregistration(subject_id);

-- Index for User lookups (User table uses capital U)
CREATE INDEX IF NOT EXISTS idx_user_user_id 
ON tutor_system."User"(user_id);

-- Index for subject lookups
CREATE INDEX IF NOT EXISTS idx_subject_subject_id 
ON tutor_system.subject(subject_id);

-- Index for tutor queries
CREATE INDEX IF NOT EXISTS idx_tutor_rating 
ON tutor_system.tutor(rating DESC);

CREATE INDEX IF NOT EXISTS idx_tutor_user_id 
ON tutor_system.tutor(user_id);

-- Index for session queries (for progress tracking)
CREATE INDEX IF NOT EXISTS idx_session_start_time 
ON tutor_system.session(start_time DESC);

CREATE INDEX IF NOT EXISTS idx_session_status 
ON tutor_system.session(status);

-- Index for progresstracking queries
CREATE INDEX IF NOT EXISTS idx_progress_tracking_student 
ON tutor_system.progresstracking(student_id);

CREATE INDEX IF NOT EXISTS idx_progress_tracking_session 
ON tutor_system.progresstracking(session_id);

CREATE INDEX IF NOT EXISTS idx_progress_tracking_subject 
ON tutor_system.progresstracking(subject_id);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_progress_tracking_student_subject 
ON tutor_system.progresstracking(student_id, subject_id);

-- Index for notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_read 
ON tutor_system.notifications(user_id, is_read);

CREATE INDEX IF NOT EXISTS idx_notifications_created_at 
ON tutor_system.notifications(created_at DESC);

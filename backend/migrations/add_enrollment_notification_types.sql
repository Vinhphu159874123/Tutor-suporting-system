-- Add notification types for student enrollment and removal
-- Run this migration to support enrollment notifications

-- Drop the existing check constraint
ALTER TABLE tutor_system.notifications 
DROP CONSTRAINT IF EXISTS notifications_type_check;

-- Recreate with enrollment types
ALTER TABLE tutor_system.notifications
ADD CONSTRAINT notifications_type_check 
CHECK (type::text = ANY (ARRAY[
    'session_created'::character varying,
    'session_updated'::character varying,
    'session_cancelled'::character varying,
    'session_booked'::character varying,
    'session_confirmed'::character varying,
    'session_rejected'::character varying,
    'registration_approved'::character varying,
    'registration_rejected'::character varying,
    'feedback_received'::character varying,
    'material_uploaded'::character varying,
    'forum_reply'::character varying,
    'group_invite'::character varying,
    'achievement_earned'::character varying,
    'system_announcement'::character varying,
    'subject_registration'::character varying,
    'subject_registration_submitted'::character varying,
    'student_enrolled'::character varying,
    'removed_from_course'::character varying
]::text[]));

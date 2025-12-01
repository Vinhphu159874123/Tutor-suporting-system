-- Add new notification types for subject registration and session booking
-- Run this migration to add new notification types

-- Drop the existing check constraint
ALTER TABLE tutor_system.notifications 
DROP CONSTRAINT IF EXISTS notifications_type_check;

-- Recreate with new types
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
    'subject_registration_submitted'::character varying
]::text[]));

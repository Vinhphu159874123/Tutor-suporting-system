-- Migration: Add SessionParticipant table for many students per session
-- Date: 2025-11-18
-- Description: Allow 1 tutor to have multiple students in a session

-- Create SessionParticipant table
CREATE TABLE IF NOT EXISTS tutor_system."SessionParticipant" (
    participant_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES tutor_system."session"(session_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES tutor_system."User"(user_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('tutor', 'student')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'pending', 'cancelled')),
    notes TEXT,
    
    -- Constraints
    UNIQUE(session_id, user_id),
    CONSTRAINT valid_role CHECK (role IN ('tutor', 'student'))
);

-- Create indexes for better query performance
CREATE INDEX idx_session_participant_session ON tutor_system."SessionParticipant"(session_id);
CREATE INDEX idx_session_participant_user ON tutor_system."SessionParticipant"(user_id);
CREATE INDEX idx_session_participant_role ON tutor_system."SessionParticipant"(role);
CREATE INDEX idx_session_participant_session_role ON tutor_system."SessionParticipant"(session_id, role);

-- Migrate existing data from session.student_id to SessionParticipant
-- Add tutor as participant
INSERT INTO tutor_system."SessionParticipant" (session_id, user_id, role, joined_at, status)
SELECT 
    s.session_id,
    t.user_id,
    'tutor',
    s.created_at,
    'confirmed'
FROM tutor_system."session" s
JOIN tutor_system."tutor" t ON s.tutor_id = t.tutor_id
WHERE NOT EXISTS (
    SELECT 1 FROM tutor_system."SessionParticipant" sp 
    WHERE sp.session_id = s.session_id AND sp.user_id = t.user_id AND sp.role = 'tutor'
);

-- Add student as participant (only if student_id is not null)
INSERT INTO tutor_system."SessionParticipant" (session_id, user_id, role, joined_at, status)
SELECT 
    s.session_id,
    st.user_id,
    'student',
    s.created_at,
    'confirmed'
FROM tutor_system."session" s
JOIN tutor_system."student" st ON s.student_id = st.student_id
WHERE s.student_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM tutor_system."SessionParticipant" sp 
    WHERE sp.session_id = s.session_id AND sp.user_id = st.user_id AND sp.role = 'student'
);

-- Optional: Add comment to session table noting deprecation of student_id
COMMENT ON COLUMN tutor_system."session".student_id IS 'DEPRECATED: Use SessionParticipant table instead. Kept for backward compatibility.';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'SessionParticipant table created successfully';
    RAISE NOTICE 'Existing sessions migrated to new structure';
END $$;

-- ============================================================================
-- DATABASE MIGRATION SCRIPT - Tutor Supporting System
-- Generated on: November 5, 2025
--
-- This script creates all missing database tables and indexes
-- for the Tutor Supporting System backend implementation.
--
-- EXECUTION ORDER:
-- 1. Run this script on your PostgreSQL database
-- 2. Update backend/app/models/database.py with new models
-- 3. Update dependencies to include new services/repositories
-- ============================================================================

-- Enable UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SESSION MATERIALS TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS session_materials (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for session_materials
CREATE INDEX IF NOT EXISTS idx_session_materials_session_id ON session_materials(session_id);
CREATE INDEX IF NOT EXISTS idx_session_materials_uploaded_by ON session_materials(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_session_materials_created_at ON session_materials(created_at);

-- ============================================================================
-- TUTOR AVAILABILITY TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS tutor_availability (
    id SERIAL PRIMARY KEY,
    tutor_id INTEGER NOT NULL REFERENCES tutors(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_recurring BOOLEAN DEFAULT TRUE,
    specific_date DATE NULL, -- For one-time availability
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint to ensure end_time is after start_time
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    
    -- Unique constraint to prevent overlapping availability
    CONSTRAINT unique_availability UNIQUE (tutor_id, day_of_week, start_time, specific_date)
);

-- Indexes for tutor_availability
CREATE INDEX IF NOT EXISTS idx_tutor_availability_tutor_id ON tutor_availability(tutor_id);
CREATE INDEX IF NOT EXISTS idx_tutor_availability_day_of_week ON tutor_availability(day_of_week);
CREATE INDEX IF NOT EXISTS idx_tutor_availability_specific_date ON tutor_availability(specific_date);

-- ============================================================================
-- LEARNING PROGRESS TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS progress_tracking (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    topics_covered TEXT[] DEFAULT '{}', -- Array of topics covered
    understanding_level INTEGER NOT NULL CHECK (understanding_level >= 1 AND understanding_level <= 5),
    notes TEXT,
    tutor_feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint: one progress entry per session
    CONSTRAINT unique_session_progress UNIQUE (session_id)
);

-- Indexes for progress_tracking
CREATE INDEX IF NOT EXISTS idx_progress_tracking_student_id ON progress_tracking(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_subject_id ON progress_tracking(subject_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_session_id ON progress_tracking(session_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_created_at ON progress_tracking(created_at);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_understanding_level ON progress_tracking(understanding_level);

CREATE TABLE IF NOT EXISTS learning_achievements (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) NOT NULL, -- 'completed_subject', 'milestone', 'improvement'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}', -- Additional achievement data
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Prevent duplicate achievements of same type
    CONSTRAINT unique_student_achievement UNIQUE (student_id, achievement_type, title)
);

-- Indexes for learning_achievements
CREATE INDEX IF NOT EXISTS idx_learning_achievements_student_id ON learning_achievements(student_id);
CREATE INDEX IF NOT EXISTS idx_learning_achievements_type ON learning_achievements(achievement_type);
CREATE INDEX IF NOT EXISTS idx_learning_achievements_earned_at ON learning_achievements(earned_at);

-- ============================================================================
-- STUDY GROUPS TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS study_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    creator_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    max_members INTEGER DEFAULT 10 CHECK (max_members >= 2 AND max_members <= 50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for study_groups
CREATE INDEX IF NOT EXISTS idx_study_groups_subject_id ON study_groups(subject_id);
CREATE INDEX IF NOT EXISTS idx_study_groups_creator_id ON study_groups(creator_id);
CREATE INDEX IF NOT EXISTS idx_study_groups_is_active ON study_groups(is_active);
CREATE INDEX IF NOT EXISTS idx_study_groups_created_at ON study_groups(created_at);

CREATE TABLE IF NOT EXISTS study_group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES study_groups(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('admin', 'moderator', 'member')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint: user can only be in group once
    CONSTRAINT unique_group_membership UNIQUE (group_id, user_id)
);

-- Indexes for study_group_members
CREATE INDEX IF NOT EXISTS idx_study_group_members_group_id ON study_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_study_group_members_user_id ON study_group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_study_group_members_role ON study_group_members(role);

-- ============================================================================
-- NOTE: LIBRARY INTEGRATION REMOVED
-- Originally planned library integration tables have been removed
-- as this feature will not be implemented in the current version
-- ============================================================================

-- ============================================================================
-- ADDITIONAL INDEXES FOR EXISTING TABLES (Performance Optimization)
-- ============================================================================

-- Sessions table additional indexes
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status) WHERE status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sessions_scheduled_at ON sessions(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_sessions_tutor_student ON sessions(tutor_id, student_id);

-- Users table additional indexes  
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Tutors table additional indexes
-- Note: Only create indexes for columns that actually exist in your tutors table
-- CREATE INDEX IF NOT EXISTS idx_tutors_subjects ON tutors USING gin(subjects) WHERE subjects IS NOT NULL;
-- CREATE INDEX IF NOT EXISTS idx_tutors_rating ON tutors(average_rating) WHERE average_rating IS NOT NULL;

-- Students table additional indexes
-- Note: Only create indexes for columns that actually exist in your students table
-- CREATE INDEX IF NOT EXISTS idx_students_year ON students(year) WHERE year IS NOT NULL;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for session statistics
CREATE OR REPLACE VIEW session_statistics AS
SELECT 
    s.id,
    s.tutor_id,
    s.student_id,
    s.subject_id,
    s.status,
    s.scheduled_at,
    COUNT(sm.id) as materials_count,
    CASE WHEN pt.id IS NOT NULL THEN TRUE ELSE FALSE END as has_progress
FROM sessions s
LEFT JOIN session_materials sm ON s.id = sm.session_id
LEFT JOIN progress_tracking pt ON s.id = pt.session_id
GROUP BY s.id, pt.id;

-- View for tutor availability summary
CREATE OR REPLACE VIEW tutor_availability_summary AS
SELECT 
    t.id as tutor_id,
    t.user_id,
    u.full_name,
    COUNT(ta.id) as availability_slots,
    ARRAY_AGG(DISTINCT ta.day_of_week ORDER BY ta.day_of_week) as available_days
FROM tutors t
JOIN users u ON t.user_id = u.id
LEFT JOIN tutor_availability ta ON t.id = ta.tutor_id AND ta.is_available = true
GROUP BY t.id, t.user_id, u.full_name;

-- View for student progress summary
CREATE OR REPLACE VIEW student_progress_summary AS
SELECT 
    s.id as student_id,
    s.user_id,
    u.full_name,
    COUNT(pt.id) as total_sessions,
    AVG(pt.understanding_level) as avg_understanding,
    COUNT(la.id) as achievements_count,
    MAX(pt.created_at) as last_session_date
FROM students s
JOIN users u ON s.user_id = u.id
LEFT JOIN progress_tracking pt ON s.id = pt.student_id
LEFT JOIN learning_achievements la ON s.id = la.student_id
GROUP BY s.id, s.user_id, u.full_name;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_session_materials_updated_at 
    BEFORE UPDATE ON session_materials 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tutor_availability_updated_at 
    BEFORE UPDATE ON tutor_availability 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_progress_tracking_updated_at 
    BEFORE UPDATE ON progress_tracking 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_groups_updated_at 
    BEFORE UPDATE ON study_groups 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Library resources trigger removed as table not implemented

-- Function to automatically create admin membership when creating study group
CREATE OR REPLACE FUNCTION create_study_group_admin()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO study_group_members (group_id, user_id, role)
    VALUES (NEW.id, NEW.creator_id, 'admin');
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER create_study_group_admin_trigger 
    AFTER INSERT ON study_groups 
    FOR EACH ROW EXECUTE FUNCTION create_study_group_admin();

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- NOTE: Library sample data removed as library integration is not implemented

-- Sample achievement types
INSERT INTO learning_achievements (student_id, achievement_type, title, description) VALUES
(1, 'first_session', 'First Session Complete', 'Completed your first tutoring session'),
(1, 'understanding_improvement', 'Great Progress', 'Improved understanding level by 2 points'),
(1, 'consistency', 'Consistent Learner', 'Attended 5 sessions in a row')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- GRANT PERMISSIONS (Adjust according to your user setup)
-- ============================================================================

-- Grant permissions to application user (replace 'tutor_app_user' with your actual user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO tutor_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO tutor_app_user;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if all tables were created successfully
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'session_materials',
        'tutor_availability', 
        'progress_tracking',
        'learning_achievements',
        'study_groups',
        'study_group_members'
    )
ORDER BY tablename;

-- Check indexes
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
    AND tablename IN (
        'session_materials',
        'tutor_availability',
        'progress_tracking', 
        'learning_achievements',
        'study_groups',
        'study_group_members'
    )
ORDER BY tablename, indexname;

-- ============================================================================
-- MIGRATION COMPLETE
-- 
-- Next Steps:
-- 1. Update backend/app/models/database.py with new SQLAlchemy models
-- 2. Update backend/app/core/dependencies.py with new service dependencies
-- 3. Add new routers to backend/app/main.py
-- 4. Run alembic revision --autogenerate (if using Alembic)
-- 5. Test all new endpoints
-- ============================================================================
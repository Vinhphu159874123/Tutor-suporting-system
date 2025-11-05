-- ============================================================================
-- SUPABASE SQL MIGRATION - Tutor Supporting System
-- Generated on: November 5, 2025
-- 
-- HƯỚNG DẪN CHẠY TRÊN SUPABASE:
-- 1. Vào Supabase Dashboard → Project → SQL Editor
-- 2. Tạo New Query và paste toàn bộ script này
-- 3. Click "Run" để thực thi
-- 4. Kiểm tra Tables tab để verify các bảng đã được tạo
-- ============================================================================

-- Enable UUID extension (Supabase có sẵn, nhưng đảm bảo enable)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. SESSION MATERIALS - Quản lý tài liệu session
-- ============================================================================

CREATE TABLE IF NOT EXISTS session_materials (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL DEFAULT 0,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_by BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_session_materials_session_id ON session_materials(session_id);
CREATE INDEX IF NOT EXISTS idx_session_materials_uploaded_by ON session_materials(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_session_materials_created_at ON session_materials(created_at);

-- ============================================================================
-- 2. TUTOR AVAILABILITY - Lịch rảnh của tutor
-- ============================================================================

CREATE TABLE IF NOT EXISTS tutor_availability (
    id BIGSERIAL PRIMARY KEY,
    tutor_id BIGINT NOT NULL REFERENCES tutors(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_recurring BOOLEAN DEFAULT TRUE,
    specific_date DATE NULL, -- For one-time availability
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    CONSTRAINT unique_availability UNIQUE (tutor_id, day_of_week, start_time, specific_date)
);

-- Indexes for queries
CREATE INDEX IF NOT EXISTS idx_tutor_availability_tutor_id ON tutor_availability(tutor_id);
CREATE INDEX IF NOT EXISTS idx_tutor_availability_day_of_week ON tutor_availability(day_of_week);
CREATE INDEX IF NOT EXISTS idx_tutor_availability_specific_date ON tutor_availability(specific_date);

-- ============================================================================
-- 3. PROGRESS TRACKING - Theo dõi tiến độ học tập
-- ============================================================================

CREATE TABLE IF NOT EXISTS progress_tracking (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_id BIGINT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    subject_id BIGINT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    topics_covered TEXT[] DEFAULT '{}', -- Array of topics covered
    understanding_level INTEGER NOT NULL CHECK (understanding_level >= 1 AND understanding_level <= 5),
    notes TEXT,
    tutor_feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- One progress entry per session
    CONSTRAINT unique_session_progress UNIQUE (session_id)
);

-- Indexes for analytics
CREATE INDEX IF NOT EXISTS idx_progress_tracking_student_id ON progress_tracking(student_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_subject_id ON progress_tracking(subject_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_session_id ON progress_tracking(session_id);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_created_at ON progress_tracking(created_at);
CREATE INDEX IF NOT EXISTS idx_progress_tracking_understanding_level ON progress_tracking(understanding_level);

-- ============================================================================
-- 4. LEARNING ACHIEVEMENTS - Thành tích học tập
-- ============================================================================

CREATE TABLE IF NOT EXISTS learning_achievements (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) NOT NULL, -- 'completed_subject', 'milestone', 'improvement'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}', -- Additional achievement data
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Prevent duplicate achievements
    CONSTRAINT unique_student_achievement UNIQUE (student_id, achievement_type, title)
);

-- Indexes for achievements
CREATE INDEX IF NOT EXISTS idx_learning_achievements_student_id ON learning_achievements(student_id);
CREATE INDEX IF NOT EXISTS idx_learning_achievements_type ON learning_achievements(achievement_type);
CREATE INDEX IF NOT EXISTS idx_learning_achievements_earned_at ON learning_achievements(earned_at);

-- ============================================================================
-- 5. STUDY GROUPS - Nhóm học tập
-- ============================================================================

CREATE TABLE IF NOT EXISTS study_groups (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    subject_id BIGINT REFERENCES subjects(id) ON DELETE SET NULL,
    creator_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    max_members INTEGER DEFAULT 10 CHECK (max_members >= 2 AND max_members <= 50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for study groups
CREATE INDEX IF NOT EXISTS idx_study_groups_subject_id ON study_groups(subject_id);
CREATE INDEX IF NOT EXISTS idx_study_groups_creator_id ON study_groups(creator_id);
CREATE INDEX IF NOT EXISTS idx_study_groups_is_active ON study_groups(is_active);
CREATE INDEX IF NOT EXISTS idx_study_groups_created_at ON study_groups(created_at);

-- ============================================================================
-- 6. STUDY GROUP MEMBERS - Thành viên nhóm học
-- ============================================================================

CREATE TABLE IF NOT EXISTS study_group_members (
    id BIGSERIAL PRIMARY KEY,
    group_id BIGINT NOT NULL REFERENCES study_groups(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('admin', 'moderator', 'member')),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- User can only be in group once
    CONSTRAINT unique_group_membership UNIQUE (group_id, user_id)
);

-- Indexes for members
CREATE INDEX IF NOT EXISTS idx_study_group_members_group_id ON study_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_study_group_members_user_id ON study_group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_study_group_members_role ON study_group_members(role);

-- ============================================================================
-- 7. PERFORMANCE OPTIMIZATION - Additional indexes cho existing tables
-- ============================================================================

-- Sessions table optimization
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status) WHERE status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sessions_scheduled_at ON sessions(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_sessions_tutor_student ON sessions(tutor_id, student_id);

-- Users table optimization  
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Tutors table optimization (commented out - columns may not exist)
-- CREATE INDEX IF NOT EXISTS idx_tutors_subjects ON tutors USING gin(subjects) WHERE subjects IS NOT NULL;
-- CREATE INDEX IF NOT EXISTS idx_tutors_rating ON tutors(average_rating) WHERE average_rating IS NOT NULL;

-- Students table optimization (commented out - columns may not exist)
-- CREATE INDEX IF NOT EXISTS idx_students_year ON students(year) WHERE year IS NOT NULL;

-- ============================================================================
-- 8. USEFUL VIEWS - Views cho analytics và reporting
-- ============================================================================

-- Session statistics view
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

-- Tutor availability summary
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

-- Student progress summary
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
-- 9. TRIGGERS - Auto-update timestamps
-- ============================================================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
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

-- ============================================================================
-- 10. AUTO-CREATE STUDY GROUP ADMIN
-- ============================================================================

-- Auto-create admin membership when creating study group
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
-- 11. SAMPLE DATA (Optional - cho testing)
-- ============================================================================

-- Sample achievement types
INSERT INTO learning_achievements (student_id, achievement_type, title, description) 
SELECT 
    s.id,
    'first_session',
    'First Session Complete',
    'Completed your first tutoring session'
FROM students s 
WHERE s.id = 1
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 12. VERIFICATION QUERIES
-- ============================================================================

-- Check if tables were created successfully
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

-- Check row counts (should be 0 for new tables)
SELECT 
    'session_materials' as table_name, COUNT(*) as row_count FROM session_materials
UNION ALL
SELECT 'tutor_availability', COUNT(*) FROM tutor_availability
UNION ALL
SELECT 'progress_tracking', COUNT(*) FROM progress_tracking
UNION ALL
SELECT 'learning_achievements', COUNT(*) FROM learning_achievements
UNION ALL
SELECT 'study_groups', COUNT(*) FROM study_groups
UNION ALL
SELECT 'study_group_members', COUNT(*) FROM study_group_members;

-- ============================================================================
-- 🎉 MIGRATION COMPLETE!
-- 
-- ✅ Tables created: 6 new tables
-- ✅ Indexes created: 20+ performance indexes  
-- ✅ Views created: 3 analytics views
-- ✅ Triggers created: Auto-update timestamps + auto-admin
-- 
-- NEXT STEPS:
-- 1. ✅ Tables are ready for backend integration
-- 2. 🔄 Update your backend models (SQLAlchemy)
-- 3. 🔄 Implement the placeholder services
-- 4. 🔄 Test API endpoints
-- ============================================================================
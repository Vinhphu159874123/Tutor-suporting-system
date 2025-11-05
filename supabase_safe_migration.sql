-- ============================================================================
-- SUPABASE SAFE MIGRATION - Tutor Supporting System
-- Version: SAFE - Only new tables and essential indexes
-- Generated on: November 5, 2025
-- 
-- ⚠️  SAFE VERSION: Chỉ tạo bảng mới, không touch existing tables
-- ============================================================================

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

-- Indexes for session_materials
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
    specific_date DATE NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_time_range CHECK (end_time > start_time),
    CONSTRAINT unique_availability UNIQUE (tutor_id, day_of_week, start_time, specific_date)
);

-- Indexes for tutor_availability
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
    topics_covered TEXT[] DEFAULT '{}',
    understanding_level INTEGER NOT NULL CHECK (understanding_level >= 1 AND understanding_level <= 5),
    notes TEXT,
    tutor_feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_session_progress UNIQUE (session_id)
);

-- Indexes for progress_tracking
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
    achievement_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_student_achievement UNIQUE (student_id, achievement_type, title)
);

-- Indexes for learning_achievements
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

-- Indexes for study_groups
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
    
    CONSTRAINT unique_group_membership UNIQUE (group_id, user_id)
);

-- Indexes for study_group_members
CREATE INDEX IF NOT EXISTS idx_study_group_members_group_id ON study_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_study_group_members_user_id ON study_group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_study_group_members_role ON study_group_members(role);

-- ============================================================================
-- 7. SAFE PERFORMANCE OPTIMIZATION - Only for existing tables (commented out)
-- ============================================================================

-- ⚠️  COMMENTED OUT: Uncomment only if these columns exist in your schema

-- Sessions table optimization (only if these columns exist)
-- CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status) WHERE status IS NOT NULL;
-- CREATE INDEX IF NOT EXISTS idx_sessions_scheduled_at ON sessions(scheduled_at);
-- CREATE INDEX IF NOT EXISTS idx_sessions_tutor_student ON sessions(tutor_id, student_id);

-- Users table optimization (only if these columns exist)
-- CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);
-- CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- ============================================================================
-- 8. TRIGGERS - Auto-update timestamps
-- ============================================================================

-- Function to update updated_at column (safe)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to new tables only
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
-- 9. AUTO-CREATE STUDY GROUP ADMIN
-- ============================================================================

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
-- 10. VERIFICATION - Check what was created
-- ============================================================================

-- Check new tables
SELECT 
    'CREATED' as status,
    tablename,
    schemaname
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
-- ✅ MIGRATION COMPLETE!
-- 
-- ✅ 6 new tables created
-- ✅ All indexes created
-- ✅ Triggers added
-- ✅ No errors from non-existent columns
-- 
-- Next: Test creating a study group and uploading materials!
-- ============================================================================
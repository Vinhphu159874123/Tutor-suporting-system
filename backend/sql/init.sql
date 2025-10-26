-- HCMUT Tutor Support System Database Schema
-- Run this SQL in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if needed (be careful in production!)
DROP TABLE IF EXISTS forum_posts CASCADE;
DROP TABLE IF EXISTS forums CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS student_registrations CASCADE;
DROP TABLE IF EXISTS tutor_registrations CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS tutors CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('student', 'tutor', 'coordinator', 'department_chair', 'academic_affair', 'admin');
CREATE TYPE session_status AS ENUM ('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'rescheduled');
CREATE TYPE registration_status AS ENUM ('pending', 'approved', 'rejected');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE,
    staff_id VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255),
    role user_role NOT NULL,
    faculty VARCHAR(100),
    major VARCHAR(100),
    phone VARCHAR(20),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    sso_id VARCHAR(100) UNIQUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tutors table
CREATE TABLE tutors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    expertise_areas TEXT,
    available_hours TEXT,
    hourly_rate FLOAT,
    rating FLOAT DEFAULT 0.0,
    total_sessions INTEGER DEFAULT 0,
    is_approved BOOLEAN DEFAULT FALSE,
    approval_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    year INTEGER,
    gpa FLOAT,
    learning_goals TEXT,
    preferred_subjects TEXT,
    study_schedule TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects table
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    faculty VARCHAR(100) NOT NULL,
    credits INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    tutor_id INTEGER REFERENCES tutors(id) ON DELETE CASCADE,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    location VARCHAR(200),
    is_online BOOLEAN DEFAULT FALSE,
    meeting_url VARCHAR(500),
    status session_status DEFAULT 'scheduled',
    materials TEXT,
    notes TEXT,
    homework TEXT,
    tutor_feedback TEXT,
    student_feedback TEXT,
    tutor_rating FLOAT,
    student_rating FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tutor Registrations table
CREATE TABLE tutor_registrations (
    id SERIAL PRIMARY KEY,
    tutor_id INTEGER REFERENCES tutors(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id),
    qualification TEXT,
    experience TEXT,
    status registration_status DEFAULT 'pending',
    coordinator_id INTEGER REFERENCES users(id),
    coordinator_notes TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- Student Registrations table
CREATE TABLE student_registrations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id),
    reason TEXT,
    current_grade VARCHAR(5),
    target_grade VARCHAR(5),
    status registration_status DEFAULT 'pending',
    coordinator_id INTEGER REFERENCES users(id),
    coordinator_notes TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- Forums table
CREATE TABLE forums (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    subject_id INTEGER REFERENCES subjects(id),
    creator_id INTEGER REFERENCES users(id),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forum Posts table
CREATE TABLE forum_posts (
    id SERIAL PRIMARY KEY,
    forum_id INTEGER REFERENCES forums(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,
    parent_id INTEGER REFERENCES forum_posts(id),
    likes INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports table
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    generated_by INTEGER REFERENCES users(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data TEXT,
    filters TEXT
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_sessions_tutor ON sessions(tutor_id);
CREATE INDEX idx_sessions_student ON sessions(student_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_scheduled_at ON sessions(scheduled_at);
CREATE INDEX idx_forum_posts_forum ON forum_posts(forum_id);

-- Insert sample data
-- Admin user
INSERT INTO users (email, full_name, role, hashed_password, is_verified, staff_id) VALUES
('admin@hcmut.edu.vn', 'Admin HCMUT', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qFZkOvC.K', TRUE, 'ADMIN001');

-- Sample students
INSERT INTO users (email, full_name, role, student_id, faculty, major, is_verified) VALUES
('student1@hcmut.edu.vn', 'Nguyễn Văn An', 'student', '2011234', 'Khoa Khoa học và Kỹ thuật Máy tính', 'Khoa học Máy tính', TRUE),
('student2@hcmut.edu.vn', 'Trần Thị Bình', 'student', '2011235', 'Khoa Khoa học và Kỹ thuật Máy tính', 'Kỹ thuật Phần mềm', TRUE);

-- Sample tutors
INSERT INTO users (email, full_name, role, student_id, faculty, major, is_verified) VALUES
('tutor1@hcmut.edu.vn', 'Lê Văn Cường', 'tutor', '1911234', 'Khoa Khoa học và Kỹ thuật Máy tính', 'Khoa học Máy tính', TRUE),
('tutor2@hcmut.edu.vn', 'Phạm Thị Dung', 'tutor', '1911235', 'Khoa Cơ khí', 'Cơ khí Chế tạo', TRUE);

-- Create tutor profiles
INSERT INTO tutors (user_id, bio, expertise_areas, is_approved, rating) VALUES
((SELECT id FROM users WHERE email = 'tutor1@hcmut.edu.vn'), 
 'Sinh viên năm 4 chuyên ngành Khoa học Máy tính', 
 '["Toán cao cấp", "Lập trình C++", "Cấu trúc dữ liệu"]', 
 TRUE, 4.8),
((SELECT id FROM users WHERE email = 'tutor2@hcmut.edu.vn'), 
 'Sinh viên năm 5 chuyên ngành Cơ khí', 
 '["Vẽ kỹ thuật", "Vật liệu", "Cơ học"]', 
 TRUE, 4.5);

-- Create student profiles
INSERT INTO students (user_id, year, gpa) VALUES
((SELECT id FROM users WHERE email = 'student1@hcmut.edu.vn'), 2, 3.2),
((SELECT id FROM users WHERE email = 'student2@hcmut.edu.vn'), 2, 3.5);

-- Sample subjects
INSERT INTO subjects (code, name, faculty, credits, description) VALUES
('MT1003', 'Toán cao cấp A1', 'Khoa Toán - Tin học ứng dụng', 4, 'Môn Toán cao cấp cho sinh viên năm nhất'),
('MT1005', 'Toán cao cấp A3', 'Khoa Toán - Tin học ứng dụng', 3, 'Môn Toán cao cấp nâng cao'),
('PH1003', 'Vật lý đại cương A1', 'Khoa Vật lý Kỹ thuật', 4, 'Môn Vật lý cơ bản'),
('CO1007', 'Cấu trúc dữ liệu và Giải thuật', 'Khoa Khoa học và Kỹ thuật Máy tính', 4, 'Data structures and algorithms'),
('CO2013', 'Hệ quản trị cơ sở dữ liệu', 'Khoa Khoa học và Kỹ thuật Máy tính', 4, 'Database management systems');

-- Sample sessions
INSERT INTO sessions (tutor_id, student_id, subject_id, title, scheduled_at, duration_minutes, status, is_online) VALUES
(1, 1, 1, 'Học Toán cao cấp - Chương 1', CURRENT_TIMESTAMP + INTERVAL '1 day', 90, 'scheduled', TRUE),
(1, 2, 4, 'Cấu trúc dữ liệu - Linked List', CURRENT_TIMESTAMP + INTERVAL '2 days', 120, 'scheduled', FALSE);

-- Sample forum
INSERT INTO forums (title, description, subject_id, creator_id, is_public) VALUES
('Thảo luận Toán cao cấp A1', 'Diễn đàn thảo luận về môn Toán cao cấp A1', 1, 1, TRUE),
('Hỏi đáp Cấu trúc dữ liệu', 'Giải đáp thắc mắc về CTDL & GT', 4, 1, TRUE);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_forum_posts_updated_at BEFORE UPDATE ON forum_posts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
SELECT 'Database schema created successfully!' as message;
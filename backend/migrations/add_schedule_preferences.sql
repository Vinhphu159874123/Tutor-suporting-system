-- Migration: Add Schedule Preferences table for student scheduling requests
-- This table stores student preferences for course scheduling

-- Create enum for preference status
CREATE TYPE tutor_system.preference_status AS ENUM ('pending', 'fulfilled', 'cancelled', 'expired');

-- Create enum for session format
CREATE TYPE tutor_system.session_format AS ENUM ('online', 'offline', 'both');

-- Create table for schedule preferences
CREATE TABLE tutor_system.SchedulePreference (
    preference_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES tutor_system.Student(student_id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES tutor_system.Subject(subject_id) ON DELETE CASCADE,
    
    -- Scheduling details
    preferred_start_date DATE NOT NULL,
    total_sessions INTEGER NOT NULL CHECK (total_sessions > 0),
    session_duration INTEGER NOT NULL CHECK (session_duration > 0), -- in minutes
    session_format VARCHAR(20) NOT NULL DEFAULT 'both', -- online, offline, both
    
    -- Available time slots (stored as JSON array)
    -- Format: [{"day": "monday", "start_time": "08:00", "end_time": "10:00"}, ...]
    available_time_slots JSONB NOT NULL,
    
    -- Additional info
    notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE, -- Auto-expire old preferences
    
    -- Constraints
    CONSTRAINT valid_start_date CHECK (preferred_start_date >= CURRENT_DATE),
    CONSTRAINT valid_time_slots CHECK (jsonb_array_length(available_time_slots) > 0)
);

-- Create indexes for better query performance
CREATE INDEX idx_schedule_preference_student ON tutor_system.SchedulePreference(student_id);
CREATE INDEX idx_schedule_preference_subject ON tutor_system.SchedulePreference(subject_id);
CREATE INDEX idx_schedule_preference_status ON tutor_system.SchedulePreference(status);
CREATE INDEX idx_schedule_preference_start_date ON tutor_system.SchedulePreference(preferred_start_date);
CREATE INDEX idx_schedule_preference_format ON tutor_system.SchedulePreference(session_format);

-- Create GIN index for JSONB queries on time slots
CREATE INDEX idx_schedule_preference_time_slots ON tutor_system.SchedulePreference USING GIN (available_time_slots);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION tutor_system.update_schedule_preference_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_schedule_preference_timestamp
    BEFORE UPDATE ON tutor_system.SchedulePreference
    FOR EACH ROW
    EXECUTE FUNCTION tutor_system.update_schedule_preference_timestamp();

-- Add comments for documentation
COMMENT ON TABLE tutor_system.SchedulePreference IS 'Stores student scheduling preferences and availability for courses';
COMMENT ON COLUMN tutor_system.SchedulePreference.available_time_slots IS 'JSON array of available time slots with day, start_time, end_time';
COMMENT ON COLUMN tutor_system.SchedulePreference.session_duration IS 'Duration of each session in minutes';
COMMENT ON COLUMN tutor_system.SchedulePreference.session_format IS 'Preferred format: online, offline, or both';

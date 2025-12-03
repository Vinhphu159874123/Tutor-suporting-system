-- Migration: Add bio column to User table
-- Created: 2025-12-03

-- Add bio column to User table
ALTER TABLE tutor_system."User" ADD COLUMN IF NOT EXISTS bio TEXT;

-- Add comment
COMMENT ON COLUMN tutor_system."User".bio IS 'User bio/self-introduction text';

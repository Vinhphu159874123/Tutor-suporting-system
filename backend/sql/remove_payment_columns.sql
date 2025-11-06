-- ============================================================================
-- REMOVE PAYMENT COLUMNS FROM SESSION TABLE
-- This migration removes price and payment_status columns
-- Run this AFTER backing up your database
-- ============================================================================

-- Remove payment_status column
ALTER TABLE tutor_system.session 
DROP COLUMN IF EXISTS payment_status;

-- Remove price column
ALTER TABLE tutor_system.session 
DROP COLUMN IF EXISTS price;

-- Verification: Check session table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'tutor_system' 
  AND table_name = 'session'
ORDER BY ordinal_position;

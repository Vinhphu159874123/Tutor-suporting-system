-- Migration: Change role from VARCHAR to TEXT[] (array)
-- This allows users to have multiple roles (student, tutor, admin)

BEGIN;

-- Step 1: Add temporary column for array
ALTER TABLE "User" ADD COLUMN role_array TEXT[];

-- Step 2: Migrate existing data - convert single role to array
UPDATE "User" SET role_array = ARRAY[role]::TEXT[];

-- Step 3: Drop old role column
ALTER TABLE "User" DROP COLUMN role;

-- Step 4: Rename role_array to role
ALTER TABLE "User" RENAME COLUMN role_array TO role;

-- Step 5: Add constraint - role array cannot be empty
ALTER TABLE "User" ADD CONSTRAINT role_not_empty CHECK (array_length(role, 1) > 0);

-- Step 6: Set default value for new users (student)
ALTER TABLE "User" ALTER COLUMN role SET DEFAULT ARRAY['student']::TEXT[];

COMMIT;

-- Rollback instructions (if needed):
-- BEGIN;
-- ALTER TABLE "User" ADD COLUMN role_string VARCHAR(50);
-- UPDATE "User" SET role_string = role[1];
-- ALTER TABLE "User" DROP COLUMN role;
-- ALTER TABLE "User" RENAME COLUMN role_string TO role;
-- COMMIT;

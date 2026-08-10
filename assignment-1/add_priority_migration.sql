-- Migration Script: Add Priority Column to Tickets Table
-- Date: 2024
-- Description: Adds a 'priority' column to support ticket prioritization
--              Values: low, medium, high, urgent

-- Step 1: Add the priority column with default value 'medium'
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';

-- Step 2: Update any existing tickets without priority to have 'medium' priority
UPDATE tickets 
SET priority = 'medium' 
WHERE priority IS NULL;

-- Step 3: Verify the column was added successfully
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'tickets' 
  AND column_name = 'priority';

-- Step 4: Show sample of updated tickets
SELECT ticket_id, title, priority, status, created_at 
FROM tickets 
ORDER BY ticket_id ASC 
LIMIT 5;

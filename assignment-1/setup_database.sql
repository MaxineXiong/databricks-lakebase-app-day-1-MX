-- Database Schema Setup and Initial Data
-- Support Ticket Management System
-- Databricks Lakebase Postgres Database
-- Date: 2024
-- 
-- This script creates the initial database schema and populates it with sample data
-- for the Support Ticket Manager application.

-- =========================================
-- SCHEMA CREATION
-- =========================================

-- Create tickets table with priority support
CREATE TABLE IF NOT EXISTS tickets (
  ticket_id BIGINT PRIMARY KEY,
  title VARCHAR NOT NULL,
  status VARCHAR,
  priority VARCHAR(20) DEFAULT 'medium',
  created_by VARCHAR,
  created_at TIMESTAMP
);

-- Create ticket_messages table with foreign key relationship
CREATE TABLE IF NOT EXISTS ticket_messages (
  message_id BIGINT PRIMARY KEY,
  ticket_id BIGINT NOT NULL,
  message_text VARCHAR,
  author VARCHAR,
  created_at TIMESTAMP,
  FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);

-- =========================================
-- CLEAR EXISTING DATA (if any)
-- =========================================

TRUNCATE tickets, ticket_messages;

-- =========================================
-- SAMPLE DATA - TICKETS
-- =========================================
-- Insert sample tickets with different statuses and priorities

INSERT INTO tickets VALUES
  (1, 'Unable to login to application', 'open', 'urgent', 'john.doe@company.com', '2026-08-08 09:15:00'),
  (2, 'Data export feature not working', 'in_progress', 'high', 'jane.smith@company.com', '2026-08-09 10:30:00'),
  (3, 'Password reset request', 'resolved', 'medium', 'mike.johnson@company.com', '2026-08-07 14:20:00'),
  (4, 'Dashboard loading very slowly', 'in_progress', 'high', 'sarah.williams@company.com', '2026-08-09 15:45:00'),
  (5, 'Request for dark mode feature', 'open', 'low', 'alex.brown@company.com', '2026-08-10 08:20:00'),
  (6, 'Incorrect calculations in summary report', 'resolved', 'urgent', 'chris.lee@company.com', '2026-08-06 11:30:00'),
  (7, 'Cannot upload files larger than 10MB', 'open', 'medium', 'emily.davis@company.com', '2026-08-10 09:05:00'),
  (8, 'Email notifications not being received', 'in_progress', 'medium', 'david.martinez@company.com', '2026-08-08 16:30:00');

-- =========================================
-- SAMPLE DATA - TICKET MESSAGES
-- =========================================
-- Insert sample messages for each ticket showing conversation threads

INSERT INTO ticket_messages VALUES
  -- Messages for ticket 1 (open, urgent)
  (1, 1, 'I am unable to login to the application. Getting error: Invalid credentials', 'john.doe@company.com', '2026-08-08 09:15:00'),
  (2, 1, 'Thank you for reporting this. Can you please try clearing your browser cache?', 'support.agent@company.com', '2026-08-08 09:45:00'),
  (3, 1, 'I cleared the cache but still having the same issue.', 'john.doe@company.com', '2026-08-08 10:10:00'),
  (4, 1, 'Can you also try using an incognito/private browser window?', 'support.agent@company.com', '2026-08-08 11:00:00'),
  
  -- Messages for ticket 2 (in_progress, high)
  (5, 2, 'The data export button is not responding when clicked.', 'jane.smith@company.com', '2026-08-09 10:30:00'),
  (6, 2, 'We are investigating this issue. It appears to be related to recent system updates.', 'support.agent@company.com', '2026-08-09 11:15:00'),
  (7, 2, 'Our team has identified the root cause. Working on a fix now.', 'support.agent@company.com', '2026-08-09 14:20:00'),
  
  -- Messages for ticket 3 (resolved, medium)
  (8, 3, 'I need to reset my password. Cannot remember the current one.', 'mike.johnson@company.com', '2026-08-07 14:20:00'),
  (9, 3, 'Password reset link has been sent to your registered email address.', 'support.agent@company.com', '2026-08-07 14:25:00'),
  (10, 3, 'Thank you! I was able to reset my password successfully.', 'mike.johnson@company.com', '2026-08-07 14:40:00'),
  
  -- Messages for ticket 4 (in_progress, high)
  (11, 4, 'The main dashboard takes over 30 seconds to load. This is impacting my daily work.', 'sarah.williams@company.com', '2026-08-09 15:45:00'),
  (12, 4, 'We have identified some performance bottlenecks. Optimizing the queries now.', 'support.agent@company.com', '2026-08-09 16:30:00'),
  (13, 4, 'Initial optimizations deployed. Can you test and let us know if it is improved?', 'support.agent@company.com', '2026-08-09 18:15:00'),
  
  -- Messages for ticket 5 (open, low)
  (14, 5, 'Would it be possible to add a dark mode option? The current bright theme strains my eyes.', 'alex.brown@company.com', '2026-08-10 08:20:00'),
  (15, 5, 'Thank you for the suggestion! I have forwarded this to our product team for consideration.', 'support.agent@company.com', '2026-08-10 09:00:00'),
  
  -- Messages for ticket 6 (resolved, urgent)
  (16, 6, 'The monthly summary report shows incorrect revenue totals for July.', 'chris.lee@company.com', '2026-08-06 11:30:00'),
  (17, 6, 'We have found the bug in the aggregation logic. Deploying a fix now.', 'support.agent@company.com', '2026-08-06 13:15:00'),
  (18, 6, 'Fix deployed. Please refresh your report and verify the numbers are now correct.', 'support.agent@company.com', '2026-08-06 14:00:00'),
  (19, 6, 'Confirmed! The numbers are now accurate. Thank you for the quick fix!', 'chris.lee@company.com', '2026-08-06 14:30:00'),
  
  -- Messages for ticket 7 (open, medium)
  (20, 7, 'I am trying to upload a 15MB presentation file but getting an error: File size exceeds limit.', 'emily.davis@company.com', '2026-08-10 09:05:00'),
  (21, 7, 'The current limit is 10MB for security reasons. Let me check if we can increase this for your account.', 'support.agent@company.com', '2026-08-10 09:30:00'),
  
  -- Messages for ticket 8 (in_progress, medium)
  (22, 8, 'I have not received any email notifications for the past 3 days.', 'david.martinez@company.com', '2026-08-08 16:30:00'),
  (23, 8, 'Can you check your spam folder? Also, what email address is registered in your profile?', 'support.agent@company.com', '2026-08-08 17:00:00'),
  (24, 8, 'I checked spam - nothing there. My registered email is david.martinez@company.com', 'david.martinez@company.com', '2026-08-08 17:15:00'),
  (25, 8, 'I see the issue - your notification preferences were accidentally disabled. Enabling them now.', 'support.agent@company.com', '2026-08-09 09:00:00');

-- =========================================
-- VERIFICATION QUERIES
-- =========================================

-- View all tickets sorted by priority and ID
SELECT 
  ticket_id, 
  title, 
  priority, 
  status, 
  created_by,
  created_at
FROM tickets
ORDER BY 
  CASE priority
    WHEN 'urgent' THEN 1
    WHEN 'high' THEN 2
    WHEN 'medium' THEN 3
    WHEN 'low' THEN 4
    ELSE 5
  END ASC,
  ticket_id ASC;

-- View all messages with ticket association
SELECT * FROM ticket_messages ORDER BY ticket_id, message_id;

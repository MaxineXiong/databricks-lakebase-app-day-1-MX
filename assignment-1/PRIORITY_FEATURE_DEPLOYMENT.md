# Priority Feature - Deployment Guide

## 🎯 Overview
Added ticket priority functionality to the Support Ticket Manager. Tickets are now sorted by **priority first, then ticket_id** in ascending order.

## 📋 Priority Levels
1. 🔥 **Urgent** (Red badge)
2. ⚠️ **High** (Orange badge)
3. 📌 **Medium** (Yellow badge) - Default
4. 📋 **Low** (Gray badge)

## 🗄️ Database Migration (REQUIRED FIRST STEP)

Before deploying the updated app, you **MUST** run the database migration to add the priority column:

### Option 1: Using psql or SQL notebook
Run the SQL commands from `add_priority_migration.sql`:

```sql
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';

UPDATE tickets 
SET priority = 'medium' 
WHERE priority IS NULL;
```

### Option 2: Using Python
```python
import psycopg2
import base64
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
secret = w.secrets.get_secret(scope="support_ticket_app", key="lakebase-url")
lakebase_url = base64.b64decode(secret.value).decode("utf-8")

conn = psycopg2.connect(lakebase_url)
cursor = conn.cursor()

cursor.execute("""
    ALTER TABLE tickets 
    ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium'
""")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM tickets WHERE priority IS NOT NULL")
print(f"✅ Tickets with priority: {cursor.fetchone()[0]}")

cursor.close()
conn.close()
```

## 📝 Changes Made

### 1. Backend (app.py)
- ✅ Updated `get_all_tickets()` to include priority and sort by priority then ticket_id
- ✅ Updated `get_ticket_by_id()` to include priority
- ✅ Updated `create_ticket()` to accept and store priority
- ✅ Added `update_ticket_priority()` function
- ✅ Updated `create_ticket_route()` to handle priority input
- ✅ Added `update_priority_route()` for updating priority

**Sorting Logic:**
```sql
ORDER BY 
    CASE priority
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        ELSE 5
    END ASC,
    ticket_id ASC
```

### 2. Frontend Templates

#### index.html
- ✅ Added priority badge display
- ✅ Shows priority before status badge
- ✅ Color-coded badges:
  - Urgent: Red background, white text, 🔥 icon
  - High: Orange background, white text, ⚠️ icon
  - Medium: Yellow background, dark text, 📌 icon
  - Low: Gray background, white text, 📋 icon

#### ticket.html
- ✅ Added priority display in ticket details
- ✅ Added "Update Priority" form with dropdown
- ✅ Rearranged layout to show both update forms side by side

#### create.html
- ✅ Added priority dropdown to ticket creation form
- ✅ Default priority is "medium"

## 🚀 Deployment Steps

### Step 1: Run Database Migration
Run the SQL migration script **BEFORE** deploying the app (see above).

### Step 2: Verify Migration
```sql
-- Should return the priority column details
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tickets' AND column_name = 'priority';

-- Should show all tickets with priority values
SELECT ticket_id, title, priority FROM tickets LIMIT 5;
```

### Step 3: Deploy Updated App
```bash
cd /Workspace/Users/maxinexiong2@gmail.com/databricks-lakebase-app-day-1-MX/assignment-1

# Deploy the app
databricks apps deploy support-ticket-manager

# Restart the app
databricks apps restart support-ticket-manager

# Check status
databricks apps get support-ticket-manager
```

### Step 4: Verify Features
1. Open the app in your browser
2. ✅ Verify tickets are sorted by priority (urgent first, low last)
3. ✅ Within same priority, verify tickets are sorted by ID (1, 2, 3...)
4. ✅ Create a new ticket with high priority - should appear near top
5. ✅ Update an existing ticket's priority - should move in list
6. ✅ All timestamps should show in Australian Eastern timezone

## 🎨 Visual Examples

### Index Page (Ticket List)
```
Ticket #1 - Server Down
[🔥 Urgent] [🔴 Open]  [View Details]

Ticket #5 - Database Slow
[⚠️ High] [🟡 In Progress]  [View Details]

Ticket #2 - Update Documentation
[📌 Medium] [🟢 Resolved]  [View Details]

Ticket #3 - Clean up logs
[📋 Low] [🔴 Open]  [View Details]
```

### Ticket Detail Page
```
Ticket #5 - Database Slow
Created by: admin@company.com
Created at: 2024-08-10 15:30:00 AEDT

Priority: [⚠️ High]
Status: [🟡 In Progress]

[Update Priority ▼]    [Update Status ▼]
```

## 📊 Expected Behavior

### Ticket Ordering
Given tickets:
- Ticket #1: Priority=urgent, Status=open
- Ticket #2: Priority=medium, Status=resolved  
- Ticket #3: Priority=low, Status=open
- Ticket #4: Priority=urgent, Status=in_progress
- Ticket #5: Priority=high, Status=in_progress

Display order:
1. Ticket #1 (urgent, ID 1)
2. Ticket #4 (urgent, ID 4)
3. Ticket #5 (high, ID 5)
4. Ticket #2 (medium, ID 2)
5. Ticket #3 (low, ID 3)

## ✅ Testing Checklist

- [ ] Database migration completed successfully
- [ ] App deployed and running
- [ ] Tickets display in priority order (urgent → high → medium → low)
- [ ] Within same priority, tickets sorted by ID ascending
- [ ] Can create new ticket with priority selection
- [ ] Can update existing ticket's priority
- [ ] Priority badges display with correct colors
- [ ] All timestamps show in Australian Eastern timezone (AEDT/AEST)

## 🐛 Troubleshooting

**Issue: "column priority does not exist"**
- Solution: Run the database migration script first

**Issue: Tickets not sorted by priority**
- Solution: Verify app was redeployed after code changes

**Issue: All tickets showing same priority**
- Solution: Check that migration set default values correctly

## 📚 API Reference

### Create Ticket
```python
create_ticket(title, status, priority, created_by)
# priority: 'low' | 'medium' | 'high' | 'urgent'
```

### Update Priority
```python
update_ticket_priority(ticket_id, new_priority)
# new_priority: 'low' | 'medium' | 'high' | 'urgent'
```

## 🎉 Feature Complete!

All changes have been implemented and are ready for deployment after the database migration.

# Support Ticket Manager - Databricks App

A web application for managing support tickets with full CRUD operations on Databricks Lakebase Postgres `tickets` and `ticket_messages` tables.

## 📚 About This Project

**This application is my submission for "Day 1 Homework: Build a Lakebase-Powered Support Ticket App"** under the [DataExpert.io](https://www.dataexpert.io) program **"The Rise of the AI Data Engineer"**.

All data is stored in **Databricks Lakebase Postgres**, demonstrating real-world use of Databricks' managed Postgres offering for transactional workloads.

## Tech Stack

- **Flask** - Web application framework and REST API
- **psycopg2** - PostgreSQL database connectivity
- **Databricks Lakebase Postgres** - Managed Postgres database backend
- **Databricks Apps** - Hosting platform
- **HTML/CSS/JavaScript** - Frontend UI with responsive design

## Features

- ✅ **View all support tickets** - Browse all tickets with status and priority indicators
- ✅ **View ticket details** - Select a ticket to see all messages in a conversation thread
- ✅ **Create new tickets** - Create tickets with title, description, and priority
- ✅ **Add messages** - Reply to existing tickets with new messages in a threaded conversation
- ✅ **Update ticket status** - Change status between open, in_progress, and resolved
- ✅ **Filter by ticket status** - Filter tickets by status (All, Open, In Progress, Resolved)
- ✅ **Delete tickets** - Select multiple tickets and delete them with a confirmation dialog
- ✅ **Ticket statistics visual** - Visual dashboard showing ticket counts by status and priority with percentage calculations

## Files

### Core Application
- `app.py` - Main Flask application with routes, database functions, and business logic
- `app.yaml` - Databricks App deployment configuration
- `requirements.txt` - Python dependencies (Flask, psycopg2-binary, pytz)

### Setup & Configuration
- `setup_secrets.py` - Helper script to configure Lakebase connection URL in Databricks secrets
- `setup_database.sql` - Complete database schema and sample data setup script

### Templates (HTML/CSS)
- `templates/base.html` - Base template with navigation, header, and shared styling
- `templates/index.html` - Home page with ticket list, statistics dashboard, and filtering
- `templates/create.html` - Create new ticket form with priority selection
- `templates/ticket.html` - Ticket detail view with conversation thread and status updates

### Documentation
- `README.md` - This file - comprehensive setup and usage guide
- `PRIORITY_FEATURE_DEPLOYMENT.md` - Priority levels feature implementation details
- `STATUS_FILTER_FEATURE.md` - Status filtering functionality documentation
- `DELETE_FEATURE.md` - Bulk delete feature with confirmation implementation
- `UI_MODERNIZATION.md` - UI design and styling updates documentation

## Prerequisites

1. **Create a Databricks Lakebase Project**:
   - Go to the **Databricks Lakebase**
   - Click **Create Project** to set up a new Lakebase Postgres database
   - Create a Postgres role with password authentication
   - Copy the **connection URL** (you'll need this for Step 1 below)

2. **Set Up Database Schema and Initial Data**:
   - Open the **SQL Editor** in the Databricks Lakebase
   - Execute the SQL code from `setup_database.sql` to create:
     - `tickets` table with general ticket attributes
     - `ticket_messages` table referencing `tickets` table with individual message attributes
     - Sample tickets and messages for testing

3. **Lakebase Connection URL**: You'll need your Databricks Lakebase connection URL for the Postgres role you created. This is required for the front-end app to connect to the Lakebase database.

## Setup Instructions

### Step 1: Configure Lakebase Connection Secret

The easiest way to configure your Lakebase connection is to use the provided setup script:

```bash
# Install databricks-sdk if not already installed
pip install databricks-sdk

# Run the setup script
python assignment-1/setup_secrets.py
```

The script will:
1. Prompt you for your Lakebase connection URL (e.g., `postgresql://role:password@ep-xxxxx.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require`)
2. Create the secret scope `support_ticket_app`
3. Store the connection URL securely as a workspace secret

**Alternative: Manual Secret Configuration**

If you prefer to use the Databricks CLI:

```bash
# Create a secret scope
databricks secrets create-scope support_ticket_app

# Add the Lakebase URL secret
databricks secrets put-secret support_ticket_app lakebase-url
```

### Step 2: Deploy the App

#### Option 1: Using Databricks CLI

```bash
# Navigate to the assignment-1 folder
cd /Workspace/Users/your-email@domain.com/databricks-lakebase-app-day-1-MX/assignment-1

# Create the app
databricks apps create support-ticket-manager \
  --source-code-path ./

# Deploy the app
databricks apps deploy support-ticket-manager

# Start the app
databricks apps start support-ticket-manager
```

#### Option 2: Using Databricks UI

1. Go to **Apps** in the Databricks workspace
2. Click **Create App**
3. Set the app name: `support-ticket-manager`
4. Set source code path: `/Workspace/Users/your-email@domain.com/databricks-lakebase-app-day-1-MX/assignment-1`
5. Click **Create**
6. Click **Deploy**
7. Once deployed, click **Start**

## Usage

Once deployed and started:

1. Navigate to the app URL (provided after deployment)

### Viewing Tickets
- The home page displays all support tickets with status and priority indicators
- **Ticket Statistics Dashboard** at the top shows real-time counts by status and priority with percentages
- **Filter by Status**: Use the filter buttons (All, Open, In Progress, Resolved) to view tickets by status
- Each ticket card shows:
  - Priority badge (🔴 Urgent, 🟠 High, 🟡 Medium, 🟢 Low)
  - Status indicator
  - Title and creation details
  - Action buttons (View Details, Delete)

### Creating New Tickets
- Click **"Create New Ticket"** in the navigation
- Fill in the ticket details:
  - Title (required)
  - Description (initial message)
  - Priority (Urgent, High, Medium, Low)
- Submit to create the ticket

### Managing Tickets
- **View Details**: Click on any ticket to see the full conversation thread
- **Add Messages**: Reply to tickets with new messages in the conversation view
- **Update Status**: Change ticket status using the dropdown (Open, In Progress, Resolved)
- **Delete Tickets**: 
  - Select multiple tickets using checkboxes
  - Click "Delete Selected" button
  - Confirm deletion in the dialog that appears

## Database Schema

The complete schema is defined in `setup_database.sql`. Key tables:

### tickets table
```sql
ticket_id BIGINT PRIMARY KEY
title VARCHAR NOT NULL
status VARCHAR
priority VARCHAR(20) DEFAULT 'medium'
created_by VARCHAR
created_at TIMESTAMP
```

### ticket_messages table
```sql
message_id BIGINT PRIMARY KEY
ticket_id BIGINT NOT NULL (FOREIGN KEY)
message_text VARCHAR
author VARCHAR
created_at TIMESTAMP
```

## Troubleshooting

**Connection errors**: Verify your Databricks Lakebase Postgres endpoint is running and accessible

**Permission errors**: Ensure the database user has SELECT, INSERT, UPDATE permissions on both tables

**Import errors**: Check that `requirements.txt` dependencies are installed (psycopg2-binary)

**Authentication errors**: Double-check your Lakebase URL in the secrets. Re-run `setup_secrets.py` if needed.

**Secret scope errors**: Ensure you have permissions to create secret scopes in your workspace

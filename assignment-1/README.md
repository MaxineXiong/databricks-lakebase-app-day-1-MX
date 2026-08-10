# Support Ticket Manager - Databricks App

A web application for managing support tickets with full CRUD operations on Lakebase Postgres `tickets` and `ticket_messages` tables.

## Features

- ✅ **View all support tickets** - Browse all tickets with status indicators
- ✅ **View ticket details** - Select a ticket to see all messages in a conversation thread
- ✅ **Create new tickets** - Create tickets with title, status, and initial message
- ✅ **Add messages** - Reply to existing tickets with new messages
- ✅ **Update ticket status** - Change status between open, in_progress, and resolved

## Files

- `app.py` - Main Streamlit application code
- `app.yaml` - Databricks App configuration
- `requirements.txt` - Python dependencies
- `setup_secrets.py` - Helper script to configure Lakebase connection URL

## Prerequisites

1. **Lakebase Postgres Database**: Ensure you have a Lakebase Postgres database with these tables:
   - `tickets`
   - `ticket_messages`

2. **Lakebase Connection URL**: You'll need your Lakebase connection URL (PostgreSQL connection string)

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
1. Prompt you for your Lakebase connection URL (e.g., `postgresql://user:password@host:5432/database`)
2. Create the secret scope `support_ticket_app`
3. Store the connection URL securely as a Databricks secret

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
2. Use the sidebar to switch between:
   - **View All Tickets** - See and interact with existing tickets
   - **Create New Ticket** - Submit a new support ticket
3. Click **View Details** on any ticket to see messages and add replies
4. Update ticket status using the dropdown in the ticket detail view

## Database Schema

### tickets table
```sql
ticket_id BIGINT PRIMARY KEY
title VARCHAR NOT NULL
status VARCHAR
created_by VARCHAR
created_at TIMESTAMP
```

### ticket_messages table
```sql
message_id BIGINT PRIMARY KEY
ticket_id BIGINT NOT NULL (FOREIGN KEY)
message_text TEXT
author VARCHAR
created_at TIMESTAMP
```

## Troubleshooting

**Connection errors**: Verify your Lakebase Postgres endpoint is running and accessible

**Permission errors**: Ensure the database user has SELECT, INSERT, UPDATE permissions on both tables

**Import errors**: Check that `requirements.txt` dependencies are installed (psycopg2-binary)

**Authentication errors**: Double-check your Lakebase URL in the secrets. Re-run `setup_secrets.py` if needed.

**Secret scope errors**: Ensure you have permissions to create secret scopes in your workspace

## Tech Stack

- **Streamlit** - Web framework
- **psycopg2** - PostgreSQL database connectivity
- **Lakebase Postgres** - Database backend
- **Databricks Apps** - Hosting platform

## Environment Variables

The app uses the following environment variable (automatically configured via `app.yaml` from secrets):

- `LAKEBASE_URL` - Your Lakebase Postgres connection URL

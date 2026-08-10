from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
import os
import base64
from datetime import datetime
import pytz
from databricks.sdk import WorkspaceClient

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration for Lakebase Postgres
TICKETS_TABLE = "tickets"
MESSAGES_TABLE = "ticket_messages"

# Timezone configuration
AUSTRALIAN_TZ = pytz.timezone('Australia/Sydney')  # Australian Eastern Time (handles AEST/AEDT)

# Initialize Databricks client
_w = WorkspaceClient()
_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "support_ticket_app")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")

def _get_lakebase_url():
    """Fetch and decode the Lakebase connection URL from the Databricks secret scope."""
    secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    return base64.b64decode(secret.value).decode("utf-8")

def get_connection():
    """Create a connection to Lakebase Postgres database."""
    return psycopg2.connect(_get_lakebase_url())

def convert_to_australian_time(dt):
    """Convert a datetime to Australian Eastern timezone."""
    if dt is None:
        return None
    # If datetime is naive, assume it's UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    # Convert to Australian Eastern timezone
    return dt.astimezone(AUSTRALIAN_TZ)

def get_ticket_statistics(status_filter=None):
    """Get ticket statistics for dashboard display.
    
    Args:
        status_filter: Optional status to filter by ('open', 'in_progress', 'resolved', or None for all)
    
    Returns:
        Dict with counts by status and priority
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Build WHERE clause for filter
            where_clause = ""
            params = []
            if status_filter and status_filter != 'all':
                where_clause = " WHERE status = %s"
                params.append(status_filter)
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {TICKETS_TABLE}{where_clause}", params)
            total = cursor.fetchone()[0]
            
            # Get counts by status
            query = f"""
                SELECT status, COUNT(*) 
                FROM {TICKETS_TABLE}
                {where_clause}
                GROUP BY status
            """
            cursor.execute(query, params)
            status_counts = dict(cursor.fetchall())
            
            # Get counts by priority
            query = f"""
                SELECT priority, COUNT(*) 
                FROM {TICKETS_TABLE}
                {where_clause}
                GROUP BY priority
            """
            cursor.execute(query, params)
            priority_counts = dict(cursor.fetchall())
            
            return {
                'total': total,
                'by_status': {
                    'open': status_counts.get('open', 0),
                    'in_progress': status_counts.get('in_progress', 0),
                    'resolved': status_counts.get('resolved', 0)
                },
                'by_priority': {
                    'urgent': priority_counts.get('urgent', 0),
                    'high': priority_counts.get('high', 0),
                    'medium': priority_counts.get('medium', 0),
                    'low': priority_counts.get('low', 0)
                }
            }
    finally:
        conn.close()

def get_all_tickets(status_filter=None):
    """Fetch all support tickets ordered by priority, then ticket_id.
    
    Args:
        status_filter: Optional status to filter by ('open', 'in_progress', 'resolved', or None for all)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Build query with optional status filter
            query = f"""
                SELECT ticket_id, title, status, priority, created_by, created_at 
                FROM {TICKETS_TABLE}
            """
            
            params = []
            if status_filter and status_filter != 'all':
                query += " WHERE status = %s"
                params.append(status_filter)
            
            query += """
                ORDER BY 
                    CASE priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END ASC,
                    ticket_id ASC
            """
            
            cursor.execute(query, params)
            return cursor.fetchall()
    finally:
        conn.close()

def get_ticket_by_id(ticket_id):
    """Fetch a single ticket by ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT ticket_id, title, status, priority, created_by, created_at 
                FROM {TICKETS_TABLE}
                WHERE ticket_id = %s
            """, (ticket_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_ticket_messages(ticket_id):
    """Fetch all messages for a specific ticket."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT message_id, message_text, author, created_at
                FROM {MESSAGES_TABLE}
                WHERE ticket_id = %s
                ORDER BY created_at ASC
            """, (ticket_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def create_ticket(title, status, priority, created_by):
    """Create a new support ticket."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COALESCE(MAX(ticket_id), 0) + 1 FROM {TICKETS_TABLE}")
            ticket_id = cursor.fetchone()[0]
            
            cursor.execute(f"""
                INSERT INTO {TICKETS_TABLE} (ticket_id, title, status, priority, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (ticket_id, title, status, priority, created_by, datetime.now()))
            conn.commit()
            return ticket_id
    finally:
        conn.close()

def add_message(ticket_id, message_text, author):
    """Add a message to an existing ticket."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COALESCE(MAX(message_id), 0) + 1 FROM {MESSAGES_TABLE}")
            message_id = cursor.fetchone()[0]
            
            cursor.execute(f"""
                INSERT INTO {MESSAGES_TABLE} (message_id, ticket_id, message_text, author, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (message_id, ticket_id, message_text, author, datetime.now()))
            conn.commit()
    finally:
        conn.close()

def update_ticket_status(ticket_id, new_status):
    """Update the status of a ticket."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                UPDATE {TICKETS_TABLE}
                SET status = %s
                WHERE ticket_id = %s
            """, (new_status, ticket_id))
            conn.commit()
    finally:
        conn.close()

def update_ticket_priority(ticket_id, new_priority):
    """Update the priority of a ticket."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                UPDATE {TICKETS_TABLE}
                SET priority = %s
                WHERE ticket_id = %s
            """, (new_priority, ticket_id))
            conn.commit()
    finally:
        conn.close()

def delete_tickets(ticket_ids):
    """Delete multiple tickets and their associated messages.
    
    Args:
        ticket_ids: List of ticket IDs to delete
    
    Returns:
        Number of tickets deleted
    """
    if not ticket_ids:
        return 0
    
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # First delete all associated messages (foreign key constraint)
            cursor.execute(f"""
                DELETE FROM {MESSAGES_TABLE}
                WHERE ticket_id = ANY(%s)
            """, (ticket_ids,))
            
            # Then delete the tickets
            cursor.execute(f"""
                DELETE FROM {TICKETS_TABLE}
                WHERE ticket_id = ANY(%s)
            """, (ticket_ids,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
    finally:
        conn.close()

# Register Jinja filter for timezone conversion
@app.template_filter('australian_time')
def australian_time_filter(dt):
    """Jinja filter to convert datetime to Australian Eastern timezone."""
    aus_dt = convert_to_australian_time(dt)
    if aus_dt:
        return aus_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    return str(dt)

# Routes
@app.route('/')
def index():
    """Home page - list all tickets with optional status filter."""
    status_filter = request.args.get('status', 'all')
    
    try:
        tickets = get_all_tickets(status_filter=status_filter)
        statistics = get_ticket_statistics(status_filter=status_filter)
        return render_template('index.html', tickets=tickets, current_filter=status_filter, stats=statistics)
    except Exception as e:
        flash(f'Error fetching tickets: {str(e)}', 'error')
        return render_template('index.html', tickets=[], current_filter=status_filter, stats={})

@app.route('/ticket/<int:ticket_id>')
def view_ticket(ticket_id):
    """View a specific ticket with its messages."""
    try:
        ticket = get_ticket_by_id(ticket_id)
        if not ticket:
            flash('Ticket not found', 'error')
            return redirect(url_for('index'))
        
        messages = get_ticket_messages(ticket_id)
        return render_template('ticket.html', ticket=ticket, messages=messages)
    except Exception as e:
        flash(f'Error loading ticket: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def create_ticket_route():
    """Create a new ticket."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        status = request.form.get('status', 'open')
        priority = request.form.get('priority', 'medium')
        created_by = request.form.get('created_by', '').strip()
        initial_message = request.form.get('initial_message', '').strip()
        
        if not title or not created_by:
            flash('Title and Your Name are required', 'error')
            return render_template('create.html')
        
        try:
            ticket_id = create_ticket(title, status, priority, created_by)
            if initial_message:
                add_message(ticket_id, initial_message, created_by)
            flash(f'Ticket #{ticket_id} created successfully!', 'success')
            return redirect(url_for('view_ticket', ticket_id=ticket_id))
        except Exception as e:
            flash(f'Error creating ticket: {str(e)}', 'error')
            return render_template('create.html')
    
    return render_template('create.html')

@app.route('/ticket/<int:ticket_id>/add_message', methods=['POST'])
def add_message_route(ticket_id):
    """Add a message to a ticket."""
    message_text = request.form.get('message_text', '').strip()
    author = request.form.get('author', '').strip()
    
    if not message_text or not author:
        flash('Message and author are required', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    try:
        add_message(ticket_id, message_text, author)
        flash('Message added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding message: {str(e)}', 'error')
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/ticket/<int:ticket_id>/update_status', methods=['POST'])
def update_status_route(ticket_id):
    """Update ticket status."""
    new_status = request.form.get('status', '').strip()
    
    if new_status not in ['open', 'in_progress', 'resolved']:
        flash('Invalid status', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    try:
        update_ticket_status(ticket_id, new_status)
        flash(f'Status updated to: {new_status}', 'success')
    except Exception as e:
        flash(f'Error updating status: {str(e)}', 'error')
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/ticket/<int:ticket_id>/update_priority', methods=['POST'])
def update_priority_route(ticket_id):
    """Update ticket priority."""
    new_priority = request.form.get('priority', '').strip()
    
    if new_priority not in ['low', 'medium', 'high', 'urgent']:
        flash('Invalid priority', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    try:
        update_ticket_priority(ticket_id, new_priority)
        flash(f'Priority updated to: {new_priority}', 'success')
    except Exception as e:
        flash(f'Error updating priority: {str(e)}', 'error')
    
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/tickets/delete', methods=['POST'])
def delete_tickets_route():
    """Delete multiple tickets."""
    # Get ticket IDs from form data (submitted as JSON)
    data = request.get_json()
    ticket_ids = data.get('ticket_ids', [])
    
    if not ticket_ids:
        return jsonify({'success': False, 'error': 'No tickets selected'}), 400
    
    # Validate that all IDs are integers
    try:
        ticket_ids = [int(tid) for tid in ticket_ids]
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid ticket IDs'}), 400
    
    try:
        deleted_count = delete_tickets(ticket_ids)
        return jsonify({
            'success': True, 
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} ticket(s)'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
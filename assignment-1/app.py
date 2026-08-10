from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
import os
import base64
from datetime import datetime
from databricks.sdk import WorkspaceClient

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration for Lakebase Postgres
TICKETS_TABLE = "tickets"
MESSAGES_TABLE = "ticket_messages"

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

def get_all_tickets():
    """Fetch all support tickets."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT ticket_id, title, status, created_by, created_at 
                FROM {TICKETS_TABLE}
                ORDER BY created_at DESC
            """)
            return cursor.fetchall()
    finally:
        conn.close()

def get_ticket_by_id(ticket_id):
    """Fetch a single ticket by ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT ticket_id, title, status, created_by, created_at 
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

def create_ticket(title, status, created_by):
    """Create a new support ticket."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COALESCE(MAX(ticket_id), 0) + 1 FROM {TICKETS_TABLE}")
            ticket_id = cursor.fetchone()[0]
            
            cursor.execute(f"""
                INSERT INTO {TICKETS_TABLE} (ticket_id, title, status, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (ticket_id, title, status, created_by, datetime.now()))
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

# Routes
@app.route('/')
def index():
    """Home page - list all tickets."""
    try:
        tickets = get_all_tickets()
        return render_template('index.html', tickets=tickets)
    except Exception as e:
        flash(f'Error fetching tickets: {str(e)}', 'error')
        return render_template('index.html', tickets=[])

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
        created_by = request.form.get('created_by', '').strip()
        initial_message = request.form.get('initial_message', '').strip()
        
        if not title or not created_by:
            flash('Title and Your Name are required', 'error')
            return render_template('create.html')
        
        try:
            ticket_id = create_ticket(title, status, created_by)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
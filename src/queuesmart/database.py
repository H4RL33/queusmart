import sqlite3
import hashlib
import os
import datetime
from typing import Optional, List, Dict, Union

DB_NAME = "queuesmart.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initializes the database with the required tables."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Enable foreign keys
    c.execute("PRAGMA foreign_keys = ON;")

    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Staff', 'Manager'))
        )
    ''')
    
    # Customers Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            preferred_contact TEXT
        )
    ''')

    # Tickets Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Housing', 'Benefits', 'Digital Support', 'Wellbeing', 'Other')),
            description TEXT NOT NULL,
            urgency TEXT NOT NULL CHECK(urgency IN ('Low', 'Medium', 'High', 'Critical')),
            status TEXT NOT NULL CHECK(status IN ('Open', 'In Progress', 'Waiting', 'Closed')),
            created_at TEXT NOT NULL,
            assigned_staff_id INTEGER,
            resolution TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (assigned_staff_id) REFERENCES users (id)
        )
    ''')

    # Appointments Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            staff_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            reason TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (staff_id) REFERENCES users (id)
        )
    ''')

    # Audit Logs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# --- User & Authentication Functions ---

def hash_password(password: str, salt: bytes = None) -> (str, str):
    """Hashes a password with a salt."""
    if salt is None:
        salt = os.urandom(16)
    else:
        # If salt implies hex string from DB, decode it? 
        # Actually better to treat input salt as bytes if passed, or hex if string.
        # Let's standardize: Internal function uses bytes, storage uses hex.
        if isinstance(salt, str):
            salt = bytes.fromhex(salt)
            
    # Use PBKDF2 for secure hashing
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hash.hex(), salt.hex()

def add_user(username, password, role):
    """Adds a new user to the database."""
    pwd_hash, salt = hash_password(password)
    
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
            (username, pwd_hash, salt, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username exists
    finally:
        conn.close()

def authenticate_user(username, password):
    """Verifies credentials and returns user details if valid."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    if user:
        stored_hash = user['password_hash']
        salt = user['salt']
        
        # Verify
        check_hash, _ = hash_password(password, salt)
        if check_hash == stored_hash:
            return dict(user)
    return None

# --- Customer Functions ---

def add_customer(name, phone, email, preferred_contact):
    """Adds a new customer."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO customers (name, phone, email, preferred_contact) VALUES (?, ?, ?, ?)",
        (name, phone, email, preferred_contact)
    )
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()
    return customer_id

def search_customers(query):
    """Searches customers by name, phone, or email."""
    conn = get_db_connection()
    q = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?",
        (q, q, q)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- Ticket Functions ---

def create_ticket(customer_id, category, description, urgency, created_by_user_id=None):
    """Creates a new support ticket."""
    conn = get_db_connection()
    created_at = datetime.datetime.now().isoformat()
    status = "Open"
    
    cursor = conn.execute(
        '''INSERT INTO tickets (customer_id, category, description, urgency, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (customer_id, category, description, urgency, status, created_at)
    )
    conn.commit()
    ticket_id = cursor.lastrowid
    
    # Log action if user is known
    if created_by_user_id:
        log_action_conn(conn, created_by_user_id, "CREATE_TICKET", f"Ticket ID {ticket_id} created for Customer {customer_id}")
        
    conn.close()
    return ticket_id

def update_ticket(ticket_id, status=None, assigned_staff_id=None, resolution=None, user_id=None):
    """Updates ticket details."""
    conn = get_db_connection()
    
    # Build dynamic query
    fields = []
    values = []
    
    if status:
        fields.append("status = ?")
        values.append(status)
    if assigned_staff_id:
        fields.append("assigned_staff_id = ?")
        values.append(assigned_staff_id)
    if resolution:
        fields.append("resolution = ?")
        values.append(resolution)
        
    if not fields:
        conn.close()
        return False
        
    values.append(ticket_id)
    query = f"UPDATE tickets SET {', '.join(fields)} WHERE id = ?"
    
    conn.execute(query, values)
    
    if user_id:
        log_action_conn(conn, user_id, "UPDATE_TICKET", f"Updated Ticket {ticket_id}: {', '.join(fields)}")
        
    conn.commit()
    conn.close()
    return True

def get_tickets(status_filter=None, staff_filter=None):
    """Retrieves tickets with optional filters."""
    conn = get_db_connection()
    query = "SELECT t.*, c.name as customer_name FROM tickets t JOIN customers c ON t.customer_id = c.id"
    params = []
    conditions = []
    
    if status_filter:
        conditions.append("t.status = ?")
        params.append(status_filter)
    if staff_filter:
        conditions.append("t.assigned_staff_id = ?")
        params.append(staff_filter)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- Appointment Functions ---

def check_clash(staff_id, start_time_str, duration_minutes):
    """Checks if a staff member is already booked."""
    new_start = datetime.datetime.fromisoformat(start_time_str)
    new_end = new_start + datetime.timedelta(minutes=duration_minutes)
    
    conn = get_db_connection()
    # Get all appointments for this staff member
    appointments = conn.execute("SELECT start_time, duration_minutes FROM appointments WHERE staff_id = ?", (staff_id,)).fetchall()
    conn.close()
    
    for appt in appointments:
        exist_start = datetime.datetime.fromisoformat(appt['start_time'])
        exist_end = exist_start + datetime.timedelta(minutes=appt['duration_minutes'])
        
        # Overlap logic: (StartA < EndB) and (EndA > StartB)
        if new_start < exist_end and new_end > exist_start:
            return True # Clash found
            
    return False

def create_appointment(customer_id, staff_id, start_time, duration_minutes, reason, created_by_user_id=None):
    """Creates an appointment if no clash exists."""
    if check_clash(staff_id, start_time, duration_minutes):
        raise ValueError("Appointment clash detected for this staff member.")
        
    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO appointments (customer_id, staff_id, start_time, duration_minutes, reason)
           VALUES (?, ?, ?, ?, ?)''',
        (customer_id, staff_id, start_time, duration_minutes, reason)
    )
    conn.commit()
    appt_id = cursor.lastrowid
    
    if created_by_user_id:
        log_action_conn(conn, created_by_user_id, "CREATE_APPT", f"Appt {appt_id} booked for Staff {staff_id}")
        
    conn.close()
    return appt_id

def get_appointments_by_staff(staff_id):
    """Gets appointments for a specific staff member."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT a.*, c.name as customer_name FROM appointments a JOIN customers c ON a.customer_id = c.id WHERE staff_id = ? ORDER BY start_time",
        (staff_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- Audit Logging ---

def log_action(user_id, action, details):
    """Logs a system action."""
    conn = get_db_connection()
    log_action_conn(conn, user_id, action, details)
    conn.close()

def log_action_conn(conn, user_id, action, details):
    """Helper to log within an existing connection/transaction."""
    timestamp = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT INTO audit_logs (user_id, action, timestamp, details) VALUES (?, ?, ?, ?)",
        (user_id, action, timestamp, details)
    )
    conn.commit()

import sqlite3
import hashlib
import os
import datetime
from typing import Optional, List, Dict, Union

# This is the name of the file where all the system's information is stored.
DB_NAME = "queuesmart.db"

def get_db_connection():
    """Opens the digital filing cabinet where all system information is kept."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This allows us to find information by using the name of the column.
    return conn

def init_db():
    """Sets up the digital filing cabinet by creating separate folders (tables) for staff, customers, tickets, and appointments."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # This ensures that all information is correctly linked between different folders.
    c.execute("PRAGMA foreign_keys = ON;")

    # Folder for Staff and Manager accounts.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Staff', 'Manager'))
        )
    ''')
    
    # Folder for Customer contact details and status.
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            preferred_contact TEXT,
            is_vulnerable INTEGER DEFAULT 0
        )
    ''')

    # Folder for Support Tickets where requests for help are tracked.
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Housing', 'Benefits', 'Digital Support', 'Wellbeing', 'Other')),
            description TEXT NOT NULL,
            urgency TEXT NOT NULL CHECK(urgency IN ('Low', 'Medium', 'High', 'Critical')),
            status TEXT NOT NULL CHECK(status IN ('Open', 'In Progress', 'Waiting', 'Closed')),
            created_at TEXT NOT NULL,
            closed_at TEXT,
            assigned_staff_id INTEGER,
            resolution TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (assigned_staff_id) REFERENCES users (id)
        )
    ''')

    # Folder for Appointments to manage meetings between customers and staff.
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

    # Folder for the Audit Log, which records every major change made in the system.
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

    # This part updates old versions of the filing cabinet to make sure they have space for 'closing dates' on tickets.
    try:
        c.execute("ALTER TABLE tickets ADD COLUMN closed_at TEXT")
    except sqlite3.OperationalError:
        # The space already exists.
        pass

    conn.commit()
    conn.close()

# --- Functions for managing people and security ---

def hash_password(password: str, salt: bytes = None) -> (str, str):
    """Scrambles a password into a secret code that can't be read by people, keeping it safe if anyone sees the files."""
    if salt is None:
        salt = os.urandom(16)
    else:
        if isinstance(salt, str):
            salt = bytes.fromhex(salt)
            
    # We use a high-security method to mix the password with a random 'salt' to create the final secret code.
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hash.hex(), salt.hex()

def add_user(username, password, role, created_by_user_id=None):
    """Adds a new person to the system by storing their name and their scrambled password."""
    pwd_hash, salt = hash_password(password)
    
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
            (username, pwd_hash, salt, role)
        )
        if created_by_user_id:
            log_action_conn(conn, created_by_user_id, "ADD_USER", f"Created user '{username}' with role '{role}'")
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Someone already has this name.
    finally:
        conn.close()

def authenticate_user(username, password):
    """Checks if the name and password entered match what we have in our digital filing cabinet."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    
    if user:
        stored_hash = user['password_hash']
        salt = user['salt']
        
        # We scramble the entered password and see if it matches the scrambled code we saved earlier.
        check_hash, _ = hash_password(password, salt)
        if check_hash == stored_hash:
            return dict(user)
    return None

def get_all_users():
    """Gives a list of everyone who can use the system, but keeps their secret passwords hidden."""
    conn = get_db_connection()
    rows = conn.execute("SELECT id, username, role FROM users").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_user(user_id, username=None, role=None, password=None, updated_by_user_id=None):
    """Changes someone's details, like their name or their job title (role), in the system's records."""
    conn = get_db_connection()
    
    fields = []
    values = []
    
    if username:
        fields.append("username = ?")
        values.append(username)
    if role:
        fields.append("role = ?")
        values.append(role)
    if password:
        pwd_hash, salt = hash_password(password)
        fields.append("password_hash = ?")
        values.append(pwd_hash)
        fields.append("salt = ?")
        values.append(salt)
        
    if not fields:
        conn.close()
        return False
        
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
    
    try:
        conn.execute(query, values)
        if updated_by_user_id:
            log_action_conn(conn, updated_by_user_id, "UPDATE_USER", f"Updated user ID {user_id}: {', '.join(fields)}")
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # The new name chosen is already taken.
    finally:
        conn.close()

def delete_user(user_id, deleted_by_user_id=None):
    """Removes a person from the system, as long as they aren't currently tied to any active work."""
    conn = get_db_connection()
    try:
        # We find their name first so we can record who was deleted in the audit log.
        user = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        username = user['username'] if user else "Unknown"

        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        if deleted_by_user_id:
            log_action_conn(conn, deleted_by_user_id, "DELETE_USER", f"Deleted user '{username}' (ID: {user_id})")
            
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Cannot delete user with assigned tickets or appointments.")
    finally:
        conn.close()

def seed_default_user():
    """Makes sure there is at least one 'admin' person who can start using the system for the first time."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
    
    if not user:
        conn.close()
        add_user("admin", "admin123", "Manager")
        print("Default user created: admin / admin123")
    else:
        conn.close()

# --- Functions for managing Customer information ---

def add_customer(name, phone, email, preferred_contact, is_vulnerable=False):
    """Adds a new customer's details (like name and phone) to our records."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO customers (name, phone, email, preferred_contact, is_vulnerable) VALUES (?, ?, ?, ?, ?)",
        (name, phone, email, preferred_contact, 1 if is_vulnerable else 0)
    )
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()
    return customer_id

def update_customer(customer_id, name, phone, email, preferred_contact, is_vulnerable):
    """Changes a customer's information if it has been updated in real life."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE customers SET name=?, phone=?, email=?, preferred_contact=?, is_vulnerable=? WHERE id=?",
        (name, phone, email, preferred_contact, 1 if is_vulnerable else 0, customer_id)
    )
    conn.commit()
    conn.close()

def delete_customer(customer_id, user_id=None):
    """Removes a customer from our records, as long as we don't need their history for tickets or meetings."""
    conn = get_db_connection()
    try:
        cust = conn.execute("SELECT name FROM customers WHERE id = ?", (customer_id,)).fetchone()
        name = cust['name'] if cust else "Unknown"

        conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        
        if user_id:
            log_action_conn(conn, user_id, "DELETE_CUSTOMER", f"Deleted customer '{name}' (ID: {customer_id})")
            
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Cannot delete customer with existing tickets or appointments.")
    conn.close()

def search_customers(query):
    """Finds customers by looking for their name, phone number, or email address in our files."""
    conn = get_db_connection()
    q = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?",
        (q, q, q)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_customer_history(customer_id):
    """Collects a list of every ticket and meeting a customer has ever had with us."""
    conn = get_db_connection()
    
    tickets = conn.execute(
        "SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,)
    ).fetchall()
    
    appts = conn.execute(
        "SELECT a.*, u.username as staff_name FROM appointments a JOIN users u ON a.staff_id = u.id WHERE customer_id = ? ORDER BY start_time DESC",
        (customer_id,)
    ).fetchall()
    
    conn.close()
    return {
        'tickets': [dict(t) for t in tickets],
        'appointments': [dict(a) for a in appts]
    }

# --- Functions for managing Help Requests (Tickets) ---

def create_ticket(customer_id, category, description, urgency, created_by_user_id=None):
    """Starts a new request for help for a customer and records the date and time it began."""
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
    
    if created_by_user_id:
        log_action_conn(conn, created_by_user_id, "CREATE_TICKET", f"Ticket ID {ticket_id} created for Customer {customer_id}")
        
    conn.close()
    return ticket_id

def update_ticket(ticket_id, status=None, assigned_staff_id=None, resolution=None, user_id=None):
    """Changes the status of a request (like moving it from 'Open' to 'Closed') and records any final notes."""
    conn = get_db_connection()
    
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
    
    # We automatically record the time a ticket is closed.
    if status == "Closed":
        fields.append("closed_at = ?")
        values.append(datetime.datetime.now().isoformat())
    elif status and status != "Closed":
        fields.append("closed_at = ?")
        values.append(None)
        
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

def delete_ticket(ticket_id, user_id=None):
    """Permanently removes a request for help from our records."""
    conn = get_db_connection()
    if user_id:
        log_action_conn(conn, user_id, "DELETE_TICKET", f"Deleted Ticket ID {ticket_id}")
    conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()

def get_tickets(status_filter=None, staff_filter=None, category_filter=None):
    """Shows a list of requests for help, with the option to filter by status, assigned staff, or category."""
    conn = get_db_connection()
    query = "SELECT t.*, c.name as customer_name, c.is_vulnerable FROM tickets t JOIN customers c ON t.customer_id = c.id"
    params = []
    conditions = []
    
    if status_filter and status_filter != "All":
        conditions.append("t.status = ?")
        params.append(status_filter)
    if staff_filter:
        conditions.append("t.assigned_staff_id = ?")
        params.append(staff_filter)
    if category_filter and category_filter != "All":
        conditions.append("t.category = ?")
        params.append(category_filter)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_tickets(query):
    """Finds requests for help by looking for keywords in the description or the customer's name."""
    conn = get_db_connection()
    q = f"%{query}%"
    sql = """
        SELECT t.*, c.name as customer_name, c.is_vulnerable 
        FROM tickets t 
        JOIN customers c ON t.customer_id = c.id 
        WHERE t.description LIKE ? OR c.name LIKE ?
    """
    rows = conn.execute(sql, (q, q)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- Functions for managing Appointments ---

def check_clash(staff_id, start_time_str, duration_minutes):
    """Looks through the calendar to make sure a staff member isn't being booked for two different meetings at the same time."""
    new_start = datetime.datetime.fromisoformat(start_time_str)
    new_end = new_start + datetime.timedelta(minutes=duration_minutes)
    
    conn = get_db_connection()
    appointments = conn.execute("SELECT start_time, duration_minutes FROM appointments WHERE staff_id = ?", (staff_id,)).fetchall()
    conn.close()
    
    for appt in appointments:
        exist_start = datetime.datetime.fromisoformat(appt['start_time'])
        exist_end = exist_start + datetime.timedelta(minutes=appt['duration_minutes'])
        
        # We check if the new meeting starts before an old one ends, and ends after an old one starts.
        if new_start < exist_end and new_end > exist_start:
            return True # A scheduling conflict was found.
            
    return False

def create_appointment(customer_id, staff_id, start_time, duration_minutes, reason, created_by_user_id=None):
    """Books a new meeting between a customer and a staff member after making sure there's no scheduling conflict."""
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

def delete_appointment(appt_id, user_id=None):
    """Cancels a meeting and removes it from the calendar."""
    conn = get_db_connection()
    if user_id:
        log_action_conn(conn, user_id, "DELETE_APPT", f"Cancelled Appointment ID {appt_id}")
    conn.execute("DELETE FROM appointments WHERE id = ?", (appt_id,))
    conn.commit()
    conn.close()

def get_appointments_by_staff(staff_id):
    """Shows a list of all meetings a specific staff member has scheduled, ordered by the time they start."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT a.*, c.name as customer_name FROM appointments a JOIN customers c ON a.customer_id = c.id WHERE staff_id = ? ORDER BY start_time",
        (staff_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- Functions for tracking system history (Auditing) ---

def log_action(user_id, action, details):
    """Keeps a permanent record of who did what and when, ensuring we can always see the history of changes in the system."""
    conn = get_db_connection()
    log_action_conn(conn, user_id, action, details)
    conn.close()

def log_action_conn(conn, user_id, action, details):
    """Helper to record a change while the system is already working on another task."""
    timestamp = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT INTO audit_logs (user_id, action, timestamp, details) VALUES (?, ?, ?, ?)",
        (user_id, action, timestamp, details)
    )
    conn.commit()

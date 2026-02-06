from queuesmart.database import (
    add_customer, search_customers, 
    create_ticket, get_tickets, update_ticket, search_tickets,
    create_appointment, get_appointments_by_staff,
    get_db_connection, add_user
)
from queuesmart.priority import sort_tickets_by_priority
from queuesmart.cli.utils import print_header, print_table, get_valid_input
import datetime

# --- Customer Actions ---

def register_customer_flow():
    print_header("REGISTER NEW CUSTOMER")
    
    name = get_valid_input("Full Name: ")
    phone = get_valid_input("Phone Number: ", allow_empty=True)
    email = get_valid_input("Email Address: ", allow_empty=True)
    
    contact_opts = ["Phone", "Email", "Post"]
    pref_contact = get_valid_input("Preferred Contact (Phone/Email/Post): ", valid_options=contact_opts)
    
    is_vuln_input = get_valid_input("Is Vulnerable? (y/n): ", valid_options=["y", "n"])
    is_vulnerable = (is_vuln_input == 'y')
    
    try:
        cust_id = add_customer(name, phone, email, pref_contact, is_vulnerable)
        print(f"\nCustomer registered successfully! ID: {cust_id}")
    except Exception as e:
        print(f"\nError registering customer: {e}")
    
    input("\nPress Enter to continue...")

def search_customer_flow():
    print_header("SEARCH CUSTOMERS")
    
    query = get_valid_input("Enter name, phone, or email to search: ")
    results = search_customers(query)
    
    headers = ["ID", "Name", "Phone", "Email", "Vulnerable"]
    rows = []
    for r in results:
        rows.append([
            r['id'], 
            r['name'], 
            r['phone'], 
            r['email'], 
            "Yes" if r['is_vulnerable'] else "No"
        ])
    
    print_table(headers, rows)
    input("\nPress Enter to continue...")

# --- Ticket Actions ---

def create_ticket_flow(current_user):
    print_header("CREATE NEW TICKET")
    
    # First, find the customer
    print("Step 1: Link Customer")
    cust_id = get_valid_input("Enter Customer ID (or 's' to search): ")
    
    if cust_id.lower() == 's':
        search_customer_flow()
        cust_id = get_valid_input("Enter Customer ID: ", input_type=int)
    else:
        try:
            cust_id = int(cust_id)
        except ValueError:
            print("Invalid ID.")
            return

    # Categories
    cats = ["Housing", "Benefits", "Digital Support", "Wellbeing", "Other"]
    print("\nCategories: " + ", ".join(cats))
    category = get_valid_input("Select Category: ", valid_options=cats)
    
    description = get_valid_input("Description: ")
    
    # Urgency
    urgencies = ["Low", "Medium", "High", "Critical"]
    print("\nUrgency Levels: " + ", ".join(urgencies))
    urgency = get_valid_input("Select Urgency: ", valid_options=urgencies)
    
    try:
        t_id = create_ticket(cust_id, category, description, urgency, created_by_user_id=current_user['id'])
        print(f"\nTicket #{t_id} created successfully!")
    except Exception as e:
        print(f"\nError creating ticket: {e}")
        
    input("\nPress Enter to continue...")

def view_tickets_flow():
    print_header("TICKET DASHBOARD")
    
    tickets = get_tickets(status_filter="Open") # Default to Open? Or show all? Let's show all non-closed by default?
    # Actually requirement says "View Ticket List", let's get all then filter/sort
    
    # Let's get ALL tickets for now to be safe, or just open ones? 
    # Usually a dashboard shows active work. Let's show Open/In Progress/Waiting.
    # The get_tickets function filters by exact status. 
    # Let's fetch all providing no filter, then sort.
    
    all_tickets = get_tickets()
    active_tickets = [t for t in all_tickets if t['status'] != 'Closed']
    
    # Apply Priority Scoring
    sorted_tickets = sort_tickets_by_priority(active_tickets)
    
    headers = ["ID", "Score", "Urgency", "Category", "Customer", "Status", "Assigned"]
    rows = []
    for t in sorted_tickets:
        rows.append([
            t['id'],
            t['priority_score'],
            t['urgency'],
            t['category'],
            t['customer_name'],
            t['status'],
            t['assigned_staff_id'] if t['assigned_staff_id'] else "Unassigned"
        ])
        
    print_table(headers, rows)
    input("\nPress Enter to continue...")

def search_ticket_flow():
    print_header("SEARCH TICKETS")
    query = get_valid_input("Enter search term (Customer Name or Description): ")
    results = search_tickets(query)
    
    if not results:
        print("No tickets found.")
        return

    headers = ["ID", "Customer", "Urgency", "Status", "Description"]
    rows = []
    for t in results:
        desc = t['description']
        if len(desc) > 30:
            desc = desc[:27] + "..."
        rows.append([
            t['id'],
            t['customer_name'],
            t['urgency'],
            t['status'],
            desc
        ])
    print_table(headers, rows)

def update_ticket_flow(current_user):
    print_header("UPDATE TICKET")
    
    while True:
        t_input = get_valid_input("Enter Ticket ID to update (or 's' to search): ")
        if t_input.lower() == 's':
            search_ticket_flow()
            continue
        try:
            t_id = int(t_input)
            break
        except ValueError:
            print("Invalid input. Please enter a number or 's'.")
    
    print("\nWhat would you like to update?")
    print("1. Status")
    print("2. Assign Staff")
    print("3. Close Ticket (Resolution)")
    
    choice = get_valid_input("Choose option: ", valid_options=["1", "2", "3"])
    
    updates = {}
    
    if choice == "1":
        statuses = ["Open", "In Progress", "Waiting"]
        new_status = get_valid_input("New Status: ", valid_options=statuses)
        updates['status'] = new_status
        
    elif choice == "2":
        staff_id = get_valid_input("Enter Staff ID: ", input_type=int)
        updates['assigned_staff_id'] = staff_id
        
    elif choice == "3":
        updates['status'] = "Closed"
        resolutions = ["Resolved", "Referred", "No Contact", "Duplicate"]
        updates['resolution'] = get_valid_input("Resolution Outcome: ", valid_options=resolutions)
        
    if updates:
        success = update_ticket(t_id, **updates, user_id=current_user['id'])
        if success:
            print("\nTicket updated.")
        else:
            print("\nUpdate failed (Ticket ID might be wrong).")
    
    input("\nPress Enter to continue...")


# --- Appointment Actions ---

def view_schedule_flow():
    print_header("VIEW SCHEDULE")
    
    # For simplicity, ask which staff member to view
    staff_id = get_valid_input("Enter Staff ID to view schedule: ", input_type=int)
    
    appts = get_appointments_by_staff(staff_id)
    
    headers = ["ID", "Time", "Duration", "Customer", "Reason"]
    rows = []
    for a in appts:
        rows.append([
            a['id'],
            a['start_time'],
            f"{a['duration_minutes']} min",
            a['customer_name'],
            a['reason']
        ])
        
    print_table(headers, rows)
    input("\nPress Enter to continue...")

def book_appointment_flow(current_user):
    print_header("BOOK APPOINTMENT")
    
    cust_id = get_valid_input("Customer ID: ", input_type=int)
    staff_id = get_valid_input("Staff ID: ", input_type=int)
    
    date_str = get_valid_input("Date (YYYY-MM-DD): ")
    time_str = get_valid_input("Time (HH:MM): ")
    
    # Combine to ISO format
    try:
        dt_str = f"{date_str}T{time_str}:00"
        # Validate format roughly
        datetime.datetime.fromisoformat(dt_str)
    except ValueError:
        print("Invalid date/time format.")
        return

    duration = get_valid_input("Duration (minutes): ", input_type=int)
    reason = get_valid_input("Reason: ")
    
    try:
        a_id = create_appointment(cust_id, staff_id, dt_str, duration, reason, created_by_user_id=current_user['id'])
        print(f"\nAppointment #{a_id} booked successfully!")
    except ValueError as e:
        print(f"\nBooking Failed: {e}") # Likely clash
    except Exception as e:
        print(f"\nError: {e}")
        
    input("\nPress Enter to continue...")

# --- User Actions ---

def register_user_flow():
    print_header("REGISTER NEW USER")
    
    username = get_valid_input("Username: ")
    password = get_valid_input("Password: ")
    
    print("\nRoles: Staff, Manager")
    role = get_valid_input("Role: ", valid_options=["Staff", "Manager"])
    
    try:
        success = add_user(username, password, role)
        if success:
            print(f"\nUser '{username}' created successfully!")
        else:
            print(f"\nError: Username '{username}' already exists.")
    except Exception as e:
        print(f"\nError creating user: {e}")
        
    input("\nPress Enter to continue...")

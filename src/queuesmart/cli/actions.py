from queuesmart.database import (
    add_customer, search_customers, 
    create_ticket, get_tickets, update_ticket, search_tickets,
    create_appointment, get_appointments_by_staff,
    get_db_connection, add_user
)
from queuesmart.priority import sort_tickets_by_priority
from queuesmart.cli.utils import print_header, print_table, get_valid_input
import datetime

# --- Functions for managing Customer actions ---

def register_customer_flow():
    """Guides the user through the process of adding a new customer's name, contact details, and status."""
    print_header("REGISTER NEW CUSTOMER")
    
    # We collect the customer's basic information.
    name = get_valid_input("Full Name: ")
    phone = get_valid_input("Phone Number: ", allow_empty=True)
    email = get_valid_input("Email Address: ", allow_empty=True)
    
    # We ask how they prefer to be contacted.
    contact_opts = ["Phone", "Email", "Post"]
    pref_contact = get_valid_input("Preferred Contact (Phone/Email/Post): ", valid_options=contact_opts)
    
    # We check if the customer needs extra support (is vulnerable).
    is_vuln_input = get_valid_input("Is Vulnerable? (y/n): ", valid_options=["y", "n"])
    is_vulnerable = (is_vuln_input == 'y')
    
    try:
        # We save the new customer in our digital filing cabinet.
        cust_id = add_customer(name, phone, email, pref_contact, is_vulnerable)
        print(f"\nCustomer registered successfully! ID: {cust_id}")
    except Exception as e:
        print(f"\nError registering customer: {e}")
    
    input("\nPress Enter to continue...")

def search_customer_flow():
    """Asks the user for a search term and displays a list of matching customers from our records."""
    print_header("SEARCH CUSTOMERS")
    
    query = get_valid_input("Enter name, phone, or email to search: ")
    # We ask the database to find any customers matching what was typed.
    results = search_customers(query)
    
    # We display the findings in a neat table.
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

# --- Functions for managing Help Requests (Tickets) ---

def create_ticket_flow(current_user):
    """Handles starting a new request for help by first identifying the customer and then collecting the issue details."""
    print_header("CREATE NEW TICKET")
    
    # Step 1: We link the request to a specific customer.
    print("Step 1: Link Customer")
    cust_id = get_valid_input("Enter Customer ID (or 's' to search): ")
    
    if cust_id.lower() == 's':
        # If the user doesn't know the ID, they can search for the customer first.
        search_customer_flow()
        cust_id = get_valid_input("Enter Customer ID: ", input_type=int)
    else:
        try:
            cust_id = int(cust_id)
        except ValueError:
            print("Invalid ID.")
            return

    # Step 2: We collect details about the request.
    cats = ["Housing", "Benefits", "Digital Support", "Wellbeing", "Other"]
    print("\nCategories: " + ", ".join(cats))
    category = get_valid_input("Select Category: ", valid_options=cats)
    
    description = get_valid_input("Description: ")
    
    urgencies = ["Low", "Medium", "High", "Critical"]
    print("\nUrgency Levels: " + ", ".join(urgencies))
    urgency = get_valid_input("Select Urgency: ", valid_options=urgencies)
    
    try:
        # We save the new ticket in our records.
        t_id = create_ticket(cust_id, category, description, urgency, created_by_user_id=current_user['id'])
        print(f"\nTicket #{t_id} created successfully!")
    except Exception as e:
        print(f"\nError creating ticket: {e}")
        
    input("\nPress Enter to continue...")

def view_tickets_flow():
    """Displays a dashboard of all active help requests, sorted so the most urgent ones are easy to see."""
    print_header("TICKET DASHBOARD")
    
    # We fetch all the tickets that are currently being worked on.
    all_tickets = get_tickets()
    active_tickets = [t for t in all_tickets if t['status'] != 'Closed']
    
    # We sort the tickets based on our priority rules.
    sorted_tickets = sort_tickets_by_priority(active_tickets)
    
    # We display the active tickets in a table.
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
    """Finds specific help requests based on keywords and displays them in a table."""
    print_header("SEARCH TICKETS")
    query = get_valid_input("Enter search term (Customer Name or Description): ")
    # We ask the database for tickets matching the search term.
    results = search_tickets(query)
    
    if not results:
        print("No tickets found.")
        return

    # We display the search results in a table.
    headers = ["ID", "Customer", "Urgency", "Status", "Description"]
    rows = []
    for t in results:
        desc = t['description']
        # If the description is too long, we shorten it for the table.
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
    """Allows staff to change the status of a request, assign it to someone else, or close it when finished."""
    print_header("UPDATE TICKET")
    
    while True:
        # We identify which ticket needs updating.
        t_input = get_valid_input("Enter Ticket ID to update (or 's' to search): ")
        if t_input.lower() == 's':
            search_ticket_flow()
            continue
        try:
            t_id = int(t_input)
            break
        except ValueError:
            print("Invalid input. Please enter a number or 's'.")
    
    # We ask what specific part of the ticket should be changed.
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
        # Closing a ticket requires a final status and a brief explanation of the outcome.
        updates['status'] = "Closed"
        resolutions = ["Resolved", "Referred", "No Contact", "Duplicate"]
        updates['resolution'] = get_valid_input("Resolution Outcome: ", valid_options=resolutions)
        
    if updates:
        # We save the changes in the digital filing cabinet.
        success = update_ticket(t_id, **updates, user_id=current_user['id'])
        if success:
            print("\nTicket updated.")
        else:
            print("\nUpdate failed (Ticket ID might be wrong).")
    
    input("\nPress Enter to continue...")


# --- Functions for managing Appointments ---

def view_schedule_flow():
    """Shows all meetings scheduled for a specific staff member."""
    print_header("VIEW SCHEDULE")
    
    # We identify whose schedule we want to look at.
    staff_id = get_valid_input("Enter Staff ID to view schedule: ", input_type=int)
    
    # We fetch their appointments from the calendar.
    appts = get_appointments_by_staff(staff_id)
    
    # We display their schedule in a table.
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
    """Guides the user through scheduling a new meeting, ensuring there are no calendar conflicts."""
    print_header("BOOK APPOINTMENT")
    
    # We identify the customer and the staff member involved.
    cust_id = get_valid_input("Customer ID: ", input_type=int)
    staff_id = get_valid_input("Staff ID: ", input_type=int)
    
    # We collect the date and time for the meeting.
    date_str = get_valid_input("Date (Year-Month-Day): ")
    time_str = get_valid_input("Time (Hour:Minute): ")
    
    try:
        # We combine the date and time into a single format the system understands.
        dt_str = f"{date_str}T{time_str}:00"
        datetime.datetime.fromisoformat(dt_str)
    except ValueError:
        print("Invalid date/time format.")
        return

    # We collect the duration and the reason for the meeting.
    duration = get_valid_input("Duration (minutes): ", input_type=int)
    reason = get_valid_input("Reason: ")
    
    try:
        # We try to book the appointment, but the system will stop us if there is a scheduling clash.
        a_id = create_appointment(cust_id, staff_id, dt_str, duration, reason, created_by_user_id=current_user['id'])
        print(f"\nAppointment #{a_id} booked successfully!")
    except ValueError as e:
        print(f"\nBooking Failed: {e}") # This usually means the staff member is already busy.
    except Exception as e:
        print(f"\nError: {e}")
        
    input("\nPress Enter to continue...")

# --- Functions for managing User accounts ---

def register_user_flow():
    """Allows a manager to create a new staff account with a name, password, and job role."""
    print_header("REGISTER NEW USER")
    
    # We collect the new account details.
    username = get_valid_input("Username: ")
    password = get_valid_input("Password: ")
    
    print("\nRoles: Staff, Manager")
    role = get_valid_input("Role: ", valid_options=["Staff", "Manager"])
    
    try:
        # We save the new staff member in our records.
        success = add_user(username, password, role)
        if success:
            print(f"\nUser '{username}' created successfully!")
        else:
            print(f"\nError: Username '{username}' already exists.")
    except Exception as e:
        print(f"\nError creating user: {e}")
        
    input("\nPress Enter to continue...")

from queuesmart.cli.utils import clear_screen, print_header, get_valid_input
from queuesmart.cli.actions import (
    register_customer_flow, search_customer_flow,
    create_ticket_flow, view_tickets_flow, update_ticket_flow,
    book_appointment_flow, view_schedule_flow, register_user_flow
)
from queuesmart.cli.reporting_cli import reporting_menu

def customer_menu():
    """Shows a list of options for managing customers, like adding a new one or searching for an existing one."""
    while True:
        clear_screen()
        print_header("CUSTOMER MANAGEMENT")
        print("1. Register New Customer")
        print("2. Search Customers")
        print("3. Back")
        
        # We wait for the user to pick an option from the list.
        choice = get_valid_input("\nSelect Option: ", valid_options=["1", "2", "3"])
        
        if choice == "1":
            register_customer_flow()
        elif choice == "2":
            search_customer_flow()
        elif choice == "3":
            # This returns the user to the main menu.
            break

def ticket_menu(user):
    """Shows a list of options for managing help requests (tickets), including creating them and updating their status."""
    while True:
        clear_screen()
        print_header("TICKET MANAGEMENT")
        print("1. Create New Ticket")
        print("2. View Ticket Dashboard (Priority Sorted)")
        print("3. Update Ticket (Status/Assign/Close)")
        print("4. Back")
        
        choice = get_valid_input("\nSelect Option: ", valid_options=["1", "2", "3", "4"])
        
        if choice == "1":
            create_ticket_flow(user)
        elif choice == "2":
            view_tickets_flow()
        elif choice == "3":
            update_ticket_flow(user)
        elif choice == "4":
            break

def appointment_menu(user):
    """Shows options for booking meetings or viewing the team's schedule."""
    while True:
        clear_screen()
        print_header("APPOINTMENT MANAGEMENT")
        print("1. Book Appointment")
        print("2. View Staff Schedule")
        print("3. Back")
        
        choice = get_valid_input("\nSelect Option: ", valid_options=["1", "2", "3"])
        
        if choice == "1":
            book_appointment_flow(user)
        elif choice == "2":
            view_schedule_flow()
        elif choice == "3":
            break

def main_menu(user):
    """The primary navigation list that appears after login, showing the different sections of the system."""
    while True:
        clear_screen()
        # We show the main options and adjust them based on whether the person is a Manager or a Staff member.
        print_header(f"MAIN MENU - {user['role'].upper()}")
        
        print("1. Customers")
        print("2. Tickets")
        print("3. Appointments")
        
        if user['role'] == "Manager":
            # Managers get extra options for reporting and creating new user accounts.
            print("4. Reporting")
            print("5. Register New User")
            print("6. Logout")
            valid_opts = ["1", "2", "3", "4", "5", "6"]
        else:
            print("4. Logout")
            valid_opts = ["1", "2", "3", "4"]
            
        choice = get_valid_input("\nSelect Option: ", valid_options=valid_opts)
        
        if choice == "1":
            customer_menu()
        elif choice == "2":
            ticket_menu(user)
        elif choice == "3":
            appointment_menu(user)
        elif choice == "4":
            if user['role'] == "Manager":
                reporting_menu()
            else:
                return # Logging out.
        elif choice == "5" and user['role'] == "Manager":
            register_user_flow()
        elif choice == "6" and user['role'] == "Manager":
            return # Logging out.

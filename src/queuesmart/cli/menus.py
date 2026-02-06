from queuesmart.cli.utils import clear_screen, print_header, get_valid_input
from queuesmart.cli.actions import (
    register_customer_flow, search_customer_flow,
    create_ticket_flow, view_tickets_flow, update_ticket_flow,
    book_appointment_flow, view_schedule_flow, register_user_flow
)
from queuesmart.cli.reporting_cli import reporting_menu

def customer_menu():
    while True:
        clear_screen()
        print_header("CUSTOMER MANAGEMENT")
        print("1. Register New Customer")
        print("2. Search Customers")
        print("3. Back")
        
        choice = get_valid_input("\nSelect Option: ", valid_options=["1", "2", "3"])
        
        if choice == "1":
            register_customer_flow()
        elif choice == "2":
            search_customer_flow()
        elif choice == "3":
            break

def ticket_menu(user):
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
    while True:
        clear_screen()
        print_header(f"MAIN MENU - {user['role'].upper()}")
        
        print("1. Customers")
        print("2. Tickets")
        print("3. Appointments")
        print("4. Reporting")
        
        if user['role'] == "Manager":
            print("5. Register New User")
            print("6. Logout")
        else:
            print("5. Logout")
        
        valid_opts = ["1", "2", "3", "4", "5"]
        if user['role'] == "Manager":
            valid_opts.append("6")
            
        choice = get_valid_input("\nSelect Option: ", valid_options=valid_opts)
        
        if choice == "1":
            customer_menu()
        elif choice == "2":
            ticket_menu(user)
        elif choice == "3":
            appointment_menu(user)
        elif choice == "4":
            reporting_menu()
        elif choice == "5":
            if user['role'] == "Manager":
                register_user_flow()
            else:
                return
        elif choice == "6" and user['role'] == "Manager":
            return

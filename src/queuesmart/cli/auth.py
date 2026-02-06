import getpass
from queuesmart.database import authenticate_user
from queuesmart.cli.utils import clear_screen, print_header

def login_loop():
    # Handles the login process
    # Returns the user dictionary if successful, or None if user quits
    
    while True:
        clear_screen()
        print_header("QUEUE SMART LOGIN")
        
        print("Please log in to continue.\n")
        
        username = input("Username (or 'q' to quit): ").strip()
        if username.lower() == 'q':
            return None
            
        password = getpass.getpass("Password: ")
        
        user = authenticate_user(username, password)
        
        if user:
            print(f"\nWelcome back, {user['username']} ({user['role']})!")
            input("Press Enter to continue...")
            return user
        else:
            print("\nInvalid username or password.")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return None

import getpass
from queuesmart.database import authenticate_user
from queuesmart.cli.utils import clear_screen, print_header

def login_loop():
    """
    Keeps asking for a username and password until the user either logs in successfully or decides to quit.
    """
    while True:
        # We start by cleaning the screen and showing a login title.
        clear_screen()
        print_header("QUEUE SMART LOGIN")
        
        print("Please log in to continue.\n")
        
        # We ask the staff member for their name.
        username = input("Username (or 'q' to quit): ").strip()
        if username.lower() == 'q':
            # If they type 'q', we stop and return nothing.
            return None
            
        # We ask for their secret password (the characters won't appear on the screen as they type).
        password = getpass.getpass("Password: ")
        
        # We check the filing cabinet to see if the name and password are correct.
        user = authenticate_user(username, password)
        
        if user:
            # If they match, we welcome them and move forward.
            print(f"\nWelcome back, {user['username']} ({user['role']})!")
            input("Press Enter to continue...")
            return user
        else:
            # If they don't match, we show a message and ask if they want to try again.
            print("\nInvalid username or password.")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return None

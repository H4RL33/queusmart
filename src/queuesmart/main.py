import sys
import os

# This makes sure the program can find all its necessary components when it starts up.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from queuesmart.database import init_db, add_user, get_db_connection, seed_default_user
from queuesmart.cli.auth import login_loop
from queuesmart.cli.menus import main_menu

def main():
    """
    This is the starting point of the entire application. 
    It prepares the digital filing cabinet, makes sure an 'admin' user exists, and then starts the login screen so staff can begin their work.
    """
    try:
        # 1. We set up the digital folders and tables where all information will be saved.
        init_db()
        
        # 2. We make sure at least one 'admin' account exists so the system can be used immediately.
        seed_default_user()
        
        while True:
            # 3. We show the login screen and wait for a staff member to enter their name and password.
            user = login_loop()
            
            if not user:
                # If they decide to exit instead of logging in, we say goodbye and close the program.
                print("\nGoodbye!")
                break
                
            # 4. Once logged in, we show the main menu where they can manage customers, tickets, and meetings.
            main_menu(user)
            
    except KeyboardInterrupt:
        # This happens if the user manually stops the program (e.g., by pressing Ctrl+C).
        print("\n\nExiting application. Goodbye!")
    except Exception as e:
        # If something unexpected goes wrong, we show a message explaining the error.
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    # This line actually tells the computer to run the 'main' instructions above.
    main()

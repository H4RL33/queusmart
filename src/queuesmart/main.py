import sys
import os

# Ensure src is in path if running directly
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from queuesmart.database import init_db, add_user, get_db_connection, seed_default_user
from queuesmart.cli.auth import login_loop
from queuesmart.cli.menus import main_menu

def main():
    try:
        # 1. Initialize Database
        init_db()
        
        # 2. Seed Default Data (Optional but helpful)
        seed_default_user()
        
        while True:
            # 3. Authentication
            user = login_loop()
            
            if not user:
                print("\nGoodbye!")
                break
                
            # 4. Main Application Loop
            main_menu(user)
            
    except KeyboardInterrupt:
        print("\n\nExiting application. Goodbye!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
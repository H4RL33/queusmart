import tkinter as tk
import sys
import os

# This ensures the program can find its necessary components when started from the graphical interface folder.
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from queuesmart.database import init_db, seed_default_user
from queuesmart.gui.utils import center_window, clear_frame
from queuesmart.gui.auth import LoginFrame
from queuesmart.gui.dashboard import DashboardFrame

class QueueSmartApp(tk.Tk):
    """
    This class represents the main visual window of the application. 
    It acts as the 'container' for everything the user sees and handles moving between different screens, like switching from the login page to the dashboard.
    """
    def __init__(self):
        super().__init__()
        self.title("QueueSmart System")
        # We make sure the window appears in the middle of the computer screen.
        center_window(self)
        
        self.current_user = None
        # We prepare the system folders and default accounts.
        self.init_system()
        
        # We start by showing the login screen.
        self.show_login()

    def init_system(self):
        """Prepares the system by setting up the database and default accounts before the window opens."""
        try:
            init_db()
            seed_default_user()
        except Exception as e:
            # If there is a problem starting up, we print an error message.
            print(f"Startup Error: {e}")

    def show_login(self):
        """Clears the window and displays the login screen for staff."""
        self.current_user = None
        self.show_frame(LoginFrame, self.on_login_success)

    def on_login_success(self, user):
        """Remembers who has logged in and then takes them to the main dashboard."""
        self.current_user = user
        self.show_dashboard()

    def show_dashboard(self):
        """Displays the main dashboard where staff can see their options."""
        self.show_frame(DashboardFrame, self.current_user, self.show_login)

    def show_frame(self, frame_class, *args, **kwargs):
        """
        A general helper that cleans the current screen and sets up a new one.
        For example, it is used when switching from a list of customers to an 'Add Customer' form.
        """
        # We stop the 'Enter' key from doing anything before we switch screens to avoid mistakes.
        self.unbind("<Return>")
        # We remove everything currently visible in the window.
        clear_frame(self)
        # We create and show the new screen.
        frame = frame_class(self, *args, **kwargs)
        return frame

if __name__ == "__main__":
    # This line starts the visual application and keeps it running until the user closes the window.
    app = QueueSmartApp()
    app.mainloop()

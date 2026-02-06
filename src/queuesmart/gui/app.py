import tkinter as tk
import sys
import os

# Ensure src is in path if running directly
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from queuesmart.database import init_db, seed_default_user
from queuesmart.gui.utils import center_window, clear_frame
from queuesmart.gui.auth import LoginFrame
from queuesmart.gui.dashboard import DashboardFrame

class QueueSmartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QueueSmart System")
        center_window(self)
        
        self.current_user = None
        self.init_system()
        
        self.show_login()

    def init_system(self):
        """Initialize database and default values."""
        try:
            init_db()
            seed_default_user()
        except Exception as e:
            print(f"Startup Error: {e}")

    def show_login(self):
        """Displays the login screen."""
        self.current_user = None
        clear_frame(self)
        self.login_frame = LoginFrame(self, self.on_login_success)

    def on_login_success(self, user):
        """Callback for successful login."""
        self.current_user = user
        clear_frame(self)
        self.show_dashboard()

    def show_dashboard(self):
        """Displays the main dashboard."""
        self.dashboard_frame = DashboardFrame(self, self.current_user, self.show_login)

    def show_frame(self, frame_class, *args, **kwargs):
        """Helper to switch frames genericly (planned for future use)."""
        clear_frame(self)
        frame = frame_class(self, *args, **kwargs)
        return frame

if __name__ == "__main__":
    app = QueueSmartApp()
    app.mainloop()

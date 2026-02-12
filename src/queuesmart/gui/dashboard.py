import tkinter as tk
from tkinter import messagebox
from queuesmart.gui.utils import clear_frame

class DashboardFrame(tk.Frame):
    """
    This is the main control panel where staff can see their options and choose what they want to do next.
    """
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        
        # We show a dark bar at the top with the user's role and a logout button.
        header = tk.Frame(self, bg="#333", height=60)
        header.pack(fill="x")
        
        tk.Label(header, text=f"QueueSmart Dashboard - {user['role']}", fg="white", bg="#333", font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=10)
        
        # Accessibility Toggle
        self.large_text = False
        tk.Button(header, text="Toggle Large Text", command=self.toggle_accessibility, bg="#607D8B", fg="white").pack(side="right", padx=10, pady=10)
        
        tk.Button(header, text="Logout", command=self.logout, bg="red", fg="white").pack(side="right", padx=20, pady=10)
        
        # We display a welcoming message with the staff member's name.
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text=f"Welcome, {user['username']}!", font=("Helvetica", 18)).pack(pady=(0, 20))
        
        # We create a grid where all the main task buttons will be placed.
        actions_frame = tk.Frame(content)
        actions_frame.pack(fill="both", expand=True)
        
        # These are the standard buttons available to all staff.
        buttons = [
            ("Manage Customers", self.go_customers),
            ("Manage Tickets", self.go_tickets),
            ("View Appointments", self.go_appointments)
        ]
        
        # We only add the 'Reports' and 'User Management' buttons if the person logged in is a Manager.
        if self.user['role'] == 'Manager':
            buttons.append(("Management Reports", self.go_reports))
            buttons.append(("Manage Users", self.go_users))
        
        # We place each button in the grid, three to a row.
        for i, (text, command) in enumerate(buttons):
            tk.Button(actions_frame, text=text, command=command, width=20, height=3, font=("Helvetica", 12)).grid(row=i // 3, column=i % 3, padx=10, pady=10)

    def logout(self):
        """Logs the current user out of the system and returns them to the login screen."""
        self.on_logout()
        
    def go_customers(self):
        """Takes the user to the screen where they can find, add, or edit customer details."""
        from queuesmart.gui.customers import CustomerListFrame
        self.master.show_frame(CustomerListFrame, self.user)
        
    def go_tickets(self):
        """Takes the user to the screen where they can manage requests for help (tickets)."""
        from queuesmart.gui.tickets import TicketListFrame
        self.master.show_frame(TicketListFrame, self.user)
        
    def go_appointments(self):
        """Takes the user to the screen where they can see and book meetings."""
        from queuesmart.gui.appointments import AppointmentScheduleFrame
        self.master.show_frame(AppointmentScheduleFrame, self.user)

    def go_reports(self):
        """Takes a manager to the screen where they can view and export performance reports."""
        from queuesmart.gui.reporting import ReportingFrame
        self.master.show_frame(ReportingFrame, self.user)

    def go_users(self):
        """Takes a manager to the screen where they can add, edit, or remove staff accounts."""
        from queuesmart.gui.users import UserManagementFrame
        self.master.show_frame(UserManagementFrame, self.user)

    def toggle_accessibility(self):
        """Switches between normal and large text sizes to help users with visual impairments."""
        from tkinter import font
        self.large_text = not self.large_text
        
        default_font = font.nametofont("TkDefaultFont")
        text_font = font.nametofont("TkTextFont")
        menu_font = font.nametofont("TkMenuFont")
        
        if self.large_text:
            size = 14
        else:
            size = 10 # Standard default
            
        default_font.configure(size=size)
        text_font.configure(size=size)
        menu_font.configure(size=size)
        
        messagebox.showinfo("Accessibility", f"Text size set to {'Large' if self.large_text else 'Standard'}.")

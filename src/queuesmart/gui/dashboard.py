import tkinter as tk
from queuesmart.gui.utils import clear_frame

class DashboardFrame(tk.Frame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(self, bg="#333", height=60)
        header.pack(fill="x")
        
        tk.Label(header, text=f"QueueSmart Dashboard - {user['role']}", fg="white", bg="#333", font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=10)
        tk.Button(header, text="Logout", command=self.logout, bg="red", fg="white").pack(side="right", padx=20, pady=10)
        
        # Main Content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text=f"Welcome, {user['username']}!", font=("Helvetica", 18)).pack(pady=(0, 20))
        
        # Grid of Actions
        actions_frame = tk.Frame(content)
        actions_frame.pack(fill="both", expand=True)
        
        # Define buttons
        buttons = [
            ("Manage Customers", self.go_customers),
            ("Manage Tickets", self.go_tickets),
            ("View Appointments", self.go_appointments)
        ]
        
        for i, (text, command) in enumerate(buttons):
            tk.Button(actions_frame, text=text, command=command, width=20, height=3, font=("Helvetica", 12)).grid(row=0, column=i, padx=10, pady=10)

    def logout(self):
        self.on_logout()
        
    def go_customers(self):
        from queuesmart.gui.customers import CustomerListFrame
        self.master.show_frame(CustomerListFrame, self.user)
        
    def go_tickets(self):
        from queuesmart.gui.tickets import TicketListFrame
        self.master.show_frame(TicketListFrame, self.user)
        
    def go_appointments(self):
        from queuesmart.gui.appointments import AppointmentScheduleFrame
        self.master.show_frame(AppointmentScheduleFrame, self.user)

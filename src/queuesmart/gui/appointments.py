import tkinter as tk
from tkinter import ttk, messagebox
from queuesmart.database import get_appointments_by_staff, create_appointment, check_clash, delete_appointment
from queuesmart.gui.utils import clear_frame

class AppointmentScheduleFrame(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text=f"Schedule for {user['username']}", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Action Bar
        action_bar = tk.Frame(self)
        action_bar.pack(fill="x", padx=10, pady=10)
        
        tk.Button(action_bar, text="+ Book Appointment", command=self.go_book, bg="#4CAF50").pack(side="right")
        tk.Button(action_bar, text="Cancel Selected", command=self.delete_selected, bg="#F44336").pack(side="right", padx=5)
        
        # Treeview
        columns = ("ID", "Time", "Duration", "Customer", "Reason")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.load_data()

    def go_back(self):
        from queuesmart.gui.dashboard import DashboardFrame
        self.master.show_frame(DashboardFrame, self.user, self.master.show_login)
        
    def load_data(self):
        # Load for current user
        # Note: If manager, might want to see others. logic for that can be added later.
        appts = get_appointments_by_staff(self.user['id'])
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for a in appts:
            self.tree.insert("", "end", values=(
                a['id'], 
                a['start_time'], 
                f"{a['duration_minutes']} min", 
                a['customer_name'], 
                a['reason']
            ))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select an appointment to cancel.")
            return
            
        item = self.tree.item(selected[0])
        a_id = item['values'][0]
        
        if messagebox.askyesno("Confirm Cancellation", f"Are you sure you want to cancel appointment #{a_id}?"):
            delete_appointment(a_id)
            self.load_data()
            messagebox.showinfo("Success", "Appointment cancelled.")

    def go_book(self):
        self.master.show_frame(BookAppointmentFrame, self.user)


class BookAppointmentFrame(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Book Appointment", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        # Fields
        tk.Label(form, text="Customer ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.cust_id_entry = tk.Entry(form, width=10)
        self.cust_id_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        tk.Label(form, text="Date/Time (ISO 8601):").grid(row=1, column=0, sticky="w", pady=5)
        self.time_entry = tk.Entry(form, width=25)
        self.time_entry.insert(0, "YYYY-MM-DDTHH:MM:SS")
        self.time_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        tk.Label(form, text="Duration (min):").grid(row=2, column=0, sticky="w", pady=5)
        self.dur_entry = tk.Entry(form, width=10)
        self.dur_entry.insert(0, "30")
        self.dur_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        tk.Label(form, text="Reason:").grid(row=3, column=0, sticky="nsew", pady=5)
        self.reason_entry = tk.Text(form, width=40, height=3)
        self.reason_entry.grid(row=3, column=1, pady=5)
        
        tk.Button(form, text="Confirm Booking", command=self.save, bg="#4CAF50").grid(row=4, column=1, sticky="e", pady=20)

    def save(self):
        try:
            cust_id = int(self.cust_id_entry.get())
            duration = int(self.dur_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Check numeric fields.")
            return
            
        start_time = self.time_entry.get()
        reason = self.reason_entry.get("1.0", "end-1c")
        staff_id = self.user['id']
        
        # Clash Check
        try:
            if check_clash(staff_id, start_time, duration):
                messagebox.showerror("Clash Detected", "This staff member is already booked for that time.")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Date format error likely: {e}")
            return
        
        try:
            create_appointment(cust_id, staff_id, start_time, duration, reason, created_by_user_id=staff_id)
            messagebox.showinfo("Success", "Appointment booked!")
            self.go_back()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def go_back(self):
        self.master.show_frame(AppointmentScheduleFrame, self.user)

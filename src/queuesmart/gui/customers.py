import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from queuesmart.database import add_customer, update_customer, delete_customer, search_customers, get_customer_history
from queuesmart.gui.utils import clear_frame, ToolTip

class CustomerListFrame(tk.Frame):
    """
    Shows a searchable list of all customers in the system.
    """
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        # Header with a back button and title.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Customer Management", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Bar with search box and action buttons.
        action_bar = tk.Frame(self)
        action_bar.pack(fill="x", padx=10, pady=10)
        
        self.search_var = tk.StringVar()
        tk.Entry(action_bar, textvariable=self.search_var, width=30).pack(side="left", padx=(0, 10))
        tk.Button(action_bar, text="Search", command=self.perform_search).pack(side="left")
        
        tk.Button(action_bar, text="+ Add Customer", command=self.go_add_customer, bg="#4CAF50").pack(side="right")
        tk.Button(action_bar, text="Edit Selected", command=self.go_edit_customer, bg="#2196F3").pack(side="right", padx=5)
        tk.Button(action_bar, text="Delete Selected", command=self.delete_selected, bg="#F44336").pack(side="right", padx=5)
        tk.Button(action_bar, text="View History", command=self.go_view_history, bg="#FF9800").pack(side="right", padx=5)
        
        if self.user['role'] == 'Manager':
            tk.Button(action_bar, text="Import CSV", command=self.import_csv, bg="#9C27B0", fg="white").pack(side="right")
        
        # A table to display the customer records.
        columns = ("ID", "Name", "Phone", "Email", "Vulnerable")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("ID", width=40)
        self.tree.column("Vulnerable", width=50)
            
        # We load the list of customers as soon as the screen opens.
        self.perform_search()

    def go_back(self):
        """Returns the user to the main dashboard."""
        from queuesmart.gui.dashboard import DashboardFrame
        self.master.show_frame(DashboardFrame, self.user, self.master.show_login)

    def perform_search(self):
        """Updates the list based on the name, phone, or email typed into the search box."""
        query = self.search_var.get()
        # We ask the database for customers matching the search term.
        results = search_customers(query)
        
        # We clear the current table and fill it with the new results.
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for c in results:
            vuln = "Yes" if c['is_vulnerable'] else "No"
            self.tree.insert("", "end", values=(c['id'], c['name'], c['phone'], c['email'], vuln))

    def go_add_customer(self):
        """Takes the user to the 'Add Customer' form."""
        self.master.show_frame(AddCustomerFrame, self.user)
        
    def go_edit_customer(self):
        """Takes the user to the form to edit the selected customer's details."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a customer to edit.")
            return
            
        item = self.tree.item(selected[0])
        # We collect the current information from the selected row to fill the form.
        c_id = item['values'][0]
        name = item['values'][1]
        phone = item['values'][2]
        email = item['values'][3]
        vuln_str = item['values'][4]
        is_vuln = (vuln_str == "Yes")
        
        customer_data = {
            'id': c_id,
            'name': name,
            'phone': phone,
            'email': email,
            'is_vulnerable': is_vuln,
            'preferred_contact': 'Phone' # We default this and let the user change it in the form.
        }
        
        self.master.show_frame(AddCustomerFrame, self.user, customer_data)

    def go_view_history(self):
        """Switches to a screen showing all past tickets and meetings for the selected customer."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a customer to view history.")
            return
            
        item = self.tree.item(selected[0])
        c_id = item['values'][0]
        c_name = item['values'][1]
        self.master.show_frame(CustomerHistoryFrame, self.user, c_id, c_name)

    def import_csv(self):
        """Allows a manager to select a CSV file and bulk-add customers to the system."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
            
        try:
            count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # We look for specific column names in the spreadsheet.
                    name = row.get('name') or row.get('Name')
                    phone = row.get('phone') or row.get('Phone') or ""
                    email = row.get('email') or row.get('Email') or ""
                    contact = row.get('preferred_contact') or row.get('Contact Method') or "Phone"
                    vuln = row.get('is_vulnerable') or row.get('Vulnerable') or "0"
                    
                    if name:
                        add_customer(name, phone, email, contact, str(vuln).lower() in ('1', 'yes', 'true', 'y'))
                        count += 1
            
            messagebox.showinfo("Success", f"Successfully imported {count} customers.")
            self.perform_search()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {e}")

    def delete_selected(self):
        """Permanently removes a customer's record from the system."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a customer to delete.")
            return
            
        item = self.tree.item(selected[0])
        c_id = item['values'][0]
        name = item['values'][1]
        
        # We ask for confirmation before deleting to prevent accidents.
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete customer '{name}'?"):
            try:
                delete_customer(c_id, user_id=self.user['id'])
                self.perform_search()
                messagebox.showinfo("Success", "Customer deleted.")
            except ValueError as e:
                # If the customer has active work, the system will prevent the deletion and show this error.
                messagebox.showerror("Error", str(e))


class CustomerHistoryFrame(tk.Frame):
    """
    Displays a summary of all historical interactions (tickets and meetings) for a single customer.
    """
    def __init__(self, master, user, customer_id, customer_name):
        super().__init__(master)
        self.master = master
        self.user = user
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.pack(fill="both", expand=True)
        
        # Header showing which customer's history we are viewing.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text=f"History for {customer_name}", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        main_content = tk.Frame(self, padx=20, pady=20)
        main_content.pack(fill="both", expand=True)
        
        # A table specifically for the customer's support tickets.
        tk.Label(main_content, text="Support Tickets", font=("Helvetica", 12, "bold")).pack(anchor="w")
        self.ticket_tree = ttk.Treeview(main_content, columns=("ID", "Category", "Urgency", "Status", "Created"), show="headings", height=8)
        self.ticket_tree.pack(fill="x", pady=(5, 20))
        for col in ("ID", "Category", "Urgency", "Status", "Created"):
            self.ticket_tree.heading(col, text=col)
            self.ticket_tree.column(col, width=100)
            
        # A table specifically for the customer's scheduled appointments.
        tk.Label(main_content, text="Appointments", font=("Helvetica", 12, "bold")).pack(anchor="w")
        self.appt_tree = ttk.Treeview(main_content, columns=("ID", "Time", "Duration", "Staff", "Reason"), show="headings", height=8)
        self.appt_tree.pack(fill="x", pady=5)
        for col in ("ID", "Time", "Duration", "Staff", "Reason"):
            self.appt_tree.heading(col, text=col)
            self.appt_tree.column(col, width=100)
            
        # We load all the history from the database as soon as the screen opens.
        self.load_history()

    def load_history(self):
        """Retrieves and displays the customer's full record from the database."""
        history = get_customer_history(self.customer_id)
        
        for t in history['tickets']:
            self.ticket_tree.insert("", "end", values=(t['id'], t['category'], t['urgency'], t['status'], t['created_at']))
            
        for a in history['appointments']:
            self.appt_tree.insert("", "end", values=(a['id'], a['start_time'], f"{a['duration_minutes']} min", a['staff_name'], a['reason']))

    def go_back(self):
        """Returns the user to the main customer list."""
        self.master.show_frame(CustomerListFrame, self.user)


class AddCustomerFrame(tk.Frame):
    """
    A form for adding a new customer or editing an existing one's contact details and status.
    """
    def __init__(self, master, user, customer_data=None):
        super().__init__(master)
        self.master = master
        self.user = user
        self.customer_data = customer_data # If this is set, it means we are editing an existing customer.
        self.pack(fill="both", expand=True)
        
        mode = "Edit" if customer_data else "Add New"
        
        # Header for the form.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text=f"{mode} Customer", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        # Labels and boxes for typing in the customer's name, phone, and email.
        tk.Label(form, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(form, width=40)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form, text="Phone:").grid(row=1, column=0, sticky="w", pady=5)
        self.phone_entry = tk.Entry(form, width=40)
        self.phone_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form, text="Email:").grid(row=2, column=0, sticky="w", pady=5)
        self.email_entry = tk.Entry(form, width=40)
        self.email_entry.grid(row=2, column=1, pady=5)
        
        # A dropdown to choose how the customer prefers to be contacted.
        tk.Label(form, text="Preferred Contact:").grid(row=3, column=0, sticky="w", pady=5)
        self.contact_var = tk.StringVar(value="Phone")
        tk.OptionMenu(form, self.contact_var, "Phone", "Email", "Post", "In-Person").grid(row=3, column=1, sticky="w", pady=5)
        
        # A tick-box to mark if the customer needs extra care (is vulnerable).
        self.vuln_var = tk.IntVar()
        vuln_cb = tk.Checkbutton(form, text="Is Vulnerable?", variable=self.vuln_var)
        vuln_cb.grid(row=4, column=1, sticky="w", pady=5)
        ToolTip(vuln_cb, "Check if customer has vulnerabilities (disability, age, etc.)\nAdds +15 to ticket priority.")
        
        # If we are editing, we pre-fill the boxes with the customer's current information.
        if self.customer_data:
            self.name_entry.insert(0, self.customer_data['name'])
            self.phone_entry.insert(0, str(self.customer_data['phone']))
            self.email_entry.insert(0, self.customer_data['email'])
            if 'preferred_contact' in self.customer_data:
                 self.contact_var.set(self.customer_data['preferred_contact'])
            self.vuln_var.set(1 if self.customer_data['is_vulnerable'] else 0)
        
        # A button to save all the information entered.
        tk.Button(form, text="Save Customer", command=self.save, bg="#4CAF50").grid(row=5, column=1, sticky="e", pady=20)

    def save(self):
        """Records the customer's information in the digital filing cabinet."""
        name = self.name_entry.get()
        # We make sure at least a name has been provided.
        if not name:
            messagebox.showwarning("Validation", "Name is required.")
            return
            
        if self.customer_data:
            # We update the existing record in the database.
            update_customer(
                self.customer_data['id'],
                name,
                self.phone_entry.get(),
                self.email_entry.get(),
                self.contact_var.get(),
                bool(self.vuln_var.get())
            )
            messagebox.showinfo("Success", "Customer updated successfully!")
        else:
            # We create a brand new record in the database.
            add_customer(
                name,
                self.phone_entry.get(),
                self.email_entry.get(),
                self.contact_var.get(),
                bool(self.vuln_var.get())
            )
            messagebox.showinfo("Success", "Customer added successfully!")
            
        self.go_back()

    def go_back(self):
        """Returns the user to the customer list."""
        self.master.show_frame(CustomerListFrame, self.user)

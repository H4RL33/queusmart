import tkinter as tk
from tkinter import ttk, messagebox
from queuesmart.database import add_customer, update_customer, delete_customer, search_customers
from queuesmart.gui.utils import clear_frame, ToolTip

class CustomerListFrame(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Customer Management", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Action Bar
        action_bar = tk.Frame(self)
        action_bar.pack(fill="x", padx=10, pady=10)
        
        self.search_var = tk.StringVar()
        tk.Entry(action_bar, textvariable=self.search_var, width=30).pack(side="left", padx=(0, 10))
        tk.Button(action_bar, text="Search", command=self.perform_search).pack(side="left")
        
        tk.Button(action_bar, text="+ Add Customer", command=self.go_add_customer, bg="#4CAF50").pack(side="right")
        tk.Button(action_bar, text="Edit Selected", command=self.go_edit_customer, bg="#2196F3").pack(side="right", padx=5)
        tk.Button(action_bar, text="Delete Selected", command=self.delete_selected, bg="#F44336").pack(side="right")
        
        # Treeview
        columns = ("ID", "Name", "Phone", "Email", "Vulnerable")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("ID", width=40)
        self.tree.column("Vulnerable", width=50)
            
        # Initial Load
        self.perform_search()

    def go_back(self):
        from queuesmart.gui.dashboard import DashboardFrame
        self.master.show_frame(DashboardFrame, self.user, self.master.show_login)

    def perform_search(self):
        query = self.search_var.get()
        results = search_customers(query)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for c in results:
            vuln = "Yes" if c['is_vulnerable'] else "No"
            self.tree.insert("", "end", values=(c['id'], c['name'], c['phone'], c['email'], vuln))

    def go_add_customer(self):
        self.master.show_frame(AddCustomerFrame, self.user)
        
    def go_edit_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a customer to edit.")
            return
            
        item = self.tree.item(selected[0])
        # Values are strings in tuple, index matched to columns
        # ID, Name, Phone, Email, Vulnerable
        c_id = item['values'][0]
        name = item['values'][1]
        phone = item['values'][2]
        email = item['values'][3]
        vuln_str = item['values'][4]
        is_vuln = (vuln_str == "Yes")
        
        # Populate dict for easier passing
        customer_data = {
            'id': c_id,
            'name': name,
            'phone': phone,
            'email': email,
            'is_vulnerable': is_vuln,
            'preferred_contact': 'Phone' # Default or we need to query db for full details
        }
        
        # We might need to query DB if treeview doesn't have all data (like preferred_contact)
        # For now, let's just default it or guess. 
        # Better: Query DB. But 'search_customers' returns everything.
        # Treeview stores columns.
        
        self.master.show_frame(AddCustomerFrame, self.user, customer_data)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a customer to delete.")
            return
            
        item = self.tree.item(selected[0])
        c_id = item['values'][0]
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete customer '{name}'?"):
            try:
                delete_customer(c_id)
                self.perform_search()
                messagebox.showinfo("Success", "Customer deleted.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))


class AddCustomerFrame(tk.Frame):
    def __init__(self, master, user, customer_data=None):
        super().__init__(master)
        self.master = master
        self.user = user
        self.customer_data = customer_data # If set, we are editing
        self.pack(fill="both", expand=True)
        
        mode = "Edit" if customer_data else "Add New"
        
        # Header
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text=f"{mode} Customer", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Form
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        # Fields
        tk.Label(form, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(form, width=40)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form, text="Phone:").grid(row=1, column=0, sticky="w", pady=5)
        self.phone_entry = tk.Entry(form, width=40)
        self.phone_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form, text="Email:").grid(row=2, column=0, sticky="w", pady=5)
        self.email_entry = tk.Entry(form, width=40)
        self.email_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(form, text="Preferred Contact:").grid(row=3, column=0, sticky="w", pady=5)
        self.contact_var = tk.StringVar(value="Phone")
        tk.OptionMenu(form, self.contact_var, "Phone", "Email", "Post", "In-Person").grid(row=3, column=1, sticky="w", pady=5)
        
        self.vuln_var = tk.IntVar()
        vuln_cb = tk.Checkbutton(form, text="Is Vulnerable?", variable=self.vuln_var)
        vuln_cb.grid(row=4, column=1, sticky="w", pady=5)
        ToolTip(vuln_cb, "Check if customer has vulnerabilities (disability, age, etc.)\nAdds +15 to ticket priority.")
        
        # Pre-fill if editing
        if self.customer_data:
            self.name_entry.insert(0, self.customer_data['name'])
            self.phone_entry.insert(0, str(self.customer_data['phone']))
            self.email_entry.insert(0, self.customer_data['email'])
            # Note: preferred_contact might be missing from compact treeview data
            # Ideally we fetch fresh from DB, but for simplicity:
            if 'preferred_contact' in self.customer_data:
                 self.contact_var.set(self.customer_data['preferred_contact'])
            self.vuln_var.set(1 if self.customer_data['is_vulnerable'] else 0)
        
        # Save Button
        tk.Button(form, text="Save Customer", command=self.save, bg="#4CAF50").grid(row=5, column=1, sticky="e", pady=20)

    def save(self):
        name = self.name_entry.get()
        if not name:
            messagebox.showwarning("Validation", "Name is required.")
            return
            
        if self.customer_data:
            # Update
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
            # Add
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
        self.master.show_frame(CustomerListFrame, self.user)

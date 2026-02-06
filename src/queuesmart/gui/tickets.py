from queuesmart.database import get_tickets, create_ticket, update_ticket, search_tickets, delete_ticket
from queuesmart.priority import sort_tickets_by_priority
from queuesmart.gui.utils import clear_frame

class TicketListFrame(tk.Frame):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        # Header
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Ticket Management", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Action Bar
        action_bar = tk.Frame(self)
        action_bar.pack(fill="x", padx=10, pady=10)
        
        self.search_var = tk.StringVar()
        tk.Entry(action_bar, textvariable=self.search_var, width=30).pack(side="left", padx=(0, 10))
        tk.Button(action_bar, text="Search", command=self.search_tickets).pack(side="left")
        
        # Buttons
        tk.Button(action_bar, text="Update", command=self.go_update, bg="#2196F3").pack(side="right", padx=5)
        tk.Button(action_bar, text="Delete", command=self.delete_selected, bg="#F44336").pack(side="right", padx=5)
        tk.Button(action_bar, text="+ New", command=self.go_create, bg="#4CAF50").pack(side="right")
        
        # Treeview
        columns = ("ID", "Customer", "Category", "Urgency", "Status", "Priority")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("ID", width=40)
        self.tree.column("Priority", width=50)
        
        self.load_data()

    def go_back(self):
        from queuesmart.gui.dashboard import DashboardFrame
        self.master.show_frame(DashboardFrame, self.user, self.master.show_login)
        
    def load_data(self):
        # Default view: all items, sorted by priority
        tickets = get_tickets() # Add filters if needed
        # Sort
        sorted_tickets = sort_tickets_by_priority(tickets)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for t in sorted_tickets:
            self.tree.insert("", "end", values=(t['id'], t['customer_name'], t['category'], t['urgency'], t['status'], t.get('priority_score', 0)))

    def search_tickets(self):
        query = self.search_var.get()
        if not query:
            self.load_data()
            return
            
        results = search_tickets(query)
        sorted_results = sort_tickets_by_priority(results)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for t in sorted_results:
            self.tree.insert("", "end", values=(t['id'], t['customer_name'], t['category'], t['urgency'], t['status'], t.get('priority_score', 0)))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a ticket to delete.")
            return
            
        item = self.tree.item(selected[0])
        t_id = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ticket #{t_id}?"):
            delete_ticket(t_id)
            self.load_data()
            messagebox.showinfo("Success", "Ticket deleted.")

    def go_create(self):
        self.master.show_frame(CreateTicketFrame, self.user)
        
    def go_update(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a ticket to update.")
            return
        
        item = self.tree.item(selected[0])
        ticket_id = item['values'][0]
        self.master.show_frame(UpdateTicketFrame, self.user, ticket_id)


class CreateTicketFrame(tk.Frame):
    def __init__(self, master, user, customer_id=None):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Create Ticket", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        tk.Label(form, text="Customer ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.cust_id_entry = tk.Entry(form, width=10)
        self.cust_id_entry.grid(row=0, column=1, sticky="w", pady=5)
        if customer_id:
            self.cust_id_entry.insert(0, str(customer_id))
            
        tk.Label(form, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        self.cat_var = tk.StringVar(value="Housing")
        tk.OptionMenu(form, self.cat_var, "Housing", "Benefits", "Digital Support", "Wellbeing", "Other").grid(row=1, column=1, sticky="w", pady=5)
        
        tk.Label(form, text="Urgency:").grid(row=2, column=0, sticky="w", pady=5)
        self.urg_var = tk.StringVar(value="Low")
        tk.OptionMenu(form, self.urg_var, "Low", "Medium", "High", "Critical").grid(row=2, column=1, sticky="w", pady=5)
        
        tk.Label(form, text="Description:").grid(row=3, column=0, sticky="nsew", pady=5)
        self.desc_entry = tk.Text(form, width=40, height=5)
        self.desc_entry.grid(row=3, column=1, pady=5)
        
        tk.Button(form, text="Create Ticket", command=self.save, bg="#4CAF50").grid(row=4, column=1, sticky="e", pady=20)

    def save(self):
        try:
            cust_id = int(self.cust_id_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Customer ID must be a number.")
            return
            
        desc = self.desc_entry.get("1.0", "end-1c")
        if not desc.strip():
            messagebox.showerror("Error", "Description is required.")
            return
            
        create_ticket(
            cust_id, 
            self.cat_var.get(), 
            desc, 
            self.urg_var.get(), 
            created_by_user_id=self.user['id']
        )
        messagebox.showinfo("Success", "Ticket created!")
        self.go_back()

    def go_back(self):
        self.master.show_frame(TicketListFrame, self.user)


class UpdateTicketFrame(tk.Frame):
    def __init__(self, master, user, ticket_id):
        super().__init__(master)
        self.master = master
        self.user = user
        self.ticket_id = ticket_id
        self.pack(fill="both", expand=True)
        
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text=f"Update Ticket #{ticket_id}", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        tk.Label(form, text="Status:").grid(row=0, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar(value="Open") # TODO: Fetch current?
        tk.OptionMenu(form, self.status_var, "Open", "In Progress", "Waiting", "Closed").grid(row=0, column=1, sticky="w", pady=5)
        
        tk.Label(form, text="Resolution (if closing):").grid(row=1, column=0, sticky="nsew", pady=5)
        self.res_entry = tk.Text(form, width=40, height=5)
        self.res_entry.grid(row=1, column=1, pady=5)
        
        tk.Button(form, text="Update Ticket", command=self.save, bg="#2196F3").grid(row=2, column=1, sticky="e", pady=20)
        
    def save(self):
        status = self.status_var.get()
        res = self.res_entry.get("1.0", "end-1c")
        
        # Simple update
        update_ticket(self.ticket_id, status=status, resolution=res, user_id=self.user['id'])
        messagebox.showinfo("Success", "Ticket updated!")
        self.go_back()

    def go_back(self):
        self.master.show_frame(TicketListFrame, self.user)

import tkinter as tk
from tkinter import ttk, messagebox
from queuesmart.database import get_tickets, create_ticket, update_ticket, search_tickets, delete_ticket
from queuesmart.priority import sort_tickets_by_priority
from queuesmart.gui.utils import clear_frame

class TicketListFrame(tk.Frame):
    """
    Shows a list of all requests for help (tickets), sorted by how urgent they are.
    """
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        # Header area with navigation and title.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Ticket Management", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Action bar with search and buttons for common tasks.
        action_bar = tk.Frame(self)
        action_bar.pack(fill="x", padx=10, pady=10)
        
        # Search
        search_frame = tk.LabelFrame(action_bar, text="Keyword Search", padx=5, pady=5)
        search_frame.pack(side="left", padx=(0, 10))
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side="left", padx=(0, 5))
        tk.Button(search_frame, text="Search", command=self.search_tickets).pack(side="left")
        
        # Filters
        filter_frame = tk.LabelFrame(action_bar, text="Filters", padx=5, pady=5)
        filter_frame.pack(side="left")
        
        tk.Label(filter_frame, text="Status:").pack(side="left", padx=(5, 0))
        self.status_filter_var = tk.StringVar(value="All")
        status_menu = tk.OptionMenu(filter_frame, self.status_filter_var, "All", "Open", "In Progress", "Waiting", "Closed", command=lambda _: self.load_data())
        status_menu.pack(side="left")
        
        tk.Label(filter_frame, text="Category:").pack(side="left", padx=(10, 0))
        self.category_filter_var = tk.StringVar(value="All")
        cat_menu = tk.OptionMenu(filter_frame, self.category_filter_var, "All", "Housing", "Benefits", "Digital Support", "Wellbeing", "Other", command=lambda _: self.load_data())
        cat_menu.pack(side="left")
        
        # Action Buttons
        btn_frame = tk.Frame(action_bar)
        btn_frame.pack(side="right")
        tk.Button(btn_frame, text="+ New", command=self.go_create, bg="#4CAF50", width=10).pack(side="top", pady=2)
        tk.Button(btn_frame, text="Update", command=self.go_update, bg="#2196F3", width=10).pack(side="top", pady=2)
        tk.Button(btn_frame, text="Delete", command=self.delete_selected, bg="#F44336", width=10).pack(side="top", pady=2)
        
        # A table to display the details of each ticket.
        columns = ("ID", "Customer", "Category", "Urgency", "Status", "Priority")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column("ID", width=40)
        self.tree.column("Priority", width=50)
        
        # We fill the table with data as soon as the screen opens.
        self.load_data()

    def go_back(self):
        """Returns the user to the main dashboard."""
        from queuesmart.gui.dashboard import DashboardFrame
        self.master.show_frame(DashboardFrame, self.user, self.master.show_login)
        
    def load_data(self):
        """Collects all tickets from our records, calculates their priority scores, and displays them in the table."""
        # We ask the database for tickets, applying any active filters.
        tickets = get_tickets(
            status_filter=self.status_filter_var.get(),
            category_filter=self.category_filter_var.get()
        )
        # We sort them so that the most urgent ones appear at the top of the list.
        sorted_tickets = sort_tickets_by_priority(tickets)
        
        # We clear the table before adding the sorted list.
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for t in sorted_tickets:
            self.tree.insert("", "end", values=(t['id'], t['customer_name'], t['category'], t['urgency'], t['status'], t.get('priority_score', 0)))

    def search_tickets(self):
        """Finds specific requests by looking for keywords in the description or the customer's name."""
        query = self.search_var.get()
        if not query:
            # If the search box is empty, we just show everything.
            self.load_data()
            return
            
        # We ask the database for tickets that match the keyword entered.
        results = search_tickets(query)
        sorted_results = sort_tickets_by_priority(results)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for t in sorted_results:
            self.tree.insert("", "end", values=(t['id'], t['customer_name'], t['category'], t['urgency'], t['status'], t.get('priority_score', 0)))

    def delete_selected(self):
        """Permanently removes a ticket from the system after asking for confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a ticket to delete.")
            return
            
        item = self.tree.item(selected[0])
        t_id = item['values'][0]
        
        # We ensure the user really wants to delete the ticket before proceeding.
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ticket #{t_id}?"):
            delete_ticket(t_id, user_id=self.user['id'])
            self.load_data()
            messagebox.showinfo("Success", "Ticket deleted.")

    def go_create(self):
        """Takes the user to the form where they can start a new request for help."""
        self.master.show_frame(CreateTicketFrame, self.user)
        
    def go_update(self):
        """Takes the user to the form where they can change the status or notes of an existing request."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a ticket to update.")
            return
        
        item = self.tree.item(selected[0])
        ticket_id = item['values'][0]
        self.master.show_frame(UpdateTicketFrame, self.user, ticket_id)


class CreateTicketFrame(tk.Frame):
    """
    A form to start a new request for help, where staff can describe the issue and set its urgency.
    """
    def __init__(self, master, user, customer_id=None):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        # Header with a cancel button and title.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Create Ticket", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        # Box to enter the ID of the customer who needs help.
        tk.Label(form, text="Customer ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.cust_id_entry = tk.Entry(form, width=10)
        self.cust_id_entry.grid(row=0, column=1, sticky="w", pady=5)
        if customer_id:
            self.cust_id_entry.insert(0, str(customer_id))
            
        # Dropdown to choose the type of help needed (e.g., Housing).
        tk.Label(form, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
        self.cat_var = tk.StringVar(value="Housing")
        tk.OptionMenu(form, self.cat_var, "Housing", "Benefits", "Digital Support", "Wellbeing", "Other").grid(row=1, column=1, sticky="w", pady=5)
        
        # Dropdown to choose how urgent the request is.
        tk.Label(form, text="Urgency:").grid(row=2, column=0, sticky="w", pady=5)
        self.urg_var = tk.StringVar(value="Low")
        tk.OptionMenu(form, self.urg_var, "Low", "Medium", "High", "Critical").grid(row=2, column=1, sticky="w", pady=5)
        
        # Larger box to type in a description of the customer's problem.
        tk.Label(form, text="Description:").grid(row=3, column=0, sticky="nsew", pady=5)
        self.desc_entry = tk.Text(form, width=40, height=5)
        self.desc_entry.grid(row=3, column=1, pady=5)
        
        # Button to confirm and save the new ticket.
        tk.Button(form, text="Create Ticket", command=self.save, bg="#4CAF50").grid(row=4, column=1, sticky="e", pady=20)

    def save(self):
        """Records the new request for help in the system's files."""
        try:
            cust_id = int(self.cust_id_entry.get())
        except ValueError:
            # We ensure the Customer ID is a valid number.
            messagebox.showerror("Error", "Customer ID must be a number.")
            return
            
        desc = self.desc_entry.get("1.0", "end-1c")
        if not desc.strip():
            # We make sure a description has been typed.
            messagebox.showerror("Error", "Description is required.")
            return
            
        # We send the information to the database to be saved.
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
        """Returns the user to the main list of tickets."""
        self.master.show_frame(TicketListFrame, self.user)


class UpdateTicketFrame(tk.Frame):
    """
    A form to change the status of an existing request, such as marking it as 'In Progress' or 'Closed'.
    """
    def __init__(self, master, user, ticket_id):
        super().__init__(master)
        self.master = master
        self.user = user
        self.ticket_id = ticket_id
        self.pack(fill="both", expand=True)
        
        # Header with cancel button and title.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text=f"Update Ticket #{ticket_id}", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        # Dropdown to select the new status for the request.
        tk.Label(form, text="Status:").grid(row=0, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar(value="Open")
        tk.OptionMenu(form, self.status_var, "Open", "In Progress", "Waiting", "Closed").grid(row=0, column=1, sticky="w", pady=5)
        
        # Larger box to type in how the issue was resolved (if it is being closed).
        tk.Label(form, text="Resolution (if closing):").grid(row=1, column=0, sticky="nsew", pady=5)
        self.res_entry = tk.Text(form, width=40, height=5)
        self.res_entry.grid(row=1, column=1, pady=5)
        
        # Button to confirm and save the changes.
        tk.Button(form, text="Update Ticket", command=self.save, bg="#2196F3").grid(row=2, column=1, sticky="e", pady=20)
        
    def save(self):
        """Records the changes made to the ticket in our digital records."""
        status = self.status_var.get()
        res = self.res_entry.get("1.0", "end-1c")
        
        # We send the updated status and resolution notes to the database.
        update_ticket(self.ticket_id, status=status, resolution=res, user_id=self.user['id'])
        messagebox.showinfo("Success", "Ticket updated!")
        self.go_back()

    def go_back(self):
        """Returns the user to the main list of tickets."""
        self.master.show_frame(TicketListFrame, self.user)

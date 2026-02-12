import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from queuesmart.reporting import (
    get_tickets_per_week_by_category, 
    get_avg_close_time_by_category, 
    get_busiest_appointment_days, 
    export_to_csv
)

class ReportingFrame(tk.Frame):
    """
    A screen specifically for Managers to view performance reports and export them as spreadsheet files.
    """
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.user = user
        self.pack(fill="both", expand=True)
        
        # Header for the reporting screen.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Management Reporting", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # We split the screen into a sidebar for picking reports and a main area for viewing data.
        sidebar = tk.Frame(self, width=200, bg="#f9f9f9", padx=10, pady=20)
        sidebar.pack(side="left", fill="y")
        
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(side="right", fill="both", expand=True)
        
        self.current_report_label = tk.Label(content, text="Select a report from the sidebar", font=("Helvetica", 12, "bold"))
        self.current_report_label.pack(anchor="w", pady=(0, 10))
        
        # Buttons in the sidebar to select different types of reports.
        tk.Button(sidebar, text="Tickets per Week", command=lambda: self.show_report("Tickets per Week", get_tickets_per_week_by_category), width=20).pack(pady=5)
        tk.Button(sidebar, text="Avg Close Time", command=lambda: self.show_report("Avg Close Time (Hours)", get_avg_close_time_by_category), width=20).pack(pady=5)
        tk.Button(sidebar, text="Busiest Appt Days", command=lambda: self.show_report("Top 5 Busiest Days", get_busiest_appointment_days), width=20).pack(pady=5)
        
        # A button to export whatever information is currently shown in the table to a spreadsheet.
        tk.Frame(sidebar, height=2, bg="gray").pack(fill="x", pady=20)
        tk.Button(sidebar, text="Export Current to CSV", command=self.export_current, bg="#2196F3").pack(pady=5)
        
        # The table used to display the report data.
        self.tree = ttk.Treeview(content, show="headings")
        self.tree.pack(fill="both", expand=True)
        
        self.current_data = []

    def go_back(self):
        """Returns the manager to the main dashboard."""
        from queuesmart.gui.dashboard import DashboardFrame
        self.master.show_frame(DashboardFrame, self.user, self.master.show_login)

    def show_report(self, title, data_fetcher):
        """Displays a chosen report (like 'Tickets per Week') in the table on the screen."""
        self.current_report_label.config(text=title)
        # We fetch the latest data from the database using the specific reporter function.
        self.current_data = data_fetcher()
        
        # We clear the previous information from the table.
        self.tree.delete(*self.tree.get_children())
        
        if not self.current_data:
            # If there's no information to show, we stop here.
            return
            
        # We set up the column titles based on the information we received.
        cols = list(self.current_data[0].keys())
        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
            
        # We fill the table with the new data.
        for row in self.current_data:
            self.tree.insert("", "end", values=tuple(row.values()))

    def export_current(self):
        """Saves the report currently being viewed as a CSV file (spreadsheet) on the computer."""
        if not self.current_data:
            # We make sure there's actually data on the screen before trying to save it.
            messagebox.showwarning("Export", "No data to export.")
            return
            
        # We ask the manager to choose a name and location for the new file.
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            # We attempt to save the information to the chosen file.
            if export_to_csv(self.current_data, filename):
                messagebox.showinfo("Success", f"Report exported to {filename}")
            else:
                messagebox.showerror("Error", "Failed to export report.")

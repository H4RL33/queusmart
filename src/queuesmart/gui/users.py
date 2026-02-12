import tkinter as tk
from tkinter import ttk, messagebox
from queuesmart.database import get_all_users, delete_user, add_user, update_user
from queuesmart.gui.utils import clear_frame

class UserManagementFrame(tk.Frame):
    """
    Shows a list of all people who can use the system and provides buttons for a manager to add, edit, or remove accounts.
    """
    def __init__(self, master, current_user):
        super().__init__(master)
        self.master = master
        self.current_user = current_user
        self.pack(fill="both", expand=True)
        
        # Header with a back button and title.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Back", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="User Management", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        # Action bar with buttons for adding, editing, or deleting accounts.
        action_bar = tk.Frame(self)
        action_bar.pack(fill="x", padx=10, pady=10)
        
        tk.Button(action_bar, text="Add New User", command=self.go_add_user, bg="#4CAF50").pack(side="left")
        tk.Button(action_bar, text="Edit Selected User", command=self.go_edit_user, bg="#2196F3").pack(side="left", padx=5)
        tk.Button(action_bar, text="Delete Selected User", command=self.delete_selected, bg="#F44336").pack(side="right")
        
        # A table to display the staff accounts.
        columns = ("ID", "Username", "Role")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.column("ID", width=50)
            
        # We load the list of users as soon as the screen opens.
        self.load_users()

    def go_back(self):
        """Returns the manager to the main dashboard."""
        from queuesmart.gui.dashboard import DashboardFrame
        self.master.show_frame(DashboardFrame, self.current_user, self.master.show_login)

    def go_add_user(self):
        """Takes the manager to the form to create a new staff account."""
        self.master.show_frame(CreateUserFrame, self.current_user)

    def go_edit_user(self):
        """Takes the manager to the form to edit the selected staff account."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user to edit.")
            return
            
        item = self.tree.item(selected[0])
        # We collect the current details from the table to fill the edit form.
        user_id = item['values'][0]
        username = item['values'][1]
        role = item['values'][2]
        
        user_data = {
            'id': user_id,
            'username': username,
            'role': role
        }
        self.master.show_frame(EditUserFrame, self.current_user, user_data)

    def load_users(self):
        """Retrieves the names and job roles of all staff members from the system records."""
        users = get_all_users()
        
        # We clear the current table and fill it with the latest user information.
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for u in users:
            self.tree.insert("", "end", values=(u['id'], u['username'], u['role']))

    def delete_selected(self):
        """Removes a staff member's access to the system, as long as it's safe to do so."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user to delete.")
            return
            
        item = self.tree.item(selected[0])
        u_id = item['values'][0]
        username = item['values'][1]
        
        # We prevent managers from accidentally deleting themselves while they are using the system.
        if u_id == self.current_user['id']:
            messagebox.showerror("Error", "You cannot delete your own account while logged in.")
            return
            
        # We also prevent the main 'admin' account from being deleted so we don't get locked out.
        if username == "admin":
            messagebox.showerror("Error", "The 'admin' account cannot be deleted.")
            return

        # We ask for confirmation before proceeding with the deletion.
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{username}'?"):
            try:
                delete_user(u_id, deleted_by_user_id=self.current_user['id'])
                self.load_users()
                messagebox.showinfo("Success", f"User '{username}' has been deleted.")
            except ValueError as e:
                # If the staff member has work tied to them, the system will prevent deletion.
                messagebox.showerror("Error", str(e))

class EditUserFrame(tk.Frame):
    """
    A form for a manager to change a staff member's name, job role, or password.
    """
    def __init__(self, master, current_user, user_data):
        super().__init__(master)
        self.master = master
        self.current_user = current_user
        self.user_data = user_data
        self.pack(fill="both", expand=True)
        
        # Header showing which user is being edited.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text=f"Edit User: {user_data['username']}", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        # Box to change the username.
        tk.Label(form, text="Username:").pack(anchor="w")
        self.username_entry = tk.Entry(form)
        self.username_entry.insert(0, user_data['username'])
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        # Box to set a new password (optional).
        tk.Label(form, text="New Password (leave blank to keep current):").pack(anchor="w")
        self.password_entry = tk.Entry(form, show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))

        # Dropdown to change the job role.
        tk.Label(form, text="Role:").pack(anchor="w")
        self.role_var = tk.StringVar(value=user_data['role'])
        self.role_combo = ttk.Combobox(form, textvariable=self.role_var, values=["Staff", "Manager"], state="readonly")
        self.role_combo.pack(fill="x", pady=(0, 20))
        
        # Button to save the updated information.
        tk.Button(form, text="Update User", command=self.save, bg="#2196F3", fg="black", width=20).pack(pady=5)

    def save(self):
        """Records the updated staff information in the digital filing cabinet."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        # We ensure that a name and role have been provided.
        if not username or not role:
            messagebox.showwarning("Input Error", "Username and Role are required.")
            return
            
        # We send the updated details to the database to be saved.
        success = update_user(
            self.user_data['id'],
            username=username,
            role=role,
            password=password if password.strip() else None,
            updated_by_user_id=self.current_user['id']
        )
        
        if success:
            messagebox.showinfo("Success", "User updated successfully!")
            self.go_back()
        else:
            messagebox.showerror("Error", "Username already exists or update failed.")

    def go_back(self):
        """Returns the manager to the main user management screen."""
        self.master.show_frame(UserManagementFrame, self.current_user)

class CreateUserFrame(tk.Frame):
    """
    A form for a manager to create a brand new staff or manager account.
    """
    def __init__(self, master, current_user):
        super().__init__(master)
        self.master = master
        self.current_user = current_user
        self.pack(fill="both", expand=True)
        
        # Header for the creation form.
        header = tk.Frame(self, bg="#eee", height=50)
        header.pack(fill="x")
        tk.Button(header, text="< Cancel", command=self.go_back).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Add New User", font=("Helvetica", 14)).pack(side="left", padx=10)
        
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)
        
        # Box to type in the new staff member's name.
        tk.Label(form, text="Username:").pack(anchor="w")
        self.username_entry = tk.Entry(form)
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        # Box to type in their new secret password.
        tk.Label(form, text="Password:").pack(anchor="w")
        self.password_entry = tk.Entry(form, show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))

        # Dropdown to select their job role.
        tk.Label(form, text="Role:").pack(anchor="w")
        self.role_var = tk.StringVar(value="Staff")
        self.role_combo = ttk.Combobox(form, textvariable=self.role_var, values=["Staff", "Manager"], state="readonly")
        self.role_combo.pack(fill="x", pady=(0, 20))
        
        # Button to confirm and create the new account.
        tk.Button(form, text="Create User", command=self.save, bg="#4CAF50", fg="black", width=20).pack(pady=5)

    def save(self):
        """Records the new staff account in the system's files."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        # We ensure all fields have been filled out correctly.
        if not username or not password or not role:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
            
        # We attempt to add the new user to our digital filing cabinet.
        if add_user(username, password, role, created_by_user_id=self.current_user['id']):
            messagebox.showinfo("Success", f"User '{username}' created successfully!")
            self.go_back()
        else:
            messagebox.showerror("Error", "Username already exists or creation failed.")

    def go_back(self):
        """Returns the manager to the main user management screen."""
        self.master.show_frame(UserManagementFrame, self.current_user)

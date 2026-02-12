import tkinter as tk
from tkinter import messagebox, ttk
from queuesmart.database import authenticate_user, add_user
from queuesmart.gui.utils import center_window

class LoginFrame(tk.Frame):
    """
    This screen allows staff to enter their username and password to access the system.
    """
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        
        # We put all the login boxes in the very middle of the screen.
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # We show a big title at the top.
        tk.Label(self.center_frame, text="QueueSmart Login", font=("Helvetica", 20, "bold")).pack(pady=20)
        
        # A box for the staff member to type their name.
        tk.Label(self.center_frame, text="Username:").pack(anchor="w")
        self.username_entry = tk.Entry(self.center_frame)
        self.username_entry.pack(fill="x", pady=(0, 10))
        self.username_entry.focus()
        
        # A box for the staff member to type their password (it will show as stars to stay secret).
        tk.Label(self.center_frame, text="Password:").pack(anchor="w")
        self.password_entry = tk.Entry(self.center_frame, show="*")
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # A button to confirm and log in.
        tk.Button(self.center_frame, text="Login", command=self.login, bg="#4CAF50", fg="black", width=20).pack(pady=5)
        
        # A button to switch to the registration screen if they don't have an account yet.
        tk.Button(self.center_frame, text="Don't have an account? Register", command=self.go_to_register, relief="flat", fg="blue", cursor="hand2").pack()
        
        # This makes it so pressing the 'Enter' key on the keyboard is the same as clicking the 'Login' button.
        self.master.bind('<Return>', lambda event: self.login())

    def login(self):
        """Checks if the entered details are correct and shows an error message if they are wrong."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # We make sure both boxes have something typed in them.
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return
            
        # we check the filing cabinet to see if the name and password match.
        user = authenticate_user(username, password)
        
        if user:
            # If they match, we move to the next screen.
            self.on_login_success(user)
        else:
            # If they don't match, we show an error message.
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def go_to_register(self):
        """Takes the user to the registration screen."""
        self.master.show_frame(RegisterFrame, self.on_login_success)

class RegisterFrame(tk.Frame):
    """
    This screen allows new staff members to create an account by choosing a name, a password, and their job role.
    """
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        
        # We center the registration boxes on the screen.
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # A big title for the registration page.
        tk.Label(self.center_frame, text="QueueSmart Register", font=("Helvetica", 20, "bold")).pack(pady=20)
        
        # A box to choose a new username.
        tk.Label(self.center_frame, text="Username:").pack(anchor="w")
        self.username_entry = tk.Entry(self.center_frame)
        self.username_entry.pack(fill="x", pady=(0, 10))
        
        # A box to choose a new password.
        tk.Label(self.center_frame, text="Password:").pack(anchor="w")
        self.password_entry = tk.Entry(self.center_frame, show="*")
        self.password_entry.pack(fill="x", pady=(0, 10))

        # A dropdown menu to pick a job role (either Staff or Manager).
        tk.Label(self.center_frame, text="Role:").pack(anchor="w")
        self.role_var = tk.StringVar(value="Staff")
        self.role_combo = ttk.Combobox(self.center_frame, textvariable=self.role_var, values=["Staff", "Manager"], state="readonly")
        self.role_combo.pack(fill="x", pady=(0, 20))
        
        # A button to confirm and create the new account.
        tk.Button(self.center_frame, text="Register", command=self.register, bg="#2196F3", fg="black", width=20).pack(pady=5)
        
        # A button to go back to the login page if they already have an account.
        tk.Button(self.center_frame, text="Already have an account? Login", command=self.go_to_login, relief="flat", fg="blue", cursor="hand2").pack()
        
        # Pressing 'Enter' will trigger the registration.
        self.master.bind('<Return>', lambda event: self.register())

    def register(self):
        """Saves the new account details in the system and lets the user know if it worked."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        # We ensure all information has been provided.
        if not username or not password or not role:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
            
        # We try to add the new person to our digital filing cabinet.
        if add_user(username, password, role):
            # If it works, we show a success message and go to the login screen.
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            self.go_to_login()
        else:
            # If the name is already taken, we show an error.
            messagebox.showerror("Error", "Username already exists or registration failed.")

    def go_to_login(self):
        """Takes the user back to the login screen."""
        self.master.show_frame(LoginFrame, self.on_login_success)

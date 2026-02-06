import tkinter as tk
from tkinter import messagebox
from queuesmart.database import authenticate_user
from queuesmart.gui.utils import center_window

class LoginFrame(tk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        
        # Center content
        self.center_frame = tk.Frame(self)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        tk.Label(self.center_frame, text="QueueSmart Login", font=("Helvetica", 20, "bold")).pack(pady=20)
        
        # Username
        tk.Label(self.center_frame, text="Username:").pack(anchor="w")
        self.username_entry = tk.Entry(self.center_frame)
        self.username_entry.pack(fill="x", pady=(0, 10))
        self.username_entry.focus()
        
        # Password
        tk.Label(self.center_frame, text="Password:").pack(anchor="w")
        self.password_entry = tk.Entry(self.center_frame, show="*")
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # Login Button
        tk.Button(self.center_frame, text="Login", command=self.login, bg="#4CAF50", fg="black", width=20).pack()
        
        # Bind Enter key
        self.master.bind('<Return>', lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return
            
        user = authenticate_user(username, password)
        
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

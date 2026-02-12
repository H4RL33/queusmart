import tkinter as tk

def clear_frame(frame):
    """Completely empties a screen by removing all its buttons, boxes, and text, making it ready for a new screen to be shown."""
    for widget in frame.winfo_children():
        # We loop through every single item currently on the screen and remove it.
        widget.destroy()

def center_window(window, width=800, height=600):
    """Adjusts the position of the main window so that it appears exactly in the middle of the computer monitor."""
    window.geometry(f"{width}x{height}")
    window.update_idletasks()
    
    # We find the total width and height of the person's screen.
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # We calculate the correct position to put the window in the center.
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    window.geometry(f"{width}x{height}+{x}+{y}")

class ToolTip:
    """
    Shows a small box with helpful information when the user hovers their mouse pointer over a button or setting.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        # We watch for when the mouse enters or leaves the area of the button.
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)

    def schedule(self, event=None):
        """Wait for half a second before showing the helpful message."""
        self.id = self.widget.after(500, self.show)

    def show(self, event=None):
        """Creates a tiny window with the helpful text next to the mouse pointer."""
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        
        # We create a small, simple box that floats above everything else.
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) # This removes the standard window borders.
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self, event=None):
        """Removes the helpful message box when the mouse moves away."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

import os

def print_logo():
    """
    Reads the ASCII logo from the project's root folder and prints it to the console.
    This provides a welcoming visual experience when the application starts.
    """
    # We find the location of the logo file relative to this code file.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "..", "ascii logo")
    
    try:
        if os.path.exists(logo_path):
            with open(logo_path, 'r') as f:
                print(f.read())
    except Exception:
        # If the logo file is missing or can't be read, we skip printing it.
        pass

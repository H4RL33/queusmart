import os

def clear_screen():
    # Clears the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    # Prints a styled header
    print("\n" + "=" * 40)
    print(f"{text:^40}")
    print("=" * 40 + "\n")

def print_table(headers, rows):
    # Prints a simple ASCII table
    # headers: list of strings
    # rows: list of lists of strings/values (must match length of headers)
    
    if not rows:
        print("No data available.")
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            # Ensure val is string for len()
            val_str = str(val) if val is not None else ""
            col_widths[i] = max(col_widths[i], len(val_str))
            
    # Add some padding
    col_widths = [w + 2 for w in col_widths]
    
    # Create format string
    fmt = "".join([f"{{:<{w}}}" for w in col_widths])
    
    # Print Header
    print("-" * sum(col_widths))
    print(fmt.format(*headers))
    print("-" * sum(col_widths))
    
    # Print Rows
    for row in rows:
        clean_row = [str(val) if val is not None else "" for val in row]
        print(fmt.format(*clean_row))
    print("-" * sum(col_widths))

def get_valid_input(prompt, valid_options=None, input_type=str, allow_empty=False):
    # Helper for robust input validation
    # valid_options: list of allowed values (optional)
    # input_type: type to cast input to (int, float, str)
    
    while True:
        user_input = input(prompt).strip()
        
        if allow_empty and not user_input:
            return None
        
        if not allow_empty and not user_input:
            print("Input cannot be empty. Please try again.")
            continue
            
        # Type Check
        try:
            casted_input = input_type(user_input)
        except ValueError:
            print(f"Invalid input type. Expected {input_type.__name__}.")
            continue
            
        # Option Check
        if valid_options:
            # Check against original string or casted value?
            # Usually strict equality on casted value is best
            if casted_input not in valid_options and user_input not in valid_options:
                print(f"Invalid option. Please choose one of: {', '.join(map(str, valid_options))}")
                continue
                
        return casted_input

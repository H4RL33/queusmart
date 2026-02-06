from queuesmart.cli.utils import clear_screen, print_header, get_valid_input
from queuesmart.reporting import (
    get_tickets_per_week_by_category, 
    get_avg_close_time_by_category, 
    get_busiest_appointment_days, 
    export_to_csv
)
import os

def print_table(data, headers):
    """Simple helper to print list of dicts as table"""
    if not data:
        print("\nNo data found.")
        return

    # Calculate column widths
    cols = headers  # List of keys
    widths = {col: len(col) for col in cols}
    for row in data:
        for col in cols:
            val = str(row.get(col, ""))
            if len(val) > widths[col]:
                widths[col] = len(val)
    
    # Print Header
    header_row = " | ".join(key.ljust(widths[key]) for key in cols)
    print("\n" + header_row)
    print("-" * len(header_row))
    
    # Print Rows
    for row in data:
        print(" | ".join(str(row.get(col, "")).ljust(widths[col]) for col in cols))

def display_report(report_name, data_fetcher):
    clear_screen()
    print_header(f"REPORT: {report_name}")
    
    data = data_fetcher()
    
    if not data:
        print("\nNo data available for this report.")
    else:
        # Determine headers from first row keys
        headers = list(data[0].keys())
        print_table(data, headers)
        
        export = input("\nExport to CSV? (y/n): ").lower()
        if export == 'y':
            filename = input("Enter filename (e.g., report.csv): ").strip()
            if not filename.endswith('.csv'):
                filename += ".csv"
            
            if export_to_csv(data, filename):
                print(f"\nSuccessfully exported to {os.getcwd()}/{filename}")
            else:
                print("\nFailed to export file.")
                
    input("\nPress Enter to return...")

def reporting_menu():
    while True:
        clear_screen()
        print_header("REPORTS & ANALYTICS")
        print("1. Tickets Created per Week (by Category)")
        print("2. Average Time to Close (by Category)")
        print("3. Busiest Days for Appointments")
        print("4. Back")
        
        choice = get_valid_input("\nSelect Option: ", valid_options=["1", "2", "3", "4"])
        
        if choice == "1":
            display_report("Tickets Per Week", get_tickets_per_week_by_category)
        elif choice == "2":
            display_report("Avg Close Time (Hours)", get_avg_close_time_by_category)
        elif choice == "3":
            display_report("Top 5 Busiest Days", get_busiest_appointment_days)
        elif choice == "4":
            break

import sys
import os
import datetime
import sqlite3

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from queuesmart import database, priority

def run_verification():
    print("Running Priority Logic Verification...")
    
    # 1. Setup Test DB (using a file so we can close/reopen if needed, or just standard flow)
    # We will use the standard DB logic but forcefully reset it for this test if we were doing integration tests.
    # However, to avoid messing with real data, let's mock the connection or use a temp DB name.
    # For simplicity in this script, we'll monkeypatch the DB_NAME in database module.
    
    database.DB_NAME = "test_priority_logic.db"
    
    # Clean up any existing test db
    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)
        
    database.init_db()
    print("[OK] Test Database initialized.")
    
    # 2. Operations
    # Add Customers
    cust_vuln = database.add_customer("John Doe", "123", "john@example.com", "Email", is_vulnerable=True)
    cust_norm = database.add_customer("Jane Smith", "456", "jane@example.com", "Phone", is_vulnerable=False)
    
    # Add Tickets
    
    # T1: Critical, Vulnerable (+50 + 15 = 65)
    t1 = database.create_ticket(cust_vuln, "Other", "System down", "Critical")
    
    # T2: Housing, Normal (+10 base). But let's make it OLD.
    # 30 hours old. (+6 aging). Total = 16.
    t2 = database.create_ticket(cust_norm, "Housing", "Need house", "Low")
    
    # T3: High, Normal (+30)
    t3 = database.create_ticket(cust_norm, "Other", "High issue", "High")
    
    # Manually update timestamps to test aging
    conn = database.get_db_connection()
    
    # Make T2 30 hours old
    time_30h_ago = (datetime.datetime.now() - datetime.timedelta(hours=30)).isoformat()
    conn.execute("UPDATE tickets SET created_at = ? WHERE id = ?", (time_30h_ago, t2))
    conn.commit()
    conn.close()
    
    # 3. Retrieve and Sort
    tickets = database.get_tickets()
    sorted_tickets = priority.sort_tickets_by_priority(tickets)
    
    # 4. Assertions
    print("\n--- Results ---")
    for t in sorted_tickets:
        print(f"ID: {t['id']}, Score: {t['priority_score']}, Urgency: {t['urgency']}, Vuln: {t['is_vulnerable']}, Category: {t['category']}")
        
    # Check T1
    t1_row = next(t for t in sorted_tickets if t['id'] == t1)
    if t1_row['priority_score'] != 65:
        print(f"[FAIL] T1 Score mismatch. Expected 65, got {t1_row['priority_score']}")
    else:
        print("[PASS] T1 Score correct (Critical+Vuln).")
        
    # Check T2
    t2_row = next(t for t in sorted_tickets if t['id'] == t2)
    # Housing(10) + Aging(30-24=6) = 16
    if t2_row['priority_score'] != 16:
        print(f"[FAIL] T2 Score mismatch. Expected 16, got {t2_row['priority_score']}. (Did aging work?)")
    else:
        print("[PASS] T2 Score correct (Housing+Aging).")
        
    # Check T3
    t3_row = next(t for t in sorted_tickets if t['id'] == t3)
    if t3_row['priority_score'] != 30:
        print(f"[FAIL] T3 Score mismatch. Expected 30, got {t3_row['priority_score']}")
    else:
        print("[PASS] T3 Score correct (High).")
        
    # Order check: T1(65) > T3(30) > T2(16)
    expected_order = [t1, t3, t2]
    actual_order = [t['id'] for t in sorted_tickets]
    
    if expected_order == actual_order:
        print("[PASS] Sort order is correct.")
    else:
        print(f"[FAIL] Order incorrect. Expected {expected_order}, got {actual_order}")

    # Cleanup
    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)

if __name__ == "__main__":
    run_verification()

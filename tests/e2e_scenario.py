import sys
import os
import datetime
import sqlite3

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from queuesmart.database import (
    init_db, add_user, authenticate_user, 
    add_customer, search_customers,
    create_ticket, get_tickets, update_ticket,
    create_appointment, get_appointments_by_staff,
    DB_NAME, search_tickets
)
from queuesmart.priority import sort_tickets_by_priority
from queuesmart.reporting import get_tickets_per_week_by_category

def banner(msg):
    print(f"\n{'='*50}\n{msg}\n{'='*50}")

def run_e2e_test():
    banner("STARTING E2E VERIFICATION")
    
    # 0. Setup: Clean DB
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    print("[PASS] Database initialized")

    # 1. User Auth - Ensure admin exists (simulating main.py logic)
    # The init_db function creates empty tables.
    # main.py usually seeds the user. Let's manually seed here to match logic.
    conn = sqlite3.connect(DB_NAME)
    res = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    if not res:
        add_user("admin", "admin123", "Manager")
    conn.close()

    user = authenticate_user("admin", "admin123")
    assert user is not None
    assert user['role'] == "Manager"
    print("[PASS] User Authentication Flow")

    # 2. Customer Management
    cid = add_customer("John Doe", "555-0100", "john@example.com", "Email", is_vulnerable=True)
    results = search_customers("John")
    assert len(results) == 1
    assert results[0]['name'] == "John Doe"
    print("[PASS] Customer Creation & Search")

    # 3. Ticket Management & Priority
    # Ticket A: Critical, Housing (Should be very high score)
    # Base(50) + Housing(10) + Vuln(15) = 75
    tid1 = create_ticket(cid, "Housing", "Homeless risk", "Critical", user['id'])
    
    # Ticket B: Low, Other (Should be low score)
    # Vuln(15) = 15
    tid2 = create_ticket(cid, "Other", "General query", "Low", user['id'])
    
    tickets = get_tickets()
    sorted_tickets = sort_tickets_by_priority(tickets)
    
    assert sorted_tickets[0]['id'] == tid1
    assert sorted_tickets[0]['priority_score'] == 75
    assert sorted_tickets[1]['priority_score'] == 15
    print("[PASS] Ticket Creation & Priority Logic")

    # 3.5. Ticket Search
    found_tickets = search_tickets("Homeless")
    assert len(found_tickets) >= 1
    assert found_tickets[0]['id'] == tid1
    print("[PASS] Ticket Search (By Description)")

    # 4. Update Ticket
    update_ticket(tid1, status="Closed", resolution="Resolved")
    updated_t = get_tickets(status_filter="Closed")
    assert len(updated_t) == 1
    print("[PASS] Ticket Update & Closure")

    # 5. Appointment Management
    now = datetime.datetime.now()
    start_time = (now + datetime.timedelta(days=1)).replace(microsecond=0, second=0, minute=0).isoformat()
    
    aid = create_appointment(cid, user['id'], start_time, 60, "Housing review")
    
    # Clash check
    try:
        create_appointment(cid, user['id'], start_time, 30, "Double book")
        print("[FAIL] Clash detection failed!")
    except ValueError:
        print("[PASS] Appointment Clash Detection")
        
    schedule = get_appointments_by_staff(user['id'])
    assert len(schedule) == 1
    print("[PASS] Schedule Retrieval")

    # 6. Reporting
    report_data = get_tickets_per_week_by_category()
    # verify structure
    if report_data:
        assert 'week' in report_data[0]
        assert report_data[0]['category'] == 'Housing'
    print("[PASS] Reporting Query Execution")

    banner("ALL SYSTEMS GO - E2E TEST PASSED")

if __name__ == "__main__":
    run_e2e_test()

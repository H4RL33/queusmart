import os
import sys
import unittest
import shutil

# Add src to path so we can import code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from queuesmart import database

class TestQueueSmartDB(unittest.TestCase):
    
    def setUp(self):
        # Use a test database file
        self.test_db = "test_queuesmart.db"
        database.DB_NAME = self.test_db
        
        # Clean up previous runs
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
        # Initialize DB
        database.init_db()

    def tearDown(self):
        # Cleanup
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_user_flow(self):
        """Test user creation and authentication."""
        print("\nTesting User Flow...")
        success = database.add_user("teststaff", "securepass123", "Staff")
        self.assertTrue(success)
        
        # Auth success
        user = database.authenticate_user("teststaff", "securepass123")
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], "Staff")
        
        # Auth failure
        user_fail = database.authenticate_user("teststaff", "wrongpass")
        self.assertIsNone(user_fail)
        print("User Flow OK")

    def test_customer_ticket_flow(self):
        """Test customer creation and ticket lifecycle."""
        print("\nTesting Ticket Flow...")
        cust_id = database.add_customer("John Doe", "555-0101", "john@example.com", "Email")
        self.assertIsNotNone(cust_id)
        
        ticket_id = database.create_ticket(cust_id, "Housing", "Need help with rent", "High")
        self.assertIsNotNone(ticket_id)
        
        tickets = database.get_tickets(status_filter="Open")
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]['category'], "Housing")
        
        database.update_ticket(ticket_id, status="Closed", resolution="Resolved")
        tickets_closed = database.get_tickets(status_filter="Closed")
        self.assertEqual(len(tickets_closed), 1)
        print("Ticket Flow OK")

    def test_appointment_clash(self):
        """Test appointment creation and clash detection."""
        print("\nTesting Appointment Clash...")
        # Create Staff
        database.add_user("staff1", "pass", "Staff")
        staff = database.authenticate_user("staff1", "pass")
        staff_id = staff['id']
        
        cust_id = database.add_customer("Jane Doe", "555-0102", "jane@example.com", "Phone")
        
        # Booking 1: 10:00 - 10:30
        appt1 = database.create_appointment(cust_id, staff_id, "2023-10-27T10:00:00", 30, "Consult")
        self.assertIsNotNone(appt1)
        
        # Booking 2: 11:00 - 11:30 (No clash)
        appt2 = database.create_appointment(cust_id, staff_id, "2023-10-27T11:00:00", 30, "Followup")
        self.assertIsNotNone(appt2)
        
        # Booking 3: 10:15 - 10:45 (Clash with Appt 1)
        with self.assertRaises(ValueError):
             database.create_appointment(cust_id, staff_id, "2023-10-27T10:15:00", 30, "Clash")
             
        # Booking 4: 09:45 - 10:15 (Clash with Appt 1)
        with self.assertRaises(ValueError):
             database.create_appointment(cust_id, staff_id, "2023-10-27T09:45:00", 30, "Clash")

        print("Appointment Clash OK")

if __name__ == '__main__':
    unittest.main()

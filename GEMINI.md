# QueueSmart — Appointment & Support Ticket System (Project Instructions)

## Project Overview
**Client:** QueueSmart CIC (Community Support Organisation)  
**Product Type:** Python Application  
**Project Length:** 15 hours (10 sessions)  
**Team Size:** Max 3 learners  

### Client Scenario
QueueSmart CIC supports local residents with housing advice, digital inclusion, and wellbeing services. Currently, appointments and tickets are tracked in spreadsheets, leading to duplicate entries, lost info, and lack of audit trails.

**Goal:** Build a software solution to log, prioritize, and manage service requests while producing simple performance reports.

## Functional Requirements

### A. Customer Management
- **Add Customer:** Name, contact details, preferred contact method.
- **Search:** By name, phone, or email.
- **View History:** See past tickets and appointments.

### B. Ticket Management (Core Feature)
- **Create Ticket:**
  - Customer linkage
  - Category: Housing, Benefits, Digital Support, Wellbeing, Other
  - Description
  - Urgency: Low, Medium, High, Critical
  - Created Date/Time
  - Status: Open, In Progress, Waiting, Closed
  - Assigned Staff (optional)
- **Update Ticket:** Change status, add notes, assign staff.
- **Close Ticket:** Outcome (Resolved, Referred, No Contact, Duplicate).

### C. Appointment Management
- **Create Appointment:**
  - Customer linkage
  - Date/Time, Duration
  - Staff Member
  - Reason
- **Clash Check:** Prevent double booking for staff.
- **View Schedule:** By staff member or by day.

### D. Prioritisation Rules
Must calculate a priority score:
- **Base:**
  - Critical: +50
  - High: +30
- **Aging:** +1 per hour after 24 hours.
- **Category:** Housing = +10.
- **Vulnerability:** Customer marked "vulnerable" = +15.
- **Sorting:** Ticket list must be sortable by strict priority score.

### E. Reporting
Produce at least 3 reports (Screen or CSV):
1. Tickets created per week by category.
2. Average time to close by category.
3. Top 5 busiest days/times for appointments.

## Non-Functional Requirements
- **Usability:** Clear navigation, consistent layout, helpful validation.
- **Reliability:** Handle bad inputs gracefully.
- **Security:** Basic data protection (hashed passwords).
- **Maintainability:** Modular code, readable naming, docstrings.
- **Testing:** Unit tests for core logic (scoring, clash detection).

## Technical Constraints
- **Language:** Python
- **UI:** Tkinter (Desktop) or Text-based CLI.
- **Storage:** SQLite (recommended), CSV, or text file.
- **Reporting:** CSV export via `csv` module.

## Data & Security
- **Data Store:** SQLite with clear schema.
- **Auth:**
  - Login screen with roles (Staff/Manager).
  - Passwords MUST be hashed (e.g., `hashlib` + salt).
- **Audit:** Log key actions (Ticket created/updated/closed) with Who, When, What.

## Delivery & Evidence
### Milestones
1. **Milestone 1:** Requirements, Wireframes, ERD approved.
2. **Milestone 2:** Ticket CRUD with persistent storage.
3. **Milestone 3:** Appointment booking + Clash detection.
4. **Milestone 4:** Priority scoring + Sorting + Audit logs.
5. **Milestone 5:** Reports + Export + Final evaluation.

### Submission Pack
- **Project Plan:** MoSCoW, Gantt, Risks.
- **Design:** User journeys, Wireframes, ERD, Architecture diagram.
- **Implementation:** Source code, DB setup, README.
- **Testing:** Test plan, Results, Unit test evidence.
- **Evaluation:** Criteria met, Security review, Improvements.
- **Project Management:** Sprint plan, Task board, Meeting notes.

## Success Criteria
- Works end-to-end with realistic data.
- Professional code structure.
- Correct implementation of prioritisation and reporting.
- Evidence of testing and security.
- Clear documentation.

### Stretch Goals
- Role-based permissions (Manager-only reporting).
- Search filters (Status, Category, Date).
- Data visualisations (`matplotlib`).
- Import existing spreadsheet data.
- Accessibility features.

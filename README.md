# QueueSmart

QueueSmart is a Python-based appointment and support ticket management system designed for QueueSmart CIC. It manages customer details, prioritizes support tickets using a weighted scoring algorithm, handles appointment bookings with clash detection, and provides performance reports.

## Features

- **Customer Management**: Add, search, and view customer history.
- **Ticket Management**: Create, update, and close tickets.
- **Priority Scoring**: Automatic calculation based on urgency, category, vulnerability, and age.
- **Appointment Booking**: Scheduling with automatic staff availability checks.
- **Reporting**: Weekly stats, average resolution times, and busy periods.
- **Security**: Role-based access (Manager/Staff) and secure password hashing.

## Requirements

- Python 3.12+
- SQLite3 (Included with Python)

## Installation

1.  **Clone the repository** (if applicable) or extract the source code.
2.  **Navigate to the project root**:
    ```bash
    cd queusmart
    ```
3.  **Run the application**:
    You can run it directly using Python. No external dependencies are required beyond the standard library.
    ```bash
    python3 src/queuesmart/main.py
    ```

## Usage

### First Run
On the very first run, the system will detect an empty database and create a default admin user:
- **Username**: `admin`
- **Password**: `admin123`

Use these credentials to log in. It is recommended to create your own staff accounts afterward if user management features are extended.

### Navigation
The CLI uses a numbered menu system.
- Enter the number corresponding to the option you wish to select.
- Follow the on-screen prompts for data entry.

### Reporting
Reports can be viewed on-screen or exported to CSV files for external analysis.

## Testing

To run the end-to-end verification script which simulates a full usage scenario:

```bash
python3 tests/e2e_scenario.py
```

To run unit tests (if configured):

```bash
python3 -m unittest discover tests
```

## Project Structure

- `src/queuesmart/`: Main source code.
    - `database.py`: Database schema and CRUD operations.
    - `priority.py`: Business logic for ticket prioritization.
    - `reporting.py`: Reporting queries and export logic.
    - `cli/`: User Interface modules.
- `tests/`: specific verification scripts.

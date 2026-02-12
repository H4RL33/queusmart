import csv
import datetime
from queuesmart.database import get_db_connection

def get_tickets_per_week_by_category():
    """
    Counts how many requests were made each week, grouped by the type of help requested (like Housing or Benefits).
    """
    conn = get_db_connection()
    # We look through our records and group requests by the week they were created and their category.
    query = """
        SELECT 
            strftime('%Y-%W', created_at) as week,
            category,
            COUNT(*) as count
        FROM tickets
        GROUP BY week, category
        ORDER BY week DESC, category ASC
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_avg_close_time_by_category():
    """
    Calculates the average number of hours it took to resolve requests in each category.
    """
    conn = get_db_connection()
    # We compare the time a request was opened with the time it was closed to find out how long it was active.
    query = """
        SELECT 
            category,
            AVG((julianday(closed_at) - julianday(created_at)) * 24) as avg_hours
        FROM tickets
        WHERE status = 'Closed' AND closed_at IS NOT NULL
        GROUP BY category
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    
    results = []
    for row in rows:
        r = dict(row)
        # We round the hours to two decimal places to make the numbers easier to read.
        if r['avg_hours']:
            r['avg_hours'] = round(r['avg_hours'], 2)
        else:
            r['avg_hours'] = 0.0
        results.append(r)
        
    return results

def get_busiest_appointment_days():
    """
    Identifies the 5 days with the most scheduled meetings, helping managers see when the team is most occupied.
    """
    conn = get_db_connection()
    # We count how many meetings are scheduled for each specific date in our calendar.
    query = """
        SELECT 
            substr(start_time, 1, 10) as date,
            COUNT(*) as count
        FROM appointments
        GROUP BY date
        ORDER BY count DESC
        LIMIT 5
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def export_to_csv(data, filename):
    """
    Saves a report as a spreadsheet file (CSV) so it can be opened and viewed in other programs like Microsoft Excel.
    """
    if not data:
        return False
        
    try:
        # We take the list of information and write it row-by-row into a new file on the computer.
        keys = data[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        return True
    except IOError:
        return False # This happens if the system can't save the file (e.g., if it's already open elsewhere).

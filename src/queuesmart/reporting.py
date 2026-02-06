import csv
import datetime
from queuesmart.database import get_db_connection

def get_tickets_per_week_by_category():
    """
    Returns a list of dictionaries with:
    - week_start (text date)
    - category
    - count
    """
    conn = get_db_connection()
    # SQLite 'strftime' with '%W' can get the week number, but '%Y-%W' can be tricky for sorting.
    # Let's simple format created_at as YYYY-WW.
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
    Returns a list of dictionaries with:
    - category
    - avg_hours (float)
    """
    conn = get_db_connection()
    # We allow SQLite to compute partial stat, but time diff is easier in Python 
    # if we want precision, or we can use julian day diff in SQLite.
    # (julianday(closed_at) - julianday(created_at)) * 24 gives hours.
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
    
    # Format the float to be nicer? Or let UI handle it.
    results = []
    for row in rows:
        r = dict(row)
        if r['avg_hours']:
            r['avg_hours'] = round(r['avg_hours'], 2)
        else:
            r['avg_hours'] = 0.0
        results.append(r)
        
    return results

def get_busiest_appointment_days():
    """
    Returns top 5 busiest dates (or days of week) by number of appointments.
    Let's go with specific dates as 'days/times' usually implies identifying hotspots.
    """
    conn = get_db_connection()
    # Extract just the date part YYYY-MM-DD
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
    Exports a list of dictionaries to a CSV file.
    """
    if not data:
        return False
        
    try:
        keys = data[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        return True
    except IOError:
        return False

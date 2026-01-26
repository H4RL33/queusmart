import sqlite3

def init_tables():
    connection = sqlite3.connect("queuesmart.db")
    cursor = connection.cursor()
    
    query = """CREATE TABLE IF NOT EXISTS customers (
    id INTEGER,
    name TEXT,
    role TEXT,
    dob TEXT
    );"""
    query.join("CREATE TABLE IF NOT EXISTS tickets;")
    query.join("CREATE TABLE IF NOT EXISTS staff;")
    query.join("CREATE TABLE IF NOT EXISTS appointments")
    
    cursor.execute(query)
    cursor.close()
    
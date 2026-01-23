import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,             # Use classic TCP port
        user="arjun",
        password="arjun@16",
        database="qr_entry_management"
    )

from db_config import get_connection

try:
    con = get_connection()
    print("Connection Successful!")
    con.close()
except Exception as e:
    print("Error:", e)

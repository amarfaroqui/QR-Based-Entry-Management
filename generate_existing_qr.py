from db_config import get_connection
from qr_generator import generate_qr_code

con = get_connection()
cur = con.cursor()

# Fetch all registrations with their event names
cur.execute("""
    SELECT r.reg_id, e.event_name
    FROM Registration r
    JOIN Event e ON r.event_id = e.event_id
""")
rows = cur.fetchall()

if not rows:
    print("No registrations found!")
else:
    for reg_id, event_name in rows:
        # Use reg_id as student name placeholder (you can change if needed)
        qr_path = generate_qr_code(reg_id, f"REG{reg_id}", event_name)
        # Save QR path to database
        cur.execute("UPDATE Registration SET qr_code_path=%s WHERE reg_id=%s", (qr_path, reg_id))
        print(f"QR generated for REG{reg_id} - {event_name} -> {qr_path}")

    con.commit()
    print("All QR codes generated successfully!")

con.close()

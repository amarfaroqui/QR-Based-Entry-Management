import os
import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_connection
from qr_generator import generate_qr_code, get_qr_image

root = tk.Tk()
root.title("QR-Based Entry Management System")
root.geometry("1150x760")
root.config(bg="#e6f2ff")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

frame_student = ttk.Frame(notebook)
frame_event = ttk.Frame(notebook)
frame_reg = ttk.Frame(notebook)
frame_log = ttk.Frame(notebook)

notebook.add(frame_student, text="Students")
notebook.add(frame_event, text="Events")
notebook.add(frame_reg, text="Registrations")
notebook.add(frame_log, text="Entry Logs")

def fetch_data(query, params=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute(query, params or ())
    rows = cur.fetchall()
    con.close()
    return rows

def execute_query(query, values=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute(query, values or ())
    con.commit()
    con.close()

# STUDENT TAB
student_tree = ttk.Treeview(frame_student,
    columns=("ID", "FName", "MName", "LName", "Email", "Phone"),
    show="headings", height=10)
for col in student_tree["columns"]:
    student_tree.heading(col, text=col)
    student_tree.column(col, width=150, anchor="center")
student_tree.pack(expand=False, fill="x", padx=32, pady=(16, 6))

def load_students():
    for row in student_tree.get_children():
        student_tree.delete(row)
    rows = fetch_data("""
        SELECT s.student_id, s.f_name, s.m_name, s.l_name, s.email, 
            GROUP_CONCAT(p.phone_no SEPARATOR ', ') AS phones
        FROM Student s
        LEFT JOIN Phone p ON s.student_id = p.student_id
        GROUP BY s.student_id
    """)
    for row in rows:
        student_tree.insert("", "end", values=row)

student_form = tk.LabelFrame(frame_student, text="Add New Student")
student_form.pack(padx=47, pady=4, fill="x")
sf_labels = ["Student ID", "First Name", "Middle Name", "Last Name", "Email", "Phone"]
sf_entries = []
for i, label in enumerate(sf_labels):
    tk.Label(student_form, text=label, width=13, anchor="e").grid(row=i, column=0, padx=5, pady=4, sticky="e")
    entry = tk.Entry(student_form, width=24)
    entry.grid(row=i, column=1, padx=5, pady=4)
    sf_entries.append(entry)

def add_student():
    try:
        sid, fn, mn, ln, em, ph = (e.get() for e in sf_entries)
        execute_query(
            "INSERT INTO Student (student_id, f_name, m_name, l_name, email) VALUES (%s,%s,%s,%s,%s)",
            (sid, fn, mn, ln, em))
        execute_query(
            "INSERT INTO Phone (student_id, phone_no) VALUES (%s,%s)",
            (sid, ph))
        for e in sf_entries:
            e.delete(0, 'end')
        messagebox.showinfo("Success", "Student added!")
        load_students()
    except Exception as e:
        messagebox.showerror("Error", str(e))

btn_frame_student = tk.Frame(student_form)
btn_frame_student.grid(row=0, column=2, rowspan=6, padx=24)
tk.Button(btn_frame_student, text="Add Student", bg="#33cc33", fg="white", command=add_student, width=16).pack(pady=5)
tk.Button(btn_frame_student, text="Refresh Students", bg="#3399ff", fg="white", command=load_students, width=16).pack(pady=5)

# EVENTS TAB
event_tree = ttk.Treeview(frame_event,
    columns=("EventID", "EventName", "EventDate", "VenueName", "AdminID"),
    show="headings", height=8)
for col in event_tree["columns"]:
    event_tree.heading(col, text=col)
    event_tree.column(col, width=180, anchor="center")
event_tree.pack(expand=False, fill="x", padx=32, pady=(16, 6))

def load_events():
    for row in event_tree.get_children():
        event_tree.delete(row)
    rows = fetch_data("""
        SELECT e.event_id, e.event_name, e.event_date, v.venue_name, e.admin_id
        FROM Event e
        LEFT JOIN Venue v ON e.event_id = v.event_id
    """)
    for row in rows:
        event_tree.insert("", "end", values=row)

tk.Button(frame_event, text="Refresh Events", bg="#3399ff", fg="white", command=load_events, width=16).pack(pady=10)

# REGISTRATIONS TAB - ADD StudentID column!
reg_tree = ttk.Treeview(frame_reg,
    columns=("RegID", "StudentID", "EventName", "QR Path", "Status"),
    show="headings", height=10)
for col in reg_tree["columns"]:
    reg_tree.heading(col, text=col)
    reg_tree.column(col, width=120, anchor="center")
reg_tree.pack(expand=False, fill="x", padx=32, pady=(13, 5))

reg_form = tk.LabelFrame(frame_reg, text="Add / Update Registration")
reg_form.pack(padx=50, pady=4, fill="x")
rf_labels = ["Reg ID", "Student ID", "Event ID", "QR Code Path", "Entry Status"]
rf_entries = []
for i, label in enumerate(rf_labels):
    tk.Label(reg_form, text=label, width=14, anchor="e").grid(row=i, column=0, padx=5, pady=4, sticky="e")
    entry = tk.Entry(reg_form, width=26)
    entry.grid(row=i, column=1, padx=5, pady=4)
    rf_entries.append(entry)

def add_registration():
    try:
        reg_id, student_id, event_id, qr_path, status = (e.get() for e in rf_entries)
        execute_query("INSERT INTO Registration (reg_id, student_id, event_id, qr_code_path, entry_status) VALUES (%s,%s,%s,%s,%s)",
                      (reg_id, student_id, event_id, qr_path, status))
        for e in rf_entries:
            e.delete(0, 'end')
        messagebox.showinfo("Success", "Registration added!")
        load_registrations()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_status():
    reg_id, _, _, _, status = (e.get() for e in rf_entries)
    execute_query("UPDATE Registration SET entry_status=%s WHERE reg_id=%s", (status, reg_id))
    messagebox.showinfo("Updated", "Entry status updated.")
    load_registrations()

def delete_registration():
    reg_id, *_ = (e.get() for e in rf_entries)
    execute_query("DELETE FROM Registration WHERE reg_id=%s", (reg_id,))
    messagebox.showinfo("Deleted", "Registration deleted.")
    load_registrations()

def show_selected_qr():
    selected = reg_tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "No registration selected!")
        return
    qr_path = reg_tree.item(selected, "values")[3]  # Update index to QR Path
    if not os.path.exists(qr_path):
        messagebox.showerror("Error", "QR code image not found!")
        return
    qr_img = get_qr_image(qr_path)
    top = tk.Toplevel(root)
    top.title("QR Code")
    lbl = tk.Label(top, image=qr_img)
    lbl.image = qr_img
    lbl.pack(padx=20, pady=20)

btns_reg = tk.Frame(reg_form)
btns_reg.grid(row=0, column=2, rowspan=7, padx=28)
tk.Button(btns_reg, text="Add Registration", bg="#33cc33", fg="white", command=add_registration, width=18).pack(pady=4)
tk.Button(btns_reg, text="Update Status", bg="#ff9933", fg="white", command=update_status, width=18).pack(pady=4)
tk.Button(btns_reg, text="Delete Registration", bg="#ff3333", fg="white", command=delete_registration, width=18).pack(pady=4)
tk.Button(btns_reg, text="Show QR", bg="#3399ff", fg="white", command=show_selected_qr, width=18).pack(pady=4)
tk.Button(btns_reg, text="Refresh Registrations", bg="#3399ff", fg="white", command=lambda: load_registrations(), width=18).pack(pady=4)

def load_registrations():
    for row in reg_tree.get_children():
        reg_tree.delete(row)
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT r.reg_id, s.student_id, e.event_name, r.qr_code_path, r.entry_status
        FROM Registration r
        JOIN Student s ON r.student_id = s.student_id
        JOIN Event e ON r.event_id = e.event_id
    """)
    rows = cur.fetchall()
    for reg_id, student_id, event_name, qr_path, status in rows:
        if not qr_path or not os.path.exists(qr_path):
            qr_path = generate_qr_code(reg_id, f"REG{reg_id}", event_name)
            cur.execute("UPDATE Registration SET qr_code_path=%s WHERE reg_id=%s", (qr_path, reg_id))
            con.commit()
        reg_tree.insert("", "end", values=(reg_id, student_id, event_name, qr_path, status))
    con.close()

# ENTRY LOGS TAB
log_tree = ttk.Treeview(frame_log, columns=("LogID", "StudentID", "EventName", "RegID", "ScannedTime"), show="headings", height=16)
for col in log_tree["columns"]:
    log_tree.heading(col, text=col)
    log_tree.column(col, width=120, anchor="center")
log_tree.pack(expand=False, fill="x", padx=28, pady=(16,6))

def load_logs():
    for row in log_tree.get_children():
        log_tree.delete(row)
    # JOIN to show Student ID, Event Name for each entry log
    rows = fetch_data("""
        SELECT l.log_id, r.student_id, e.event_name, l.reg_id, l.scanned_item
        FROM Entry_log l
        JOIN Registration r ON l.reg_id = r.reg_id
        JOIN Event e ON r.event_id = e.event_id
        ORDER BY l.scanned_item DESC
    """)
    for log_id, student_id, event_name, reg_id, scanned_time in rows:
        log_tree.insert("", "end", values=(log_id, student_id, event_name, reg_id, scanned_time))

tk.Button(frame_log, text="Refresh Logs", bg="#3399ff", fg="white", command=load_logs, width=18).pack(padx=6, pady=8, anchor="w")

# INITIAL LOADS
load_students()
load_events()
load_registrations()
load_logs()

root.mainloop()

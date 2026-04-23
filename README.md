# QR-Based Entry Management System

A desktop application for managing student event registrations using QR codes. Built with Python, Tkinter, and MySQL.

---

## Features

- **Student Management** – Add and view students with their contact details
- **Event Management** – View events along with venue and admin info
- **Registration Management** – Register students for events, auto-generate QR codes, update entry status, and view/delete registrations
- **Entry Logs** – Track and display timestamped entry logs for each event
- **QR Code Generation** – Automatically generates and stores QR code images per registration

---

## Project Structure

```
├── main3.py                  # Main GUI application (Tkinter)
├── db_config.py              # MySQL database connection config
├── qr_generator.py           # QR code generation and image loading
├── generate_existing_qr.py   # Batch script to generate QRs for existing registrations
├── test_connection.py        # DB connection test utility
├── qr_entry_management.sql   # Full database schema, sample data, triggers, procedures & functions
├── qr_codes/                 # Auto-created folder where QR images are saved
└── package-lock.json
```

---

## Database Schema

| Table          | Description                                      |
|----------------|--------------------------------------------------|
| `Admin`        | Admin users who manage events                    |
| `Student`      | Student records (name, email)                    |
| `Phone`        | Student phone numbers (multi-valued)             |
| `Event`        | Events with date and admin association           |
| `Venue`        | Venue details linked to events                   |
| `Registration` | Student-event registrations with QR path & status|
| `Entry_log`    | Timestamped entry scan logs                      |
| `Enrolls`      | Many-to-many relationship between students & events |

### Triggers
- `before_registration_insert` – Validates that the event exists before registration
- `after_registration_insert` – Logs entry when a registration is created with `entry_status = TRUE`
- `after_registration_update` – Logs entry when `entry_status` is updated from `FALSE` to `TRUE`

### Stored Procedure
- `GetEventsByAdmin(adminID)` – Returns all events managed by a given admin

### Functions
- `TotalEventsByAdmin(adminID)` – Returns count of events for an admin
- `TotalStudentsInEvent(eventID)` – Returns count of enrolled students for an event

---

## Prerequisites

- Python 3.8+
- MySQL Server (running on `localhost:3306`)
- The following Python packages:

```
mysql-connector-python
qrcode[pil]
Pillow
```

Install them with:

```bash
pip install mysql-connector-python "qrcode[pil]" Pillow
```

---

## Setup

### 1. Configure the Database

Open MySQL and run the provided SQL script to create the database, tables, sample data, triggers, and routines:

```bash
mysql -u root -p < qr_entry_management.sql
```

### 2. Update Database Credentials

Edit `db_config.py` to match your MySQL credentials:

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="your_username",
        password="your_password",
        database="qr_entry_management"
    )
```

### 3. Test the Connection

```bash
python test_connection.py
```

You should see: `Connection Successful!`

### 4. Generate QR Codes for Existing Registrations (Optional)

If you loaded the sample data and want to generate QR codes for those records:

```bash
python generate_existing_qr.py
```

### 5. Run the Application

```bash
python main3.py
```

---

## Usage

| Tab             | What You Can Do                                                              |
|-----------------|------------------------------------------------------------------------------|
| **Students**    | View all students; add new students with name, email, and phone              |
| **Events**      | View all events with venue and admin details                                 |
| **Registrations** | Add/delete registrations; update entry status; view QR codes             |
| **Entry Logs**  | View a timestamped history of all scanned/entered registrations              |

QR codes are saved automatically to the `qr_codes/` folder in the project directory and their paths are stored in the database.

---

## Notes

- QR codes are generated automatically when a registration is added or when a registration's QR path is missing.
- Each QR code encodes: `REG_ID`, `STUDENT`, and `EVENT` name.
- The `entry_status` field is a boolean — `TRUE` means the student has entered the event.

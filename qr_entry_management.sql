-- Drop and recreate database
DROP DATABASE IF EXISTS qr_entry_management;
CREATE DATABASE qr_entry_management;
USE qr_entry_management;

-- Table creation
CREATE TABLE Admin (
    admin_id INT PRIMARY KEY,
    name VARCHAR(100),
    password VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE Student (
    student_id INT PRIMARY KEY,
    f_name VARCHAR(50),
    m_name VARCHAR(50),
    l_name VARCHAR(50),
    email VARCHAR(100)
);

CREATE TABLE Phone (
    student_id INT,
    phone_no VARCHAR(15),
    PRIMARY KEY (student_id, phone_no),
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Event (
    event_id INT PRIMARY KEY,
    event_name VARCHAR(100),
    event_date DATE,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Venue (
    venue_id INT PRIMARY KEY,
    capacity INT,
    venue_name VARCHAR(100),
    location VARCHAR(100),
    event_id INT,
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Registration (
    reg_id INT PRIMARY KEY,
    student_id INT,
    event_id INT,
    qr_code_path VARCHAR(255),
    entry_status BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Entry_log (
    log_id INT PRIMARY KEY,
    reg_id INT,
    scanned_item DATETIME,
    FOREIGN KEY (reg_id) REFERENCES Registration(reg_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Enrolls (
    student_id INT,
    event_id INT,
    PRIMARY KEY (student_id, event_id),
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (event_id) REFERENCES Event(event_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Sample data inserts
INSERT INTO Admin VALUES
(1, 'AdminOne', 'securepass', 'admin@example.com'),
(2, 'AdminTwo', 'pass123', 'admin2@example.com'),
(3, 'AdminThree', 'adminpass', 'admin3@example.com');

INSERT INTO Student VALUES
(101, 'Riya', 'M.', 'Patel', 'riya@example.com'),
(102, 'Amit', 'K.', 'Sharma', 'amitsharma@example.com'),
(103, 'Neha', 'R.', 'Gupta', 'neha_gupta@example.com'),
(104, 'Suresh', 'M.', 'Patel', 'suresh.patel@example.com');

INSERT INTO Phone VALUES
(101, '9876543210'),
(102, '9123456789'),
(103, '9234567890'),
(104, '9345678901');

INSERT INTO Event VALUES
(301, 'Tech Talk', '2025-10-20', 1),
(302, 'AI Workshop', '2025-11-05', 2),
(303, 'Annual Meetup', '2025-12-15', 3);

INSERT INTO Venue VALUES
(201, 150, 'Main Hall', 'Block A', 301),
(202, 80, 'Conference Room A', 'Second Floor', 302),
(203, 200, 'Auditorium', 'Main Building', 303);

INSERT INTO Registration VALUES
(401, 101, 301, '/qrcodes/tech_talk.png', TRUE),
(402, 102, 302, '/qrcodes/ai_workshop.png', TRUE),
(403, 103, 303, '/qrcodes/annual_meetup.png', FALSE);

INSERT INTO Enrolls VALUES
(101, 301),
(102, 302),
(103, 303),
(104, 301);

INSERT INTO Entry_log VALUES
(1, 401, '2025-10-20 09:00:00'),
(2, 402, '2025-11-05 10:30:00');

-- Triggers
DELIMITER //
CREATE TRIGGER before_registration_insert
BEFORE INSERT ON Registration
FOR EACH ROW
BEGIN
    DECLARE eventExists INT;
    SELECT COUNT(*) INTO eventExists FROM Event WHERE event_id = NEW.event_id;
    IF eventExists = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot insert registration: Event does not exist.';
    END IF;
END;
//

CREATE TRIGGER after_registration_insert
AFTER INSERT ON Registration
FOR EACH ROW
BEGIN
    DECLARE new_log_id INT;
    IF NEW.entry_status = TRUE THEN
        SELECT MAX_ID INTO new_log_id FROM (SELECT IFNULL(MAX(log_id), 0) + 1 AS MAX_ID FROM Entry_log) AS temp_table;
        INSERT INTO Entry_log (log_id, reg_id, scanned_item)
        VALUES (new_log_id, NEW.reg_id, NOW());
    END IF;
END;
//

CREATE TRIGGER after_registration_update
AFTER UPDATE ON Registration
FOR EACH ROW
BEGIN
    DECLARE new_log_id INT;
    IF NEW.entry_status = TRUE AND OLD.entry_status = FALSE THEN
        SELECT MAX_ID INTO new_log_id FROM (SELECT IFNULL(MAX(log_id), 0) + 1 AS MAX_ID FROM Entry_log) AS temp_table;
        INSERT INTO Entry_log (log_id, reg_id, scanned_item)
        VALUES (new_log_id, NEW.reg_id, NOW());
    END IF;
END;
//
DELIMITER ;

-- Stored Procedure
DELIMITER //
CREATE PROCEDURE GetEventsByAdmin(IN adminID INT)
BEGIN
    SELECT event_id, event_name, event_date
    FROM Event
    WHERE admin_id = adminID;
END;
//
DELIMITER ;

-- Functions
DELIMITER //
CREATE FUNCTION TotalEventsByAdmin(adminID INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM Event WHERE admin_id = adminID;
    RETURN total;
END;
//

CREATE FUNCTION TotalStudentsInEvent(eventID INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM Enrolls WHERE event_id = eventID;
    RETURN total;
END;
//
DELIMITER ;

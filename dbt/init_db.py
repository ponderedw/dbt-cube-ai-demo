"""Initialize DuckDB with raw educational data for the demo."""
import os
import sys
import duckdb

DB_PATH = os.environ.get("DUCKDB_PATH", "/data/education.duckdb")

def init(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS raw_edu")

    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.departments (
            department_id INTEGER PRIMARY KEY,
            department_name TEXT NOT NULL,
            department_code TEXT UNIQUE,
            head_faculty_id INTEGER,
            budget DECIMAL(12,2),
            building_location TEXT,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.faculty (
            faculty_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            department_id INTEGER,
            position TEXT,
            salary DECIMAL(10,2),
            hire_date DATE,
            office_number TEXT,
            research_interests TEXT[],
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.semesters (
            semester_id INTEGER PRIMARY KEY,
            semester_name TEXT NOT NULL,
            academic_year TEXT,
            start_date DATE,
            end_date DATE,
            is_current BOOLEAN DEFAULT false,
            semester_type TEXT,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.courses (
            course_id INTEGER PRIMARY KEY,
            course_code TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            description TEXT,
            credits INTEGER NOT NULL,
            department_id INTEGER,
            prerequisite_course_id INTEGER,
            difficulty_level INTEGER,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.students (
            student_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            date_of_birth DATE,
            enrollment_date DATE,
            graduation_date DATE,
            student_status TEXT,
            gpa DECIMAL(3,2),
            major_id INTEGER,
            advisor_id INTEGER,
            address_id INTEGER,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.enrollments (
            enrollment_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            course_id INTEGER,
            semester_id INTEGER,
            enrollment_date DATE,
            completion_date DATE,
            grade TEXT,
            grade_points DECIMAL(3,2),
            attendance_percentage DECIMAL(5,2),
            enrollment_status TEXT DEFAULT 'Completed',
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.class_sessions (
            session_id INTEGER PRIMARY KEY,
            course_id INTEGER,
            faculty_id INTEGER,
            semester_id INTEGER,
            session_time TIME,
            session_date DATE,
            room_id INTEGER,
            attendance_count INTEGER,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.assignments (
            assignment_id INTEGER PRIMARY KEY,
            course_id INTEGER,
            semester_id INTEGER,
            assignment_name TEXT NOT NULL,
            assignment_type TEXT,
            due_date DATE,
            max_points DECIMAL(6,2),
            weight_percentage DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.assignment_submissions (
            submission_id INTEGER PRIMARY KEY,
            assignment_id INTEGER,
            student_id INTEGER,
            submission_date TIMESTAMP,
            score DECIMAL(6,2),
            late_submission BOOLEAN DEFAULT false,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.financial_aid (
            aid_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            aid_type TEXT,
            amount DECIMAL(10,2),
            academic_year TEXT,
            disbursement_date DATE,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.tuition_payments (
            payment_id INTEGER PRIMARY KEY,
            student_id INTEGER,
            semester_id INTEGER,
            amount DECIMAL(10,2),
            payment_date DATE,
            payment_method TEXT,
            late_fee DECIMAL(8,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_edu.student_persistence (
            persistence_id INTEGER PRIMARY KEY,
            student_dcid INTEGER,
            student_number VARCHAR(20),
            in_school_year_attrition_flag BOOLEAN NOT NULL DEFAULT FALSE,
            academic_year VARCHAR(10),
            semester_id INTEGER,
            created_at TIMESTAMP DEFAULT current_timestamp
        )
    """)


def seed(con: duckdb.DuckDBPyConnection) -> None:
    # Departments
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.departments (department_id, department_name, department_code, budget, building_location)
        VALUES
            (1, 'Computer Science', 'CS', 2500000.00, 'Tech Building A'),
            (2, 'Mathematics', 'MATH', 1800000.00, 'Science Hall'),
            (3, 'Business Administration', 'BUS', 3200000.00, 'Business Center'),
            (4, 'Psychology', 'PSYC', 1500000.00, 'Liberal Arts Building'),
            (5, 'Engineering', 'ENG', 4000000.00, 'Engineering Complex')
    """)

    # Faculty
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.faculty (faculty_id, first_name, last_name, email, department_id, position, salary, hire_date, office_number)
        VALUES
            (1, 'John', 'Smith', 'j.smith@edu.edu', 1, 'Professor', 95000.00, '2015-08-15', 'TA-201'),
            (2, 'Sarah', 'Johnson', 's.johnson@edu.edu', 1, 'Associate Professor', 78000.00, '2018-01-10', 'TA-205'),
            (3, 'Michael', 'Brown', 'm.brown@edu.edu', 2, 'Professor', 89000.00, '2012-09-01', 'SH-301'),
            (4, 'Emily', 'Davis', 'e.davis@edu.edu', 3, 'Assistant Professor', 72000.00, '2020-08-20', 'BC-401'),
            (5, 'Robert', 'Wilson', 'r.wilson@edu.edu', 5, 'Professor', 105000.00, '2010-01-15', 'EC-101')
    """)

    # Semesters
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.semesters (semester_id, semester_name, academic_year, start_date, end_date, is_current, semester_type)
        VALUES
            (1, 'Fall 2023', '2023-2024', '2023-08-28', '2023-12-15', false, 'Fall'),
            (2, 'Spring 2024', '2023-2024', '2024-01-15', '2024-05-10', false, 'Spring'),
            (3, 'Fall 2024', '2024-2025', '2024-08-26', '2024-12-13', true, 'Fall'),
            (4, 'Spring 2025', '2024-2025', '2025-01-13', '2025-05-08', false, 'Spring')
    """)

    # Courses
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.courses (course_id, course_code, course_name, credits, department_id, difficulty_level)
        VALUES
            (1,  'CS101',   'Introduction to Computer Science', 3, 1, 1),
            (2,  'CS201',   'Data Structures and Algorithms',   4, 1, 3),
            (3,  'CS301',   'Database Systems',                 3, 1, 3),
            (4,  'CS401',   'Machine Learning',                 4, 1, 4),
            (5,  'MATH101', 'Calculus I',                       4, 2, 2),
            (6,  'MATH201', 'Linear Algebra',                   3, 2, 3),
            (7,  'MATH301', 'Statistics',                       3, 2, 2),
            (8,  'BUS101',  'Introduction to Business',         3, 3, 1),
            (9,  'BUS201',  'Marketing Principles',             3, 3, 2),
            (10, 'BUS301',  'Financial Management',             4, 3, 3),
            (11, 'PSYC101', 'General Psychology',               3, 4, 1),
            (12, 'ENG101',  'Engineering Fundamentals',         4, 5, 2)
    """)

    # Students
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.students (student_id, first_name, last_name, email, date_of_birth, enrollment_date, student_status, gpa, major_id, address_id)
        VALUES
            (1, 'Alice',   'Anderson', 'alice.anderson@student.edu',   '2002-03-15', '2022-08-28', 'active',    3.75, 1, 1),
            (2, 'Bob',     'Baker',    'bob.baker@student.edu',         '2001-11-22', '2021-08-30', 'active',    3.20, 1, 2),
            (3, 'Charlie', 'Chen',     'charlie.chen@student.edu',      '2003-07-08', '2023-08-28', 'active',    3.90, 2, 3),
            (4, 'Diana',   'Davis',    'diana.davis@student.edu',       '2002-01-12', '2022-08-28', 'active',    3.45, 3, 4),
            (5, 'Edward',  'Evans',    'edward.evans@student.edu',      '2000-09-18', '2020-08-31', 'graduated', 3.60, 1, 5),
            (6, 'Fiona',   'Foster',   'fiona.foster@student.edu',      '2002-05-25', '2022-08-28', 'active',    3.85, 5, 6),
            (7, 'George',  'Garcia',   'george.garcia@student.edu',     '2003-12-03', '2023-08-28', 'active',    2.95, 4, 7),
            (8, 'Hannah',  'Harris',   'hannah.harris@student.edu',     '2001-06-14', '2021-08-30', 'active',    3.70, 2, 8)
    """)

    # Enrollments
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.enrollments
            (enrollment_id, student_id, course_id, semester_id, enrollment_date, grade, grade_points, attendance_percentage, enrollment_status, completion_date)
        VALUES
            (1,  1, 1, 3, '2024-08-26', 'A',  3.7, 95.0, 'Completed', '2024-12-13'),
            (2,  1, 5, 3, '2024-08-26', 'B+', 3.3, 88.0, 'Completed', '2024-12-13'),
            (3,  2, 1, 3, '2024-08-26', 'B',  3.0, 82.0, 'Completed', '2024-12-13'),
            (4,  2, 2, 3, '2024-08-26', 'A-', 3.5, 90.0, 'Completed', '2024-12-13'),
            (5,  3, 5, 3, '2024-08-26', 'A',  4.0, 98.0, 'Completed', '2024-12-13'),
            (6,  3, 6, 3, '2024-08-26', 'A',  3.8, 96.0, 'Completed', '2024-12-13'),
            (7,  4, 8, 3, '2024-08-26', 'B+', 3.3, 85.0, 'Completed', '2024-12-13'),
            (8,  4, 9, 3, '2024-08-26', 'A-', 3.7, 92.0, 'Completed', '2024-12-13'),
            (9,  5, 1, 2, '2024-01-15', 'A-', 3.7, 93.0, 'Completed', '2024-05-10'),
            (10, 6, 1, 2, '2024-01-15', 'B',  3.0, 87.0, 'Completed', '2024-05-10'),
            (11, 7, 1, 2, '2024-01-15', 'C+', 2.3, 78.0, 'Completed', '2024-05-10'),
            (12, 8, 1, 2, '2024-01-15', 'B+', 3.3, 91.0, 'Completed', '2024-05-10'),
            (13, 3, 2, 3, '2024-08-26', 'A',  4.0, 95.0, 'Completed', '2024-12-13'),
            (14, 4, 2, 3, '2024-08-26', 'B-', 2.7, 84.0, 'Completed', '2024-12-13'),
            (15, 5, 2, 2, '2024-01-15', 'B+', 3.3, 89.0, 'Completed', '2024-05-10'),
            (16, 6, 2, 2, '2024-01-15', 'A-', 3.7, 92.0, 'Completed', '2024-05-10'),
            (17, 1, 6, 3, '2024-08-26', 'B+', 3.3, 88.0, 'Completed', '2024-12-13'),
            (18, 2, 6, 3, '2024-08-26', 'A',  4.0, 96.0, 'Completed', '2024-12-13'),
            (19, 4, 6, 3, '2024-08-26', 'B',  3.0, 85.0, 'Completed', '2024-12-13'),
            (20, 5, 8, 2, '2024-01-15', 'B+', 3.3, 90.0, 'Completed', '2024-05-10'),
            (21, 6, 8, 2, '2024-01-15', 'A',  4.0, 94.0, 'Completed', '2024-05-10'),
            (22, 7, 8, 2, '2024-01-15', 'B',  3.0, 86.0, 'Completed', '2024-05-10'),
            (23, 1, 9, 3, '2024-08-26', 'A-', 3.7, 91.0, 'Completed', '2024-12-13'),
            (24, 2, 9, 3, '2024-08-26', 'B+', 3.3, 88.0, 'Completed', '2024-12-13'),
            (25, 3, 9, 3, '2024-08-26', 'A',  4.0, 97.0, 'Completed', '2024-12-13')
    """)

    # Class sessions
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.class_sessions
            (session_id, course_id, faculty_id, semester_id, session_date, session_time, attendance_count)
        VALUES
            (1, 1, 1, 3, '2024-08-26', '10:00:00', 25),
            (2, 2, 1, 3, '2024-08-26', '14:00:00', 20),
            (3, 5, 3, 3, '2024-08-26', '09:00:00', 30),
            (4, 6, 3, 3, '2024-08-26', '11:00:00', 22),
            (5, 8, 4, 3, '2024-08-26', '13:00:00', 35),
            (6, 9, 4, 3, '2024-08-26', '15:00:00', 28),
            (7, 1, 1, 2, '2024-01-15', '10:00:00', 22),
            (8, 2, 1, 2, '2024-01-15', '14:00:00', 18),
            (9, 8, 4, 2, '2024-01-15', '13:00:00', 32)
    """)

    # Assignments
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.assignments
            (assignment_id, course_id, semester_id, assignment_name, assignment_type, due_date, max_points, weight_percentage)
        VALUES
            (1,  1, 3, 'Homework 1: Basic Programming',      'homework',   '2024-09-15', 100.00, 15.0),
            (2,  1, 3, 'Midterm Exam',                       'exam',       '2024-10-15', 200.00, 30.0),
            (3,  1, 3, 'Final Project',                      'project',    '2024-12-10', 300.00, 40.0),
            (4,  2, 3, 'Algorithm Analysis',                 'homework',   '2024-09-20', 150.00, 20.0),
            (5,  2, 3, 'Data Structure Implementation',      'project',    '2024-11-15', 250.00, 35.0),
            (6,  5, 3, 'Calculus Problem Set 1',             'homework',   '2024-09-10', 80.00,  10.0),
            (7,  5, 3, 'Calculus Midterm',                   'exam',       '2024-10-20', 150.00, 25.0),
            (8,  6, 3, 'Linear Algebra Assignments',         'homework',   '2024-09-25', 120.00, 20.0),
            (9,  8, 3, 'Business Case Study',                'case_study', '2024-10-05', 100.00, 25.0),
            (10, 9, 3, 'Marketing Campaign Project',         'project',    '2024-11-20', 200.00, 40.0)
    """)

    # Assignment submissions
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.assignment_submissions
            (submission_id, assignment_id, student_id, submission_date, score, late_submission, feedback)
        VALUES
            (1,  1, 1, '2024-09-14 15:30:00', 92.00, false, 'Excellent work on basic programming concepts'),
            (2,  1, 2, '2024-09-16 10:20:00', 78.00, true,  'Good effort, submitted late'),
            (3,  2, 1, '2024-10-14 14:00:00', 185.00, false, 'Outstanding performance on midterm'),
            (4,  2, 2, '2024-10-15 14:00:00', 165.00, false, 'Solid understanding of concepts'),
            (5,  4, 2, '2024-09-19 16:45:00', 140.00, false, 'Great analysis of algorithms'),
            (6,  6, 3, '2024-09-09 12:00:00', 75.00,  false, 'Good work on calculus problems'),
            (7,  7, 3, '2024-10-19 13:30:00', 138.00, false, 'Strong performance on midterm'),
            (8,  8, 3, '2024-09-24 18:20:00', 110.00, false, 'Excellent linear algebra work'),
            (9,  9, 4, '2024-10-04 11:15:00', 88.00,  false, 'Insightful business case analysis'),
            (10, 10, 4, '2024-11-19 22:30:00', 175.00, false, 'Creative marketing campaign')
    """)

    # Financial aid
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.financial_aid
            (aid_id, student_id, aid_type, amount, academic_year, disbursement_date)
        VALUES
            (1, 1, 'Merit Scholarship',           5000.00, '2024-2025', '2024-08-15'),
            (2, 2, 'Need-based Grant',             3500.00, '2024-2025', '2024-08-15'),
            (3, 3, 'Academic Excellence Award',   7500.00, '2024-2025', '2024-08-15'),
            (4, 4, 'Work Study',                  2000.00, '2024-2025', '2024-09-01'),
            (5, 5, 'Merit Scholarship',            4000.00, '2023-2024', '2023-08-15'),
            (6, 6, 'Engineering Excellence Grant', 6000.00, '2024-2025', '2024-08-15'),
            (7, 7, 'Need-based Grant',             2500.00, '2024-2025', '2024-08-15'),
            (8, 8, 'Dean''s List Scholarship',     3000.00, '2024-2025', '2024-08-15')
    """)

    # Tuition payments
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.tuition_payments
            (payment_id, student_id, semester_id, amount, payment_date, payment_method, late_fee)
        VALUES
            (1, 1, 3, 12500.00, '2024-08-20', 'Credit Card',   0.00),
            (2, 2, 3, 12500.00, '2024-08-25', 'Bank Transfer', 0.00),
            (3, 3, 3, 12500.00, '2024-08-18', 'Check',         0.00),
            (4, 4, 3, 12500.00, '2024-09-05', 'Credit Card',   150.00),
            (5, 6, 3, 15000.00, '2024-08-22', 'Bank Transfer', 0.00),
            (6, 7, 3, 12500.00, '2024-08-30', 'Credit Card',   0.00),
            (7, 8, 3, 12500.00, '2024-08-19', 'Check',         0.00)
    """)

    # Student persistence
    con.execute("""
        INSERT OR IGNORE INTO raw_edu.student_persistence
            (persistence_id, student_dcid, student_number, in_school_year_attrition_flag, academic_year, semester_id)
        VALUES
            (1, 1, 'STU001', false, '2023-2024', 1),
            (2, 2, 'STU002', false, '2023-2024', 1),
            (3, 3, 'STU003', true,  '2023-2024', 2),
            (4, 4, 'STU004', false, '2024-2025', 3),
            (5, 5, 'STU005', false, '2024-2025', 3),
            (6, 6, 'STU006', false, '2024-2025', 3),
            (7, 7, 'STU007', false, '2024-2025', 3),
            (8, 8, 'STU008', true,  '2024-2025', 3)
    """)

    print("Raw data seeded successfully.")


def main() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    print(f"Initializing DuckDB at {DB_PATH}")
    con = duckdb.connect(DB_PATH)
    init(con)
    seed(con)
    con.close()
    print("Done.")


if __name__ == "__main__":
    main()

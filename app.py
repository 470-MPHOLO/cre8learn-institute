import streamlit as st
import pandas as pd
import json
import random
import os
import base64
from datetime import datetime, timedelta
import time
import re
from io import BytesIO
import sqlite3

# Page configuration
st.set_page_config(
    page_title="Cre8Learn Institute",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        background: linear-gradient(135deg, #1E90FF 0%, #2E8B57 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .main-logo {
        font-size: 4rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    }
    .institute-subtitle {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .student-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2E8B57;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .quiz-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .material-card {
        background: linear-gradient(135deg, #e7f3ff 0%, #d4edff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #1E90FF;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #1E90FF;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .verified-badge {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .unverified-badge {
        background: #dc3545;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize SQLite Database
def init_database():
    conn = sqlite3.connect('cre8learn.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            courses TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            status TEXT NOT NULL,
            grades TEXT NOT NULL,
            progress TEXT NOT NULL,
            fees_paid TEXT NOT NULL,
            email_verified BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Course materials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            file_name TEXT,
            file_content BLOB,
            file_type TEXT,
            upload_date TEXT NOT NULL,
            uploaded_by TEXT
        )
    ''')
    
    # Quizzes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            quiz_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            course TEXT NOT NULL,
            duration INTEGER NOT NULL,
            questions TEXT NOT NULL,
            created_date TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Quiz results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            completed_date TEXT NOT NULL,
            answers TEXT NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (quiz_id),
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    # Email verification table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_verification (
            email TEXT PRIMARY KEY,
            verification_code TEXT NOT NULL,
            created_date TEXT NOT NULL,
            verified BOOLEAN DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    return conn

# Initialize database
DB_CONN = init_database()

class StudentManager:
    def __init__(self):
        self.conn = DB_CONN
        
    def generate_student_id(self):
        while True:
            new_id = f"CL{random.randint(100000, 999999)}"
            cursor = self.conn.cursor()
            cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (new_id,))
            if not cursor.fetchone():
                return new_id
    
    def generate_verification_code(self):
        return f"{random.randint(100000, 999999)}"
    
    def verify_email_format(self, email):
        # Simple but effective email validation
        if not email or '@' not in email or '.' not in email:
            return False
        
        parts = email.split('@')
        if len(parts) != 2 or not parts[0]:
            return False
            
        domain_parts = parts[1].split('.')
        if len(domain_parts) < 2 or not all(domain_parts):
            return False
            
        return True
    
    def save_verification_code(self, email, code):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO email_verification 
            (email, verification_code, created_date, verified)
            VALUES (?, ?, ?, ?)
        ''', (email, code, datetime.now().isoformat(), False))
        self.conn.commit()
    
    def verify_email_code(self, email, code):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT verification_code, created_date FROM email_verification 
            WHERE email = ? AND verified = FALSE
        ''', (email,))
        result = cursor.fetchone()
        
        if result:
            stored_code, created_date = result
            time_diff = datetime.now() - datetime.fromisoformat(created_date)
            if time_diff.total_seconds() < 600:  # 10 minutes
                if stored_code == code:
                    cursor.execute('''
                        UPDATE email_verification SET verified = TRUE WHERE email = ?
                    ''', (email,))
                    cursor.execute('''
                        UPDATE students SET email_verified = TRUE WHERE email = ?
                    ''', (email,))
                    self.conn.commit()
                    return True
        return False
    
    def add_student(self, name, age, email, phone, courses):
        student_id = self.generate_student_id()
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO students 
            (student_id, name, age, email, phone, courses, registration_date, status, grades, progress, fees_paid, email_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, name, age, email, phone, 
            json.dumps(courses),
            datetime.now().isoformat(),
            'Active',
            json.dumps({course: 'Not Assessed' for course in courses}),
            json.dumps({course: '0%' for course in courses}),
            json.dumps({course: False for course in courses}),
            False
        ))
        self.conn.commit()
        return student_id
    
    def get_students(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = []
        for row in cursor.fetchall():
            student = {
                'student_id': row[0],
                'name': row[1],
                'age': row[2],
                'email': row[3],
                'phone': row[4],
                'courses': json.loads(row[5]),
                'registration_date': row[6],
                'status': row[7],
                'grades': json.loads(row[8]),
                'progress': json.loads(row[9]),
                'fees_paid': json.loads(row[10]),
                'email_verified': bool(row[11])
            }
            students.append(student)
        return students
    
    def search_student(self, student_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        if row:
            return {
                'student_id': row[0],
                'name': row[1],
                'age': row[2],
                'email': row[3],
                'phone': row[4],
                'courses': json.loads(row[5]),
                'registration_date': row[6],
                'status': row[7],
                'grades': json.loads(row[8]),
                'progress': json.loads(row[9]),
                'fees_paid': json.loads(row[10]),
                'email_verified': bool(row[11])
            }
        return None
    
    def add_course_to_student(self, student_id, course):
        student = self.search_student(student_id)
        if student and course not in student['courses']:
            student['courses'].append(course)
            student['grades'][course] = 'Not Assessed'
            student['progress'][course] = '0%'
            student['fees_paid'][course] = False
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE students SET 
                courses = ?, grades = ?, progress = ?, fees_paid = ?
                WHERE student_id = ?
            ''', (
                json.dumps(student['courses']),
                json.dumps(student['grades']),
                json.dumps(student['progress']),
                json.dumps(student['fees_paid']),
                student_id
            ))
            self.conn.commit()
            return True
        return False
    
    def update_student_progress(self, student_id, course, progress, grade=None):
        student = self.search_student(student_id)
        if student and course in student['courses']:
            student['progress'][course] = progress
            if grade:
                student['grades'][course] = grade
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE students SET progress = ?, grades = ? WHERE student_id = ?
            ''', (json.dumps(student['progress']), json.dumps(student['grades']), student_id))
            self.conn.commit()
            return True
        return False

class CourseManager:
    def __init__(self):
        self.conn = DB_CONN
    
    def save_course_material(self, course_name, title, description, file_name, file_content, file_type, uploaded_by="Admin"):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO course_materials 
            (course_name, title, description, file_name, file_content, file_type, upload_date, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            course_name, title, description, file_name, 
            file_content, file_type,
            datetime.now().isoformat(), uploaded_by
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_course_materials(self, course_name=None):
        cursor = self.conn.cursor()
        if course_name:
            cursor.execute("SELECT * FROM course_materials WHERE course_name = ? ORDER BY upload_date DESC", (course_name,))
        else:
            cursor.execute("SELECT * FROM course_materials ORDER BY upload_date DESC")
        
        materials = []
        for row in cursor.fetchall():
            materials.append({
                'id': row[0],
                'course_name': row[1],
                'title': row[2],
                'description': row[3],
                'file_name': row[4],
                'file_content': row[5],
                'file_type': row[6],
                'upload_date': row[7],
                'uploaded_by': row[8]
            })
        return materials
    
    def delete_course_material(self, material_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM course_materials WHERE id = ?", (material_id,))
        self.conn.commit()
        return cursor.rowcount > 0

class QuizManager:
    def __init__(self):
        self.conn = DB_CONN
    
    def create_quiz(self, quiz_id, title, course, duration, questions):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO quizzes (quiz_id, title, course, duration, questions, created_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (quiz_id, title, course, duration, json.dumps(questions), datetime.now().isoformat(), True))
        self.conn.commit()
    
    def get_quizzes(self, course=None, active_only=True):
        cursor = self.conn.cursor()
        if course:
            if active_only:
                cursor.execute("SELECT * FROM quizzes WHERE course = ? AND is_active = TRUE ORDER BY created_date DESC", (course,))
            else:
                cursor.execute("SELECT * FROM quizzes WHERE course = ? ORDER BY created_date DESC", (course,))
        else:
            if active_only:
                cursor.execute("SELECT * FROM quizzes WHERE is_active = TRUE ORDER BY created_date DESC")
            else:
                cursor.execute("SELECT * FROM quizzes ORDER BY created_date DESC")
        
        quizzes = []
        for row in cursor.fetchall():
            quizzes.append({
                'quiz_id': row[0],
                'title': row[1],
                'course': row[2],
                'duration': row[3],
                'questions': json.loads(row[4]),
                'created_date': row[5],
                'is_active': bool(row[6])
            })
        return quizzes
    
    def save_quiz_result(self, quiz_id, student_id, score, total_questions, answers):
        percentage = (score / total_questions) * 100
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO quiz_results 
            (quiz_id, student_id, score, total_questions, percentage, completed_date, answers)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (quiz_id, student_id, score, total_questions, percentage, datetime.now().isoformat(), json.dumps(answers)))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_student_results(self, student_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT qr.*, q.title, q.course 
            FROM quiz_results qr
            JOIN quizzes q ON qr.quiz_id = q.quiz_id
            WHERE qr.student_id = ?
            ORDER BY qr.completed_date DESC
        ''', (student_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'quiz_id': row[1],
                'student_id': row[2],
                'score': row[3],
                'total_questions': row[4],
                'percentage': row[5],
                'completed_date': row[6],
                'quiz_title': row[8],
                'course': row[9]
            })
        return results

def create_logo():
    st.markdown("""
    <div class="logo-container">
        <div class="main-logo">Cre8Learn</div>
        <div class="institute-subtitle">INSTITUTE</div>
        <div style="font-size: 1.3rem; margin-bottom: 0.5rem; opacity: 0.9;">
            Maseru, Lesotho
        </div>
        <div style="font-size: 1rem; opacity: 0.8;">
            Business Registration No: A2025/28312
        </div>
    </div>
    """, unsafe_allow_html=True)

def admin_login():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin Access")
    
    if not st.session_state.get('admin_logged_in', False):
        password = st.sidebar.text_input("Admin Password", type="password", value="cre8learn2024")
        if st.sidebar.button("Login as Admin"):
            if password == "cre8learn2024":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect password")
        return False
    else:
        st.sidebar.success("✅ Admin Mode")
        if st.sidebar.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
        return True

def main():
    # Initialize managers
    student_manager = StudentManager()
    course_manager = CourseManager()
    quiz_manager = QuizManager()
    
    is_admin = admin_login()
    create_logo()
    
    # Courses list
    COURSES = [
        "Engineering Mathematics (Number Systems & Logic)",
        "Computer Hardware Basics", 
        "Windows Operating System Fundamentals",
        "Cybersecurity 1: Fundamentals, Threats & Tools",
        "Leadership, Ethics & Professional Workplace Etiquette",
        "Introduction to Computer Networking",
        "C++ 1: Introductory Programming",
        "Introduction to Programming & Computational Thinking",
        "Proficiency in English Language"
    ]
    
    # Navigation
    if is_admin:
        menu = [
            "🏠 Admin Dashboard",
            "➕ Register Student", 
            "👥 Student Management",
            "📚 Course Materials",
            "🎯 Quiz Management",
            "📊 Analytics & Reports"
        ]
    else:
        menu = [
            "🏠 Student Portal",
            "🔍 My Profile & Courses", 
            "📖 Learning Materials",
            "🎯 Take Quiz",
            "📊 My Results",
            "📞 Contact Support"
        ]
    
    choice = st.sidebar.selectbox("Menu", menu)
    
    # ADMIN SECTIONS
    if is_admin:
        if choice == "🏠 Admin Dashboard":
            st.subheader("📊 Admin Dashboard")
            
            students = student_manager.get_students()
            total_courses = sum(len(student.get('courses', [])) for student in students)
            verified_count = len([s for s in students if s.get('email_verified', False)])
            materials = course_manager.get_course_materials()
            quizzes = quiz_manager.get_quizzes()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(students))
            with col2:
                st.metric("Verified Emails", verified_count)
            with col3:
                st.metric("Course Materials", len(materials))
            with col4:
                st.metric("Active Quizzes", len(quizzes))
            
            # Recent activity
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Recent Registrations")
                recent_students = sorted(students, key=lambda x: x['registration_date'], reverse=True)[:5]
                for student in recent_students:
                    verified_status = "✅" if student['email_verified'] else "❌"
                    st.write(f"**{student['name']}** ({student['student_id']}) {verified_status}")

        elif choice == "➕ Register Student":
            st.subheader("Register New Student")
            
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name *")
                    age = st.number_input("Age *", min_value=16, max_value=100, value=25)
                    email = st.text_input("Email *")
                    
                with col2:
                    phone = st.text_input("Phone Number *")
                    selected_courses = st.multiselect("Select Courses *", COURSES)
                    auto_verify = st.checkbox("Auto-verify email", value=True)
                
                submitted = st.form_submit_button("🎯 Register Student")
                
                if submitted:
                    if name and email and phone and selected_courses:
                        if not student_manager.verify_email_format(email):
                            st.error("❌ Please enter a valid email address!")
                        else:
                            # REGISTER STUDENT FIRST
                            student_id = student_manager.add_student(name, age, email, phone, selected_courses)
                            
                            if auto_verify:
                                # Auto-verify the email
                                cursor = DB_CONN.cursor()
                                cursor.execute('''
                                    UPDATE students SET email_verified = TRUE WHERE student_id = ?
                                ''', (student_id,))
                                DB_CONN.commit()
                                st.success(f"""
                                ✅ Student registered successfully!
                                
                                **Student ID:** {student_id}  
                                **Name:** {name}  
                                **Courses:** {', '.join(selected_courses)}  
                                **Email:** ✅ Verified
                                """)
                            else:
                                # Send verification code
                                verification_code = student_manager.generate_verification_code()
                                student_manager.save_verification_code(email, verification_code)
                                
                                st.success(f"""
                                ✅ Student registered successfully!
                                
                                **Student ID:** {student_id}  
                                **Name:** {name}  
                                **Courses:** {', '.join(selected_courses)}
                                """)
                                
                                st.info(f"📧 **Verification Code:** {verification_code}")
                                st.write("Share this code with the student to verify their email in the Student Portal.")
                    else:
                        st.error("Please fill all required fields (*)")

        elif choice == "👥 Student Management":
            st.subheader("Student Management")
            
            students = student_manager.get_students()
            if students:
                for student in students:
                    with st.expander(f"🎯 {student['name']} ({student['student_id']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Personal Info**")
                            st.write(f"**Email:** {student['email']}")
                            st.write(f"**Phone:** {student['phone']}")
                            st.write(f"**Status:** {student['status']}")
                            st.write(f"**Verified:** {'✅ Yes' if student['email_verified'] else '❌ No'}")
                        
                        with col2:
                            st.write("**Courses & Progress**")
                            for course in student['courses']:
                                progress = student['progress'][course]
                                grade = student['grades'][course]
                                st.write(f"• **{course}:** {progress} | {grade}")

        elif choice == "📚 Course Materials":
            st.subheader("Course Materials Management")
            
            selected_course = st.selectbox("Select Course", COURSES)
            
            tab1, tab2 = st.tabs(["📁 Upload Materials", "📋 View Materials"])
            
            with tab1:
                st.subheader("Upload Course Material")
                
                material_title = st.text_input("Material Title *")
                material_description = st.text_area("Description")
                uploaded_file = st.file_uploader("Choose file *", type=['pdf', 'docx', 'ppt', 'pptx', 'txt', 'jpg', 'png'])
                
                if st.button("Upload Material"):
                    if material_title and uploaded_file and selected_course:
                        # Read file content
                        file_content = uploaded_file.read()
                        file_type = uploaded_file.type
                        
                        # Save to database
                        material_id = course_manager.save_course_material(
                            selected_course, material_title, material_description,
                            uploaded_file.name, file_content, file_type
                        )
                        
                        st.success(f"✅ Material '{material_title}' uploaded successfully!")
                    else:
                        st.error("Please fill all required fields (*)")
            
            with tab2:
                st.subheader("Course Materials")
                materials = course_manager.get_course_materials(selected_course)
                
                if materials:
                    for material in materials:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**{material['title']}**")
                            st.write(material['description'])
                            st.write(f"*Uploaded: {material['upload_date'][:16]}*")
                        
                        with col2:
                            # Download button
                            st.download_button(
                                label="Download",
                                data=material['file_content'],
                                file_name=material['file_name'],
                                mime=material['file_type'],
                                key=f"dl_{material['id']}"
                            )
                        
                        with col3:
                            if st.button("Delete", key=f"del_{material['id']}"):
                                if course_manager.delete_course_material(material['id']):
                                    st.success("Material deleted!")
                                    st.rerun()

        elif choice == "🎯 Quiz Management":
            st.subheader("Quiz Management")
            
            tab1, tab2 = st.tabs(["➕ Create Quiz", "📋 Manage Quizzes"])
            
            with tab1:
                st.subheader("Create New Quiz")
                
                quiz_title = st.text_input("Quiz Title *")
                quiz_course = st.selectbox("Course *", COURSES)
                quiz_duration = st.number_input("Duration (minutes) *", min_value=1, max_value=180, value=30)
                
                st.subheader("Add Questions")
                
                if 'quiz_questions' not in st.session_state:
                    st.session_state.quiz_questions = []
                
                with st.form("add_question_form"):
                    question_text = st.text_area("Question *")
                    col1, col2 = st.columns(2)
                    with col1:
                        option_a = st.text_input("Option A *")
                        option_b = st.text_input("Option B *")
                    with col2:
                        option_c = st.text_input("Option C")
                        option_d = st.text_input("Option D")
                    correct_answer = st.selectbox("Correct Answer *", ["A", "B", "C", "D"])
                    
                    if st.form_submit_button("Add Question"):
                        if question_text and option_a and option_b:
                            st.session_state.quiz_questions.append({
                                'question': question_text,
                                'options': [opt for opt in [option_a, option_b, option_c, option_d] if opt],
                                'correct': correct_answer
                            })
                            st.success("✅ Question added!")
                
                if st.session_state.quiz_questions:
                    st.write("**Current Questions:**")
                    for i, q in enumerate(st.session_state.quiz_questions):
                        st.write(f"{i+1}. {q['question']}")
                
                if st.button("Create Quiz", type="primary"):
                    if quiz_title and quiz_course and st.session_state.quiz_questions:
                        quiz_id = f"quiz_{int(time.time())}"
                        quiz_manager.create_quiz(quiz_id, quiz_title, quiz_course, quiz_duration, st.session_state.quiz_questions)
                        st.session_state.quiz_questions = []
                        st.success(f"✅ Quiz '{quiz_title}' created successfully!")
                    else:
                        st.error("Please fill all required fields and add at least one question!")
            
            with tab2:
                st.subheader("Existing Quizzes")
                quizzes = quiz_manager.get_quizzes(active_only=False)
                
                if quizzes:
                    for quiz in quizzes:
                        with st.expander(f"🎯 {quiz['title']} - {quiz['course']}"):
                            st.write(f"**Duration:** {quiz['duration']} minutes")
                            st.write(f"**Questions:** {len(quiz['questions'])}")
                            st.write(f"**Created:** {quiz['created_date'][:16]}")
                            st.write(f"**Status:** {'✅ Active' if quiz['is_active'] else '❌ Inactive'}")

    # STUDENT SECTIONS
    else:
        if choice == "🏠 Student Portal":
            st.subheader("Welcome to Cre8Learn Institute")
            
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = student_manager.search_student(student_id)
                if student:
                    st.success(f"Welcome back, {student['name']}! 🎉")
                    
                    # Dashboard
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Courses", len(student['courses']))
                    with col2:
                        completed = sum(1 for course in student['courses'] if student['progress'][course] == '100%')
                        st.metric("Completed", completed)
                    with col3:
                        email_status = "✅ Verified" if student['email_verified'] else "❌ Pending"
                        st.metric("Email Status", email_status)
                    
                    # Email verification section
                    if not student['email_verified']:
                        st.markdown("---")
                        st.subheader("📧 Verify Your Email")
                        st.warning("Your email is not verified. Please verify to access all features.")
                        
                        verification_code = st.text_input("Enter verification code:")
                        if st.button("Verify Email"):
                            if student_manager.verify_email_code(student['email'], verification_code):
                                st.success("✅ Email verified successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Invalid verification code!")
                    
                    # Course progress
                    st.subheader("📚 Your Course Progress")
                    for course in student['courses']:
                        progress = student['progress'][course]
                        grade = student['grades'][course]
                        
                        st.markdown(f"""
                        <div class="student-card">
                            <strong>📖 {course}</strong><br>
                            Progress: <strong>{progress}</strong> | Grade: <strong>{grade}</strong><br>
                            Status: {'✅ Completed' if progress == '100%' else '📚 In Progress'}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("Student ID not found. Please check your ID.")

        elif choice == "📖 Learning Materials":
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = student_manager.search_student(student_id)
                if student:
                    st.subheader("Available Learning Materials")
                    
                    for course in student['courses']:
                        st.write(f"### 📚 {course}")
                        materials = course_manager.get_course_materials(course)
                        
                        if materials:
                            for material in materials:
                                st.markdown(f"""
                                <div class="material-card">
                                    <strong>📄 {material['title']}</strong><br>
                                    {material['description']}<br>
                                    <small>Available since: {material['upload_date'][:16]}</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Download button
                                st.download_button(
                                    label=f"Download {material['file_name']}",
                                    data=material['file_content'],
                                    file_name=material['file_name'],
                                    mime=material['file_type'],
                                    key=f"dl_{material['id']}"
                                )
                                st.write("---")
                        else:
                            st.info("No materials available for this course yet.")

        elif choice == "🎯 Take Quiz":
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = student_manager.search_student(student_id)
                if student:
                    st.subheader("Available Quizzes")
                    
                    available_quizzes = []
                    for course in student['courses']:
                        quizzes = quiz_manager.get_quizzes(course=course, active_only=True)
                        available_quizzes.extend(quizzes)
                    
                    if available_quizzes:
                        for quiz in available_quizzes:
                            st.markdown(f"""
                            <div class="quiz-card">
                                <strong>🎯 {quiz['title']}</strong><br>
                                Course: {quiz['course']}<br>
                                Duration: {quiz['duration']} minutes<br>
                                Questions: {len(quiz['questions'])}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("Start Quiz", key=f"start_{quiz['quiz_id']}"):
                                st.session_state.current_quiz = quiz
                                st.session_state.quiz_start_time = datetime.now()
                                st.session_state.quiz_answers = {}
                                st.rerun()
                    else:
                        st.info("No quizzes available for your courses yet.")

        elif choice == "📊 My Results":
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = student_manager.search_student(student_id)
                if student:
                    st.subheader("Your Quiz Results")
                    
                    results = quiz_manager.get_student_results(student_id)
                    if results:
                        for result in results:
                            st.write(f"**{result['quiz_title']}** ({result['course']})")
                            st.write(f"Score: {result['score']}/{result['total_questions']} ({result['percentage']:.1f}%)")
                            st.write(f"Completed: {result['completed_date'][:16]}")
                            st.write("---")
                    else:
                        st.info("No quiz results yet.")

        elif choice == "📞 Contact Support":
            st.subheader("Contact Cre8Learn Institute")
            st.info("""
            **Institute Information:**
            - **Business Registration:** A2025/28312
            - **Location:** Maseru, Lesotho
            
            **Support Channels:**
            - 📧 Email: support@cre8learn.com
            - 📞 Phone: +266 1234 5678
            - 🕒 Hours: Mon-Fri, 8AM-5PM
            """)

if __name__ == "__main__":
    main()

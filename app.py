import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime, timedelta
import time
import re

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
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(135deg, #1E90FF 0%, #2E8B57 100%);
        border-radius: 15px;
        color: white;
    }
    .main-logo {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .institute-subtitle {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    .student-card {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 1rem 0;
    }
    .quiz-card {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .material-card {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #1E90FF;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StudentManager:
    def __init__(self):
        if 'students' not in st.session_state:
            st.session_state.students = []
        if 'admin_logged_in' not in st.session_state:
            st.session_state.admin_logged_in = False
        if 'course_materials' not in st.session_state:
            st.session_state.course_materials = {}
        if 'quizzes' not in st.session_state:
            st.session_state.quizzes = {}
        if 'student_results' not in st.session_state:
            st.session_state.student_results = {}
        if 'email_verification' not in st.session_state:
            st.session_state.email_verification = {}
    
    def generate_student_id(self):
        while True:
            new_id = f"CL{random.randint(100000, 999999)}"
            if not any(student['student_id'] == new_id for student in st.session_state.students):
                return new_id
    
    def generate_verification_code(self):
        return f"{random.randint(100000, 999999)}"
    
    def verify_email_format(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def send_verification_code(self, email, code):
        # Simulate sending email (in real app, integrate with email service)
        st.session_state.email_verification[email] = {
            'code': code,
            'timestamp': datetime.now(),
            'verified': False
        }
    
    def verify_email_code(self, email, code):
        if email in st.session_state.email_verification:
            verification_data = st.session_state.email_verification[email]
            time_diff = datetime.now() - verification_data['timestamp']
            if time_diff.total_seconds() < 600:  # 10 minutes expiry
                if verification_data['code'] == code:
                    st.session_state.email_verification[email]['verified'] = True
                    return True
        return False
    
    def get_students(self):
        return st.session_state.students
    
    def add_student(self, name, age, email, phone, courses):
        student_id = self.generate_student_id()
        new_student = {
            'student_id': student_id,
            'name': name,
            'age': int(age),
            'email': email,
            'phone': phone,
            'courses': courses,  # Now supports multiple courses
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'Active',
            'grades': {course: 'Not Assessed' for course in courses},
            'progress': {course: '0%' for course in courses},
            'fees_paid': {course: False for course in courses},
            'email_verified': st.session_state.email_verification.get(email, {}).get('verified', False)
        }
        st.session_state.students.append(new_student)
        return student_id
    
    def search_student(self, student_id):
        for student in st.session_state.students:
            if student['student_id'] == student_id:
                return student
        return None
    
    def add_course_to_student(self, student_id, course):
        student = self.search_student(student_id)
        if student and course not in student['courses']:
            student['courses'].append(course)
            student['grades'][course] = 'Not Assessed'
            student['progress'][course] = '0%'
            student['fees_paid'][course] = False
            return True
        return False
    
    def update_student(self, student_id, name, age, email, phone, status, grades=None, progress=None, fees_paid=None):
        student = self.search_student(student_id)
        if student:
            student.update({
                'name': name,
                'age': int(age),
                'email': email,
                'phone': phone,
                'status': status
            })
            if grades:
                student['grades'].update(grades)
            if progress:
                student['progress'].update(progress)
            if fees_paid:
                student['fees_paid'].update(fees_paid)
            return True
        return False
    
    def delete_student(self, student_id):
        st.session_state.students = [s for s in st.session_state.students if s['student_id'] != student_id]
        return True

def admin_login():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin Access")
    
    if not st.session_state.admin_logged_in:
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

def create_logo():
    st.markdown("""
    <div class="logo-container">
        <div class="main-logo">Cre8Learn</div>
        <div class="institute-subtitle">INSTITUTE</div>
        <div class="tagline">Maseru, Lesotho</div>
        <div class="registration-info">Business Registration No: A2025/28312</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Initialize manager
    manager = StudentManager()
    is_admin = admin_login()
    
    # Create custom logo
    create_logo()
    
    # Courses list from your curriculum
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
    
    # Sidebar Navigation
    if is_admin:
        menu = [
            "🏠 Admin Dashboard",
            "➕ Register Student", 
            "👥 View All Students",
            "🔍 Search Student",
            "📚 Course Management",
            "🎯 Assessment Center",
            "💰 Fee Management",
            "⏰ Quiz Manager",
            "📊 Analytics"
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
    
    # ADMIN FUNCTIONALITY
    if is_admin:
        if choice == "🏠 Admin Dashboard":
            st.subheader("📊 Admin Dashboard")
            
            students = manager.get_students()
            total_courses = sum(len(student.get('courses', [])) for student in students)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(students))
            with col2:
                st.metric("Total Course Registrations", total_courses)
            with col3:
                verified = len([s for s in students if s.get('email_verified', False)])
                st.metric("Verified Emails", verified)
            with col4:
                active_quizzes = len(st.session_state.quizzes)
                st.metric("Active Quizzes", active_quizzes)
            
            # Quick actions
            st.subheader("🚀 Quick Actions")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📧 Send Bulk Verification"):
                    st.info("Bulk verification feature coming soon!")
            with col2:
                if st.button("📊 Generate Reports"):
                    st.info("Report generation in progress...")
            with col3:
                if st.button("🎯 Create New Quiz"):
                    st.session_state.create_quiz = True
                    st.rerun()

        elif choice == "➕ Register Student":
            st.subheader("Register New Student")
            
            with st.form("add_student_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name *")
                    age = st.number_input("Age *", min_value=16, max_value=100, value=25)
                    email = st.text_input("Email *")
                    
                with col2:
                    phone = st.text_input("Phone Number *")
                    selected_courses = st.multiselect("Select Courses *", COURSES)
                    status = st.selectbox("Status", ["Active", "Inactive"])
                
                submitted = st.form_submit_button("🎯 Register Student")
                
                if submitted:
                    if name and email and phone and selected_courses:
                        if not manager.verify_email_format(email):
                            st.error("❌ Please enter a valid email address!")
                        else:
                            # Email verification process
                            if email not in st.session_state.email_verification or not st.session_state.email_verification[email].get('verified', False):
                                verification_code = manager.generate_verification_code()
                                manager.send_verification_code(email, verification_code)
                                
                                st.warning(f"📧 Verification code sent to {email}")
                                st.info(f"**Verification Code:** {verification_code}")
                                st.write("*(In production, this would be sent via email)*")
                                
                                verify_code = st.text_input("Enter verification code:")
                                if st.button("Verify Email"):
                                    if manager.verify_email_code(email, verify_code):
                                        student_id = manager.add_student(name, age, email, phone, selected_courses)
                                        st.success(f"✅ Email verified! Student registered with ID: {student_id}")
                                    else:
                                        st.error("❌ Invalid verification code!")
                            else:
                                student_id = manager.add_student(name, age, email, phone, selected_courses)
                                st.success(f"✅ Student registered successfully! ID: {student_id}")
                    else:
                        st.error("Please fill all required fields (*)")

        elif choice == "👥 View All Students":
            st.subheader("All Students")
            students = manager.get_students()
            
            if students:
                for student in students:
                    with st.expander(f"🎯 {student['name']} ({student['student_id']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Email:** {student['email']}")
                            st.write(f"**Phone:** {student['phone']}")
                            st.write(f"**Status:** {student['status']}")
                        with col2:
                            st.write(f"**Verified:** {'✅' if student.get('email_verified') else '❌'}")
                            st.write(f"**Registration:** {student['registration_date']}")
                        
                        st.write("**Registered Courses:**")
                        for course in student.get('courses', []):
                            fee_status = "✅ Paid" if student['fees_paid'].get(course) else "❌ Pending"
                            st.write(f"- {course} | Grade: {student['grades'].get(course, 'N/A')} | Fees: {fee_status}")

        elif choice == "📚 Course Management":
            st.subheader("Course Materials Management")
            
            selected_course = st.selectbox("Select Course", COURSES)
            
            tab1, tab2, tab3 = st.tabs(["📁 Upload Materials", "📋 View Materials", "🎯 Create Quiz"])
            
            with tab1:
                st.subheader("Upload Course Materials")
                material_title = st.text_input("Material Title")
                material_description = st.text_area("Description")
                material_file = st.file_uploader("Upload File", type=['pdf', 'docx', 'ppt', 'pptx', 'txt'])
                
                if st.button("Upload Material"):
                    if material_title and selected_course:
                        if selected_course not in st.session_state.course_materials:
                            st.session_state.course_materials[selected_course] = []
                        
                        st.session_state.course_materials[selected_course].append({
                            'title': material_title,
                            'description': material_description,
                            'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'type': 'document'
                        })
                        st.success("✅ Material uploaded successfully!")
            
            with tab2:
                st.subheader("Course Materials")
                if selected_course in st.session_state.course_materials:
                    for i, material in enumerate(st.session_state.course_materials[selected_course]):
                        st.markdown(f"""
                        <div class="material-card">
                            <strong>📚 {material['title']}</strong><br>
                            {material['description']}<br>
                            <small>Uploaded: {material['upload_date']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No materials uploaded for this course yet.")
            
            with tab3:
                st.subheader("Create Timed Quiz")
                quiz_title = st.text_input("Quiz Title")
                quiz_duration = st.number_input("Duration (minutes)", min_value=1, max_value=180, value=30)
                
                if 'questions' not in st.session_state:
                    st.session_state.questions = []
                
                st.write("**Add Questions:**")
                question_text = st.text_area("Question")
                option1 = st.text_input("Option A")
                option2 = st.text_input("Option B")
                option3 = st.text_input("Option C")
                option4 = st.text_input("Option D")
                correct_answer = st.selectbox("Correct Answer", ["A", "B", "C", "D"])
                
                if st.button("Add Question"):
                    if question_text and option1 and option2:
                        st.session_state.questions.append({
                            'question': question_text,
                            'options': [option1, option2, option3, option4],
                            'correct': correct_answer
                        })
                        st.success("✅ Question added!")
                
                if st.session_state.questions:
                    st.write("**Current Questions:**")
                    for i, q in enumerate(st.session_state.questions):
                        st.write(f"{i+1}. {q['question']}")
                
                if st.button("Create Quiz") and quiz_title:
                    quiz_id = f"quiz_{int(time.time())}"
                    st.session_state.quizzes[quiz_id] = {
                        'title': quiz_title,
                        'course': selected_course,
                        'duration': quiz_duration,
                        'questions': st.session_state.questions.copy(),
                        'created_date': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.questions = []
                    st.success(f"✅ Quiz '{quiz_title}' created successfully!")

        elif choice == "⏰ Quiz Manager":
            st.subheader("Quiz Management")
            
            if st.session_state.quizzes:
                for quiz_id, quiz in st.session_state.quizzes.items():
                    with st.expander(f"🎯 {quiz['title']} - {quiz['course']}"):
                        st.write(f"**Duration:** {quiz['duration']} minutes")
                        st.write(f"**Questions:** {len(quiz['questions'])}")
                        st.write(f"**Created:** {quiz['created_date']}")
                        
                        if st.button(f"Delete {quiz['title']}", key=quiz_id):
                            del st.session_state.quizzes[quiz_id]
                            st.rerun()
            else:
                st.info("No quizzes created yet.")

    # USER FUNCTIONALITY
    else:
        if choice == "🏠 Student Portal":
            st.subheader("Welcome to Cre8Learn Institute")
            
            student_id = st.text_input("Enter Your Student ID to Access Portal")
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    st.success(f"Welcome back, {student['name']}! 🎉")
                    
                    # Dashboard overview
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Courses", len(student.get('courses', [])))
                    with col2:
                        completed = sum(1 for course in student.get('courses', []) 
                                      if student['progress'].get(course) == '100%')
                        st.metric("Completed", completed)
                    with col3:
                        verified = "✅" if student.get('email_verified') else "❌"
                        st.metric("Email Verified", verified)
                    
                    # Recent activity
                    st.subheader("📚 Your Courses")
                    for course in student.get('courses', []):
                        progress = student['progress'].get(course, '0%')
                        grade = student['grades'].get(course, 'Not Assessed')
                        
                        st.markdown(f"""
                        <div class="student-card">
                            <strong>📖 {course}</strong><br>
                            Progress: {progress} | Grade: {grade}<br>
                            Fees: {'✅ Paid' if student['fees_paid'].get(course) else '❌ Pending'}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("Student ID not found.")

        elif choice == "🔍 My Profile & Courses":
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    st.subheader(f"Student Profile: {student['name']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Personal Information:**")
                        st.write(f"Name: {student['name']}")
                        st.write(f"Student ID: {student['student_id']}")
                        st.write(f"Email: {student['email']} {'✅' if student.get('email_verified') else '❌'}")
                        st.write(f"Phone: {student['phone']}")
                    
                    with col2:
                        st.write("**Academic Information:**")
                        st.write(f"Status: {student['status']}")
                        st.write(f"Registration: {student['registration_date']}")
                        st.write(f"Total Courses: {len(student.get('courses', []))}")
                    
                    # Add more courses
                    st.subheader("➕ Register for Additional Courses")
                    available_courses = [c for c in COURSES if c not in student.get('courses', [])]
                    if available_courses:
                        new_course = st.selectbox("Select additional course", available_courses)
                        if st.button("Add Course"):
                            if manager.add_course_to_student(student_id, new_course):
                                st.success(f"✅ Added {new_course} to your courses!")
                            else:
                                st.error("❌ Failed to add course")
                    else:
                        st.info("You are registered for all available courses! 🎉")

        elif choice == "📖 Learning Materials":
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    st.subheader("Available Learning Materials")
                    
                    for course in student.get('courses', []):
                        st.write(f"### 📚 {course}")
                        if course in st.session_state.course_materials:
                            for material in st.session_state.course_materials[course]:
                                st.markdown(f"""
                                <div class="material-card">
                                    <strong>📄 {material['title']}</strong><br>
                                    {material['description']}<br>
                                    <small>Available since: {material['upload_date']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No materials available for this course yet.")

        elif choice == "🎯 Take Quiz":
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    st.subheader("Available Quizzes")
                    
                    available_quizzes = []
                    for quiz_id, quiz in st.session_state.quizzes.items():
                        if quiz['course'] in student.get('courses', []):
                            available_quizzes.append((quiz_id, quiz))
                    
                    if available_quizzes:
                        for quiz_id, quiz in available_quizzes:
                            with st.expander(f"🎯 {quiz['title']} - {quiz['duration']} minutes"):
                                st.write(f"Course: {quiz['course']}")
                                st.write(f"Questions: {len(quiz['questions'])}")
                                
                                if st.button(f"Start Quiz", key=quiz_id):
                                    st.session_state.current_quiz = quiz_id
                                    st.session_state.quiz_start_time = datetime.now()
                                    st.session_state.quiz_answers = {}
                                    st.rerun()
                    else:
                        st.info("No quizzes available for your courses yet.")

        elif choice == "📊 My Results":
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    st.subheader("Your Academic Results")
                    
                    for course in student.get('courses', []):
                        grade = student['grades'].get(course, 'Not Assessed')
                        progress = student['progress'].get(course, '0%')
                        
                        st.markdown(f"""
                        <div class="student-card">
                            <strong>📖 {course}</strong><br>
                            Current Grade: **{grade}**<br>
                            Progress: **{progress}**<br>
                            Status: {'✅ Completed' if progress == '100%' else '📚 In Progress'}
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime
import base64
from PIL import Image
import io

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
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .institute-subtitle {
        font-size: 1.8rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .tagline {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .student-card {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #1E90FF;
    }
    .admin-section {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .course-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class StudentManager:
    def __init__(self):
        if 'students' not in st.session_state:
            st.session_state.students = []
        if 'admin_logged_in' not in st.session_state:
            st.session_state.admin_logged_in = False
    
    def generate_student_id(self):
        while True:
            new_id = f"CL{random.randint(100000, 999999)}"
            if not any(student['student_id'] == new_id for student in st.session_state.students):
                return new_id
    
    def get_students(self):
        return st.session_state.students
    
    def add_student(self, name, age, email, phone, course):
        student_id = self.generate_student_id()
        new_student = {
            'student_id': student_id,
            'name': name,
            'age': int(age),
            'email': email,
            'phone': phone,
            'course': course,
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'Active',
            'grade': 'Not Assessed',
            'progress': '0%',
            'fees_paid': False
        }
        st.session_state.students.append(new_student)
        return student_id
    
    def search_student(self, student_id):
        for student in st.session_state.students:
            if student['student_id'] == student_id:
                return student
        return None
    
    def update_student(self, student_id, name, age, email, phone, course, status, grade=None, progress=None, fees_paid=None):
        for student in st.session_state.students:
            if student['student_id'] == student_id:
                student.update({
                    'name': name,
                    'age': int(age),
                    'email': email,
                    'phone': phone,
                    'course': course,
                    'status': status
                })
                if grade:
                    student['grade'] = grade
                if progress:
                    student['progress'] = progress
                if fees_paid is not None:
                    student['fees_paid'] = fees_paid
                return True
        return False
    
    def delete_student(self, student_id):
        st.session_state.students = [s for s in st.session_state.students if s['student_id'] != student_id]
        return True

def admin_login():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Admin Access")
    
    if not st.session_state.admin_logged_in:
        password = st.sidebar.text_input("Admin Password", type="password")
        if st.sidebar.button("Login as Admin"):
            if password == "cre8learn2024":  # Change this password
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
    # Custom logo implementation
    st.markdown("""
    <div class="logo-container">
        <h1 class="main-header">Cre8Learn</h1>
        <h2 class="institute-subtitle">INSTITUTE</h2>
        <p class="tagline">Maseru, Lesotho • Business Registration No: A2025/28312</p>
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
    
    # Course descriptions from your PDF
    COURSE_DESCRIPTIONS = {
        "Engineering Mathematics (Number Systems & Logic)": """
        **Course Description:** Provides the mathematical foundation essential for understanding how computers process and represent information.
        
        **Duration:** 4-6 weeks
        **Skills:** Number systems, Boolean algebra, logic gates, circuit design
        **Format:** Online with practical exercises
        """,
        
        "Computer Hardware Basics": """
        **Course Description:** Hands-on introduction to the physical components of a computer. Learn to identify and assemble PC components.
        
        **Duration:** 4 weeks  
        **Skills:** PC assembly, troubleshooting, hardware maintenance
        **Format:** Practical workshops with real components
        """,
        
        "Windows Operating System Fundamentals": """
        **Course Description:** Comprehensive skills for effectively using, managing, and troubleshooting Microsoft Windows.
        
        **Duration:** 5 weeks
        **Skills:** System configuration, command line, user management
        **Format:** Interactive online sessions
        """,
        
        "Cybersecurity 1: Fundamentals, Threats & Tools": """
        **Course Description:** Essential introduction to cybersecurity threats and foundational protection practices.
        
        **Duration:** 6 weeks
        **Skills:** Threat identification, security tools, ethical hacking basics
        **Format:** Theory + practical labs
        """,
        
        "Leadership, Ethics & Professional Workplace Etiquette": """
        **Course Description:** Develop essential professional soft skills for career success in technology environments.
        
        **Duration:** 4 weeks
        **Skills:** Leadership, communication, ethics, project management
        **Format:** Interactive workshops
        """,
        
        "Introduction to Computer Networking": """
        **Course Description:** Solid grounding in modern networking principles from local configurations to global internet connectivity.
        
        **Duration:** 6 weeks
        **Skills:** Network configuration, troubleshooting, IP addressing
        **Format:** Online labs and simulations
        """,
        
        "C++ 1: Introductory Programming": """
        **Course Description:** Hands-on introduction to C++ syntax and core concepts for building efficient software.
        
        **Duration:** 8 weeks
        **Skills:** C++ programming, OOP concepts, problem-solving
        **Format:** Code-along sessions and projects
        """,
        
        "Introduction to Programming & Computational Thinking": """
        **Course Description:** Master the universal language of problem-solving through core logic and structured thinking.
        
        **Duration:** 6 weeks
        **Skills:** Algorithm design, computational thinking, debugging
        **Format:** Interactive problem-solving sessions
        """,
        
        "Proficiency in English Language": """
        **Course Description:** Elevate professional and academic potential through masterful English communication.
        
        **Duration:** 8 weeks
        **Skills:** Business writing, presentations, professional communication
        **Format:** Interactive language labs
        """
    }
    
    # Sidebar Navigation - Different for admin vs user
    if is_admin:
        menu = [
            "🏠 Admin Dashboard",
            "➕ Register Student", 
            "👥 View All Students",
            "🔍 Search Student",
            "✏️ Update Student",
            "🎯 Assess Student",
            "💰 Fee Management",
            "📊 Reports & Analytics"
        ]
    else:
        menu = [
            "🏠 Student Portal",
            "🔍 My Profile", 
            "📚 Course Catalog",
            "📞 Contact Support",
            "ℹ️ About Institute"
        ]
    
    choice = st.sidebar.selectbox("Menu", menu)
    
    # ADMIN FUNCTIONALITY
    if is_admin:
        if choice == "🏠 Admin Dashboard":
            st.subheader("📊 Admin Dashboard")
            
            students = manager.get_students()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total Students", len(students))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                active_students = len([s for s in students if s.get('status') == 'Active'])
                st.metric("Active Students", active_students)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                paid_students = len([s for s in students if s.get('fees_paid') == True])
                st.metric("Fees Paid", paid_students)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                assessed = len([s for s in students if s.get('grade') != 'Not Assessed'])
                st.metric("Assessed", assessed)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Recent Registrations
            st.subheader("📈 Recent Registrations")
            if students:
                recent_students = sorted(students, key=lambda x: x.get('registration_date', ''), reverse=True)[:5]
                for student in recent_students:
                    with st.container():
                        fee_status = "✅ Paid" if student.get('fees_paid') else "❌ Pending"
                        st.markdown(f"""
                        <div class="student-card">
                            <strong>🎯 {student['name']}</strong> ({student['student_id']})<br>
                            📧 {student['email']} | 📞 {student.get('phone', 'N/A')}<br>
                            📚 {student.get('course', 'N/A')} | 💰 Fees: {fee_status}<br>
                            🎯 Status: {student.get('status', 'Active')} | 📅 {student.get('registration_date', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No students registered yet.")
        
        elif choice == "➕ Register Student":
            st.subheader("Register New Student")
            
            with st.form("add_student_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name *")
                    age = st.number_input("Age *", min_value=16, max_value=100, value=25)
                    course = st.selectbox("Course *", COURSES)
                
                with col2:
                    email = st.text_input("Email *")
                    phone = st.text_input("Phone Number *")
                    fees_paid = st.checkbox("Fees Paid")
                    status = st.selectbox("Status", ["Active", "Inactive", "Completed"])
                
                submitted = st.form_submit_button("🎯 Register Student")
                
                if submitted:
                    if name and email and phone and course:
                        student_id = manager.add_student(name, age, email, phone, course)
                        # Update fee status
                        for student in st.session_state.students:
                            if student['student_id'] == student_id:
                                student['fees_paid'] = fees_paid
                        
                        st.success(f"""
                        ✅ Student registered successfully!
                        
                        **Student ID:** {student_id}  
                        **Name:** {name}  
                        **Course:** {course}  
                        **Fees Status:** {'Paid' if fees_paid else 'Pending'}
                        **Status:** {status}
                        
                        *Share the Student ID with the student for profile access*
                        """)
                    else:
                        st.error("Please fill all required fields (*)")
        
        elif choice == "👥 View All Students":
            st.subheader("All Students")
            
            students = manager.get_students()
            if students:
                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    course_filter = st.selectbox("Filter by Course", ["All"] + list(set(s.get('course', '') for s in students)))
                with col2:
                    status_filter = st.selectbox("Filter by Status", ["All"] + list(set(s.get('status', '') for s in students)))
                with col3:
                    fee_filter = st.selectbox("Filter by Fee Status", ["All", "Paid", "Pending"])
                
                # Apply filters
                filtered_students = students
                if course_filter != "All":
                    filtered_students = [s for s in filtered_students if s.get('course') == course_filter]
                if status_filter != "All":
                    filtered_students = [s for s in filtered_students if s.get('status') == status_filter]
                if fee_filter != "All":
                    fee_status = True if fee_filter == "Paid" else False
                    filtered_students = [s for s in filtered_students if s.get('fees_paid') == fee_status]
                
                # Display as dataframe
                display_data = []
                for student in filtered_students:
                    display_data.append({
                        'Student ID': student['student_id'],
                        'Name': student['name'],
                        'Course': student.get('course', ''),
                        'Age': student['age'],
                        'Status': student.get('status', ''),
                        'Grade': student.get('grade', 'Not Assessed'),
                        'Fees Paid': '✅' if student.get('fees_paid') else '❌',
                        'Registration Date': student.get('registration_date', '')
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Export option
                if st.button("📥 Export to CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"cre8learn_students_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No students registered yet.")
        
        elif choice == "🔍 Search Student":
            st.subheader("Search Student")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                search_type = st.radio("Search by:", ["Student ID", "Name", "Email"])
            with col2:
                if search_type == "Student ID":
                    search_term = st.text_input("Enter Student ID")
                elif search_type == "Name":
                    search_term = st.text_input("Enter Student Name")
                else:
                    search_term = st.text_input("Enter Email")
            
            if search_term:
                if search_type == "Student ID":
                    student = manager.search_student(search_term)
                    results = [student] if student else []
                else:
                    key = 'name' if search_type == "Name" else 'email'
                    results = [s for s in manager.get_students() if search_term.lower() in str(s.get(key, '')).lower()]
                
                if results:
                    st.success(f"Found {len(results)} student(s)")
                    for student in results:
                        fee_status = "✅ Paid" if student.get('fees_paid') else "❌ Pending"
                        with st.container():
                            st.markdown(f"""
                            <div class="student-card">
                                <strong>🎯 {student['name']}</strong> ({student['student_id']})<br>
                                📧 {student['email']} | 📞 {student.get('phone', 'N/A')}<br>
                                📚 {student.get('course', 'N/A')} | 🎓 Grade: {student.get('grade', 'Not Assessed')}<br>
                                💰 Fees: {fee_status} | 🎯 Status: {student.get('status', 'Active')}<br>
                                📅 Registered: {student.get('registration_date', 'N/A')}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("No students found!")
        
        elif choice == "🎯 Assess Student":
            st.subheader("Assess Student & Add Grade")
            
            student_id = st.text_input("Enter Student ID to Assess")
            
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    st.info(f"Assessing: {student['name']} ({student_id}) - {student.get('course', 'N/A')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        grade = st.selectbox("Assign Grade", 
                                           ["Not Assessed", "A+", "A", "B+", "B", "C+", "C", "D", "F", "Pass", "Fail", "Distinction"])
                        progress = st.select_slider("Course Progress", 
                                                  options=["0%", "25%", "50%", "75%", "100%"],
                                                  value=student.get('progress', '0%'))
                    
                    with col2:
                        assessment_date = st.date_input("Assessment Date")
                        remarks = st.text_area("Remarks/Feedback")
                    
                    if st.button("💾 Save Assessment"):
                        if manager.update_student(student_id, 
                                                student['name'], 
                                                student['age'], 
                                                student['email'],
                                                student.get('phone', ''),
                                                student.get('course', ''),
                                                student.get('status', 'Active'),
                                                grade, progress):
                            st.success("✅ Assessment saved successfully!")
                        else:
                            st.error("❌ Error saving assessment!")
                else:
                    st.error("Student not found!")
        
        elif choice == "💰 Fee Management":
            st.subheader("Student Fee Management")
            
            student_id = st.text_input("Enter Student ID for Fee Update")
            
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    current_status = "✅ Paid" if student.get('fees_paid') else "❌ Pending"
                    st.info(f"Fee Status for {student['name']} ({student_id}): {current_status}")
                    
                    new_status = st.radio("Update Fee Status:", ["Paid", "Pending"], 
                                        index=0 if student.get('fees_paid') else 1)
                    
                    amount = st.number_input("Amount Paid (M)", min_value=0.0, value=0.0)
                    payment_date = st.date_input("Payment Date")
                    
                    if st.button("💳 Update Fee Status"):
                        fees_paid = True if new_status == "Paid" else False
                        if manager.update_student(student_id, 
                                                student['name'], 
                                                student['age'], 
                                                student['email'],
                                                student.get('phone', ''),
                                                student.get('course', ''),
                                                student.get('status', 'Active'),
                                                fees_paid=fees_paid):
                            st.success(f"✅ Fee status updated to: {new_status}")
                            if amount > 0:
                                st.info(f"Payment recorded: M{amount:.2f} on {payment_date}")
                        else:
                            st.error("❌ Error updating fee status!")
                else:
                    st.error("Student not found!")
        
        elif choice == "📊 Reports & Analytics":
            st.subheader("Institute Reports & Analytics")
            
            students = manager.get_students()
            if students:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Course Enrollment
                    st.write("**📚 Course Enrollment**")
                    course_counts = pd.Series([s.get('course', 'Unknown') for s in students]).value_counts()
                    st.bar_chart(course_counts)
                
                with col2:
                    # Status Overview
                    st.write("**🎯 Student Status Overview**")
                    status_counts = pd.Series([s.get('status', 'Active') for s in students]).value_counts()
                    st.bar_chart(status_counts)
                
                # Fee Status
                st.write("**💰 Fee Payment Status**")
                fee_counts = pd.Series(['Paid' if s.get('fees_paid') else 'Pending' for s in students]).value_counts()
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Students", len(students))
                col2.metric("Fees Paid", fee_counts.get('Paid', 0))
                col3.metric("Fees Pending", fee_counts.get('Pending', 0))
                col4.metric("Payment Rate", f"{(fee_counts.get('Paid', 0)/len(students)*100):.1f}%")
                
            else:
                st.info("No data available for reports.")
    
    # USER FUNCTIONALITY
    else:
        if choice == "🏠 Student Portal":
            st.subheader("Welcome to Cre8Learn Institute")
            st.info("""
            **Student Portal Features:**
            - 🔍 View your profile and progress
            - 📚 Access course information and materials
            - 📞 Contact support for assistance
            - ℹ️ Learn about our institute
            
            *Please use your Student ID to access your profile*
            """)
            
            # Quick profile access
            student_id = st.text_input("Enter Your Student ID")
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    st.success(f"Welcome back, {student['name']}!")
                    fee_status = "✅ Paid" if student.get('fees_paid') else "❌ Pending - Please contact administration"
                    st.markdown(f"""
                    <div class="student-card">
                        <strong>🎯 {student['name']}</strong><br>
                        <strong>Student ID:</strong> {student['student_id']}<br>
                        <strong>Course:</strong> {student.get('course', 'N/A')}<br>
                        <strong>Progress:</strong> {student.get('progress', '0%')}<br>
                        <strong>Grade:</strong> {student.get('grade', 'Not assessed yet')}<br>
                        <strong>Fee Status:</strong> {fee_status}<br>
                        <strong>Status:</strong> {student.get('status', 'Active')}<br>
                        <strong>Registration Date:</strong> {student.get('registration_date', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Student ID not found. Please check your ID or contact support.")
        
        elif choice == "🔍 My Profile":
            st.subheader("My Student Profile")
            student_id = st.text_input("Enter Your Student ID to View Profile")
            
            if student_id:
                student = manager.search_student(student_id)
                if student:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Personal Information:**
                        - **Full Name:** {student['name']}
                        - **Student ID:** {student['student_id']}
                        - **Age:** {student['age']}
                        - **Email:** {student['email']}
                        - **Phone:** {student.get('phone', 'Not provided')}
                        """)
                    
                    with col2:
                        fee_status = "✅ Paid" if student.get('fees_paid') else "❌ Pending"
                        st.markdown(f"""
                        **Academic Information:**
                        - **Course:** {student.get('course', 'N/A')}
                        - **Progress:** {student.get('progress', '0%')}
                        - **Grade:** {student.get('grade', 'Not assessed yet')}
                        - **Fee Status:** {fee_status}
                        - **Status:** {student.get('status', 'Active')}
                        - **Registration Date:** {student.get('registration_date', 'N/A')}
                        """)
                    
                    # Progress section
                    st.markdown("---")
                    st.subheader("📊 Your Progress")
                    if student.get('grade') != 'Not Assessed':
                        st.success(f"**Assessment Completed:** {student.get('grade')}")
                    else:
                        st.info("**Status:** Your assessment is pending. You will be notified when results are available.")
                else:
                    st.error("Student ID not found. Please check your ID or contact support.")
        
        elif choice == "📚 Course Catalog":
            st.subheader("Cre8Learn Course Catalog")
            st.info("**Short Courses Curriculum Package 1** - Designed for school leavers, IT beginners, career changers, and professionals seeking to upskill.")
            
            for course in COURSES:
                with st.expander(f"🎯 {course}"):
                    st.markdown(COURSE_DESCRIPTIONS.get(course, "Course details coming soon..."))
        
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
            
            **Office Address:**
            Cre8Learn Institute
            123 Education Street
            Maseru 100, Lesotho
            """)
            
            # Contact form
            with st.form("contact_form"):
                st.write("**Send us a message:**")
                name = st.text_input("Your Name *")
                email = st.text_input("Your Email *")
                student_id = st.text_input("Student ID (if applicable)")
                subject = st.selectbox("Subject", ["General Inquiry", "Course Information", "Technical Support", "Fee Payment", "Other"])
                message = st.text_area("Message *")
                
                if st.form_submit_button("Send Message"):
                    if name and email and message:
                        st.success("Message sent! We'll respond within 24 hours.")
                    else:
                        st.error("Please fill all required fields (*)")
        
        elif choice == "ℹ️ About Institute":
            st.subheader("About Cre8Learn Institute")
            st.markdown("""
            **Our Mission:**
            To equip learners with fundamental principles of computing and essential professional skills 
            for success in the digital economy.
            
            **Our Vision:**
            To be Lesotho's leading institute for practical technology education and professional development.
            
            **What We Offer:**
            - Comprehensive short courses in technology and professional skills
            - Hands-on, practical learning approach
            - Industry-relevant curriculum
            - Professional certification
            - Career support and guidance
            
            **Why Choose Cre8Learn?**
            ✅ Expert instructors with industry experience
            ✅ Modern, practical curriculum
            ✅ Flexible learning options
            ✅ Career-focused education
            ✅ Supportive learning environment
            
            **Registration:** A2025/28312 • Maseru, Lesotho
            """)

if __name__ == "__main__":
    main()

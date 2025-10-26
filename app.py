import streamlit as st
import pandas as pd
import json
import random
from datetime import datetime

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
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 2rem;
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
    }
</style>
""", unsafe_allow_html=True)

class StudentManager:
    def __init__(self):
        self.students = self.load_students()
    
    def generate_student_id(self):
        while True:
            new_id = f"CL{random.randint(100000, 999999)}"
            if not any(student['student_id'] == new_id for student in self.students):
                return new_id
    
    def load_students(self):
        try:
            return st.session_state.get('students', [])
        except:
            return []
    
    def save_students(self, students):
        st.session_state.students = students
    
    def add_student(self, name, age, grade, email, phone, course):
        student_id = self.generate_student_id()
        new_student = {
            'student_id': student_id,
            'name': name,
            'age': int(age),
            'grade': grade,
            'email': email,
            'phone': phone,
            'course': course,
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'status': 'Active'
        }
        self.students.append(new_student)
        self.save_students(self.students)
        return student_id
    
    def search_student(self, student_id):
        for student in self.students:
            if student['student_id'] == student_id:
                return student
        return None
    
    def update_student(self, student_id, name, age, grade, email, phone, course, status):
        for student in self.students:
            if student['student_id'] == student_id:
                student.update({
                    'name': name,
                    'age': int(age),
                    'grade': grade,
                    'email': email,
                    'phone': phone,
                    'course': course,
                    'status': status
                })
                self.save_students(self.students)
                return True
        return False
    
    def delete_student(self, student_id):
        self.students = [s for s in self.students if s['student_id'] != student_id]
        self.save_students(self.students)
        return True

def main():
    # Initialize manager
    manager = StudentManager()
    
    # Header
    st.markdown('<h1 class="main-header">🎓 Cre8Learn Institute</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Student Management System</h2>', unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2997/2997892.png", width=80)
    st.sidebar.title("Navigation")
    
    menu = [
        "🏠 Dashboard",
        "➕ Add Student", 
        "👥 View All Students",
        "🔍 Search Student",
        "✏️ Update Student",
        "🗑️ Delete Student",
        "📊 Reports"
    ]
    
    choice = st.sidebar.selectbox("Menu", menu)
    
    # Dashboard
    if choice == "🏠 Dashboard":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Students", len(manager.students))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            active_students = len([s for s in manager.students if s.get('status') == 'Active'])
            st.metric("Active Students", active_students)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_age = sum(s['age'] for s in manager.students) / len(manager.students) if manager.students else 0
            st.metric("Average Age", f"{avg_age:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            courses = len(set(s.get('course', '') for s in manager.students))
            st.metric("Total Courses", courses)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Registrations
        st.subheader("📈 Recent Registrations")
        if manager.students:
            recent_students = sorted(manager.students, key=lambda x: x.get('registration_date', ''), reverse=True)[:5]
            for student in recent_students:
                with st.container():
                    st.markdown(f"""
                    <div class="student-card">
                        <strong>🎯 {student['name']}</strong> ({student['student_id']})<br>
                        📧 {student['email']} | 📞 {student.get('phone', 'N/A')}<br>
                        📚 {student.get('course', 'N/A')} | 🎓 Grade: {student['grade']}<br>
                        📅 Registered: {student.get('registration_date', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No students registered yet.")
    
    # Add Student
    elif choice == "➕ Add Student":
        st.subheader("Add New Student")
        
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *")
                age = st.number_input("Age *", min_value=5, max_value=100, value=18)
                grade = st.selectbox("Grade *", ["A+", "A", "B+", "B", "C+", "C", "D", "F"])
                course = st.selectbox("Course *", [
                    "Web Development", "Data Science", "Digital Marketing", 
                    "Graphic Design", "Business Management", "English Language"
                ])
            
            with col2:
                email = st.text_input("Email *")
                phone = st.text_input("Phone Number")
                status = st.selectbox("Status", ["Active", "Inactive", "Completed"])
            
            submitted = st.form_submit_button("🎯 Register Student")
            
            if submitted:
                if name and email and course:
                    student_id = manager.add_student(name, age, grade, email, phone, course)
                    st.success(f"""
                    ✅ Student registered successfully!
                    
                    **Student ID:** {student_id}  
                    **Name:** {name}  
                    **Course:** {course}  
                    **Status:** {status}
                    """)
                else:
                    st.error("Please fill all required fields (*)")
    
    # View All Students
    elif choice == "👥 View All Students":
        st.subheader("All Students")
        
        if manager.students:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                course_filter = st.selectbox("Filter by Course", ["All"] + list(set(s.get('course', '') for s in manager.students)))
            with col2:
                grade_filter = st.selectbox("Filter by Grade", ["All"] + list(set(s.get('grade', '') for s in manager.students)))
            with col3:
                status_filter = st.selectbox("Filter by Status", ["All"] + list(set(s.get('status', '') for s in manager.students)))
            
            # Apply filters
            filtered_students = manager.students
            if course_filter != "All":
                filtered_students = [s for s in filtered_students if s.get('course') == course_filter]
            if grade_filter != "All":
                filtered_students = [s for s in filtered_students if s.get('grade') == grade_filter]
            if status_filter != "All":
                filtered_students = [s for s in filtered_students if s.get('status') == status_filter]
            
            # Display as dataframe
            df = pd.DataFrame(filtered_students)
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
    
    # Search Student
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
                results = [s for s in manager.students if search_term.lower() in str(s.get(key, '')).lower()]
            
            if results:
                st.success(f"Found {len(results)} student(s)")
                for student in results:
                    with st.container():
                        st.markdown(f"""
                        <div class="student-card">
                            <strong>🎯 {student['name']}</strong> ({student['student_id']})<br>
                            📧 {student['email']} | 📞 {student.get('phone', 'N/A')}<br>
                            📚 {student.get('course', 'N/A')} | 🎓 Grade: {student['grade']}<br>
                            🎯 Status: {student.get('status', 'Active')}<br>
                            📅 Registered: {student.get('registration_date', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("No students found!")
    
    # Update Student
    elif choice == "✏️ Update Student":
        st.subheader("Update Student Information")
        
        student_id = st.text_input("Enter Student ID to Update")
        
        if student_id:
            student = manager.search_student(student_id)
            if student:
                with st.form("update_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Full Name", value=student['name'])
                        age = st.number_input("Age", value=student['age'], min_value=5, max_value=100)
                        grade = st.selectbox("Grade", ["A+", "A", "B+", "B", "C+", "C", "D", "F"], 
                                           index=["A+", "A", "B+", "B", "C+", "C", "D", "F"].index(student['grade']))
                    
                    with col2:
                        email = st.text_input("Email", value=student['email'])
                        phone = st.text_input("Phone", value=student.get('phone', ''))
                        course = st.selectbox("Course", [
                            "Web Development", "Data Science", "Digital Marketing", 
                            "Graphic Design", "Business Management", "English Language"
                        ], index=[
                            "Web Development", "Data Science", "Digital Marketing", 
                            "Graphic Design", "Business Management", "English Language"
                        ].index(student.get('course', 'Web Development')))
                        status = st.selectbox("Status", ["Active", "Inactive", "Completed"], 
                                            index=["Active", "Inactive", "Completed"].index(student.get('status', 'Active')))
                    
                    if st.form_submit_button("💾 Update Student"):
                        if manager.update_student(student_id, name, age, grade, email, phone, course, status):
                            st.success("✅ Student updated successfully!")
                        else:
                            st.error("❌ Error updating student!")
            else:
                st.error("Student not found!")
    
    # Delete Student
    elif choice == "🗑️ Delete Student":
        st.subheader("Delete Student")
        
        student_id = st.text_input("Enter Student ID to Delete")
        
        if student_id:
            student = manager.search_student(student_id)
            if student:
                st.warning(f"⚠️ You are about to delete: {student['name']} ({student_id})")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        if manager.delete_student(student_id):
                            st.success("✅ Student deleted successfully!")
                        else:
                            st.error("❌ Error deleting student!")
                with col2:
                    if st.button("❌ Cancel"):
                        st.info("Deletion cancelled")
            else:
                st.error("Student not found!")
    
    # Reports
    elif choice == "📊 Reports":
        st.subheader("Institute Reports")
        
        if manager.students:
            col1, col2 = st.columns(2)
            
            with col1:
                # Grade Distribution
                st.write("**Grade Distribution**")
                grade_counts = pd.Series([s['grade'] for s in manager.students]).value_counts()
                st.bar_chart(grade_counts)
            
            with col2:
                # Course Enrollment
                st.write("**Course Enrollment**")
                course_counts = pd.Series([s.get('course', 'Unknown') for s in manager.students]).value_counts()
                st.bar_chart(course_counts)
            
            # Status Overview
            st.write("**Student Status Overview**")
            status_counts = pd.Series([s.get('status', 'Active') for s in manager.students]).value_counts()
            col1, col2, col3 = st.columns(3)
            col1.metric("Active", status_counts.get('Active', 0))
            col2.metric("Inactive", status_counts.get('Inactive', 0))
            col3.metric("Completed", status_counts.get('Completed', 0))
        else:
            st.info("No data available for reports.")

if __name__ == "__main__":
    main()
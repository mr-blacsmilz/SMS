import hardware_core  
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. PAGE CONFIGURATION & SESSION STATE INITIALISATION
st.set_page_config(page_title="Meal Attendance Dashboard", layout="wide")

# Initialise persistent system storage using Streamlit Session State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "report_emails" not in st.session_state:
    # Default authorized administrative email distribution list
    st.session_state["report_emails"] = ["headmaster@school.edu", "welfare@school.edu"]
if "registered_users" not in st.session_state:
    # Dictionary to keep track of created staff accounts (Email -> Password)
    st.session_state["registered_users"] = {}

# 2. LOGIN AND USER MANAGEMENT INTERFACE
def show_login_page():
    st.title("🔒 School Meal System - Access Control")
    
    auth_mode = st.radio("Choose Action:", ["System Admin Login", "Staff Account Registration", "Staff Login"])
    
    # --- SYSTEM ADMIN LOGIN (Mr. Blac) ---
    if auth_mode == "System Admin Login":
        st.subheader("Creator Administrative Portal")
        admin_user = st.text_input("Username", placeholder="Enter admin username")
        admin_pass = st.text_input("Password", type="password", placeholder="Enter admin password")
        
        if st.button("Access Creator Panel"):
            if admin_user == "Mr.blac" and admin_pass == "mummy2023":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Creator"
                st.success("Welcome back, Mr. Blac! Access granted.")
                st.rerun()
            else:
                st.error("Invalid Creator credentials. Please try again.")

    # --- STAFF ACCOUNT REGISTRATION ---
    elif auth_mode == "Staff Account Registration":
        st.subheader("Create Staff Account")
        st.info("Account creation is strictly locked. Your email must be pre-approved on the report distribution list.")
        
        reg_email = st.text_input("Your Official Email Address")
        reg_pass = st.text_input("Choose a Secure Password", type="password")
        reg_pass_conf = st.text_input("Confirm Password", type="password")
        
        if st.button("Register Account"):
            if not reg_email or not reg_pass:
                st.warning("Please fill out all fields.")
            elif reg_pass != reg_pass_conf:
                st.error("Passwords do not match.")
            # Security Rule: Check if the registering email exists in the authorized list
            elif reg_email not in st.session_state["report_emails"]:
                st.error("Access Denied: This email is not authorized to receive reports or hold an account.")
            elif reg_email in st.session_state["registered_users"]:
                st.warning("An account already exists for this email address.")
            else:
                st.session_state["registered_users"][reg_email] = reg_pass
                st.success("Account successfully created! You can now log in under the 'Staff Login' tab.")

    # --- STAFF LOGIN ---
    elif auth_mode == "Staff Login":
        st.subheader("Staff Dashboard Sign-In")
        login_email = st.text_input("Email Address")
        login_pass = st.text_input("Password", type="password")
        
        if st.button("Sign In"):
            if login_email in st.session_state["registered_users"] and st.session_state["registered_users"][login_email] == login_pass:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Staff"
                st.success("Authentication successful.")
                st.rerun()
            else:
                st.error("Invalid email or password. Please verify credentials or register.")

# 3. MOCK DATABASE (Simulating server data collected from QR scans)
@st.cache_data
def load_mock_data():
    students_data = {
        "Student ID": ["STU001", "STU002", "STU003", "STU004", "STU005"],
        "Name": ["John Doe", "Alice Nsubuga", "Brian Cheptegei", "Mary Atwine", "David Okello"],
        "Class/Stream": ["Senior 4A", "Senior 4B", "Senior 4A", "Senior 3A", "Senior 4B"],
        "Age":,
        "Monday_Lunch": ["Scanned", "Scanned", "Skipped", "Scanned", "Scanned"],
        "Monday_Supper": ["Scanned", "Scanned", "Skipped", "Scanned", "Scanned"],
        "Tuesday_Lunch": ["Scanned", "Scanned", "Skipped", "Scanned", "Skipped"],
        "Tuesday_Supper": ["Scanned", "Scanned", "Skipped", "Scanned", "Skipped"],
        "Wednesday_Lunch": ["Scanned", "Skipped", "Scanned", "Scanned", "Skipped"],
        "Wednesday_Supper": ["Scanned", "Skipped", "Scanned", "Scanned", "Skipped"],
        "Thursday_Lunch": ["Scanned", "Scanned", "Scanned", "Scanned", "Skipped"],
        "Thursday_Supper": ["Scanned", "Scanned", "Scanned", "Scanned", "Skipped"],
        "Friday_Lunch": ["Scanned", "Scanned", "Scanned", "Scanned", "Skipped"],
        "Friday_Supper": ["Scanned", "Scanned", "Scanned", "Scanned", "Skipped"]
    }
    return pd.DataFrame(students_data)

# 4. MAIN APP CONTENT (Executes only after successful login)
if not st.session_state["logged_in"]:
    show_login_page()
else:
    # Top Navigation Bar with Log Out button
    st.sidebar.markdown(f"**Current User:** {st.session_state['user_role']}")
    if st.sidebar.button("🔒 Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["user_role"] = None
        st.rerun()

    st.title(" 🍽️ Student Meal Attendance Analytics")
    st.markdown("### Weekly System Monitoring & Welfare Report")

    # Load tracking metrics
    df = load_mock_data()
    meal_columns = [col for col in df.columns if "Lunch" in col or "Supper" in col]
    df["Meals Attended"] = df[meal_columns].apply(lambda row: sum(row == "Scanned"), axis=1)
    df["Meals Skipped"] = len(meal_columns) - df["Meals Attended"]

    total_students = len(df)
    perfect_attendance = len(df[df["Meals Skipped"] == 0])
    critical_skips = df[df["Meals Skipped"] >= 5]

    # --- CREATOR ONLY CONTROL PANEL: EMAIL & DISTRIBUTION MANAGEMENT ---
    if st.session_state["user_role"] == "Creator":
        st.markdown("---")
        with st.expander("🛠️ Creator Control Panel (Mr. Blac Only)", expanded=True):
            st.subheader("Manage Report Email Distribution List")
            st.write("Adding an email here automatically authorizes that person to create a staff account.")
            
            # Form to add a new recipient email address
            new_email = st.text_input("Enter New Administrator Email to Authorize:")
            if st.button("➕ Add to Distribution List"):
                if new_email and new_email not in st.session_state["report_emails"]:
                    st.session_state["report_emails"].append(new_email)
                    st.success(f"Success: '{new_email}' is now authorized to receive reports and register.")
                    st.rerun()
                elif new_email in st.session_state["report_emails"]:
                    st.warning("This email address is already on the list.")
                else:
                    st.error("Please enter a valid email address.")
            
            # Display current authorized distribution list
            st.markdown("**Active Report Recipients & Authorized Accounts:**")
            for idx, email in enumerate(st.session_state["report_emails"]):
                st.write(f"{idx + 1}. {email}")
        st.markdown("---")

    # 5. SIDEBAR CONTROLS (Room for error / Delay management)
    st.sidebar.header("🎛️ System Controls")
    st.sidebar.markdown("### Active Meal Windows")
    st.sidebar.info("Lunch: 12:30 PM - 2:00 PM\n\nSupper: 6:00 PM - 7:30 PM")

    st.sidebar.markdown("### Kitchen Delays Buffer")
    lunch_delay = st.sidebar.checkbox("Extend Lunch Window (Kitchen Delay)")
    supper_delay = st.sidebar.checkbox("Extend Supper Window (Kitchen Delay)")

    if lunch_delay:
        st.sidebar.success("⏳ Lunch extended until 2:30 PM")
    if supper_delay:
        st.sidebar.success("⏳ Supper extended until 8:00 PM")

    # 6. MAIN DASHBOARD METRICS DISPLAY
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Registered Students", value=total_students)
    col2.metric(label="Perfect Attendance This Week", value=perfect_attendance)
    col3.metric(label="Welfare Alerts (Skipped ≥ 5 Meals)", value=len(critical_skips))

    st.markdown("---")

    # 7. WEEKLY REPORTS SECTION
    tab1, tab2, tab3 = st.tabs(["📋 All Student Records", "🚨 Welfare Skip List", "📊 Attendance Insights"])

    with tab1:
        st.subheader("Master Attendance Sheet")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("🚨 Student Welfare Alert (The Skip List)")
        if not critical_skips.empty:
            st.warning(f"Found {len(critical_skips)} students requiring immediate attention.")
            st.dataframe(critical_skips[["Student ID", "Name", "Class/Stream", "Meals Skipped"]], use_container_width=True)
        else:
            st.success("Great news! No students have skipped a critical number of meals this week.")

    with tab3:
        st.subheader("Visual Data Insights")
        fig_bar = px.bar(
            df, x="Name", y=["Meals Attended", "Meals Skipped"], 
            title="Meal Distribution per Student", barmode="stack",
            color_discrete_sequence=["#2ECC71", "#E74C3C"]
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        # When a scan arrives via the Cat6 cable, process it instantly
response = hardware_core.process_raw_scan(scanned_id, active_lane, df, lunch_delay)


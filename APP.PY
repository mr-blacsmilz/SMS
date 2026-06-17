import pandas as pd
import plotly.express as px
import streamlit as st

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Meal Attendance Dashboard", layout="wide")
st.title(" 🍽️ Student Meal Attendance Analytics")
st.markdown("### Weekly System Monitoring & Welfare Report")

# 2. MOCK DATABASE (Simulating server data collected from QR scans)
# In a real system, this data would come from a SQL database linked to the scanners.
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

df = load_mock_data()

# 3. CALCULATE METRICS
# Count total potential meals per student (10 meals tracked in this sample)
meal_columns = [col for col in df.columns if "Lunch" in col or "Supper" in col]
df["Meals Attended"] = df[meal_columns].apply(lambda row: sum(row == "Scanned"), axis=1)
df["Meals Skipped"] = len(meal_columns) - df["Meals Attended"]

# Global High-Level Metrics
total_students = len(df)
perfect_attendance = len(df[df["Meals Skipped"] == 0])
critical_skips = df[df["Meals Skipped"] >= 5] # Flag if they missed half or more meals

# 4. SIDEBAR CONTROLS (Room for error / Delay management)
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

# 5. MAIN DASHBOARD METRICS DISPLAY
col1, col2, col3 = st.columns(3)
col1.metric(label="Total Registered Students", value=total_students)
col2.metric(label="Perfect Attendance This Week", value=perfect_attendance)
col3.metric(label="Welfare Alerts (Skipped ≥ 5 Meals)", value=len(critical_skips))

st.markdown("---")

# 6. WEEKLY REPORTS SECTION
tab1, tab2, tab3 = st.tabs(["📋 All Student Records", "🚨 Welfare Skip List", "📊 Attendance Insights"])

with tab1:
    st.subheader("Master Attendance Sheet")
    st.markdown("This table shows the real-time scanning log of all students.")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("🚨 Student Welfare Alert (The Skip List)")
    st.markdown("These students have missed multiple consecutive meals. Please conduct a health or welfare check.")
    if not critical_skips.empty:
        st.warning(f"Found {len(critical_skips)} students requiring immediate attention.")
        st.dataframe(critical_skips[["Student ID", "Name", "Class/Stream", "Meals Skipped"]], use_container_width=True)
    else:
        st.success("Great news! No students have skipped a critical number of meals this week.")

with tab3:
    st.subheader("Visual Data Insights")
    
    # Chart 1: Attendance Breakdown by Student
    fig_bar = px.bar(
        df, 
        x="Name", 
        y=["Meals Attended", "Meals Skipped"], 
        title="Meal Distribution per Student",
        barmode="stack",
        color_discrete_sequence=["#2ECC71", "#E74C3C"]
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Chart 2: Stream Analysis (Which stream skips the most meals?)
    stream_skips = df.groupby("Class/Stream")["Meals Skipped"].sum().reset_index()
    fig_pie = px.pie(
        stream_skips, 
        values="Meals Skipped", 
        names="Class/Stream", 
        title="Total Skipped Meals Proportions by Class/Stream",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

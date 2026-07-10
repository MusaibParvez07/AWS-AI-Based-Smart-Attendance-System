import streamlit as st
from aws_helper import aws

st.set_page_config(page_title='Cloud Based Smart Attendance System', layout='wide')

with st.spinner("Initializing face recognition components..."):
    import face_rec

if hasattr(face_rec, 'apply_custom_css'):
    face_rec.apply_custom_css()

# Big Gorgeous Title
st.markdown(
    """
    <h1 style="display: flex; align-items: center; gap: 15px; margin-bottom: 0px; padding-bottom: 0px;">
        <span style="-webkit-text-fill-color: initial !important; background: none !important; -webkit-background-clip: unset !important; font-size: 3rem;">📸</span>
        <span style="background: linear-gradient(135deg, #00F2FE 0%, #9B5DE5 55%, #F15BB5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Cloud Based Smart Attendance System</span>
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("### Smart Face Recognition Attendance Dashboard")
st.write("---")

# Active Database & System Status (Glowing metrics)
st.subheader("🌐 System Integration & Connection Status")
col1, col2, col3 = st.columns(3)

with col1:
    if aws.is_configured():
        st.metric(label="Active Database Engine", value="AWS RDS MySQL", delta="Online")
    else:
        st.metric(label="Active Database Engine", value="Local Backup (Pickle)", delta="Offline (Redis)")

with col2:
    if aws.is_configured():
        st.metric(label="Face Verification Cloud", value="AWS Rekognition", delta="Active")
    else:
        st.metric(label="Face Verification Cloud", value="InsightFace (Local)", delta="Standby")

with col3:
    if aws.is_configured():
        st.metric(label="AWS Storage Bucket", value="Amazon S3", delta="Connected")
    else:
        st.metric(label="AWS Storage Bucket", value="Local Drive", delta="Fallback")

st.write("---")

# Feature Panels
st.subheader("⚙️ Core Capabilities")
col_feat1, col_feat2 = st.columns(2)

with col_feat1:
    st.info("### 📹 Real-Time Attendance Prediction\n"
            "Deploy a high-speed webcam Predicter to recognize face features, "
            "verify identities using cloud databases, log timestamps automatically, and publish real-time notifications to your Amazon SNS email topic.")

with col_feat2:
    st.success("### 👤 User Registration Form\n"
              "Register new members easily by snapping a photo of their face directly in the web browser. "
              "Profile information is saved to your RDS database while the image is securely indexed into your AWS Rekognition collection.")

st.write("---")

# Visual workflow
st.subheader("🚀 System Workflow Guide")
workflow_col1, workflow_col2, workflow_col3 = st.columns(3)

with workflow_col1:
    st.markdown("""
    #### **1. Face Registration**
    Go to **Registration Form** from the sidebar, fill details, capture your face profile, and register in the database.
    """)

with workflow_col2:
    st.markdown("""
    #### **2. Real-Time Detection**
    Go to **Real Time Prediction**, open the live webcam, and look at the camera. The system will detect your face, verify identity, and log attendance.
    """)

with workflow_col3:
    st.markdown("""
    #### **3. Analytics & Management**
    Go to **Report** to view registered profiles, analyze computed attendance, search logs by date, or delete entries.
    """)

st.write("---")
st.caption("Powered by AWS Cloud Services | Designed for Enterprise Security")

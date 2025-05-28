import streamlit as st
st.set_page_config(page_title="HYS Consulting", page_icon="💼", layout="wide")
import os
from PIL import Image
from datetime import datetime
from uuid import uuid4
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager

# ---------------------- CONFIGURATION ----------------------
VISIT_LOG = "visit_logs.txt"
CONTACT_LOG = "contact_logs.txt"



# ---------------------- COOKIES ----------------------
cookies = EncryptedCookieManager(
    prefix="hys_",
    password=os.getenv("COOKIE_SECRET", "super_secret_password")
)
if not cookies.ready():
    st.stop()

if not cookies.get("consent"):
    st.warning("We use cookies to enhance your experience. Click **Allow Cookies** to continue.")
    if st.button("Allow Cookies"):
        cookies["consent"] = "true"
        cookies["first_visit"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cookies["visitor_id"] = str(uuid4())
        cookies.save()
        st.success("Thank you! Cookies enabled.")
        st.experimental_rerun()
else:
    st.info("Cookies accepted ✔")
    st.caption(f"First visit: {cookies.get('first_visit')}")

visitor_id = cookies.get("visitor_id")
if visitor_id is None:
    visitor_id = str(uuid4())
    cookies["visitor_id"] = visitor_id
    cookies.save()

# ---------------------- STYLE ----------------------
st.markdown("""
    <style>
        .main {background-color:#f4f4f9;font-family:'Segoe UI',sans-serif;}
        .title {color:#003366;font-size:40px;font-weight:bold;text-align:center;margin-bottom:0;}
        .subtitle {color:#004080;font-size:20px;text-align:center;margin-bottom:30px;}
        .section-header {color:#00264d;font-size:26px;margin-top:30px;}
        .info-box {background-color:#e6f0ff;padding:20px;border-radius:10px;
                   box-shadow:2px 2px 8px rgba(0,0,0,.1);margin-bottom:20px;}
    </style>
""", unsafe_allow_html=True)

# ---------------------- HEADER ----------------------
st.image("HYSConsulting.png", width=150)
st.markdown("<div class='title'>HYS Consulting</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Empowering Businesses with Smart IT Solutions</div>", unsafe_allow_html=True)

# ---------------------- NAVIGATION ----------------------
section = st.sidebar.radio(
    "Navigate",
    ["Home", "Services", "About", "Student Classes",
     "Software Expertise", "Projects", "Contact", "Reports", "Data Insights"]
)

# ---------------------- VISIT LOGGING ----------------------
def log_visit(sec: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts},{visitor_id},{sec}\n"
    with open(VISIT_LOG, "a") as f:
        f.write(line)
log_visit(section)

# ---------------------- MAIN CONTENT ----------------------
if section == "Home":
    st.markdown("<div class='section-header'>Welcome to HYS Consulting</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='info-box'>
        HYS Consulting is a premier IT consultancy offering cutting-edge solutions in Data Engineering, AI/ML, Business Intelligence, and Cloud Infrastructure.
        </div>
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1603574670812-d24560880210",
             caption="Innovating IT Solutions", use_container_width=True)

elif section == "Services":
    st.markdown("<div class='section-header'>Our Services</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    cols[0].markdown("<div class='info-box'><h4>🔍 Data Engineering</h4><p>Design robust data pipelines & warehouses.</p></div>", unsafe_allow_html=True)
    cols[1].markdown("<div class='info-box'><h4>🤖 AI & ML Solutions</h4><p>Tailored ML models and AI strategy.</p></div>", unsafe_allow_html=True)
    cols[0].markdown("<div class='info-box'><h4>📊 Business Intelligence</h4><p>Turn data into actionable insight.</p></div>", unsafe_allow_html=True)
    cols[1].markdown("<div class='info-box'><h4>☁️ Cloud Strategy</h4><p>Modernize with cloud-native architecture.</p></div>", unsafe_allow_html=True)

elif section == "About":
    st.markdown("<div class='section-header'>About Us</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='info-box'>
        Founded by IT veterans with 20+ years’ experience delivering digital transformation for Fortune 500 firms.
        <ul>
            <li><strong>Vision:</strong> Global leader in strategic IT consulting.</li>
            <li><strong>Mission:</strong> Deliver future-ready solutions that drive success.</li>
            <li><strong>Values:</strong> Integrity • Innovation • Excellence • Client-first</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

elif section == "Student Classes":
    st.markdown("<div class='section-header'>Student Training Programs</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='info-box'>
        <ul>
            <li><strong>Topics:</strong> Python, Data Analysis, SQL, Web Dev, AI Basics</li>
            <li><strong>For:</strong> Grades 8-12 & college freshmen</li>
            <li><strong>Location:</strong> Ace City (C006), Greater Noida West</li>
            <li><strong>Fee:</strong> ₹500/hr (India) • $12/hr (Intl)</li>
            <li><strong>Mode:</strong> Online / In-person</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

elif section == "Software Expertise":
    st.markdown("<div class='section-header'>Software Expertise</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='info-box'>
        Python • SQL • Java • Apache Spark • Databricks • Airflow • Power BI • Tableau • Looker •
        Azure • AWS • GCP • Git • Jenkins • Docker • Kubernetes
        </div>
    """, unsafe_allow_html=True)

elif section == "Projects":
    st.markdown("<div class='section-header'>Showcasing Our Work</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='info-box'>
        <ul>
            <li><strong>Retail BI Dashboard:</strong> Real-time inventory & sales KPIs.</li>
            <li><strong>Healthcare Predictive Analytics:</strong> Patient risk score models.</li>
            <li><strong>Cloud Migration:</strong> Lift-and-shift & cloud-native redesign.</li>
            <li><strong>Education Analytics:</strong> Dashboards for student performance.</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)

elif section == "Contact":
    st.markdown("<div class='section-header'>Get in Touch</div>", unsafe_allow_html=True)
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Your Message")
        submitted = st.form_submit_button("Send")
        if submitted:
            if name and email:
                st.success(f"Thanks {name}! We’ll get back to you shortly.")
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(CONTACT_LOG, "a") as f:
                    f.write(f"{ts},{visitor_id},{name},{email},{message}\n")
                cookies["user_name"] = name
                cookies["user_email"] = email
                cookies.save()
            else:
                st.error("Please fill in both name and email.")

    st.markdown("""
        <div class='info-box'>
        <p><strong>📍 Location:</strong> Ace City (C006), Greater Noida West</p>
        <p><strong>📞 Phone:</strong> +91-9811508110</p>
        <p><strong>🌐 Website:</strong> www.hysconsulting.com (coming soon)</p>
        </div>
    """, unsafe_allow_html=True)

elif section == "Reports":
    st.markdown("<div class='section-header'>Visitor Movement Report</div>", unsafe_allow_html=True)

    if not os.path.exists(VISIT_LOG):
        st.info("No visit data yet.")
    else:
        df = pd.read_csv(
            VISIT_LOG,
            names=["timestamp", "visitor_id", "section"],
            parse_dates=["timestamp"]
        )
        st.dataframe(df)
        st.markdown("#### Section Visit Counts")
        section_counts = df["section"].value_counts()
        st.bar_chart(section_counts)
        st.markdown("#### Unique Visitors")
        st.metric("Total Visitors", df["visitor_id"].nunique())

elif section == "Data Insights":
    st.markdown("<div class='section-header'>Upload Your Data for Insight</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        try:
            data = pd.read_csv(uploaded_file)
            st.subheader("Your Data Preview")
            st.dataframe(data.head())

            st.subheader("Data Summary")
            st.write(data.describe(include='all'))

            st.subheader("Missing Values")
            st.write(data.isnull().sum())

            st.subheader("Column-wise Distribution")
            num_cols = data.select_dtypes(include=['int64', 'float64']).columns
            for col in num_cols:
                st.markdown(f"### {col}")
                st.bar_chart(data[col].value_counts().sort_index())

        except Exception as e:
            st.error(f"Error loading file: {e}")

# ---------------------- SIDEBAR MSG ----------------------
if cookies.get("user_name"):
    st.sidebar.success(f"👋 Welcome back, {cookies.get('user_name')}!")

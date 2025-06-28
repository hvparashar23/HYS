import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import json
import os
import pandas as pd
import altair as alt
import datetime
from PIL import Image
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import toml
import csv
import base64
import urllib.parse
import sqlite3
import logging
from typing import List, Dict, Optional
import bcrypt

# ---------- Setup & Config ----------
st.set_page_config(
    page_title="HYS Consulting", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

# Initialize logging
logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Database Setup (Auto-Created) ----------
def init_db():
    """Initialize SQLite database with required tables"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect('data/app.db')
    cursor = conn.cursor()
    
    # Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        tech TEXT NOT NULL,
        description TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Leads table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # CEO messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ceo_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Admin credentials (in real app, use proper auth)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')
    
    # Insert default admin if none exists
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    if cursor.fetchone()[0] == 0:
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            ("admin", hashed_pw)
        )
    
    conn.commit()
    return conn

# Initialize database
db_conn = init_db()

# ---------- Helper Functions (Cached) ----------
@st.cache_data(ttl=300)
def load_project_data() -> List[Dict]:
    """Load projects from database"""
    try:
        return pd.read_sql("SELECT * FROM projects ORDER BY created_at DESC", db_conn).to_dict('records')
    except Exception as e:
        logger.error(f"Error loading projects: {e}")
        return []

@st.cache_data(ttl=300)
def load_leads_data() -> List[Dict]:
    """Load leads from database"""
    try:
        return pd.read_sql("SELECT * FROM leads ORDER BY timestamp DESC", db_conn).to_dict('records')
    except Exception as e:
        logger.error(f"Error loading leads: {e}")
        return []

@st.cache_data(ttl=300)
def load_ceo_data() -> List[Dict]:
    """Load CEO messages from database"""
    try:
        return pd.read_sql("SELECT * FROM ceo_messages ORDER BY created_at DESC", db_conn).to_dict('records')
    except Exception as e:
        logger.error(f"Error loading CEO data: {e}")
        return []

def save_project_data(project_data: Dict) -> bool:
    """Save project to database"""
    try:
        db_conn.execute(
            "INSERT INTO projects (title, tech, description, image_url) VALUES (?, ?, ?, ?)",
            (project_data['title'], project_data['tech'], project_data['description'], project_data.get('image_url', ''))
        )
        db_conn.commit()
        st.cache_data.clear()  # Clear cache to reflect changes
        return True
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        return False

def save_lead_data(lead_data: Dict) -> bool:
    """Save lead to database"""
    try:
        db_conn.execute(
            "INSERT INTO leads (name, email, message) VALUES (?, ?, ?)",
            (lead_data['name'], lead_data['email'], lead_data['message'])
        )
        db_conn.commit()
        st.cache_data.clear()
        return True
    except Exception as e:
        logger.error(f"Error saving lead: {e}")
        return False

def save_ceo_message(message_data: Dict) -> bool:
    """Save CEO message to database"""
    try:
        db_conn.execute(
            "INSERT INTO ceo_messages (name, message) VALUES (?, ?)",
            (message_data['name'], message_data['message'])
        )
        db_conn.commit()
        st.cache_data.clear()
        return True
    except Exception as e:
        logger.error(f"Error saving CEO message: {e}")
        return False

def export_leads_to_csv() -> Optional[str]:
    """Export leads to CSV file"""
    try:
        df = pd.read_sql("SELECT name, email, message, timestamp FROM leads", db_conn)
        csv_path = "data/leads_export.csv"
        df.to_csv(csv_path, index=False)
        
        with open(csv_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            return f'<a href="data:file/csv;base64,{b64}" download="leads_export.csv">Download CSV</a>'
    except Exception as e:
        logger.error(f"Error exporting leads: {e}")
        return None

def send_email(name: str, email: str, message: str) -> bool:
    """Send email notification"""
    try:
        secrets = toml.load("secrets.toml")
        msg = MIMEMultipart()
        msg["From"] = secrets["email"]
        msg["To"] = secrets["to"]
        msg["Subject"] = f"New Lead from {name}"
        msg.attach(MIMEText(f"Name: {name}\nEmail: {email}\nMessage: {message}", "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(secrets["email"], secrets["password"].replace("\xa0", " "))
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def get_whatsapp_url(message: str) -> str:
    """Generate WhatsApp share URL"""
    return f"https://wa.me/?text={urllib.parse.quote(message)}"

def verify_admin(username: str, password: str) -> bool:
    """Verify admin credentials"""
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT password_hash FROM admin_users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            return bcrypt.checkpw(password.encode(), result[0])
        return False
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return False

# ---------- Session State Setup ----------
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------- Page Navigation ----------
main_tabs = [
    "Home", "Services", "Projects", "Contact", "Pricing",
    "Business Growth", "Leadership"
]

if st.session_state.is_admin:
    main_tabs += ["Business Analytics", "Admin Panel", "Logout"]
else:
    main_tabs.append("Login")

tabs = st.tabs(main_tabs)

# ---------- Home Tab ----------
with tabs[0]:
    st.markdown("""
    <h1 style='text-align: center; color: #2C3E50;'>
        Welcome to HYS Consulting
    </h1>
    <p style='text-align: center; font-size:18px;'>
        Empowering your business with cutting-edge Data Science, AI, and ML solutions
    </p>
    """, unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1603791440384-56cd371ee9a7", 
             use_container_width=True, 
             caption="Innovative Solutions for Your Business")

# ---------- Services Tab ----------
with tabs[1]:
    st.header("Our Services")
    services = {
        "Data Engineering": "Build robust, scalable data pipelines",
        "Machine Learning": "Predictive modeling and AI solutions",
        "BI Dashboards": "Interactive dashboards with Power BI/Tableau",
        "Cloud Integration": "AWS/Azure/GCP deployment expertise",
        "Consultation": "Proof-of-concept development and strategy"
    }
    
    cols = st.columns(2)
    for i, (service, desc) in enumerate(services.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.subheader(service)
                st.markdown(f"<p style='color: #555;'>{desc}</p>", unsafe_allow_html=True)

# ---------- Projects Tab ----------
with tabs[2]:
    st.header("Client Projects Showcase")
    
    sort_col, filter_col = st.columns(2)
    with sort_col:
        sort_option = st.selectbox("Sort by", ["Newest First", "Title A-Z"])
    with filter_col:
        tech_filter = st.multiselect("Filter by tech", ["Python", "SQL", "ML", "Cloud"])
    
    projects = load_project_data()
    
    if tech_filter:
        projects = [p for p in projects if any(tech in p['tech'] for tech in tech_filter)]
    
    if sort_option == "Title A-Z":
        projects = sorted(projects, key=lambda x: x['title'])
    
    if projects:
        for proj in projects:
            with st.expander(f"{proj['title']} ({proj['tech']})"):
                cols = st.columns([1, 3])
                with cols[0]:
                    if proj.get('image_url'):
                        st.image(proj['image_url'], width=200)
                with cols[1]:
                    st.markdown(proj['description'])
    else:
        st.info("No projects found. Add some in the Admin Panel!")

# ---------- Contact Tab ----------
with tabs[3]:
    st.header("Get in Touch")
    
    with st.form("contact_form", clear_on_submit=True):
        name = st.text_input("Name*", placeholder="Your name")
        email = st.text_input("Email*", placeholder="your@email.com")
        message = st.text_area("Message*", placeholder="How can we help?")
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not all([name, email, message]):
                st.error("Please fill all required fields")
            else:
                lead = {"name": name, "email": email, "message": message}
                if save_lead_data(lead):
                    st.success("Thank you! We'll contact you soon.")
                    
                    # Send email notification
                    if send_email(name, email, message):
                        st.markdown(
                            f"""<a href='{get_whatsapp_url(f"New inquiry from {name}: {message}")}' 
                            target='_blank' class='button'>
                            📱 Notify via WhatsApp
                            </a>""", 
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning("Message saved but email failed (check logs)")

# ---------- Pricing Tab ----------
with tabs[4]:
    st.header("Flexible Pricing")
    
    pricing_plans = {
        "Starter": {
            "price": "₹20,000+",
            "features": ["Basic dashboards", "POC development", "Email support"]
        },
        "Growth": {
            "price": "₹50,000+",
            "features": ["Advanced analytics", "Cloud integration", "Priority support"]
        },
        "Enterprise": {
            "price": "₹1,00,000+",
            "features": ["End-to-end solutions", "Dedicated team", "24/7 support"]
        }
    }
    
    cols = st.columns(3)
    for i, (plan, details) in enumerate(pricing_plans.items()):
        with cols[i]:
            with st.container(border=True):
                st.subheader(plan)
                st.markdown(f"**{details['price']}**")
                st.divider()
                for feature in details['features']:
                    st.markdown(f"- {feature}")
                st.button("Get Quote", key=f"plan_{i}")

# ---------- Business Growth Tab ----------
with tabs[5]:
    st.header("Market Trends")
    
    growth_data = {
        "Technology": ["AI", "ML", "Cloud", "BI", "Automation"],
        "Demand (%)": [88, 85, 90, 75, 80]
    }
    
    st.altair_chart(
        alt.Chart(pd.DataFrame(growth_data))
        .mark_bar()
        .encode(
            x=alt.X("Technology", sort="-y"),
            y="Demand (%)",
            color=alt.Color("Technology", legend=None)
        ),
        use_container_width=True
    )
    
    st.markdown("""
    > Our analysis shows increasing demand for AI and Cloud solutions across industries.
    """)

# ---------- Leadership Tab ----------
with tabs[6]:
    st.header("Leadership Insights")
    
    messages = load_ceo_data()
    if messages:
        for msg in messages:
            with st.container(border=True):
                st.subheader(msg['name'])
                st.markdown(f"> {msg['message']}")
    else:
        st.info("No leadership messages yet")

# ---------- Admin Features ----------
if st.session_state.is_admin:
    # Business Analytics Tab
    with tabs[7]:
        st.header("Business Analytics")
        
        leads = load_leads_data()
        if leads:
            df = pd.DataFrame(leads)
            
            st.subheader("Lead Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Leads", len(df))
            with col2:
                st.metric("Latest Lead", df.iloc[0]['timestamp'][:10])
            
            st.subheader("Lead Timeline")
            st.line_chart(df['timestamp'].str[:10].value_counts().sort_index())
            
            st.subheader("All Leads")
            st.dataframe(df, hide_index=True)
            
            if csv_link := export_leads_to_csv():
                st.markdown(csv_link, unsafe_allow_html=True)
        else:
            st.info("No leads data available")

    # Admin Panel Tab
    with tabs[8]:
        st.header("Admin Panel")
        
        tab1, tab2 = st.tabs(["Add Project", "Post Message"])
        
        with tab1:
            with st.form("add_project", clear_on_submit=True):
                title = st.text_input("Project Title*")
                tech = st.text_input("Tech Stack* (comma separated)")
                description = st.text_area("Description*")
                image_url = st.text_input("Image URL")
                
                if st.form_submit_button("Save Project"):
                    if not all([title, tech, description]):
                        st.error("Missing required fields")
                    elif save_project_data({
                        "title": title,
                        "tech": tech,
                        "description": description,
                        "image_url": image_url
                    }):
                        st.success("Project saved!")
                    else:
                        st.error("Failed to save project")
        
        with tab2:
            with st.form("ceo_message", clear_on_submit=True):
                name = st.text_input("Author Name*")
                message = st.text_area("Message*")
                
                if st.form_submit_button("Post Message"):
                    if not all([name, message]):
                        st.error("Missing required fields")
                    elif save_ceo_message({"name": name, "message": message}):
                        st.success("Message posted!")
                    else:
                        st.error("Failed to save message")

    # Logout Tab
    with tabs[9]:
        if st.button("Logout", type="primary"):
            st.session_state.is_admin = False
            st.session_state.username = ""
            st.rerun()

# ---------- Login Tab ----------
else:
    with tabs[-1]:
        st.header("User Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                if verify_admin(username, password):
                    st.session_state.is_admin = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")

# ---------- Footer ----------
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>© 2023 HYS Consulting | <a href='/privacy'>Privacy Policy</a></p>
</div>
""", unsafe_allow_html=True)
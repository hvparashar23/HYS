import streamlit as st
from PIL import Image

# Page config
st.set_page_config(page_title="HYS Consulting", layout="wide")

# Sidebar or top image/logo
st.image("HYSConsulting.png", width=150)
st.title("HYS Consulting")
st.subheader("Empowering Businesses with Smart IT Solutions")

# Navigation Tabs
section = st.sidebar.radio("Navigate", ["Home", "Services", "About", "Contact"])

# Home Section
if section == "Home":
    st.header("Welcome to HYS Consulting")
    st.write("We are a team of IT experts offering cutting-edge consulting services in Data Engineering, AI Solutions, Business Intelligence, and Cloud Infrastructure.")
    st.image("https://images.unsplash.com/photo-1603574670812-d24560880210", caption="Innovating IT Solutions", use_container_width=True)

# Services Section
elif section == "Services":
    st.header("Our Services")
    cols = st.columns(2)
    cols[0].subheader("🔍 Data Engineering")
    cols[0].write("We help build robust data pipelines and warehouses.")

    cols[1].subheader("🤖 AI & ML Solutions")
    cols[1].write("Tailored machine learning models to suit your business.")

    cols[0].subheader("📊 Business Intelligence")
    cols[0].write("Transform your data into actionable insights.")

    cols[1].subheader("☁️ Cloud Strategy")
    cols[1].write("Optimize your operations with modern cloud solutions.")

# About Section
elif section == "About":
    st.header("About Us")
    st.write("HYS Consulting is driven by a vision to digitally transform businesses using advanced IT strategies. With over 20 years of industry experience, we aim to provide scalable and secure digital solutions.")
    st.write("**Our Mission:** To simplify technology and amplify business value.")

# Contact Section
elif section == "Contact":
    st.header("Get in Touch")
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Your Message")
        submitted = st.form_submit_button("Send")
        if submitted:
            st.success(f"Thank you {name}, we will get back to you at {email}!")

    st.markdown("**Location:** Ace City, Noida Sector 1")
    st.markdown("📞 **Phone:** +91-9811508110")
    st.markdown("🌐 **Website:** www.hysconsulting.com (coming soon)")

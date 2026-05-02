import streamlit as st
import pandas as pd
import os
import subprocess
import time
import sys # <-- We added this to track the exact Python path

# Set the page configuration
st.set_page_config(page_title="NexGen Intel Engine", layout="wide", page_icon="⚡")

# Custom Title Header
st.title("⚡ NexGen Builds: Smart-Lead Gen Engine")
st.markdown("Automated Lead Scoring and Outreach Generation Pipeline.")

# --- THE SECURITY GATE ---
st.sidebar.title("🔒 Engine Access")
engine_password = st.sidebar.text_input("Enter Admin Password", type="password")

# If the password is wrong, stop everything and don't load the rest of the app
if engine_password != "NexGenSecure2026":
    st.warning("Please enter the correct password in the sidebar to access the pipeline.")
    st.stop()

# --- THE MAGIC ONE-CLICK PIPELINE ---
st.markdown("### ⚙️ Engine Control")
if st.button("🚀 Run Full Intel Pipeline (Scrape ➔ Score ➔ Draft)", type="primary"):
    with st.status("Executing NexGen Pipeline...", expanded=True) as status:
        try:
            # sys.executable forces it to use the (venv) Python!
            st.write("🕵️‍♂️ Scraping Hacker News for high-intent leads...")
            subprocess.run([sys.executable, "scraper.py"], check=True)
            
            st.write("🧠 Scoring leads with VADER Sentiment Analysis...")
            subprocess.run([sys.executable, "intel_engine.py"], check=True)
            
            st.write("🤖 Drafting personalized outreach with Gemini 2.5 Flash...")
            subprocess.run([sys.executable, "action_layer.py"], check=True)
            
            status.update(label="Pipeline Complete! Reloading data...", state="complete", expanded=False)
            time.sleep(1) 
            st.rerun() 
            
        except subprocess.CalledProcessError as e:
            status.update(label="Pipeline Failed", state="error")
            st.error("An error occurred while running the scripts. Check your terminal for details.")

st.markdown("---")

# --- DATA LOADING AND DISPLAY ---
def load_data():
    file_path = 'final_actionable_leads.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data found. Click the 'Run Full Intel Pipeline' button above to generate leads.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Leads Found", value=len(df))
    with col2:
        top_score = df['Lead_Score'].max()
        st.metric(label="Hottest Lead Score", value=f"{top_score}/100")
    with col3:
        st.metric(label="Platform Active", value="Hacker News (MVP)")

    st.markdown("---")
    
    st.subheader("🔥 Actionable Pipeline")
    
    for index, row in df.iterrows():
        with st.expander(f"Lead: {row['Post_Title']} (Score: {row['Lead_Score']})"):
            info_col, action_col = st.columns([1, 1])
            
            with info_col:
                st.markdown("**Author:** " + str(row['Author']))
                st.markdown(f"**Source Link:** [View Original Post]({row['URL']})")
                
            with action_col:
                st.markdown("**AI Drafted Outreach:**")
                st.info(row['Draft_Message'])
                
                if st.button("🚀 Approve & Send", key=f"send_{index}"):
                    st.success("Message Approved! (In production, this triggers the API).")

    st.markdown("---")
    st.caption("NexGen Builds Proprietary Intel Engine v1.1")

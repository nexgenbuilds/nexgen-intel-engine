import streamlit as st
import pandas as pd
import os
import subprocess
import time
import sys
import re
from emailer import send_outreach_email

st.set_page_config(page_title="NexGen Intel Engine", layout="wide", page_icon="⚡")

st.title("⚡ NexGen Builds: Smart-Lead Gen Engine")
st.markdown("Automated Lead Scoring and Outreach Generation Pipeline.")

st.sidebar.title("🔒 Engine Access")
engine_password = st.sidebar.text_input("Enter Admin Password", type="password")

if engine_password != "NexGenSecure2026": 
    st.warning("Please enter the correct password in the sidebar to access the pipeline.")
    st.stop()

st.markdown("### ⚙️ Engine Control")
if st.button("🚀 Run Full Intel Pipeline (Scrape ➔ Score ➔ Draft)", type="primary"):
    with st.status("Executing NexGen Pipeline...", expanded=True) as status:
        try:
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
        st.metric(label="Platform Active", value="Omni-Channel")

    st.markdown("---")
    st.subheader("🔥 Actionable Pipeline")
    
    for index, row in df.iterrows():
        with st.expander(f"Lead: {row['Post_Title']} (Score: {row['Lead_Score']})"):
            info_col, action_col = st.columns([1, 1])
            
            with info_col:
                # BUG FIX: Intercept the literal string "Unknown" from the CSV
                author_val = str(row['Author']).strip()
                display_author = "LinkedIn User" if author_val == "Unknown" or author_val == "nan" else author_val
                
                st.markdown(f"**Author:** {display_author}")
                st.markdown(f"**Source Link:** [View Original Post]({row['URL']})")
                
            with action_col:
                st.markdown("**AI Drafted Outreach:**")
                
                safe_title_key = re.sub(r'\W+', '', str(row['Post_Title']))[:15]
                unique_key = f"draft_{index}_{safe_title_key}"
                
                final_draft = st.text_area("Edit Message:", value=row['Draft_Message'], height=150, key=unique_key)
                target_email = st.text_input("Target Email Address:", placeholder="client@company.com", key=f"email_{unique_key}")
                
                if st.button("🚀 Approve & Send", key=f"send_{unique_key}"):
                    if target_email:
                        with st.spinner("Dispatching email..."):
                            subject = f"Quick question regarding your post about {str(row['Post_Title'])[:20]}..."
                            success, message = send_outreach_email(target_email, subject, final_draft)
                            
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                    else:
                        st.warning("Please enter a target email address first.")

    st.markdown("---")
    st.caption("NexGen Builds Proprietary Intel Engine v1.2")
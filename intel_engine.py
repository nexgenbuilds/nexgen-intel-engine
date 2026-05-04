import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print("[*] Initializing VADER Sentiment NLP...")
analyzer = SentimentIntensityAnalyzer()

# 1. Load Data from ALL Sources
df_list = []

hn_file = 'raw_leads_mvp.csv'
if os.path.exists(hn_file):
    print(f"[*] Loading Hacker News leads from {hn_file}...")
    df_list.append(pd.read_csv(hn_file))

li_file = 'linkedin_raw_leads.csv'
if os.path.exists(li_file):
    print(f"[*] Loading LinkedIn leads from {li_file}...")
    df_list.append(pd.read_csv(li_file))

if not df_list:
    print("[-] No raw leads found. Run a scraper (scraper.py or linkedin_adapter.py) first.")
    exit()

# Combine all leads into one master dataframe
df = pd.concat(df_list, ignore_index=True)
print(f"[*] Merged a total of {len(df)} leads for scoring...")

# 2. Score the Leads
scores = []
for index, row in df.iterrows():
    # Safely get text, handling NaN values
    title = str(row.get('Post_Title', ''))
    body = str(row.get('Post_Body', ''))
    text_to_analyze = title + " " + body
    
    sentiment_dict = analyzer.polarity_scores(text_to_analyze)
    
    # Core logic: Base score (50) + Frustration/Pain points
    base_score = 50 
    frustration_bonus = sentiment_dict['neg'] * 50 
    
    # 🌟 The B2B Multiplier: Give LinkedIn leads a priority bump
    platform_bump = 10 if row.get('Platform') == 'LinkedIn' else 0
    
    final_score = round(base_score + frustration_bonus + platform_bump, 1)
    
    # Cap the maximum score at 100
    final_score = min(final_score, 100.0)
    scores.append(final_score)

df['Lead_Score'] = scores

# 3. Sort and Save
df = df.sort_values(by='Lead_Score', ascending=False)
df.to_csv('scored_leads_mvp.csv', index=False)

print(f"[+] SUCCESS: Scored {len(df)} leads across multiple platforms.")
print("[+] Master ranked data saved to scored_leads_mvp.csv")

if not df.empty:
    top_lead = df.iloc[0]
    print("\n=== 🔥 HOTTEST LEAD 🔥 ===")
    print(f"Platform: {top_lead.get('Platform', 'Unknown')}")
    print(f"Score: {top_lead['Lead_Score']}/100")
    print(f"Title: {top_lead['Post_Title'][:50]}...")
    print("===========================\n")
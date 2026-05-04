import pandas as pd
from google import genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def draft_outreach(post_title, post_body="", retries=3):
    prompt = f"""
    You are the Founder and Lead Developer of NexGen Builds, a technical data science and automation agency. 
    You are browsing social media for leads and saw a post from a potential client.
    
    Title: "{post_title}"
    Body: "{post_body}"
    
    Write a short, casual direct message (2 to 3 sentences maximum) to the author.
    
    Rules:
    - Position yourself as a professional automation expert/founder. Do NOT mention being a student.
    - Do NOT sell anything aggressively; focus on starting a conversation.
    - Acknowledge their specific problem or project naturally.
    - Offer a quick observation or mention that your agency builds custom data pipelines that solve this exact issue.
    - Keep the tone highly professional but approachable.
    """
    
    # Retry logic: Try up to 3 times if the server is busy
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                print(f"[*] Gemini API busy (Attempt {attempt+1}/{retries}). Waiting 3 seconds...")
                time.sleep(3)
            else:
                return f"Error generating draft: {e}"
                
    return "Error: AI generation failed after multiple attempts. The server is overloaded right now."

def generate_drafts(input_csv, output_csv):
    if not os.path.exists(input_csv):
        print(f"Can't find {input_csv}. Make sure you ran the intel engine first.")
        return
        
    print(f"Loading scored leads from {input_csv}...")
    df = pd.read_csv(input_csv)
    top_leads = df.head(3).copy()
    
    print("Writing professional agency outreach messages via Gemini...")
    
    drafts = []
    for index, row in top_leads.iterrows():
        print(f"[*] Drafting message for lead {index + 1}...")
        draft = draft_outreach(row['Post_Title'], str(row.get('Post_Body', '')))
        drafts.append(draft)
        # Give the API a 2-second breather between each request
        time.sleep(2) 
        
    top_leads['Draft_Message'] = drafts
    top_leads.to_csv(output_csv, index=False)
    
    print("\n=== AI DRAFTING COMPLETE ===")
    best_lead = top_leads.iloc[0]
    print(f"\nLead Title: {best_lead['Post_Title']}")
    print(f"Drafted Message:\n{best_lead['Draft_Message']}")
    print("\nEverything saved to", output_csv)

if __name__ == "__main__":
    generate_drafts(input_csv='scored_leads_mvp.csv', output_csv='final_actionable_leads.csv')
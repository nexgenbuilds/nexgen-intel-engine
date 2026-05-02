import pandas as pd
from google import genai
import os
from dotenv import load_dotenv

# load the keys from the .env file
load_dotenv()

# set up the new official gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def draft_outreach(post_title):
    # strict prompt to prevent the AI from sounding like a salesman
    prompt = f"""
    You are a friendly computer science student and developer browsing Hacker News. 
    You just saw a post with this title: "{post_title}"
    
    Write a short, casual direct message (2 to 3 sentences maximum) to the author.
    
    Rules:
    - Do NOT sell anything.
    - Do NOT use corporate jargon or buzzwords.
    - Sound like a student just reaching out to chat or offer a free tip.
    - Mention their specific project naturally.
    """
    
    try:
        # using the newest flash model for speed and reliability
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating draft: {e}"

def generate_drafts(input_csv, output_csv):
    if not os.path.exists(input_csv):
        print(f"Can't find {input_csv}. Make sure you ran the intel engine first.")
        return
        
    print(f"Loading scored leads from {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # just taking the top 3 leads to save api tokens during testing
    top_leads = df.head(3).copy()
    
    print("Writing personalized outreach messages via Gemini...")
    
    # apply the drafting function to the top titles
    top_leads['Draft_Message'] = top_leads['Post_Title'].apply(draft_outreach)
    
    # save the final results
    top_leads.to_csv(output_csv, index=False)
    
    print("\n=== AI DRAFTING COMPLETE ===")
    
    # show off the number one result
    best_lead = top_leads.iloc[0]
    print(f"\nLead Title: {best_lead['Post_Title']}")
    print(f"Drafted Message:\n{best_lead['Draft_Message']}")
    print("\nEverything saved to", output_csv)

if __name__ == "__main__":
    generate_drafts(input_csv='scored_leads_mvp.csv', output_csv='final_actionable_leads.csv')
import requests
import pandas as pd
from datetime import datetime

class HackerNewsScraper:
    def __init__(self):
        # Hacker news provides a free open database we can read from
        self.base_url = "https://hacker-news.firebaseio.com/v0"

    def fetch_leads(self, keywords, limit=50):
        leads = []
        print("Connecting to Hacker News to scan for leads...")
        
        try:
            # Grab the IDs of the newest posts
            response = requests.get(f"{self.base_url}/newstories.json")
            story_ids = response.json()[:limit * 2] 
            
            for story_id in story_ids:
                # Get the actual content of each post
                story_resp = requests.get(f"{self.base_url}/item/{story_id}.json").json()
                
                if not story_resp or 'title' not in story_resp:
                    continue
                
                # Combine title and text to search for our keywords
                text_content = story_resp.get('title', '').lower()
                if 'text' in story_resp:
                    text_content += " " + str(story_resp['text']).lower()
                
                # If they say something we are looking for, save them as a lead
                if any(kw.lower() in text_content for kw in keywords):
                    leads.append({
                        'Platform': 'Hacker News',
                        'Author': story_resp.get('by', 'Unknown'),
                        'Post_Title': story_resp.get('title', ''),
                        'URL': f"https://news.ycombinator.com/item?id={story_id}",
                        'Timestamp': datetime.fromtimestamp(story_resp.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S')
                    })
        except Exception as e:
            print(f"Oops, ran into an issue fetching data: {e}")
            
        return pd.DataFrame(leads)


if __name__ == "__main__":
    print("Starting the engine...")
    hn_engine = HackerNewsScraper()
    
    # Words that show someone is looking for a solution
    target_keywords = ['automate', 'api', 'help', 'tool', 'need', 'how to']
    
    # We will scan the latest 50 posts
    df_leads = hn_engine.fetch_leads(keywords=target_keywords, limit=50)

    if not df_leads.empty:
        df_leads.to_csv('raw_leads_mvp.csv', index=False)
        print(f"Success! Found {len(df_leads)} potential leads.")
        print("Saved everything to raw_leads_mvp.csv")
    else:
        print("No leads found in the latest posts right now. Try again in a bit!")
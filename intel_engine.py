import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

class LeadScorer:
    def __init__(self):
        print("[*] Initializing VADER Sentiment NLP...")
        self.analyzer = SentimentIntensityAnalyzer()

    def calculate_score(self, text):
        # Handle empty text safely
        if not isinstance(text, str):
            return 50  # Base score for just matching our keywords

        # Analyze the text
        sentiment = self.analyzer.polarity_scores(text)
        
        # We want to measure "Pain" or "Frustration" (Negative sentiment)
        # VADER 'neg' score is between 0.0 and 1.0
        pain_intensity = sentiment['neg']
        
        # Calculate Lead Score (Out of 100)
        # Base score is 50 because they already matched our intent keywords in Phase 1
        # We add up to 50 more points based on how frustrated they sound
        lead_score = 50 + (pain_intensity * 50)
        
        return round(lead_score, 1)

    def process_leads(self, input_csv, output_csv):
        if not os.path.exists(input_csv):
            print(f"[!] Error: Could not find {input_csv}. Run scraper.py first.")
            return

        print(f"[*] Loading raw leads from {input_csv}...")
        df = pd.read_csv(input_csv)

        print("[*] Running sentiment analysis and calculating Lead Scores...")
        # Apply the scoring formula to the Post Title 
        # (For Hacker News, the title usually contains the main pain point)
        df['Lead_Score'] = df['Post_Title'].apply(self.calculate_score)

        # Sort the leads so the most desperate/highest score is at the top
        df = df.sort_values(by='Lead_Score', ascending=False)

        # Save the upgraded data
        df.to_csv(output_csv, index=False)
        print(f"[+] SUCCESS: Scored {len(df)} leads.")
        print(f"[+] Ranked data saved to {output_csv}\n")

        # Display the hottest lead
        top_lead = df.iloc[0]
        print("=== 🔥 HOTTEST LEAD 🔥 ===")
        print(f"Score: {top_lead['Lead_Score']}/100")
        print(f"Title: {top_lead['Post_Title']}")
        print(f"Link:  {top_lead['URL']}")
        print("===========================")

if __name__ == "__main__":
    scorer = LeadScorer()
    scorer.process_leads(input_csv='raw_leads_mvp.csv', output_csv='scored_leads_mvp.csv')
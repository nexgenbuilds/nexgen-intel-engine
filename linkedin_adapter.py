from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
from dotenv import load_dotenv
from datetime import datetime

# Load credentials
load_dotenv()
LINKEDIN_USER = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASS = os.getenv('LINKEDIN_PASSWORD')

class LinkedInAdapter:
    def __init__(self):
        print("[*] Initializing LinkedIn Stealth Adapter with Persistent Context...")
        self.user_data_dir = "./linkedin_profile_data"

    def fetch_leads(self, keyword, limit=10):
        leads = []
        
        with sync_playwright() as p:
            print("[*] Launching browser (Visible Mode)...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False, 
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.pages[0] if context.pages else context.new_page()

            try:
                print("[*] Navigating to LinkedIn Feed...")
                # Go to the feed and wait for the network to settle
                page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)
                time.sleep(5) # Give LinkedIn a moment to auto-redirect if needed

                # Bulletproof Login Check based on URL
                current_url = page.url
                
                if "login" in current_url or "signup" in current_url:
                    print("[!] Redirected to login page. Attempting login...")
                    
                    page.wait_for_selector("#username", timeout=60000)
                    page.locator("#username").fill(LINKEDIN_USER)
                    time.sleep(1)
                    page.locator("#password").fill(LINKEDIN_PASS)
                    time.sleep(1)
                    page.locator("[type='submit']").click()

                    print("\n=======================================================")
                    print("🚨 MANUAL INTERVENTION REQUIRED 🚨")
                    print("Look at the browser window! If there is a CAPTCHA,")
                    print("a security code, or an onboarding screen, SOLVE IT NOW.")
                    print("You have 60 seconds before the script continues...")
                    print("=======================================================\n")
                    
                    # Wait for the feed URL to confirm login success
                    page.wait_for_url("**/feed/**", timeout=60000)
                    print("[+] Security cleared. We are in the feed.")
                else:
                    print("[+] URL confirms we are already in the feed! Saved cookies worked.")

                # 2. Search Process
                print(f"[*] Searching for high-intent keyword: '{keyword}'")
                search_url = f"https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER"
                page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                
                print("[*] Waiting for posts to load...")
                # LinkedIn uses multiple classes for posts, we wait for the main feed container
                page.wait_for_selector(".search-results-container", timeout=60000)
                
                # Scroll to load dynamic content
                for _ in range(3):
                    page.mouse.wheel(0, 1500)
                    time.sleep(2)

                # 3. Extraction Process
                print("[*] Extracting posts...")
                # Updated selectors to catch variations in LinkedIn's HTML
                posts = page.locator(".update-components-text").all_inner_texts()
                authors = page.locator(".update-components-actor__name").all_inner_texts()

                for i in range(min(len(posts), limit)):
                    if len(posts[i]) > 20: 
                        leads.append({
                            'Platform': 'LinkedIn',
                            'Author': authors[i].strip() if i < len(authors) else 'Unknown',
                            'Post_Title': posts[i][:50].replace('\n', ' ') + "...",
                            'Post_Body': posts[i].strip(),
                            'URL': search_url, 
                            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

            except Exception as e:
                print(f"\n[!] Encountered a roadblock: {e}")
            finally:
                context.close()
                
        return pd.DataFrame(leads)

if __name__ == "__main__":
    adapter = LinkedInAdapter()
    
    # Broadened the keyword slightly to ensure we catch results
    target_keyword = 'need help data scraping'
    
    df_leads = adapter.fetch_leads(keyword=target_keyword, limit=5)
    
    if not df_leads.empty:
        df_leads.to_csv('linkedin_raw_leads.csv', index=False)
        print(f"\n[+] SUCCESS: Extracted {len(df_leads)} LinkedIn leads.")
        print(df_leads[['Author', 'Post_Title']].head())
    else:
        print("\n[-] No leads extracted. Try running it again.")
import psycopg2
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import pandas as pd

def connect_to_db():
    return psycopg2.connect(
        dbname='postgres',
        user='YOUR USER NAME',
        password='YOUR PASSWORD',
        host='localhost',
        port='5432'
    )

def get_software_keywords():
    conn = connect_to_db()
    cur = conn.cursor()
    
    # Get keywords and corresponding software providers
    cur.execute("SELECT keyword, software_provider FROM softwares")
    keyword_data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Create a dictionary of keywords to software providers
    keyword_dict = {keyword.lower(): provider for keyword, provider in keyword_data}
    return keyword_dict

def analyze_website(url, keyword_dict):
    try:
        # Add scheme if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Get website content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all text content
        page_text = soup.get_text().lower()
        page_source = response.text.lower()
        
        # Search for keywords
        for keyword, provider in keyword_dict.items():
            if keyword.lower() in page_text or keyword.lower() in page_source:
                return provider
                
        return None
        
    except Exception as e:
        print(f"Error analyzing {url}: {str(e)}")
        return None

def main():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        
        # Get software keywords
        keyword_dict = get_software_keywords()
        print(f"Loaded {len(keyword_dict)} keywords to search for")
        
        # Get first 5 links for testing
        cur.execute("""
            SELECT url, link 
            FROM website_scraping 
            WHERE link IS NOT NULL 
            AND length(link) > 0 
            LIMIT 5
        """)
        
        links = cur.fetchall()
        print(f"\nAnalyzing {len(links)} websites...")
        
        results = []
        for url, link in links:
            print(f"\nProcessing: {url}")
            software = analyze_website(link, keyword_dict)
            
            if software:
                print(f"✓ Found software: {software}")
                # Update database
                cur.execute("""
                    UPDATE website_scraping 
                    SET software = %s 
                    WHERE url = %s
                """, (software, url))
                conn.commit()
                
                results.append({
                    'url': url,
                    'link': link,
                    'software': software
                })
            else:
                print("✗ No matching software found")
        
        # Print summary
        print("\n=== Results ===")
        if results:
            df = pd.DataFrame(results)
            print("\nMatched Software:")
            print(df.to_string(index=False))
        else:
            print("No software matches found in the test sample")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 

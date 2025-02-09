import psycopg2
import pandas as pd
from collections import defaultdict
import re
from urllib.parse import urlparse
import csv
import sys
from datetime import datetime

def connect_to_db():
    return psycopg2.connect(
        dbname='postgres',
        user='YOUR USER NAME',
        password='YOUR PASSWORD',
        host='localhost',
        port='5432'
    )

def extract_domain_patterns(url):
    try:
        # Ensure URL has a protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        parsed = urlparse(url)
        full_domain = parsed.netloc.lower()
        
        # Split into parts (subdomain.domain.tld)
        parts = full_domain.split('.')
        
        # Common booking platform patterns
        patterns = {
            'zenoti': 'Zenoti',
            'boulevard': 'Boulevard',
            'blvd': 'Boulevard',
            'vagaro': 'Vagaro',
            'moxie': 'Moxie',
            'joinmoxie': 'Moxie',
            'fresha': 'Fresha',
            'glossgenius': 'GlossGenius',
            'gloss': 'GlossGenius',
            'squareup': 'Square',
            'square': 'Square',
            'mindbody': 'Mindbody',
            'mindbodyonline': 'Mindbody',
            'appointmentplus': 'AppointmentPlus',
            'booksy': 'Booksy',
            'schedulicity': 'Schedulicity',
            'acuity': 'Acuity',
            'genbook': 'Genbook',
            'resurva': 'Resurva',
            'shedul': 'Shedul',
            'booker': 'Booker',
            'salonrunner': 'SalonRunner',
            'shortcuts': 'Shortcuts',
            'phorest': 'Phorest',
            'timely': 'Timely',
            'setmore': 'Setmore',
            'calendly': 'Calendly'
        }
        
        # Check each part for patterns
        found_patterns = []
        for part in parts[:-1]:  # Exclude TLD
            for pattern, platform in patterns.items():
                if pattern in part:
                    found_patterns.append({
                        'pattern': pattern,
                        'platform': platform,
                        'location': 'subdomain' if part != parts[-2] else 'domain',
                        'full_url': url
                    })
                    
        return found_patterns
    except:
        return []

def analyze_url_patterns():
    try:
        # Connect to database
        conn = connect_to_db()
        cur = conn.cursor()
        
        # Get all non-null links
        cur.execute("""
            SELECT link 
            FROM website_scraping 
            WHERE link IS NOT NULL 
            AND length(link) > 0
        """)
        
        links = cur.fetchall()
        print(f"Analyzing {len(links)} links...")
        
        # Process all links
        all_patterns = []
        for link_tuple in links:
            link = link_tuple[0]
            patterns = extract_domain_patterns(link)
            all_patterns.extend(patterns)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_patterns)
        
        if not df.empty:
            # Group by pattern and platform
            summary = df.groupby(['pattern', 'platform', 'location']).agg({
                'full_url': ['count', 'first']
            }).reset_index()
            
            # Flatten column names
            summary.columns = ['pattern', 'platform', 'location', 'count', 'example_url']
            
            # Calculate percentage
            total_links = len(links)
            summary['percentage'] = (summary['count'] / total_links * 100).round(2)
            
            # Sort by count
            summary = summary.sort_values('count', ascending=False)
            
            # Save to CSV
            output_file = 'domain_patterns.csv'
            summary.to_csv(output_file, index=False)
            print(f"\nResults saved to {output_file}")
            
            # Print results
            print("\nDomain/Subdomain Patterns Found:")
            print("=" * 100)
            for _, row in summary.iterrows():
                print(f"\nPattern: {row['pattern']} ({row['platform']})")
                print(f"Location: {row['location']}")
                print(f"Count: {row['count']} ({row['percentage']}%)")
                print(f"Example: {row['example_url']}")
                print("-" * 50)
            
            # Print summary by platform
            print("\nPlatform Summary:")
            platform_summary = df.groupby('platform')['full_url'].count().sort_values(ascending=False)
            for platform, count in platform_summary.items():
                print(f"{platform}: {count} ({(count/total_links*100):.2f}%)")
        
        else:
            print("No patterns found in the analyzed URLs")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    analyze_url_patterns()

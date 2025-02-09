import pandas as pd
import os
from datetime import datetime
import psycopg2
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
import io

# Create website_scraping directory if it doesn't exist
if not os.path.exists('website_scraping'):
    os.makedirs('website_scraping')
if not os.path.exists('website_scraping/screenshots'):
    os.makedirs('website_scraping/screenshots')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('website_scraping', 'scraper.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

booking_texts = [
    # Basic terms
    'book', 'schedule', 'appointment', 'reserve', 'consultation', 'booking',
    'appointments', 'reservations', 'scheduling', 'consult',
    
    # Book variations
    'book now', 'book online', 'book appointment', 'book consultation',
    'book your', 'book a', 'book today', 'book an', 'book free',
    'booking now', 'book here', 'book visit', 'book session',
    'book your appointment', 'book your consultation', 'book your visit',
    'book your session', 'book my appointment', 'book my consultation',
    'book an appointment', 'book a consultation', 'book a session',
    'book a visit', 'book instantly', 'book appointment now',
    'book consultation now', 'book your spot', 'book a spot',
    
    # Schedule variations
    'schedule now', 'schedule online', 'schedule appointment',
    'schedule your', 'schedule a', 'schedule today', 'schedule an',
    'scheduling', 'schedule here', 'schedule visit', 'schedule session',
    'schedule your appointment', 'schedule your consultation',
    'schedule your visit', 'schedule your session', 'schedule my appointment',
    'schedule my consultation', 'schedule an appointment',
    'schedule a consultation', 'schedule a session', 'schedule a visit',
    'schedule instantly', 'schedule appointment now',
    'schedule consultation now', 'schedule your spot', 'schedule a spot',
    
    # Appointment variations
    'get appointment', 'make appointment', 'request appointment',
    'start appointment', 'appointment here', 'new appointment',
    'make an appointment', 'get an appointment', 'request an appointment',
    'set appointment', 'set an appointment', 'book appointment',
    'schedule appointment', 'start your appointment', 'make your appointment',
    'get your appointment', 'request your appointment',
    'appointment booking', 'appointment scheduling',
    'appointment request', 'appointment now', 'appointment online',
    
    # Reserve variations
    'reserve now', 'reserve online', 'reserve appointment',
    'reserve your', 'reserve a', 'reserve today', 'reserve spot',
    'reserve your spot', 'reserve your appointment', 'reserve your consultation',
    'reserve your session', 'reserve appointment now', 'reserve consultation',
    'reserve session', 'make reservation', 'make a reservation',
    'reserve instantly', 'reserve here',
    
    # Consultation variations
    'free consultation', 'start consultation', 'get consultation',
    'consultation here', 'request consultation', 'book consultation',
    'schedule consultation', 'consultation now', 'consultation online',
    'get your consultation', 'request your consultation',
    'start your consultation', 'consultation booking', 'consultation request',
    'consultation scheduling', 'free consult', 'request a consultation',
    'get a consultation', 'book a consultation', 'schedule a consultation',
    
    # Visit variations
    'schedule visit', 'book visit', 'reserve visit', 'plan visit',
    'schedule your visit', 'book your visit', 'reserve your visit',
    'plan your visit', 'visit booking', 'visit scheduling',
    'schedule a visit', 'book a visit', 'reserve a visit',
    
    # Session variations
    'book session', 'schedule session', 'reserve session',
    'book your session', 'schedule your session', 'reserve your session',
    'session booking', 'session scheduling', 'book a session',
    'schedule a session', 'reserve a session',
    
    # Action words and phrases
    'start booking', 'get started', 'begin here', 'start here',
    'request visit', 'schedule visit', 'book visit', 'start now',
    'begin now', 'make a booking', 'make reservation', 'get started now',
    'start your booking', 'begin booking', 'instant booking',
    'instant scheduling', 'quick book', 'quick schedule',
    'easy booking', 'easy scheduling', 'online booking',
    'online scheduling', 'book instantly', 'schedule instantly',
    
    # Common button text
    'get started', 'start now', 'begin now', 'book online now',
    'schedule online now', 'reserve now', 'book instantly',
    'schedule instantly', 'reserve instantly', 'get appointment now',
    'make appointment now', 'request appointment now',
    'get consultation now', 'request consultation now',
    
    # Time-related variations
    'book today', 'schedule today', 'reserve today',
    'book now', 'schedule now', 'reserve now',
    'book appointment today', 'schedule appointment today',
    'book consultation today', 'schedule consultation today',
    
    # Call-to-action variations
    'start your journey', 'begin your journey', 'get started today',
    'start here', 'begin here', 'book here', 'schedule here',
    'reserve here', 'click to book', 'click to schedule',
    'click to reserve', 'tap to book', 'tap to schedule',
    
    # Additional common variations
    'set up appointment', 'set up consultation',
    'make your appointment', 'make your reservation',
    'secure your spot', 'secure your appointment',
    'secure your consultation', 'secure your session',
    'request your spot', 'request your appointment',
    'request your consultation', 'request your session'
] 

def get_websites_from_db():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='YOUR PASSOWRD',
            password='YOUR PASSWORD',
            host='localhost',
            port='5432'
        )
        
        # First, let's verify the count
        count_query = """
        SELECT COUNT(*) 
        FROM clinics_usa 
        WHERE category = 'Medical spa' 
        AND website IS NOT NULL;
        """
        
        df_count = pd.read_sql_query(count_query, conn)
        logger.info(f"Found {df_count.iloc[0,0]} Medical spa websites in database")
        
        # Get the websites
        query = """
        SELECT website, business_name 
        FROM clinics_usa 
        WHERE category = 'Medical spa'
        AND website IS NOT NULL;
        """
        
        df = pd.read_sql_query(query, conn)
        
        # Create dictionary of website to business name
        websites_dict = {
            url: name for url, name in zip(df['website'], df['business_name'])
            if url and isinstance(url, str) and name and isinstance(name, str)
        }
        
        logger.info(f"After filtering invalid entries: {len(websites_dict)} valid websites")
        
        # Print first few entries for verification
        logger.info("\nSample of websites to process:")
        for i, (url, name) in enumerate(list(websites_dict.items())[:5]):
            logger.info(f"{i+1}. {name}: {url}")
        
        conn.close()
        return websites_dict
        
    except Exception as e:
        logger.error(f"Error getting websites from database: {str(e)}")
        raise e

def clean_filename(business_name):
    # Convert to lowercase and replace spaces with hyphens
    cleaned = business_name.lower().strip()
    cleaned = cleaned.replace(' ', '-')
    # Remove any special characters except hyphens
    cleaned = ''.join(c for c in cleaned if c.isalnum() or c == '-')
    return cleaned

def create_scraping_table():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='YOUR USER NAME',
            password='YOUR PASSWORD',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()
        
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS website_scraping (
            id SERIAL PRIMARY KEY,
            url TEXT,
            business_name TEXT,
            text_button TEXT,
            link TEXT,
            screenshot_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cur.execute(create_table_query)
        conn.commit()
        logger.info("Website scraping table created/verified")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        raise e

def save_to_db(result):
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='YOUR USER NAME',
            password='YOUR PASSWORD',
            host='localhost',
            port='5432'
        )
        cur = conn.cursor()
        
        # Check if URL already exists
        check_query = """
        SELECT id FROM website_scraping 
        WHERE url = %s;
        """
        cur.execute(check_query, (result['url'],))
        existing_record = cur.fetchone()
        
        if existing_record:
            # Update existing record
            update_query = """
            UPDATE website_scraping 
            SET 
                business_name = %s,
                text_button = %s,
                link = %s,
                screenshot_name = %s,
                created_at = CURRENT_TIMESTAMP
            WHERE url = %s;
            """
            
            cur.execute(update_query, (
                result['business_name'],
                result['text_button'],
                result['link'],
                result['screenshot_name'],
                result['url']
            ))
            logger.info(f"Updated existing record for URL: {result['url']}")
            
        else:
            # Insert new record
            insert_query = """
            INSERT INTO website_scraping 
                (url, business_name, text_button, link, screenshot_name)
            VALUES 
                (%s, %s, %s, %s, %s);
            """
            
            cur.execute(insert_query, (
                result['url'],
                result['business_name'],
                result['text_button'],
                result['link'],
                result['screenshot_name']
            ))
            logger.info(f"Inserted new record for URL: {result['url']}")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error saving to database: {str(e)}")

def compress_screenshot(png_data, max_size_kb=200):
    """Compress screenshot to target size while maintaining readability"""
    try:
        # Convert PNG data to PIL Image
        image = Image.open(io.BytesIO(png_data))
        
        # Convert to RGB if image is in RGBA mode
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Start with quality=85 and reduce until file size is small enough
        quality = 85
        while quality > 10:
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            size_kb = len(output.getvalue()) / 1024
            
            if size_kb <= max_size_kb:
                logger.info(f"Compressed image to {size_kb:.1f}KB with quality {quality}")
                return output.getvalue()
                
            quality -= 5
        
        # If we get here, use lowest quality
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=10, optimize=True)
        logger.info(f"Compressed image to {len(output.getvalue())/1024:.1f}KB with minimum quality")
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error compressing image: {str(e)}")
        raise e

def find_booking_buttons(websites_dict):
    try:
        logger.info("Starting web scraping process for Medical Spas...")
        
        # Create the database table
        create_scraping_table()
        
        # Create directories
        base_dir = 'web_scraping'
        screenshots_dir = os.path.join(base_dir, 'screenshots')
        
        for directory in [base_dir, screenshots_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
        
        results = []
        processed_urls = set()
        
        # Setup Chrome driver with simplified fullscreen settings
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')  # Set initial window size
        
        driver = webdriver.Chrome(options=options)
        
        # Set viewport size
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': 1920,
            'height': 1080,
            'deviceScaleFactor': 1,
            'mobile': False
        })
        
        total_sites = len(websites_dict)
        current_site = 0
        
        for url, business_name in websites_dict.items():
            try:
                current_site += 1
                
                # Print progress
                progress = (current_site / total_sites) * 100
                logger.info(f"\n{'='*50}")
                logger.info(f"Progress: {current_site} out of {total_sites} websites ({progress:.1f}%)")
                logger.info(f"Currently processing: {business_name}")
                logger.info(f"URL: {url}")
                logger.info(f"{'='*50}")
                
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                driver.get(url)
                time.sleep(10)
                
                # Take screenshot and compress
                png_data = driver.get_screenshot_as_png()
                compressed_data = compress_screenshot(png_data)
                
                # Save compressed screenshot
                screenshot_name = clean_filename(business_name) + '.jpg'
                screenshot_path = os.path.join(screenshots_dir, screenshot_name)
                
                with open(screenshot_path, 'wb') as f:
                    f.write(compressed_data)
                
                file_size = os.path.getsize(screenshot_path) / 1024  # Size in KB
                logger.info(f"Screenshot saved as: {screenshot_name} ({file_size:.1f}KB)")
                
                found_button = False
                
                for text in booking_texts:
                    if found_button:
                        break
                        
                    xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]"
                    elements = driver.find_elements(By.XPATH, xpath)
                    
                    for element in elements:
                        try:
                            element_text = element.text.strip()
                            if element_text:
                                href = element.get_attribute('href') if element.tag_name == 'a' else None
                                onclick = element.get_attribute('onclick')
                                
                                if href or onclick:
                                    result = {
                                        'url': url,
                                        'business_name': business_name,
                                        'text_button': element_text,
                                        'link': href if href else onclick,
                                        'screenshot_name': screenshot_name
                                    }
                                    
                                    # Save to database immediately
                                    save_to_db(result)
                                    results.append(result)
                                    
                                    found_button = True
                                    logger.info(f"Found booking button: {element_text}")
                                    logger.info("Saved result to database")
                                    break
                        except Exception as e:
                            continue
                
                # If no booking button was found, save with "Not Found" values
                if not found_button:
                    result = {
                        'url': url,
                        'business_name': business_name,
                        'text_button': 'Not Found',
                        'link': None,
                        'screenshot_name': screenshot_name
                    }
                    
                    # Save to database
                    save_to_db(result)
                    results.append(result)
                    logger.info("No booking button found. Saved 'Not Found' result to database")
                
                # Print summary after each website
                logger.info(f"Status: {'✓ Found booking button' if found_button else '✗ No booking button found'}")
                logger.info(f"Total websites processed: {current_site}")
                logger.info(f"Total booking buttons found: {len([r for r in results if r['text_button'] != 'Not Found'])}")
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                # Even if there's an error, try to save a record
                error_result = {
                    'url': url,
                    'business_name': business_name,
                    'text_button': 'Error',
                    'link': None,
                    'screenshot_name': None
                }
                save_to_db(error_result)
                logger.info("Saved error result to database")
                continue
        
        driver.quit()
        
        # Print final statistics
        total_found = len([r for r in results if r['text_button'] != 'Not Found' and r['text_button'] != 'Error'])
        total_not_found = len([r for r in results if r['text_button'] == 'Not Found'])
        total_errors = len([r for r in results if r['text_button'] == 'Error'])
        
        logger.info(f"\n{'='*50}")
        logger.info("FINAL RESULTS")
        logger.info(f"{'='*50}")
        logger.info(f"Total websites processed: {total_sites}")
        logger.info(f"Booking buttons found: {total_found}")
        logger.info(f"No booking buttons found: {total_not_found}")
        logger.info(f"Errors encountered: {total_errors}")
        logger.info(f"Success rate: {(total_found/total_sites)*100:.1f}%")
        logger.info(f"Screenshots saved in: {screenshots_dir}/")
        logger.info(f"Results saved in database table: website_scraping")
        logger.info(f"{'='*50}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise e

if __name__ == "__main__":
    websites_dict = get_websites_from_db()
    
    if websites_dict:
        results = find_booking_buttons(websites_dict)
    else:
        logger.error("No Medical Spa websites found in database")

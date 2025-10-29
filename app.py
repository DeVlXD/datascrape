from flask import Flask, render_template_string, request, send_file, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
from datetime import datetime
import re
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'

# Create downloads folder if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataScrape Pro - Google Maps Business Scraper</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }

        /* Navbar */
        .navbar {
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-badge {
            background: #dbeafe;
            color: #1e40af;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            padding: 4rem 2rem 3rem;
            text-align: center;
        }

        .hero h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            line-height: 1.2;
        }

        .hero p {
            font-size: 1.25rem;
            opacity: 0.95;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Main Content */
        .main-content {
            max-width: 1200px;
            margin: -2rem auto 0;
            padding: 0 2rem 4rem;
            position: relative;
            z-index: 10;
        }

        .card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            padding: 2.5rem;
            margin-bottom: 2rem;
        }

        .form-section h2 {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            color: #1e293b;
        }

        .form-section .subtitle {
            color: #64748b;
            margin-bottom: 2rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #334155;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }

        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 0.875rem 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.2s;
            background: #f8fafc;
        }

        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #3b82f6;
            background: white;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .btn {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 1rem;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 3rem 0;
        }

        .spinner {
            border: 4px solid #e2e8f0;
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: #64748b;
            font-size: 1.125rem;
            font-weight: 500;
        }

        .loading-subtext {
            color: #94a3b8;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }

        /* Features Grid */
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .feature {
            text-align: center;
            padding: 1.5rem;
            background: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        .feature h3 {
            font-size: 1.125rem;
            margin-bottom: 0.5rem;
            color: #1e293b;
        }

        .feature p {
            color: #64748b;
            font-size: 0.875rem;
        }

        /* Info Boxes */
        .info-box {
            padding: 1rem 1.25rem;
            border-radius: 8px;
            margin-top: 1.5rem;
            font-size: 0.875rem;
            border-left: 4px solid;
        }

        .info-box.warning {
            background: #fef3c7;
            border-color: #f59e0b;
            color: #92400e;
        }

        .info-box.info {
            background: #dbeafe;
            border-color: #3b82f6;
            color: #1e40af;
        }

        .info-box strong {
            font-weight: 600;
        }

        /* Footer */
        .footer {
            background: #1e293b;
            color: #94a3b8;
            padding: 2rem;
            text-align: center;
            font-size: 0.875rem;
        }

        .footer a {
            color: #60a5fa;
            text-decoration: none;
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }

            .card {
                padding: 1.5rem;
            }

            .features {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">DataScrape Pro</div>
            <span class="nav-badge">Beta v1.0</span>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <h1>Extract Business Data from Google Maps</h1>
        <p>Get comprehensive business information including emails, phone numbers, and more in minutes</p>
    </section>

    <!-- Main Content -->
    <main class="main-content">
        <div class="card">
            <div class="form-section">
                <h2>Start Your Search</h2>
                <p class="subtitle">Enter your search criteria to begin scraping business data</p>

                <form method="POST" action="/scrape" onsubmit="showLoading()" id="scrapeForm">
                    <div class="form-group">
                        <label for="location">Location</label>
                        <input type="text" id="location" name="location"
                               placeholder="e.g., New York, NY" required>
                    </div>

                    <div class="form-group">
                        <label for="keyword">Business Type / Keywords</label>
                        <input type="text" id="keyword" name="keyword"
                               placeholder="e.g., restaurants, coffee shops, dentists" required>
                    </div>

                    <div class="form-group">
                        <label for="max_results">Maximum Results (1-50)</label>
                        <input type="number" id="max_results" name="max_results"
                               value="10" min="1" max="50" required>
                    </div>

                    <button type="submit" class="btn">Start Scraping</button>
                </form>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <div class="loading-text">Scraping business data...</div>
                    <div class="loading-subtext">This may take 2-5 minutes depending on the number of results</div>
                </div>

                <div class="info-box warning">
                    <strong>Note:</strong> For production use, consider the Google Places API. It offers better reliability, official support, and $200/month in free credits.
                </div>

                <div class="info-box info">
                    <strong>What we extract:</strong> Business name, address, phone number, website, email (from website), rating, reviews, category, and plus code.
                </div>
            </div>
        </div>

        <!-- Features Section -->
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📧</div>
                <h3>Email Extraction</h3>
                <p>Automatically visits business websites to extract contact emails</p>
            </div>
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <h3>Fast & Efficient</h3>
                <p>Scrapes up to 50 businesses with comprehensive data in minutes</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📊</div>
                <h3>Excel Export</h3>
                <p>Get organized data in a ready-to-use Excel spreadsheet</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🎯</div>
                <h3>Accurate Data</h3>
                <p>Extracts 9+ data points per business with high accuracy</p>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <p>&copy; 2025 DataScrape Pro. For educational purposes only.</p>
    </footer>

    <script>
        function showLoading() {
            document.getElementById('scrapeForm').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
        }

        // Reset form visibility when page loads (fixes back button issue)
        window.addEventListener('pageshow', function(event) {
            document.getElementById('scrapeForm').style.display = 'block';
            document.getElementById('loading').style.display = 'none';
        });
    </script>
</body>
</html>
'''

RESULTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your File is Ready - DataScrape Pro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }

        .navbar {
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }

        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-badge {
            background: #dbeafe;
            color: #1e40af;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }

        .container {
            max-width: 800px;
            margin: 3rem auto;
            padding: 0 2rem;
        }

        .success-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            padding: 3rem 2.5rem;
            text-align: center;
        }

        .success-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 2rem;
            animation: scaleIn 0.5s ease-out;
        }

        .success-icon svg {
            width: 50px;
            height: 50px;
            color: white;
        }

        @keyframes scaleIn {
            0% {
                transform: scale(0);
            }
            50% {
                transform: scale(1.1);
            }
            100% {
                transform: scale(1);
            }
        }

        h1 {
            font-size: 2rem;
            color: #1e293b;
            margin-bottom: 1rem;
            font-weight: 700;
        }

        .subtitle {
            color: #64748b;
            font-size: 1.125rem;
            margin-bottom: 2rem;
        }

        .file-info {
            background: #f8fafc;
            border-radius: 12px;
            padding: 2rem;
            margin: 2rem 0;
            border: 2px solid #e2e8f0;
        }

        .file-info-row {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e2e8f0;
        }

        .file-info-row:last-child {
            border-bottom: none;
        }

        .file-info-label {
            color: #64748b;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }

        .file-info-value {
            color: #1e293b;
            font-weight: 600;
        }

        .download-btn {
            display: inline-block;
            padding: 1rem 3rem;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 1.125rem;
            font-weight: 600;
            transition: all 0.3s;
            margin-top: 1rem;
        }

        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }

        .download-btn:active {
            transform: translateY(0);
        }

        .secondary-btn {
            display: inline-block;
            padding: 0.875rem 2rem;
            background: white;
            color: #3b82f6;
            text-decoration: none;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s;
            margin-top: 1rem;
            margin-left: 1rem;
        }

        .secondary-btn:hover {
            background: #eff6ff;
        }

        .footer {
            background: #1e293b;
            color: #94a3b8;
            padding: 2rem;
            text-align: center;
            font-size: 0.875rem;
            margin-top: 4rem;
        }

        @media (max-width: 768px) {
            .success-card {
                padding: 2rem 1.5rem;
            }

            h1 {
                font-size: 1.5rem;
            }

            .download-btn, .secondary-btn {
                display: block;
                margin: 1rem auto;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="logo">DataScrape Pro</div>
            <span class="nav-badge">Beta v1.0</span>
        </div>
    </nav>

    <div class="container">
        <div class="success-card">
            <div class="success-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>

            <h1>Your File is Ready!</h1>
            <p class="subtitle">We've successfully scraped the business data you requested</p>

            <div class="file-info">
                <div class="file-info-row">
                    <span class="file-info-label">Results Found</span>
                    <span class="file-info-value">{{ results_count }} businesses</span>
                </div>
                <div class="file-info-row">
                    <span class="file-info-label">File Size</span>
                    <span class="file-info-value">{{ file_size }}</span>
                </div>
                <div class="file-info-row">
                    <span class="file-info-label">File Name</span>
                    <span class="file-info-value">{{ filename }}</span>
                </div>
                <div class="file-info-row">
                    <span class="file-info-label">Format</span>
                    <span class="file-info-value">Microsoft Excel (.xlsx)</span>
                </div>
            </div>

            <a href="/download/{{ file_id }}" class="download-btn">Download File</a>
            <a href="/" class="secondary-btn">Scrape More Data</a>
        </div>
    </div>

    <footer class="footer">
        <p>&copy; 2025 DataScrape Pro. For educational purposes only.</p>
    </footer>
</body>
</html>
'''

class GoogleMapsScraper:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        
    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            from selenium.webdriver.chrome.service import Service
            import os

            # Add Chrome binary location for production (Linux)
            if os.path.exists('/usr/bin/google-chrome'):
                chrome_options.binary_location = '/usr/bin/google-chrome'

            # Check if we're in production (ChromeDriver in /usr/local/bin)
            if os.path.exists('/usr/local/bin/chromedriver'):
                print("Using production ChromeDriver from /usr/local/bin/chromedriver")
                service = Service('/usr/local/bin/chromedriver')
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Local development - use webdriver-manager
                print("Using webdriver-manager for local development")
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Error setting up driver: {e}")
            # Final fallback
            self.driver = webdriver.Chrome(options=chrome_options)

        print("Chrome driver initialized successfully")
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def scrape_businesses(self, location, keyword, max_results=10):
        if not self.driver:
            self.setup_driver()
        
        print(f"Searching for: {keyword} in {location}")
        
        # Go to Google Maps
        self.driver.get("https://www.google.com/maps")
        time.sleep(3)
        
        # Find and use the search box
        try:
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_query = f"{keyword} in {location}"
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            print("Search submitted")
            time.sleep(5)
        except Exception as e:
            print(f"Error with search: {e}")
            return []
        
        results = []
        
        try:
            # Wait for results to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            
            # Scroll to load more results
            scrollable_div = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            
            scroll_count = 0
            max_scrolls = 10
            
            while scroll_count < max_scrolls and len(results) < max_results:
                # Scroll down
                self.driver.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollHeight', 
                    scrollable_div
                )
                time.sleep(2)
                scroll_count += 1
                
                # Check if we've reached the end
                try:
                    end_message = self.driver.find_element(By.CSS_SELECTOR, "p.fontBodyMedium")
                    if "You've reached the end" in end_message.text:
                        print("Reached end of results")
                        break
                except:
                    pass
            
            # Get all business links
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
            unique_links = []
            seen = set()
            
            for link in links:
                href = link.get_attribute('href')
                if href and href not in seen and '/maps/place/' in href:
                    unique_links.append(href)
                    seen.add(href)
                    if len(unique_links) >= max_results:
                        break
            
            print(f"Found {len(unique_links)} unique businesses")
            
            # Visit each business page
            for idx, url in enumerate(unique_links[:max_results]):
                try:
                    print(f"Scraping business {idx + 1}/{len(unique_links)}")
                    self.driver.get(url)
                    time.sleep(3)
                    
                    business_data = self.extract_business_info()
                    if business_data and business_data.get('Name'):
                        results.append(business_data)
                        print(f"  ✓ {business_data['Name']}")
                    
                except Exception as e:
                    print(f"  ✗ Error processing business {idx + 1}: {str(e)}")
                    continue
                    
        except TimeoutException:
            print("Timeout waiting for results")
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
        
        return results
    
    def extract_email_from_website(self, website_url):
        """Try to extract email from business website"""
        if not website_url:
            return ''
        
        try:
            # Open website in new tab
            self.driver.execute_script(f"window.open('{website_url}', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(3)
            
            # Get page source and search for email patterns
            page_source = self.driver.page_source.lower()
            
            # Email regex pattern
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_source)
            
            # Filter out common non-business emails
            excluded_domains = ['example.com', 'domain.com', 'email.com', 'wix.com', 
                              'wordpress.com', 'sentry.io', 'google.com', 'facebook.com']
            
            valid_emails = [email for email in emails 
                          if not any(domain in email for domain in excluded_domains)]
            
            # Close the tab and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return valid_emails[0] if valid_emails else ''
            
        except Exception as e:
            print(f"    Error extracting email from website: {str(e)}")
            try:
                # Make sure we're back on the main tab
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return ''
    
    def extract_business_info(self):
        data = {
            'Name': '',
            'Address': '',
            'Phone': '',
            'Website': '',
            'Email': '',
            'Rating': '',
            'Reviews': '',
            'Category': '',
            'Plus Code': ''
        }
        
        try:
            # Name - try multiple selectors
            try:
                name = self.driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
                data['Name'] = name
            except:
                try:
                    name = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                    data['Name'] = name
                except:
                    pass
            
            # Get all buttons and divs that might contain info
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-item-id]")
                for button in buttons:
                    aria_label = button.get_attribute('aria-label') or ''
                    text = button.text
                    
                    # Address
                    if 'address' in button.get_attribute('data-item-id'):
                        data['Address'] = text
                    
                    # Phone
                    if 'phone' in aria_label.lower() or 'phone' in button.get_attribute('data-item-id'):
                        data['Phone'] = text
            except:
                pass
            
            # Website
            try:
                website_link = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id='authority']")
                data['Website'] = website_link.get_attribute('href')
                
                # Try to extract email from website
                print("    Checking website for email...")
                data['Email'] = self.extract_email_from_website(data['Website'])
                if data['Email']:
                    print(f"    ✓ Found email: {data['Email']}")
            except:
                pass
            
            # Rating and Reviews
            try:
                rating_elem = self.driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']")
                data['Rating'] = rating_elem.text
                
                review_elem = self.driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-label*='reviews']")
                reviews_text = review_elem.get_attribute('aria-label')
                reviews_match = re.findall(r'([\d,]+)\s*review', reviews_text)
                if reviews_match:
                    data['Reviews'] = reviews_match[0].replace(',', '')
            except:
                pass
            
            # Category
            try:
                category = self.driver.find_element(By.CSS_SELECTOR, "button.DkEaL").text
                data['Category'] = category
            except:
                pass
            
            # Plus Code
            try:
                plus_code = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='oloc']").text
                data['Plus Code'] = plus_code
            except:
                pass
                
        except Exception as e:
            print(f"    Error extracting info: {str(e)}")
            
        return data if data['Name'] else None
    
    def close(self):
        if self.driver:
            self.driver.quit()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    location = request.form.get('location')
    keyword = request.form.get('keyword')
    max_results = int(request.form.get('max_results', 10))

    scraper = GoogleMapsScraper(headless=True)  # Runs Chrome in background (invisible)

    try:
        results = scraper.scrape_businesses(location, keyword, max_results)

        if not results:
            return """
            <html>
            <head>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                        padding: 40px;
                        text-align: center;
                        background: #f8fafc;
                    }
                    .error-container {
                        max-width: 600px;
                        margin: 0 auto;
                        background: white;
                        padding: 2rem;
                        border-radius: 16px;
                        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                    }
                    h2 { color: #1e293b; margin-bottom: 1rem; }
                    ul { text-align: left; color: #64748b; line-height: 1.8; }
                    a {
                        color: #3b82f6;
                        text-decoration: none;
                        font-weight: 600;
                        display: inline-block;
                        margin-top: 1rem;
                    }
                    a:hover { color: #2563eb; }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h2>No results found</h2>
                    <p>Try these suggestions:</p>
                    <ul>
                        <li>Use more specific keywords (e.g., "fine dining restaurants" instead of just "restaurants")</li>
                        <li>Include the country in location (e.g., "New York, USA")</li>
                        <li>Check if Chrome is opening and loading Google Maps</li>
                        <li>Try with headless=False to see what's happening</li>
                        <li>Consider using Google Places API instead</li>
                    </ul>
                    <a href="/">← Go Back</a>
                </div>
            </body>
            </html>
            """, 404

        # Create DataFrame and Excel file
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())
        filename = f"scraped_{keyword.replace(' ', '_')}_{location.replace(' ', '_')}_{timestamp}.xlsx"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")

        # Create Excel with formatting
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
            worksheet = writer.sheets['Results']

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

        # Get file size
        file_size_bytes = os.path.getsize(filepath)
        if file_size_bytes < 1024:
            file_size = f"{file_size_bytes} bytes"
        elif file_size_bytes < 1024 * 1024:
            file_size = f"{file_size_bytes / 1024:.2f} KB"
        else:
            file_size = f"{file_size_bytes / (1024 * 1024):.2f} MB"

        # Render results page
        return render_template_string(
            RESULTS_TEMPLATE,
            results_count=len(results),
            file_size=file_size,
            filename=filename,
            file_id=file_id
        )

    except Exception as e:
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    padding: 40px;
                    background: #f8fafc;
                }}
                .error-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 2rem;
                    border-radius: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                }}
                h2 {{ color: #ef4444; margin-bottom: 1rem; }}
                pre {{
                    background: #f8fafc;
                    padding: 20px;
                    border-radius: 8px;
                    border: 2px solid #e2e8f0;
                    overflow-x: auto;
                    font-size: 0.875rem;
                }}
                a {{
                    color: #3b82f6;
                    text-decoration: none;
                    font-weight: 600;
                    display: inline-block;
                    margin-top: 1rem;
                }}
                a:hover {{ color: #2563eb; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2>An error occurred</h2>
                <pre>{str(e)}</pre>
                <a href="/">← Go Back</a>
            </div>
        </body>
        </html>
        """, 500

    finally:
        scraper.close()

@app.route('/download/<file_id>')
def download(file_id):
    try:
        # Find file with matching file_id
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(file_id):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # Remove the UUID prefix from the download name
                download_name = '_'.join(filename.split('_')[1:])
                return send_file(
                    filepath,
                    as_attachment=True,
                    download_name=download_name,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

        return """
        <html>
        <head>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    padding: 40px;
                    text-align: center;
                    background: #f8fafc;
                }
                .error-container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 2rem;
                    border-radius: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                }
                h2 { color: #ef4444; }
                a {
                    color: #3b82f6;
                    text-decoration: none;
                    font-weight: 600;
                    display: inline-block;
                    margin-top: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2>File not found</h2>
                <p>The file you requested does not exist or has been deleted.</p>
                <a href="/">← Go Back</a>
            </div>
        </body>
        </html>
        """, 404
    except Exception as e:
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                    padding: 40px;
                    background: #f8fafc;
                }}
                .error-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 2rem;
                    border-radius: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
                }}
                h2 {{ color: #ef4444; }}
                a {{
                    color: #3b82f6;
                    text-decoration: none;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h2>Download Error</h2>
                <p>{str(e)}</p>
                <a href="/">← Go Back</a>
            </div>
        </body>
        </html>
        """, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'

    if debug:
        print(f"Starting Flask app on http://localhost:{port}")
        print("Press Ctrl+C to stop")

    app.run(debug=debug, host='0.0.0.0', port=port)
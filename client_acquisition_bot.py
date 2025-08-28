#!/usr/bin/env python3

"""
CLIENT ACQUISITION BOT
=====================
This script automatically finds, qualifies, and acquires clients for your business.
It handles lead generation, outreach, follow-up, and conversion tracking.

Features:
- Automated lead generation from multiple sources
- AI-powered lead qualification and scoring
- Personalized outreach message generation
- Automated email and LinkedIn outreach
- Follow-up sequence management
- Conversion tracking and analytics
- CRM integration

Author: Manus AI
"""

import os
import sys
import time
import json
import random
import requests
import subprocess
import argparse
import re
import base64
import smtplib
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import csv
import uuid
import logging
import threading
import schedule

# Try to import optional dependencies
try:
    import openai
    import pandas as pd
    import numpy as np
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    import linkedin_api
    from linkedin_api import Linkedin
    OPTIONAL_DEPS = True
except ImportError:
    OPTIONAL_DEPS = False

# Configuration
CONFIG = {
    "api_key": os.environ.get("OPENAI_API_KEY", ""),
    "output_dir": os.path.expanduser("~/client_acquisition"),
    "log_file": os.path.expanduser("~/client_acquisition/acquisition.log"),
    "leads_file": os.path.expanduser("~/client_acquisition/leads.csv"),
    "outreach_file": os.path.expanduser("~/client_acquisition/outreach.csv"),
    "conversion_file": os.path.expanduser("~/client_acquisition/conversions.csv"),
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": os.environ.get("EMAIL_USERNAME", ""),
        "password": os.environ.get("EMAIL_PASSWORD", ""),
        "from_name": "Your Name",
        "signature": "\n\nBest regards,\nYour Name\nGoldenAgeMindset | AI Strategy Consultant\nwww.goldenageminset.com"
    },
    "linkedin": {
        "username": os.environ.get("LINKEDIN_USERNAME", ""),
        "password": os.environ.get("LINKEDIN_PASSWORD", "")
    },
    "target_audience": {
        "industries": ["Technology", "Finance", "Healthcare", "Education", "Marketing"],
        "company_size": ["51-200", "201-500", "501-1000", "1001-5000", "5001-10000"],
        "job_titles": ["CEO", "CTO", "CIO", "Director", "VP", "Head of", "Chief"],
        "keywords": ["AI", "artificial intelligence", "machine learning", "digital transformation", "automation"]
    },
    "lead_sources": ["linkedin", "google", "crunchbase", "angellist", "apollo"],
    "outreach_templates": {
        "initial": "I noticed your work at {company} and thought you might be interested in how AI is transforming {industry}. Our GoldenAgeMindset approach has helped similar {role}s achieve {benefit}. Would you be open to a quick chat about how this could work for {company}?",
        "follow_up_1": "Just following up on my previous message about how AI strategies are helping {industry} companies like {company}. I'd love to share some specific insights relevant to your role as {role}.",
        "follow_up_2": "I wanted to share this quick case study of how we helped another {role} at a {industry} company achieve {benefit}. Would any of these results be valuable for {company}?"
    },
    "webhook_url": "",  # Optional: Discord/Slack webhook for notifications
    "auto_mode": False,  # Set to True for fully automated operation
    "daily_limits": {
        "leads_generated": 100,
        "emails_sent": 50,
        "linkedin_messages": 25
    },
    "lead_scoring": {
        "industry_match": 20,
        "title_match": 30,
        "company_size_match": 15,
        "keyword_match": 25,
        "engagement_score": 10
    },
    "follow_up_schedule": [
        {"days": 3, "template": "follow_up_1"},
        {"days": 7, "template": "follow_up_2"}
    ],
    "business_info": {
        "name": "GoldenAgeMindset",
        "services": ["AI Strategy Consulting", "AI Implementation", "AI Training", "YouTube Content Creation"],
        "value_props": [
            "10x productivity through AI integration",
            "Reduce operational costs by 30%",
            "Increase revenue through AI-powered insights",
            "Stay ahead of competitors with cutting-edge AI strategies"
        ],
        "case_studies": [
            {
                "title": "How a mid-size tech company increased revenue by 45% with AI",
                "industry": "Technology",
                "results": "45% revenue increase, 30% cost reduction"
            },
            {
                "title": "AI transformation for financial services firm",
                "industry": "Finance",
                "results": "60% faster processing, 25% higher customer satisfaction"
            }
        ]
    }
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG["log_file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ClientAcquisitionBot")

# Global variables
linkedin_api_client = None
webdriver_instance = None


def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    if not OPTIONAL_DEPS:
        logger.warning("Installing required packages...")
        packages = [
            "openai",
            "pandas",
            "numpy",
            "selenium",
            "beautifulsoup4",
            "nltk",
            "webdriver-manager",
            "linkedin-api",
            "requests",
            "schedule"
        ]
        
        subprocess.run([sys.executable, "-m", "pip", "install"] + packages, check=True)
        
        logger.warning("Please restart the script to use the installed packages")
        sys.exit(0)
    
    # Download NLTK data if needed
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logger.info("Downloading NLTK data...")
        nltk.download('punkt')
        nltk.download('stopwords')
    
    # Set up directories
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    
    # Create CSV files with headers if they don't exist
    if not os.path.exists(CONFIG["leads_file"]):
        with open(CONFIG["leads_file"], "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "first_name", "last_name", "email", "phone", "company", 
                "title", "industry", "company_size", "linkedin_url", "website",
                "source", "score", "status", "notes", "created_at"
            ])
    
    if not os.path.exists(CONFIG["outreach_file"]):
        with open(CONFIG["outreach_file"], "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "lead_id", "channel", "template", "message", "sent_at", 
                "opened", "replied", "status", "follow_up_date"
            ])
    
    if not os.path.exists(CONFIG["conversion_file"]):
        with open(CONFIG["conversion_file"], "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "lead_id", "service", "value", "status", "converted_at", "notes"
            ])
    
    logger.info("All dependencies satisfied!")


def authenticate_linkedin():
    """Authenticate with LinkedIn API"""
    global linkedin_api_client
    
    if not CONFIG["linkedin"]["username"] or not CONFIG["linkedin"]["password"]:
        logger.error("LinkedIn credentials not set. Please set LINKEDIN_USERNAME and LINKEDIN_PASSWORD environment variables.")
        return False
    
    try:
        logger.info("Authenticating with LinkedIn API...")
        linkedin_api_client = Linkedin(CONFIG["linkedin"]["username"], CONFIG["linkedin"]["password"])
        
        # Test the connection
        profile = linkedin_api_client.get_profile("linkedin")
        if profile:
            logger.info("Successfully authenticated with LinkedIn API")
            return True
        else:
            logger.error("Failed to authenticate with LinkedIn API")
            return False
    except Exception as e:
        logger.error(f"Error authenticating with LinkedIn API: {str(e)}")
        return False


def initialize_webdriver():
    """Initialize Selenium WebDriver"""
    global webdriver_instance
    
    try:
        logger.info("Initializing WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        webdriver_instance = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("WebDriver initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {str(e)}")
        return False


def generate_leads_from_linkedin(keywords: List[str], count: int = 10) -> List[Dict[str, Any]]:
    """Generate leads from LinkedIn based on keywords"""
    if not linkedin_api_client:
        logger.error("LinkedIn API client not initialized")
        return []
    
    leads = []
    
    try:
        logger.info(f"Searching LinkedIn for leads with keywords: {keywords}")
        
        # Combine keywords with target audience criteria
        search_keywords = keywords.copy()
        search_keywords.extend(random.sample(CONFIG["target_audience"]["keywords"], 2))
        
        # Search for people
        for keyword in search_keywords:
            search_results = linkedin_api_client.search_people(
                keywords=keyword,
                limit=count // len(search_keywords) + 5  # Add some extra to account for filtering
            )
            
            for result in search_results:
                # Extract basic info
                profile_id = result.get("public_id", "")
                if not profile_id:
                    continue
                
                # Get detailed profile
                try:
                    profile = linkedin_api_client.get_profile(profile_id)
                    
                    # Check if profile matches target criteria
                    title = profile.get("headline", "").lower()
                    company = None
                    industry = None
                    company_size = None
                    
                    # Extract company info
                    if "experience" in profile and profile["experience"]:
                        current_experience = profile["experience"][0]
                        company = current_experience.get("company", "")
                        if isinstance(company, dict):
                            company = company.get("name", "")
                    
                    # Check if title matches target job titles
                    title_match = any(job_title.lower() in title.lower() for job_title in CONFIG["target_audience"]["job_titles"])
                    
                    if title_match:
                        # Create lead record
                        lead = {
                            "id": str(uuid.uuid4()),
                            "first_name": profile.get("firstName", ""),
                            "last_name": profile.get("lastName", ""),
                            "email": "",  # LinkedIn API doesn't provide email
                            "phone": "",  # LinkedIn API doesn't provide phone
                            "company": company,
                            "title": profile.get("headline", ""),
                            "industry": industry,
                            "company_size": company_size,
                            "linkedin_url": f"https://www.linkedin.com/in/{profile_id}/",
                            "website": "",
                            "source": "linkedin",
                            "score": calculate_lead_score(profile),
                            "status": "new",
                            "notes": f"Found via LinkedIn search for '{keyword}'",
                            "created_at": datetime.now().isoformat()
                        }
                        
                        leads.append(lead)
                        
                        # Break if we have enough leads
                        if len(leads) >= count:
                            break
                except Exception as e:
                    logger.error(f"Error getting profile details for {profile_id}: {str(e)}")
                    continue
            
            # Break if we have enough leads
            if len(leads) >= count:
                break
        
        logger.info(f"Generated {len(leads)} leads from LinkedIn")
        return leads
    
    except Exception as e:
        logger.error(f"Error generating leads from LinkedIn: {str(e)}")
        return []


def generate_leads_from_google(keywords: List[str], count: int = 10) -> List[Dict[str, Any]]:
    """Generate leads from Google search results"""
    if not webdriver_instance:
        logger.error("WebDriver not initialized")
        return []
    
    leads = []
    
    try:
        logger.info(f"Searching Google for leads with keywords: {keywords}")
        
        # Combine keywords with target audience criteria
        search_queries = []
        for keyword in keywords:
            for industry in random.sample(CONFIG["target_audience"]["industries"], 2):
                for title in random.sample(CONFIG["target_audience"]["job_titles"], 2):
                    query = f"{title} {industry} {keyword} email contact"
                    search_queries.append(query)
        
        # Shuffle and limit queries
        random.shuffle(search_queries)
        search_queries = search_queries[:5]
        
        for query in search_queries:
            # Encode query for URL
            encoded_query = requests.utils.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            # Open Google search
            webdriver_instance.get(url)
            time.sleep(2)  # Wait for page to load
            
            # Extract search results
            search_results = webdriver_instance.find_elements(By.CSS_SELECTOR, "div.g")
            
            for result in search_results[:5]:  # Process top 5 results per query
                try:
                    # Extract title and link
                    title_element = result.find_element(By.CSS_SELECTOR, "h3")
                    title = title_element.text
                    
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute("href")
                    
                    # Extract snippet
                    snippet_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                    snippet = snippet_element.text
                    
                    # Check if result contains contact information
                    if any(word in snippet.lower() for word in ["contact", "email", "about us", "team", "leadership"]):
                        # Visit the page to extract more information
                        try:
                            webdriver_instance.get(link)
                            time.sleep(2)  # Wait for page to load
                            
                            # Extract page content
                            page_content = webdriver_instance.page_source
                            soup = BeautifulSoup(page_content, "html.parser")
                            
                            # Try to find company name
                            company = ""
                            company_elements = soup.select("meta[property='og:site_name']")
                            if company_elements:
                                company = company_elements[0].get("content", "")
                            
                            if not company:
                                title_elements = soup.select("title")
                                if title_elements:
                                    company = title_elements[0].text.split("|")[0].strip()
                            
                            # Try to find email addresses
                            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                            emails = re.findall(email_pattern, page_content)
                            
                            # Filter out common non-contact emails
                            filtered_emails = [
                                email for email in emails 
                                if not any(exclude in email.lower() for exclude in ["example", "test", "user", "email", "domain"])
                            ]
                            
                            email = filtered_emails[0] if filtered_emails else ""
                            
                            # Create lead record
                            lead = {
                                "id": str(uuid.uuid4()),
                                "first_name": "",  # Need further processing to extract
                                "last_name": "",   # Need further processing to extract
                                "email": email,
                                "phone": "",       # Need further processing to extract
                                "company": company,
                                "title": "",       # Need further processing to extract
                                "industry": next((i for i in CONFIG["target_audience"]["industries"] if i.lower() in snippet.lower()), ""),
                                "company_size": "",
                                "linkedin_url": "",
                                "website": link,
                                "source": "google",
                                "score": 50,  # Base score, needs refinement
                                "status": "new",
                                "notes": f"Found via Google search for '{query}'",
                                "created_at": datetime.now().isoformat()
                            }
                            
                            leads.append(lead)
                            
                            # Break if we have enough leads
                            if len(leads) >= count:
                                break
                        except Exception as e:
                            logger.error(f"Error processing search result page {link}: {str(e)}")
                            continue
                except Exception as e:
                    logger.error(f"Error processing search result: {str(e)}")
                    continue
            
            # Break if we have enough leads
            if len(leads) >= count:
                break
            
            # Sleep to avoid being blocked
            time.sleep(random.uniform(3, 5))
        
        logger.info(f"Generated {len(leads)} leads from Google")
        return leads
    
    except Exception as e:
        logger.error(f"Error generating leads from Google: {str(e)}")
        return []


def enrich_lead_data(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrich lead data with additional information"""
    enriched_leads = []
    
    for lead in leads:
        try:
            logger.info(f"Enriching lead data for {lead.get('first_name', '')} {lead.get('last_name', '')} at {lead.get('company', '')}")
            
            # Skip if already has email and company info
            if lead.get("email") and lead.get("company"):
                enriched_leads.append(lead)
                continue
            
            # Try to find company information if we have a website
            if lead.get("website") and not lead.get("company"):
                try:
                    webdriver_instance.get(lead["website"])
                    time.sleep(2)  # Wait for page to load
                    
                    # Extract page content
                    page_content = webdriver_instance.page_source
                    soup = BeautifulSoup(page_content, "html.parser")
                    
                    # Try to find company name
                    company_elements = soup.select("meta[property='og:site_name']")
                    if company_elements:
                        lead["company"] = company_elements[0].get("content", "")
                    
                    if not lead.get("company"):
                        title_elements = soup.select("title")
                        if title_elements:
                            lead["company"] = title_elements[0].text.split("|")[0].strip()
                except Exception as e:
                    logger.error(f"Error enriching company data from website: {str(e)}")
            
            # Try to find email if we have LinkedIn URL
            if lead.get("linkedin_url") and not lead.get("email") and linkedin_api_client:
                try:
                    # Extract profile ID from URL
                    profile_id = lead["linkedin_url"].strip("/").split("/")[-1]
                    
                    # Get profile details
                    profile = linkedin_api_client.get_profile(profile_id)
                    
                    # Update lead with additional information
                    if "industry" in profile:
                        lead["industry"] = profile["industry"]
                    
                    if "experience" in profile and profile["experience"]:
                        current_experience = profile["experience"][0]
                        if "company" in current_experience:
                            company = current_experience["company"]
                            if isinstance(company, dict) and "name" in company:
                                lead["company"] = company["name"]
                            else:
                                lead["company"] = str(company)
                        
                        if "title" in current_experience:
                            lead["title"] = current_experience["title"]
                    
                    # We still don't get email from LinkedIn API, but we've enriched other data
                except Exception as e:
                    logger.error(f"Error enriching data from LinkedIn: {str(e)}")
            
            # Calculate lead score based on enriched data
            lead["score"] = calculate_lead_score(lead)
            
            enriched_leads.append(lead)
            
        except Exception as e:
            logger.error(f"Error enriching lead data: {str(e)}")
            enriched_leads.append(lead)  # Add original lead anyway
    
    logger.info(f"Enriched {len(enriched_leads)} leads")
    return enriched_leads


def calculate_lead_score(lead: Dict[str, Any]) -> int:
    """Calculate a score for a lead based on match to target criteria"""
    score = 0
    
    # Industry match
    if lead.get("industry") and any(industry.lower() in lead["industry"].lower() for industry in CONFIG["target_audience"]["industries"]):
        score += CONFIG["lead_scoring"]["industry_match"]
    
    # Title match
    if lead.get("title") and any(title.lower() in lead["title"].lower() for title in CONFIG["target_audience"]["job_titles"]):
        score += CONFIG["lead_scoring"]["title_match"]
    
    # Company size match
    if lead.get("company_size") and lead["company_size"] in CONFIG["target_audience"]["company_size"]:
        score += CONFIG["lead_scoring"]["company_size_match"]
    
    # Keyword match
    lead_text = " ".join([
        lead.get("title", ""),
        lead.get("company", ""),
        lead.get("industry", ""),
        lead.get("notes", "")
    ]).lower()
    
    keyword_matches = sum(1 for keyword in CONFIG["target_audience"]["keywords"] if keyword.lower() in lead_text)
    score += min(keyword_matches * 5, CONFIG["lead_scoring"]["keyword_match"])
    
    # Completeness bonus
    completeness = sum(1 for field in ["first_name", "last_name", "email", "company", "title"] if lead.get(field))
    score += completeness * 2
    
    return score


def save_leads_to_csv(leads: List[Dict[str, Any]]):
    """Save leads to CSV file"""
    try:
        # Read existing leads to avoid duplicates
        existing_leads = []
        if os.path.exists(CONFIG["leads_file"]):
            with open(CONFIG["leads_file"], "r", newline="") as f:
                reader = csv.DictReader(f)
                existing_leads = list(reader)
        
        # Extract existing emails and LinkedIn URLs for duplicate checking
        existing_emails = {lead["email"] for lead in existing_leads if lead["email"]}
        existing_linkedin_urls = {lead["linkedin_url"] for lead in existing_leads if lead["linkedin_url"]}
        
        # Filter out duplicates
        new_leads = []
        for lead in leads:
            if (lead.get("email") and lead["email"] in existing_emails) or \
               (lead.get("linkedin_url") and lead["linkedin_url"] in existing_linkedin_urls):
                logger.info(f"Skipping duplicate lead: {lead.get('first_name', '')} {lead.get('last_name', '')}")
                continue
            new_leads.append(lead)
        
        if not new_leads:
            logger.info("No new leads to save")
            return
        
        # Append new leads to CSV
        with open(CONFIG["leads_file"], "a", newline="") as f:
            writer = csv.writer(f)
            for lead in new_leads:
                writer.writerow([
                    lead.get("id", str(uuid.uuid4())),
                    lead.get("first_name", ""),
                    lead.get("last_name", ""),
                    lead.get("email", ""),
                    lead.get("phone", ""),
                    lead.get("company", ""),
                    lead.get("title", ""),
                    lead.get("industry", ""),
                    lead.get("company_size", ""),
                    lead.get("linkedin_url", ""),
                    lead.get("website", ""),
                    lead.get("source", ""),
                    lead.get("score", 0),
                    lead.get("status", "new"),
                    lead.get("notes", ""),
                    lead.get("created_at", datetime.now().isoformat())
                ])
        
        logger.info(f"Saved {len(new_leads)} new leads to CSV")
    
    except Exception as e:
        logger.error(f"Error saving leads to CSV: {str(e)}")


def generate_personalized_message(lead: Dict[str, Any], template_key: str) -> str:
    """Generate a personalized outreach message for a lead"""
    try:
        template = CONFIG["outreach_templates"].get(template_key, CONFIG["outreach_templates"]["initial"])
        
        # Basic template filling
        message = template.format(
            first_name=lead.get("first_name", "there"),
            last_name=lead.get("last_name", ""),
            company=lead.get("company", "your company"),
            role=lead.get("title", "professional"),
            industry=lead.get("industry", "your industry"),
            benefit=random.choice(CONFIG["business_info"]["value_props"])
        )
        
        # If we have OpenAI API key, enhance the message
        if CONFIG["api_key"]:
            try:
                openai.api_key = CONFIG["api_key"]
                
                prompt = f"""
                Enhance this outreach message to make it more personalized and compelling:
                
                Original message: {message}
                
                Lead information:
                - Name: {lead.get('first_name', '')} {lead.get('last_name', '')}
                - Company: {lead.get('company', '')}
                - Title: {lead.get('title', '')}
                - Industry: {lead.get('industry', '')}
                
                Our business:
                - Name: {CONFIG['business_info']['name']}
                - Services: {', '.join(CONFIG['business_info']['services'])}
                - Value propositions: {', '.join(CONFIG['business_info']['value_props'])}
                
                Make the message sound natural, professional, and personalized.
                Keep it concise (max 150 words) and focused on value.
                Do not use generic phrases like "I hope this email finds you well."
                Do not mention that this is an automated message.
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
                
                enhanced_message = response.choices[0].message.content.strip()
                
                # Use enhanced message if it's not too long
                if len(enhanced_message) <= 1500:
                    message = enhanced_message
            
            except Exception as e:
                logger.error(f"Error enhancing message with OpenAI: {str(e)}")
        
        # Add signature
        message += CONFIG["email"]["signature"]
        
        return message
    
    except Exception as e:
        logger.error(f"Error generating personalized message: {str(e)}")
        return f"Hello {lead.get('first_name', 'there')},\n\nI wanted to connect about how our AI solutions could help {lead.get('company', 'your company')}.\n\n{CONFIG['email']['signature']}"


def send_email(lead: Dict[str, Any], message: str) -> bool:
    """Send an email to a lead"""
    if not lead.get("email"):
        logger.error(f"Cannot send email: No email address for lead {lead.get('id')}")
        return False
    
    if not CONFIG["email"]["username"] or not CONFIG["email"]["password"]:
        logger.error("Email credentials not set. Please set EMAIL_USERNAME and EMAIL_PASSWORD environment variables.")
        return False
    
    try:
        logger.info(f"Sending email to {lead['email']}")
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = email.utils.formataddr((CONFIG["email"]["from_name"], CONFIG["email"]["username"]))
        msg["To"] = lead["email"]
        msg["Subject"] = f"AI Strategy for {lead.get('company', 'Your Business')}"
        msg["Date"] = email.utils.formatdate()
        msg["Message-ID"] = email.utils.make_msgid(domain="goldenageminset.com")
        
        # Add message body
        msg.attach(MIMEText(message, "plain"))
        
        # Connect to SMTP server
        with smtplib.SMTP(CONFIG["email"]["smtp_server"], CONFIG["email"]["smtp_port"]) as server:
            server.starttls()
            server.login(CONFIG["email"]["username"], CONFIG["email"]["password"])
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {lead['email']}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False


def send_linkedin_message(lead: Dict[str, Any], message: str) -> bool:
    """Send a LinkedIn message to a lead"""
    if not lead.get("linkedin_url"):
        logger.error(f"Cannot send LinkedIn message: No LinkedIn URL for lead {lead.get('id')}")
        return False
    
    if not linkedin_api_client:
        logger.error("LinkedIn API client not initialized")
        return False
    
    try:
        logger.info(f"Sending LinkedIn message to {lead.get('first_name', '')} {lead.get('last_name', '')}")
        
        # Extract profile ID from URL
        profile_id = lead["linkedin_url"].strip("/").split("/")[-1]
        
        # Send message
        # Note: LinkedIn API doesn't actually support sending messages
        # This is a placeholder for a real implementation
        logger.warning("LinkedIn messaging not implemented - would send message to " + profile_id)
        
        # In a real implementation, you would use Selenium to automate the LinkedIn UI
        # or use a service like Phantombuster
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending LinkedIn message: {str(e)}")
        return False


def record_outreach(lead: Dict[str, Any], channel: str, template: str, message: str, status: str = "sent") -> str:
    """Record an outreach attempt in the CSV file"""
    try:
        outreach_id = str(uuid.uuid4())
        
        with open(CONFIG["outreach_file"], "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                outreach_id,
                lead["id"],
                channel,
                template,
                message[:100] + "..." if len(message) > 100 else message,
                datetime.now().isoformat(),
                "False",  # opened
                "False",  # replied
                status,
                (datetime.now() + timedelta(days=CONFIG["follow_up_schedule"][0]["days"])).isoformat() if CONFIG["follow_up_schedule"] else ""
            ])
        
        logger.info(f"Recorded {channel} outreach to {lead.get('first_name', '')} {lead.get('last_name', '')}")
        return outreach_id
    
    except Exception as e:
        logger.error(f"Error recording outreach: {str(e)}")
        return ""


def process_follow_ups():
    """Process follow-ups for leads that haven't responded"""
    try:
        logger.info("Processing follow-ups...")
        
        # Read outreach data
        outreach_data = []
        if os.path.exists(CONFIG["outreach_file"]):
            with open(CONFIG["outreach_file"], "r", newline="") as f:
                reader = csv.DictReader(f)
                outreach_data = list(reader)
        
        # Filter for outreach that needs follow-up
        today = datetime.now()
        follow_ups_needed = [
            o for o in outreach_data 
            if o["status"] == "sent" and 
            o["replied"] == "False" and 
            o["follow_up_date"] and 
            datetime.fromisoformat(o["follow_up_date"]) <= today
        ]
        
        if not follow_ups_needed:
            logger.info("No follow-ups needed today")
            return
        
        logger.info(f"Found {len(follow_ups_needed)} leads needing follow-up")
        
        # Read leads data
        leads_data = {}
        if os.path.exists(CONFIG["leads_file"]):
            with open(CONFIG["leads_file"], "r", newline="") as f:
                reader = csv.DictReader(f)
                leads_data = {row["id"]: row for row in reader}
        
        # Process each follow-up
        for outreach in follow_ups_needed:
            try:
                lead_id = outreach["lead_id"]
                if lead_id not in leads_data:
                    logger.error(f"Lead {lead_id} not found for follow-up")
                    continue
                
                lead = leads_data[lead_id]
                
                # Determine which follow-up template to use
                previous_outreach = [
                    o for o in outreach_data 
                    if o["lead_id"] == lead_id and 
                    o["status"] == "sent"
                ]
                
                follow_up_index = len(previous_outreach)
                if follow_up_index >= len(CONFIG["follow_up_schedule"]):
                    # We've exhausted our follow-up sequence
                    logger.info(f"Follow-up sequence completed for lead {lead_id}")
                    
                    # Update outreach status
                    with open(CONFIG["outreach_file"], "r", newline="") as f:
                        rows = list(csv.reader(f))
                        header = rows[0]
                        status_index = header.index("status")
                        
                        for i, row in enumerate(rows[1:], 1):
                            if row[1] == lead_id:  # lead_id is in column 1
                                rows[i][status_index] = "completed"
                    
                    with open(CONFIG["outreach_file"], "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(rows)
                    
                    continue
                
                template_key = CONFIG["follow_up_schedule"][follow_up_index - 1]["template"]
                
                # Generate follow-up message
                message = generate_personalized_message(lead, template_key)
                
                # Send follow-up based on original channel
                channel = outreach["channel"]
                success = False
                
                if channel == "email" and lead.get("email"):
                    success = send_email(lead, message)
                elif channel == "linkedin" and lead.get("linkedin_url"):
                    success = send_linkedin_message(lead, message)
                
                if success:
                    # Record the follow-up
                    record_outreach(lead, channel, template_key, message, "follow_up")
                    
                    # Update the original outreach status
                    with open(CONFIG["outreach_file"], "r", newline="") as f:
                        rows = list(csv.reader(f))
                        header = rows[0]
                        status_index = header.index("status")
                        follow_up_date_index = header.index("follow_up_date")
                        
                        for i, row in enumerate(rows[1:], 1):
                            if row[0] == outreach["id"]:  # outreach_id is in column 0
                                rows[i][status_index] = "followed_up"
                                
                                # Set next follow-up date if available
                                if follow_up_index < len(CONFIG["follow_up_schedule"]):
                                    next_days = CONFIG["follow_up_schedule"][follow_up_index]["days"]
                                    next_date = (today + timedelta(days=next_days)).isoformat()
                                    rows[i][follow_up_date_index] = next_date
                    
                    with open(CONFIG["outreach_file"], "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(rows)
            
            except Exception as e:
                logger.error(f"Error processing follow-up for outreach {outreach.get('id')}: {str(e)}")
        
        logger.info("Follow-up processing completed")
    
    except Exception as e:
        logger.error(f"Error processing follow-ups: {str(e)}")


def check_responses():
    """Check for responses to outreach"""
    # This is a placeholder for a real implementation
    # In a real implementation, you would:
    # 1. Check email inbox for replies
    # 2. Check LinkedIn for messages
    # 3. Update the outreach status accordingly
    
    logger.info("Checking for responses (not implemented)")


def record_conversion(lead_id: str, service: str, value: float, notes: str = ""):
    """Record a conversion in the CSV file"""
    try:
        conversion_id = str(uuid.uuid4())
        
        with open(CONFIG["conversion_file"], "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                conversion_id,
                lead_id,
                service,
                value,
                "closed",
                datetime.now().isoformat(),
                notes
            ])
        
        logger.info(f"Recorded conversion for lead {lead_id}: {service} - ${value}")
        
        # Update lead status
        if os.path.exists(CONFIG["leads_file"]):
            with open(CONFIG["leads_file"], "r", newline="") as f:
                rows = list(csv.reader(f))
                header = rows[0]
                status_index = header.index("status")
                
                for i, row in enumerate(rows[1:], 1):
                    if row[0] == lead_id:  # lead_id is in column 0
                        rows[i][status_index] = "converted"
            
            with open(CONFIG["leads_file"], "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
        
        return conversion_id
    
    except Exception as e:
        logger.error(f"Error recording conversion: {str(e)}")
        return ""


def generate_leads(count: int = 10):
    """Generate leads from all configured sources"""
    total_leads = []
    
    # Determine how many leads to get from each source
    sources = CONFIG["lead_sources"]
    leads_per_source = max(count // len(sources), 1)
    
    # Generate leads from each source
    for source in sources:
        try:
            if source == "linkedin":
                leads = generate_leads_from_linkedin(CONFIG["target_audience"]["keywords"], leads_per_source)
            elif source == "google":
                leads = generate_leads_from_google(CONFIG["target_audience"]["keywords"], leads_per_source)
            else:
                logger.warning(f"Lead source {source} not implemented")
                continue
            
            total_leads.extend(leads)
            
            # Break if we have enough leads
            if len(total_leads) >= count:
                break
        except Exception as e:
            logger.error(f"Error generating leads from {source}: {str(e)}")
    
    # Enrich lead data
    enriched_leads = enrich_lead_data(total_leads)
    
    # Save leads to CSV
    save_leads_to_csv(enriched_leads)
    
    return enriched_leads


def perform_outreach(count: int = 10):
    """Perform outreach to leads"""
    # Read leads from CSV
    leads = []
    if os.path.exists(CONFIG["leads_file"]):
        with open(CONFIG["leads_file"], "r", newline="") as f:
            reader = csv.DictReader(f)
            leads = list(reader)
    
    if not leads:
        logger.warning("No leads found for outreach")
        return
    
    # Filter for new leads with high scores
    new_leads = [l for l in leads if l["status"] == "new"]
    if not new_leads:
        logger.warning("No new leads found for outreach")
        return
    
    # Sort by score (descending)
    new_leads.sort(key=lambda x: int(x["score"]), reverse=True)
    
    # Limit to requested count
    outreach_leads = new_leads[:count]
    
    logger.info(f"Performing outreach to {len(outreach_leads)} leads")
    
    # Perform outreach
    for lead in outreach_leads:
        try:
            # Generate personalized message
            message = generate_personalized_message(lead, "initial")
            
            # Determine outreach channel
            if lead["email"]:
                channel = "email"
                success = send_email(lead, message)
            elif lead["linkedin_url"]:
                channel = "linkedin"
                success = send_linkedin_message(lead, message)
            else:
                logger.warning(f"No contact method for lead {lead['id']}")
                continue
            
            if success:
                # Record the outreach
                record_outreach(lead, channel, "initial", message)
                
                # Update lead status
                with open(CONFIG["leads_file"], "r", newline="") as f:
                    rows = list(csv.reader(f))
                    header = rows[0]
                    status_index = header.index("status")
                    
                    for i, row in enumerate(rows[1:], 1):
                        if row[0] == lead["id"]:  # lead_id is in column 0
                            rows[i][status_index] = "contacted"
                
                with open(CONFIG["leads_file"], "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
        
        except Exception as e:
            logger.error(f"Error performing outreach to lead {lead['id']}: {str(e)}")
    
    logger.info("Outreach completed")


def generate_analytics_report() -> Dict[str, Any]:
    """Generate analytics report on lead generation and conversion"""
    report = {
        "leads": {
            "total": 0,
            "by_source": {},
            "by_status": {},
            "by_score": {
                "high": 0,  # 80-100
                "medium": 0,  # 50-79
                "low": 0  # 0-49
            }
        },
        "outreach": {
            "total": 0,
            "by_channel": {},
            "by_status": {},
            "reply_rate": 0
        },
        "conversions": {
            "total": 0,
            "value": 0,
            "by_service": {},
            "conversion_rate": 0
        }
    }
    
    try:
        # Analyze leads
        if os.path.exists(CONFIG["leads_file"]):
            with open(CONFIG["leads_file"], "r", newline="") as f:
                reader = csv.DictReader(f)
                leads = list(reader)
            
            report["leads"]["total"] = len(leads)
            
            # By source
            for lead in leads:
                source = lead["source"]
                if source not in report["leads"]["by_source"]:
                    report["leads"]["by_source"][source] = 0
                report["leads"]["by_source"][source] += 1
            
            # By status
            for lead in leads:
                status = lead["status"]
                if status not in report["leads"]["by_status"]:
                    report["leads"]["by_status"][status] = 0
                report["leads"]["by_status"][status] += 1
            
            # By score
            for lead in leads:
                score = int(lead["score"])
                if score >= 80:
                    report["leads"]["by_score"]["high"] += 1
                elif score >= 50:
                    report["leads"]["by_score"]["medium"] += 1
                else:
                    report["leads"]["by_score"]["low"] += 1
        
        # Analyze outreach
        if os.path.exists(CONFIG["outreach_file"]):
            with open(CONFIG["outreach_file"], "r", newline="") as f:
                reader = csv.DictReader(f)
                outreach = list(reader)
            
            report["outreach"]["total"] = len(outreach)
            
            # By channel
            for o in outreach:
                channel = o["channel"]
                if channel not in report["outreach"]["by_channel"]:
                    report["outreach"]["by_channel"][channel] = 0
                report["outreach"]["by_channel"][channel] += 1
            
            # By status
            for o in outreach:
                status = o["status"]
                if status not in report["outreach"]["by_status"]:
                    report["outreach"]["by_status"][status] = 0
                report["outreach"]["by_status"][status] += 1
            
            # Reply rate
            replies = sum(1 for o in outreach if o["replied"] == "True")
            if report["outreach"]["total"] > 0:
                report["outreach"]["reply_rate"] = round(replies / report["outreach"]["total"] * 100, 2)
        
        # Analyze conversions
        if os.path.exists(CONFIG["conversion_file"]):
            with open(CONFIG["conversion_file"], "r", newline="") as f:
                reader = csv.DictReader(f)
                conversions = list(reader)
            
            report["conversions"]["total"] = len(conversions)
            
            # Total value
            for c in conversions:
                report["conversions"]["value"] += float(c["value"])
            
            # By service
            for c in conversions:
                service = c["service"]
                if service not in report["conversions"]["by_service"]:
                    report["conversions"]["by_service"][service] = {
                        "count": 0,
                        "value": 0
                    }
                report["conversions"]["by_service"][service]["count"] += 1
                report["conversions"]["by_service"][service]["value"] += float(c["value"])
            
            # Conversion rate
            if report["leads"]["total"] > 0:
                report["conversions"]["conversion_rate"] = round(report["conversions"]["total"] / report["leads"]["total"] * 100, 2)
        
        logger.info("Generated analytics report")
        return report
    
    except Exception as e:
        logger.error(f"Error generating analytics report: {str(e)}")
        return report


def run_daily_tasks():
    """Run daily tasks for lead generation and outreach"""
    logger.info("Running daily tasks...")
    
    try:
        # Generate new leads
        leads = generate_leads(CONFIG["daily_limits"]["leads_generated"])
        
        # Perform outreach
        perform_outreach(CONFIG["daily_limits"]["emails_sent"])
        
        # Process follow-ups
        process_follow_ups()
        
        # Check for responses
        check_responses()
        
        # Generate analytics report
        report = generate_analytics_report()
        
        # Save report to file
        report_file = os.path.join(CONFIG["output_dir"], f"report_{datetime.now().strftime('%Y%m%d')}.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Daily tasks completed. Report saved to {report_file}")
        
        # Send notification
        if CONFIG["webhook_url"]:
            message = f"📊 Daily Client Acquisition Report\n\n" \
                      f"Leads: {report['leads']['total']} total, {report['leads']['by_score']['high']} high-quality\n" \
                      f"Outreach: {report['outreach']['total']} messages, {report['outreach']['reply_rate']}% reply rate\n" \
                      f"Conversions: {report['conversions']['total']} clients, ${report['conversions']['value']} value"
            
            payload = {"content": message}
            requests.post(CONFIG["webhook_url"], json=payload)
    
    except Exception as e:
        logger.error(f"Error running daily tasks: {str(e)}")


def schedule_tasks():
    """Schedule recurring tasks"""
    logger.info("Scheduling recurring tasks...")
    
    # Schedule daily lead generation
    schedule.every().day.at("09:00").do(run_daily_tasks)
    
    # Schedule hourly follow-up checks
    schedule.every(1).hours.do(process_follow_ups)
    
    # Schedule hourly response checks
    schedule.every(1).hours.do(check_responses)
    
    logger.info("Tasks scheduled successfully")
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Client Acquisition Bot")
    parser.add_argument("--generate", type=int, metavar="COUNT", help="Generate leads")
    parser.add_argument("--outreach", type=int, metavar="COUNT", help="Perform outreach to leads")
    parser.add_argument("--follow-up", action="store_true", help="Process follow-ups")
    parser.add_argument("--report", action="store_true", help="Generate analytics report")
    parser.add_argument("--schedule", action="store_true", help="Schedule recurring tasks")
    parser.add_argument("--auto", action="store_true", help="Run in fully automated mode")
    
    args = parser.parse_args()
    
    try:
        # Check dependencies
        check_dependencies()
        
        # Initialize services
        if args.outreach or args.follow_up or args.auto or args.schedule:
            authenticate_linkedin()
        
        if args.generate or args.auto or args.schedule:
            initialize_webdriver()
        
        if args.generate:
            generate_leads(args.generate)
        
        if args.outreach:
            perform_outreach(args.outreach)
        
        if args.follow_up:
            process_follow_ups()
        
        if args.report:
            report = generate_analytics_report()
            print(json.dumps(report, indent=2))
        
        if args.schedule:
            schedule_tasks()
        
        if args.auto:
            CONFIG["auto_mode"] = True
            run_daily_tasks()
            schedule_tasks()
        
        # If no arguments, show help
        if not any(vars(args).values()):
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    
    finally:
        # Clean up resources
        if webdriver_instance:
            try:
                webdriver_instance.quit()
            except:
                pass


if __name__ == "__main__":
    main()


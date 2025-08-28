#!/usr/bin/env python3

"""
YOUTUBE CONTENT GENERATOR
=========================
This script automatically generates complete YouTube videos including:
- Topic research and selection
- Script writing
- Video generation
- Thumbnail creation
- SEO optimization
- Upload and scheduling

Features:
- Fully automated content creation
- Trend analysis and topic selection
- AI-generated scripts and visuals
- Automatic uploading and scheduling
- Performance tracking and optimization

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
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

# Try to import optional dependencies
try:
    import openai
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import moviepy.editor as mp
    from pydub import AudioSegment
    OPTIONAL_DEPS = True
except ImportError:
    OPTIONAL_DEPS = False

# Configuration
CONFIG = {
    "api_key": os.environ.get("OPENAI_API_KEY", ""),
    "youtube_client_secrets_file": "client_secrets.json",
    "youtube_credentials_file": "youtube_credentials.json",
    "output_dir": os.path.expanduser("~/youtube_content"),
    "temp_dir": os.path.expanduser("~/youtube_content/temp"),
    "log_file": os.path.expanduser("~/youtube_content/generator.log"),
    "video_resolution": "1080p",  # 720p, 1080p, 4K
    "video_length": {
        "tutorial": (10, 15),  # minutes (min, max)
        "tips": (5, 7)
    },
    "posting_schedule": {
        "tutorial": 1,  # Tuesday (0 = Monday)
        "tips": 4       # Friday
    },
    "auto_upload": True,
    "auto_schedule": True,
    "webhook_url": "",  # Optional: Discord/Slack webhook for notifications
    "target_audience": "professionals interested in AI technology",
    "brand_voice": "professional, informative, and slightly enthusiastic",
    "channel_name": "GoldenAgeMindset",
    "content_pillars": [
        {"name": "AI Tools & Applications", "weight": 0.4},
        {"name": "AI Mindset & Strategy", "weight": 0.2},
        {"name": "AI Business Opportunities", "weight": 0.3},
        {"name": "AI Ethics & Future", "weight": 0.1}
    ]
}

# Global variables
youtube = None


def log(message, level="INFO"):
    """Log message to console and file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    
    print(log_message)
    
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    with open(CONFIG["log_file"], "a") as f:
        f.write(log_message + "\n")


def check_dependencies():
    """Check if all required dependencies are installed"""
    log("Checking dependencies...")
    
    if not OPTIONAL_DEPS:
        log("Installing required packages...", "WARNING")
        packages = [
            "openai",
            "google-api-python-client",
            "google-auth-oauthlib",
            "google-auth-httplib2",
            "numpy",
            "pillow",
            "opencv-python",
            "moviepy",
            "pydub",
            "requests"
        ]
        
        subprocess.run([sys.executable, "-m", "pip", "install"] + packages, check=True)
        
        log("Please restart the script to use the installed packages", "WARNING")
        sys.exit(0)
    
    # Check for ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("ffmpeg not found. Installing...", "WARNING")
        
        # Try to install ffmpeg based on platform
        if sys.platform.startswith("linux"):
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
        else:
            log("Please install ffmpeg manually: https://ffmpeg.org/download.html", "ERROR")
            sys.exit(1)
    
    # Check OpenAI API key
    if not CONFIG["api_key"]:
        log("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.", "ERROR")
        sys.exit(1)
    
    # Set up directories
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    os.makedirs(CONFIG["temp_dir"], exist_ok=True)
    
    log("All dependencies satisfied!")


def authenticate_youtube():
    """Authenticate with YouTube API"""
    global youtube
    
    log("Authenticating with YouTube API...")
    
    # If client secrets file doesn't exist, create a template
    if not os.path.exists(CONFIG["youtube_client_secrets_file"]):
        log(f"YouTube client secrets file not found: {CONFIG['youtube_client_secrets_file']}", "WARNING")
        log("Please create a project in Google Cloud Console and download OAuth client ID credentials")
        log("1. Go to https://console.cloud.google.com/")
        log("2. Create a new project")
        log("3. Enable the YouTube Data API v3")
        log("4. Create OAuth client ID credentials")
        log("5. Download the credentials as JSON")
        log("6. Save the file as client_secrets.json in the current directory")
        
        # Create a template file
        template = {
            "installed": {
                "client_id": "YOUR_CLIENT_ID",
                "project_id": "YOUR_PROJECT_ID",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "YOUR_CLIENT_SECRET",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }
        
        with open(CONFIG["youtube_client_secrets_file"], "w") as f:
            json.dump(template, f, indent=2)
        
        log(f"Created template file: {CONFIG['youtube_client_secrets_file']}")
        log("Please update it with your actual credentials")
        return False
    
    # Set up the OAuth flow
    scopes = ["https://www.googleapis.com/auth/youtube.upload", 
              "https://www.googleapis.com/auth/youtube"]
    
    creds = None
    if os.path.exists(CONFIG["youtube_credentials_file"]):
        creds = Credentials.from_authorized_user_info(
            json.load(open(CONFIG["youtube_credentials_file"]))
        )
    
    # If credentials don't exist or are invalid, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CONFIG["youtube_client_secrets_file"], scopes
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open(CONFIG["youtube_credentials_file"], "w") as f:
            f.write(creds.to_json())
    
    # Build the YouTube API client
    youtube = build("youtube", "v3", credentials=creds)
    
    # Test the connection
    try:
        channel_response = youtube.channels().list(
            part="snippet",
            mine=True
        ).execute()
        
        channel_name = channel_response["items"][0]["snippet"]["title"]
        log(f"Successfully authenticated with YouTube as: {channel_name}")
        return True
    except Exception as e:
        log(f"Failed to authenticate with YouTube: {str(e)}", "ERROR")
        return False


def get_trending_topics() -> List[Dict[str, Any]]:
    """Get trending AI topics from various sources"""
    log("Researching trending AI topics...")
    
    topics = []
    
    # Use OpenAI to generate trending topics
    openai.api_key = CONFIG["api_key"]
    
    prompt = f"""
    Generate 10 trending AI topics for YouTube videos that would appeal to {CONFIG['target_audience']}.
    For each topic:
    1. Provide a catchy title
    2. Explain why it's trending now
    3. Suggest key points to cover
    4. Identify which content pillar it belongs to: {[p['name'] for p in CONFIG['content_pillars']]}
    5. Suggest a video type: tutorial or tips
    
    Format the response as JSON with the following structure:
    [
        {{
            "title": "Catchy Title Here",
            "trending_reason": "Why this topic is trending now",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "content_pillar": "One of the content pillars",
            "video_type": "tutorial or tips"
        }},
        ...
    ]
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract and parse the JSON response
        content = response.choices[0].message.content
        json_match = re.search(r'```json\n(.*?)```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        
        topics = json.loads(content)
        log(f"Generated {len(topics)} trending topics")
        
    except Exception as e:
        log(f"Error generating trending topics: {str(e)}", "ERROR")
        # Fallback to some default topics
        topics = [
            {
                "title": "5 AI Tools That Will 10x Your Productivity in 2025",
                "trending_reason": "Productivity tools are always in demand",
                "key_points": ["Tool 1: AI Writing Assistant", "Tool 2: Smart Calendar", "Tool 3: Voice Transcription"],
                "content_pillar": "AI Tools & Applications",
                "video_type": "tips"
            },
            {
                "title": "How to Build a Profitable AI Business in 30 Days",
                "trending_reason": "Entrepreneurship with AI is growing",
                "key_points": ["Market Research", "MVP Development", "Marketing Strategy"],
                "content_pillar": "AI Business Opportunities",
                "video_type": "tutorial"
            }
        ]
    
    return topics


def select_next_topic(topics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Select the next topic to create based on content calendar"""
    log("Selecting next topic to create...")
    
    # Determine what type of video we need based on the day of the week
    today = datetime.now().weekday()
    
    # Find the next scheduled day
    days_until_tutorial = (CONFIG["posting_schedule"]["tutorial"] - today) % 7
    days_until_tips = (CONFIG["posting_schedule"]["tips"] - today) % 7
    
    # If today is a posting day, create that type of content
    if days_until_tutorial == 0:
        video_type = "tutorial"
    elif days_until_tips == 0:
        video_type = "tips"
    # Otherwise, choose the one that's coming up sooner
    elif days_until_tutorial < days_until_tips:
        video_type = "tutorial"
    else:
        video_type = "tips"
    
    log(f"Next video type: {video_type}")
    
    # Filter topics by video type
    matching_topics = [t for t in topics if t["video_type"] == video_type]
    
    if not matching_topics:
        log(f"No {video_type} topics found, using any available topic", "WARNING")
        matching_topics = topics
    
    if not matching_topics:
        log("No topics available", "ERROR")
        return None
    
    # Apply content pillar weights to prioritize topics
    weighted_topics = []
    for topic in matching_topics:
        pillar = topic["content_pillar"]
        weight = next((p["weight"] for p in CONFIG["content_pillars"] if p["name"] == pillar), 0.1)
        weighted_topics.append((topic, weight))
    
    # Select a topic based on weights
    topics, weights = zip(*weighted_topics)
    selected_topic = random.choices(topics, weights=weights, k=1)[0]
    
    log(f"Selected topic: {selected_topic['title']}")
    return selected_topic


def generate_script(topic: Dict[str, Any]) -> str:
    """Generate a video script based on the topic"""
    log(f"Generating script for: {topic['title']}...")
    
    # Determine target length based on video type
    if topic["video_type"] == "tutorial":
        min_length, max_length = CONFIG["video_length"]["tutorial"]
    else:
        min_length, max_length = CONFIG["video_length"]["tips"]
    
    # Calculate approximate word count (150 words per minute)
    min_words = min_length * 150
    max_words = max_length * 150
    
    openai.api_key = CONFIG["api_key"]
    
    prompt = f"""
    Write a complete YouTube script for a video titled "{topic['title']}" for the {CONFIG['channel_name']} channel.
    
    Channel focus: AI topics, how AI is ushering in a new golden age of human potential
    Target audience: {CONFIG['target_audience']}
    Brand voice: {CONFIG['brand_voice']}
    Video type: {topic['video_type']}
    Content pillar: {topic['content_pillar']}
    Target length: {min_length}-{max_length} minutes ({min_words}-{max_words} words)
    
    Key points to cover:
    {', '.join(topic['key_points'])}
    
    The script should include:
    
    1. HOOK (15 seconds): Attention-grabbing opening that introduces the problem or opportunity
    2. INTRO (30-45 seconds): Channel intro, topic introduction, and what viewers will learn
    3. MAIN CONTENT: Clearly structured sections covering each key point
    4. PATTERN INTERRUPTS: Every 2-3 minutes, include a pattern interrupt (question, stat, visual cue)
    5. CONCLUSION: Summary of key points
    6. CALL TO ACTION: Ask viewers to like, subscribe, comment, and check out related content
    
    Format the script with clear section headings, timestamps, and visual/b-roll suggestions in [brackets].
    
    Example format:
    
    ## HOOK [0:00]
    [Exciting b-roll of AI in action]
    Script text here...
    
    ## INTRO [0:15]
    [Channel intro animation]
    Script text here...
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        
        script = response.choices[0].message.content
        
        # Save the script to a file
        script_file = os.path.join(CONFIG["output_dir"], f"{sanitize_filename(topic['title'])}_script.md")
        with open(script_file, "w") as f:
            f.write(script)
        
        log(f"Script generated and saved to: {script_file}")
        return script
    
    except Exception as e:
        log(f"Error generating script: {str(e)}", "ERROR")
        return None


def generate_thumbnail(topic: Dict[str, Any]) -> str:
    """Generate a thumbnail for the video"""
    log(f"Generating thumbnail for: {topic['title']}...")
    
    try:
        # Use OpenAI to generate a thumbnail image
        openai.api_key = CONFIG["api_key"]
        
        prompt = f"""
        Create a YouTube thumbnail for a video titled "{topic['title']}".
        
        Style:
        - Professional and eye-catching
        - Bold text overlay
        - High contrast
        - Related to {topic['content_pillar']}
        - Include visual elements related to AI and technology
        - Golden color scheme to match "GoldenAgeMindset" branding
        """
        
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1280x720"
        )
        
        # Download the image
        image_url = response['data'][0]['url']
        image_data = requests.get(image_url).content
        
        # Save the image
        thumbnail_file = os.path.join(CONFIG["output_dir"], f"{sanitize_filename(topic['title'])}_thumbnail.png")
        with open(thumbnail_file, "wb") as f:
            f.write(image_data)
        
        log(f"Thumbnail generated and saved to: {thumbnail_file}")
        return thumbnail_file
    
    except Exception as e:
        log(f"Error generating thumbnail: {str(e)}", "ERROR")
        
        # Create a basic thumbnail with PIL as fallback
        try:
            # Create a blank image
            img = Image.new('RGB', (1280, 720), color=(33, 33, 33))
            d = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not available
            try:
                font_title = ImageFont.truetype("Arial.ttf", 60)
                font_subtitle = ImageFont.truetype("Arial.ttf", 40)
            except IOError:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()
            
            # Add text
            title = topic['title']
            if len(title) > 40:
                title = title[:37] + "..."
            
            d.text((640, 300), title, fill=(255, 215, 0), anchor="mm", font=font_title)
            d.text((640, 400), CONFIG['channel_name'], fill=(255, 255, 255), anchor="mm", font=font_subtitle)
            
            # Add border
            d.rectangle([(20, 20), (1260, 700)], outline=(255, 215, 0), width=10)
            
            # Save the image
            thumbnail_file = os.path.join(CONFIG["output_dir"], f"{sanitize_filename(topic['title'])}_thumbnail.png")
            img.save(thumbnail_file)
            
            log(f"Basic thumbnail created as fallback: {thumbnail_file}")
            return thumbnail_file
            
        except Exception as e2:
            log(f"Failed to create fallback thumbnail: {str(e2)}", "ERROR")
            return None


def generate_video(topic: Dict[str, Any], script: str) -> str:
    """Generate a video based on the script"""
    log(f"Generating video for: {topic['title']}...")
    
    # This is a placeholder for actual video generation
    # In a real implementation, this would use a video generation API or tool
    
    # For now, we'll create a simple video with text slides
    try:
        # Parse the script to extract sections
        sections = []
        current_section = {"title": "Intro", "content": "", "timestamp": "0:00"}
        
        for line in script.split("\n"):
            if line.startswith("## "):
                # Save previous section if it has content
                if current_section["content"]:
                    sections.append(current_section)
                
                # Parse section header
                parts = line.strip("# ").split("[")
                title = parts[0].strip()
                timestamp = parts[1].strip("]") if len(parts) > 1 else "0:00"
                
                current_section = {"title": title, "content": "", "timestamp": timestamp}
            else:
                current_section["content"] += line + "\n"
        
        # Add the last section
        if current_section["content"]:
            sections.append(current_section)
        
        # Create a temporary directory for video generation
        temp_dir = os.path.join(CONFIG["temp_dir"], sanitize_filename(topic['title']))
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create slides for each section
        slide_files = []
        for i, section in enumerate(sections):
            # Create a slide image
            img = Image.new('RGB', (1920, 1080), color=(33, 33, 33))
            d = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not available
            try:
                font_title = ImageFont.truetype("Arial.ttf", 60)
                font_content = ImageFont.truetype("Arial.ttf", 40)
            except IOError:
                font_title = ImageFont.load_default()
                font_content = ImageFont.load_default()
            
            # Add text
            d.text((960, 100), section["title"], fill=(255, 215, 0), anchor="mt", font=font_title)
            
            # Wrap and add content text
            content = section["content"]
            if len(content) > 500:
                content = content[:497] + "..."
            
            # Simple text wrapping
            y_position = 200
            words = content.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                # Check if line is too long
                if len(test_line) > 50:
                    d.text((960, y_position), line, fill=(255, 255, 255), anchor="mt", font=font_content)
                    y_position += 50
                    line = word + " "
                else:
                    line = test_line
            
            # Add the last line
            if line:
                d.text((960, y_position), line, fill=(255, 255, 255), anchor="mt", font=font_content)
            
            # Add timestamp
            d.text((50, 50), f"[{section['timestamp']}]", fill=(200, 200, 200), anchor="lt", font=font_content)
            
            # Add channel branding
            d.text((960, 1000), CONFIG['channel_name'], fill=(255, 215, 0), anchor="mb", font=font_content)
            
            # Save the slide
            slide_file = os.path.join(temp_dir, f"slide_{i:03d}.png")
            img.save(slide_file)
            slide_files.append(slide_file)
        
        # Create a video from the slides
        video_file = os.path.join(CONFIG["output_dir"], f"{sanitize_filename(topic['title'])}.mp4")
        
        # Determine video duration based on video type
        if topic["video_type"] == "tutorial":
            duration = random.uniform(CONFIG["video_length"]["tutorial"][0], CONFIG["video_length"]["tutorial"][1])
        else:
            duration = random.uniform(CONFIG["video_length"]["tips"][0], CONFIG["video_length"]["tips"][1])
        
        # Calculate duration per slide
        slide_duration = duration * 60 / len(slide_files)
        
        # Create clips for each slide
        clips = [mp.ImageClip(slide).set_duration(slide_duration) for slide in slide_files]
        
        # Concatenate clips
        final_clip = mp.concatenate_videoclips(clips, method="compose")
        
        # Add simple audio (silent)
        final_clip = final_clip.set_audio(mp.AudioClip(lambda t: 0, duration=final_clip.duration))
        
        # Write the video file
        final_clip.write_videofile(video_file, fps=24, codec="libx264", audio_codec="aac")
        
        log(f"Basic video created: {video_file}")
        return video_file
        
    except Exception as e:
        log(f"Error generating video: {str(e)}", "ERROR")
        return None


def optimize_metadata(topic: Dict[str, Any], script: str) -> Dict[str, Any]:
    """Generate optimized metadata for the video"""
    log(f"Optimizing metadata for: {topic['title']}...")
    
    try:
        openai.api_key = CONFIG["api_key"]
        
        prompt = f"""
        Create optimized YouTube metadata for a video titled "{topic['title']}" for the {CONFIG['channel_name']} channel.
        
        The video is about: {topic['trending_reason']}
        
        Key points covered:
        {', '.join(topic['key_points'])}
        
        Generate the following:
        1. An SEO-optimized title (max 60 characters)
        2. A compelling description (first 100 chars are crucial, 200+ words total)
        3. 10-15 relevant tags including broad, medium, and specific keywords
        4. 3-5 relevant hashtags
        
        Format the response as JSON with the following structure:
        {{
            "title": "SEO-optimized title here",
            "description": "Full description here...",
            "tags": ["tag1", "tag2", "tag3", ...],
            "hashtags": ["#hashtag1", "#hashtag2", ...]
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and parse the JSON response
        content = response.choices[0].message.content
        json_match = re.search(r'```json\n(.*?)```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        
        metadata = json.loads(content)
        
        # Save metadata to file
        metadata_file = os.path.join(CONFIG["output_dir"], f"{sanitize_filename(topic['title'])}_metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        log(f"Metadata optimized and saved to: {metadata_file}")
        return metadata
        
    except Exception as e:
        log(f"Error optimizing metadata: {str(e)}", "ERROR")
        
        # Create basic metadata as fallback
        metadata = {
            "title": topic['title'],
            "description": f"In this video, we explore {topic['title']}. {topic['trending_reason']}\n\n" +
                          f"Key points covered:\n" +
                          "\n".join([f"- {point}" for point in topic['key_points']]) +
                          f"\n\nSubscribe to {CONFIG['channel_name']} for more AI content!",
            "tags": ["AI", "artificial intelligence", topic['content_pillar'].lower(), "technology", "future"],
            "hashtags": ["#AI", "#ArtificialIntelligence", "#Tech"]
        }
        
        return metadata


def upload_to_youtube(video_file: str, thumbnail_file: str, metadata: Dict[str, Any], topic: Dict[str, Any]) -> str:
    """Upload the video to YouTube"""
    if not CONFIG["auto_upload"]:
        log("Auto upload disabled. Skipping upload.")
        return None
    
    if not youtube:
        log("YouTube API not authenticated. Skipping upload.", "ERROR")
        return None
    
    log(f"Uploading video to YouTube: {metadata['title']}...")
    
    try:
        # Prepare the request body
        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "categoryId": "28"  # Science & Technology
            },
            "status": {
                "privacyStatus": "private",  # Start as private for review
                "selfDeclaredMadeForKids": False
            }
        }
        
        # If auto_schedule is enabled, schedule the video
        if CONFIG["auto_schedule"]:
            # Determine publish date based on video type
            today = datetime.now()
            if topic["video_type"] == "tutorial":
                # Schedule for next Tuesday
                days_until_tuesday = (1 - today.weekday()) % 7
                if days_until_tuesday == 0:
                    days_until_tuesday = 7  # Schedule for next week if today is Tuesday
                publish_date = today + timedelta(days=days_until_tuesday)
            else:
                # Schedule for next Friday
                days_until_friday = (4 - today.weekday()) % 7
                if days_until_friday == 0:
                    days_until_friday = 7  # Schedule for next week if today is Friday
                publish_date = today + timedelta(days=days_until_friday)
            
            # Set to 9:00 AM
            publish_date = publish_date.replace(hour=9, minute=0, second=0)
            
            # Format for YouTube API
            publish_date_str = publish_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            body["status"]["publishAt"] = publish_date_str
            log(f"Scheduling video for: {publish_date_str}")
        
        # Create the upload request
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )
        
        # Execute the upload
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                log(f"Uploaded {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        log(f"Video uploaded successfully! Video ID: {video_id}")
        
        # Upload thumbnail
        if thumbnail_file:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            log("Thumbnail uploaded successfully!")
        
        # Save video info
        video_info = {
            "video_id": video_id,
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "hashtags": metadata["hashtags"],
            "upload_date": datetime.now().isoformat(),
            "scheduled_publish_date": body["status"].get("publishAt"),
            "topic": topic
        }
        
        video_info_file = os.path.join(CONFIG["output_dir"], f"{sanitize_filename(topic['title'])}_video_info.json")
        with open(video_info_file, "w") as f:
            json.dump(video_info, f, indent=2)
        
        # Return the video ID
        return video_id
        
    except Exception as e:
        log(f"Error uploading video: {str(e)}", "ERROR")
        return None


def track_performance(video_id: str) -> Dict[str, Any]:
    """Track the performance of a video"""
    if not youtube or not video_id:
        return None
    
    log(f"Tracking performance for video ID: {video_id}...")
    
    try:
        # Get video statistics
        video_response = youtube.videos().list(
            part="statistics,snippet",
            id=video_id
        ).execute()
        
        if not video_response["items"]:
            log(f"Video not found: {video_id}", "ERROR")
            return None
        
        stats = video_response["items"][0]["statistics"]
        snippet = video_response["items"][0]["snippet"]
        
        # Get analytics data (limited in API)
        # For detailed analytics, you would need to use the YouTube Analytics API
        
        performance = {
            "video_id": video_id,
            "title": snippet["title"],
            "views": stats.get("viewCount", 0),
            "likes": stats.get("likeCount", 0),
            "comments": stats.get("commentCount", 0),
            "check_date": datetime.now().isoformat()
        }
        
        log(f"Performance data: Views: {performance['views']}, Likes: {performance['likes']}, Comments: {performance['comments']}")
        return performance
        
    except Exception as e:
        log(f"Error tracking performance: {str(e)}", "ERROR")
        return None


def optimize_future_content(performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze performance data to optimize future content"""
    if not performance_data or len(performance_data) < 3:
        log("Not enough performance data for optimization")
        return None
    
    log("Optimizing future content based on performance data...")
    
    try:
        # Extract key metrics
        videos = []
        for data in performance_data:
            if "topic" in data:
                video = {
                    "title": data["title"],
                    "views": int(data.get("views", 0)),
                    "likes": int(data.get("likes", 0)),
                    "comments": int(data.get("comments", 0)),
                    "content_pillar": data["topic"]["content_pillar"],
                    "video_type": data["topic"]["video_type"]
                }
                videos.append(video)
        
        if not videos:
            return None
        
        # Calculate engagement rate (likes + comments / views)
        for video in videos:
            if video["views"] > 0:
                video["engagement_rate"] = (video["likes"] + video["comments"]) / video["views"]
            else:
                video["engagement_rate"] = 0
        
        # Analyze by content pillar
        pillar_performance = {}
        for pillar in [p["name"] for p in CONFIG["content_pillars"]]:
            pillar_videos = [v for v in videos if v["content_pillar"] == pillar]
            if pillar_videos:
                avg_views = sum(v["views"] for v in pillar_videos) / len(pillar_videos)
                avg_engagement = sum(v["engagement_rate"] for v in pillar_videos) / len(pillar_videos)
                pillar_performance[pillar] = {
                    "avg_views": avg_views,
                    "avg_engagement": avg_engagement,
                    "video_count": len(pillar_videos)
                }
        
        # Analyze by video type
        type_performance = {}
        for video_type in ["tutorial", "tips"]:
            type_videos = [v for v in videos if v["video_type"] == video_type]
            if type_videos:
                avg_views = sum(v["views"] for v in type_videos) / len(type_videos)
                avg_engagement = sum(v["engagement_rate"] for v in type_videos) / len(type_videos)
                type_performance[video_type] = {
                    "avg_views": avg_views,
                    "avg_engagement": avg_engagement,
                    "video_count": len(type_videos)
                }
        
        # Find top performing videos
        videos_by_views = sorted(videos, key=lambda x: x["views"], reverse=True)
        videos_by_engagement = sorted(videos, key=lambda x: x["engagement_rate"], reverse=True)
        
        top_videos = {
            "by_views": videos_by_views[:3],
            "by_engagement": videos_by_engagement[:3]
        }
        
        # Generate optimization recommendations
        optimization = {
            "pillar_performance": pillar_performance,
            "type_performance": type_performance,
            "top_videos": top_videos,
            "recommendations": {
                "best_content_pillar": max(pillar_performance.items(), key=lambda x: x[1]["avg_engagement"])[0],
                "best_video_type": max(type_performance.items(), key=lambda x: x[1]["avg_engagement"])[0],
                "title_patterns": [v["title"] for v in videos_by_engagement[:3]]
            }
        }
        
        # Update content pillar weights based on performance
        total_engagement = sum(p["avg_engagement"] * p["video_count"] for p in pillar_performance.values())
        if total_engagement > 0:
            new_weights = {}
            for pillar, perf in pillar_performance.items():
                weight = (perf["avg_engagement"] * perf["video_count"]) / total_engagement
                new_weights[pillar] = weight
            
            # Update config
            for pillar in CONFIG["content_pillars"]:
                if pillar["name"] in new_weights:
                    pillar["weight"] = new_weights[pillar["name"]]
        
        log(f"Content optimization complete. Best content pillar: {optimization['recommendations']['best_content_pillar']}")
        return optimization
        
    except Exception as e:
        log(f"Error optimizing content: {str(e)}", "ERROR")
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename"""
    # Remove invalid characters
    s = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores
    s = re.sub(r'\s+', "_", s)
    # Limit length
    return s[:100].lower()


def send_notification(message: str):
    """Send notification to webhook"""
    if not CONFIG["webhook_url"]:
        return
    
    try:
        payload = {"content": message}
        requests.post(CONFIG["webhook_url"], json=payload)
    except Exception as e:
        log(f"Failed to send notification: {str(e)}", "ERROR")


def create_content():
    """Main content creation function"""
    log("Starting content creation process...")
    
    try:
        # Get trending topics
        topics = get_trending_topics()
        if not topics:
            log("No topics found", "ERROR")
            return
        
        # Select next topic
        topic = select_next_topic(topics)
        if not topic:
            log("Failed to select topic", "ERROR")
            return
        
        # Generate script
        script = generate_script(topic)
        if not script:
            log("Failed to generate script", "ERROR")
            return
        
        # Generate thumbnail
        thumbnail = generate_thumbnail(topic)
        
        # Generate video
        video = generate_video(topic, script)
        if not video:
            log("Failed to generate video", "ERROR")
            return
        
        # Optimize metadata
        metadata = optimize_metadata(topic, script)
        
        # Upload to YouTube
        video_id = upload_to_youtube(video, thumbnail, metadata, topic)
        
        if video_id:
            # Send notification
            send_notification(f"🎬 New video created and uploaded: {metadata['title']}\nVideo ID: {video_id}")
            
            # Track initial performance
            performance = track_performance(video_id)
            
            # Schedule performance tracking
            # In a real implementation, this would set up a scheduled task
            
            log("Content creation process completed successfully!")
            return video_id
        else:
            log("Upload failed or skipped", "WARNING")
            return None
        
    except Exception as e:
        log(f"Error in content creation process: {str(e)}", "ERROR")
        send_notification(f"❌ Error in content creation process: {str(e)}")
        return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="YouTube Content Generator")
    parser.add_argument("--create", action="store_true", help="Create new content")
    parser.add_argument("--track", metavar="VIDEO_ID", help="Track performance of a video")
    parser.add_argument("--optimize", action="store_true", help="Optimize future content based on performance")
    parser.add_argument("--schedule", action="store_true", help="Schedule content creation")
    
    args = parser.parse_args()
    
    # Create log file directory
    os.makedirs(os.path.dirname(CONFIG["log_file"]), exist_ok=True)
    
    try:
        # Check dependencies
        check_dependencies()
        
        if args.create:
            # Authenticate with YouTube
            if CONFIG["auto_upload"]:
                authenticate_youtube()
            
            # Create content
            create_content()
            
        elif args.track:
            # Authenticate with YouTube
            authenticate_youtube()
            
            # Track performance
            performance = track_performance(args.track)
            if performance:
                print(json.dumps(performance, indent=2))
            
        elif args.optimize:
            # Load performance data
            performance_data = []
            for file in os.listdir(CONFIG["output_dir"]):
                if file.endswith("_video_info.json"):
                    try:
                        with open(os.path.join(CONFIG["output_dir"], file), "r") as f:
                            video_info = json.load(f)
                        
                        # Get latest performance data
                        if "video_id" in video_info:
                            authenticate_youtube()
                            performance = track_performance(video_info["video_id"])
                            if performance:
                                # Merge with video info
                                performance.update(video_info)
                                performance_data.append(performance)
                    except Exception as e:
                        log(f"Error loading video info: {str(e)}", "ERROR")
            
            # Optimize future content
            optimization = optimize_future_content(performance_data)
            if optimization:
                print(json.dumps(optimization, indent=2))
            
        elif args.schedule:
            # Schedule content creation
            log("Scheduling content creation...")
            
            # In a real implementation, this would set up a cron job or similar
            # For now, we'll just print instructions
            print("To schedule content creation, add the following to your crontab:")
            print(f"0 9 * * 2 python3 {os.path.abspath(__file__)} --create  # Tuesday at 9 AM")
            print(f"0 9 * * 5 python3 {os.path.abspath(__file__)} --create  # Friday at 9 AM")
            
        else:
            # Default: show help
            parser.print_help()
        
    except Exception as e:
        log(f"Error: {str(e)}", "ERROR")
        send_notification(f"❌ Error in YouTube Content Generator: {str(e)}")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to check MangaDex image URLs.
"""

import requests
import json
import webbrowser
import os
import time

# API endpoint
API_URL = "http://127.0.0.1:7227/api/metadata/search?query=dandadan&provider=MangaDex"

# Create a simple HTML page to test image loading
def create_test_html(cover_url):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MangaDex Cover Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .image-container {{ margin: 20px 0; }}
            img {{ max-height: 300px; }}
            .debug {{ background: #f0f0f0; padding: 10px; margin: 20px 0; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <h1>MangaDex Cover Test</h1>
        
        <div class="image-container">
            <h2>Direct Image Test</h2>
            <img src="{cover_url}" alt="Manga Cover (Direct)" onerror="this.style.border='2px solid red'; document.getElementById('direct-error').textContent='Error loading image';">
            <p id="direct-error" style="color: red;"></p>
        </div>
        
        <div class="image-container">
            <h2>Proxy Image Test</h2>
            <img src="/get-image?url={cover_url}" alt="Manga Cover (Proxied)" onerror="this.style.border='2px solid red'; document.getElementById('proxy-error').textContent='Error loading image';">
            <p id="proxy-error" style="color: red;"></p>
        </div>
        
        <div class="debug">
            <h3>Debug Information</h3>
            <p>Cover URL: {cover_url}</p>
            <p>Current Time: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <script>
            // Check if images loaded correctly
            window.onload = function() {{
                const images = document.querySelectorAll('img');
                images.forEach(img => {{
                    console.log('Image:', img.src, 'Loaded:', !img.complete || img.naturalHeight === 0 ? 'No' : 'Yes');
                }});
            }};
        </script>
    </body>
    </html>
    """
    
    with open("cover_test.html", "w") as f:
        f.write(html)
    
    return os.path.abspath("cover_test.html")

def main():
    # Get data from API
    print("Fetching data from API...")
    response = requests.get(API_URL)
    data = response.json()
    
    if "results" in data and "MangaDex" in data["results"]:
        results = data["results"]["MangaDex"]
        if results:
            manga = results[0]
            cover_url = manga.get("cover_url", "")
            title = manga.get("title", "Unknown")
            
            print(f"Manga: {title}")
            print(f"Cover URL: {cover_url}")
            
            if cover_url:
                # Try to directly request the image
                print("\nTesting direct image request...")
                try:
                    img_response = requests.get(cover_url)
                    print(f"Status code: {img_response.status_code}")
                    print(f"Content type: {img_response.headers.get('Content-Type', 'Unknown')}")
                    print(f"Content length: {len(img_response.content)} bytes")
                    
                    # Create a test HTML file and open it
                    test_file = create_test_html(cover_url)
                    print(f"\nCreated test file: {test_file}")
                    print("Opening in browser...")
                    webbrowser.open(f"file://{test_file}")
                    
                except Exception as e:
                    print(f"Error requesting image: {e}")
            else:
                print("No cover URL found!")
        else:
            print("No results found!")
    else:
        print("Invalid API response!")
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()

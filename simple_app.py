#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template_string
import argparse
import os
from pathlib import Path

app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MangaArr - Coming Soon</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 {
            color: #0d6efd;
            margin-bottom: 20px;
        }
        .logo {
            font-size: 48px;
            margin-bottom: 20px;
        }
        .features {
            text-align: left;
            margin: 30px 0;
        }
        .feature {
            margin-bottom: 10px;
            padding-left: 20px;
            position: relative;
        }
        .feature:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #0d6efd;
        }
        .footer {
            margin-top: 40px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📚</div>
        <h1>MangaArr</h1>
        <p>Manga, Manwa, and Comics Collection Manager</p>
        <p><strong>Coming Soon!</strong></p>
        
        <div class="features">
            <h2>Features</h2>
            <div class="feature">Interactive release calendar for manga and comics</div>
            <div class="feature">Track your manga/comic collection</div>
            <div class="feature">Monitor upcoming releases</div>
            <div class="feature">Home Assistant integration</div>
            <div class="feature">Homarr integration</div>
            <div class="feature">Modern, responsive web interface</div>
        </div>
        
        <div class="footer">
            <p>MangaArr v0.0.1 | &copy; 2025 MangaArr Contributors</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def main():
    parser = argparse.ArgumentParser(description="MangaArr Simple App")
    parser.add_argument('-d', '--DatabaseFolder', type=str, help="Database folder path")
    parser.add_argument('-l', '--LogFolder', type=str, help="Log folder path")
    parser.add_argument('-o', '--Host', type=str, default='127.0.0.1', help="Host to bind to")
    parser.add_argument('-p', '--Port', type=int, default=7227, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Create log directory if it doesn't exist
    if args.LogFolder:
        log_dir = Path(args.LogFolder)
        log_dir.mkdir(exist_ok=True)
    
    # Create database directory if it doesn't exist
    if args.DatabaseFolder:
        db_dir = Path(args.DatabaseFolder)
        db_dir.mkdir(exist_ok=True)
    
    print(f"Starting MangaArr Simple App on {args.Host}:{args.Port}")
    app.run(host=args.Host, port=args.Port, debug=False)

if __name__ == "__main__":
    main()

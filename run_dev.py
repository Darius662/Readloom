#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
from pathlib import Path

def setup_dev_environment():
    """Set up development environment."""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("data/logs")
    logs_dir.mkdir(exist_ok=True)
    
    print("Development environment set up successfully!")

def generate_test_data():
    """Generate test data."""
    try:
        # Run test data generator
        subprocess.run([sys.executable, "tests/test_data_generator.py"], check=True)
        print("Test data generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating test data: {e}")
        sys.exit(1)

def run_application(host, port):
    """Run the MangaArr application.
    
    Args:
        host (str): Host to bind to.
        port (int): Port to bind to.
    """
    try:
        # Run MangaArr
        cmd = [
            sys.executable, 
            "MangaArr.py",
            "-d", "data",
            "-l", "data/logs",
            "-o", host,
            "-p", str(port)
        ]
        
        print(f"Starting MangaArr on {host}:{port}...")
        print(f"Command: {' '.join(cmd)}")
        
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running MangaArr: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMangaArr stopped by user.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MangaArr in development mode")
    parser.add_argument("--no-setup", action="store_true", help="Skip development environment setup")
    parser.add_argument("--no-data", action="store_true", help="Skip test data generation")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7227, help="Port to bind to (default: 7227)")
    
    args = parser.parse_args()
    
    # Setup development environment
    if not args.no_setup:
        setup_dev_environment()
    
    # Generate test data
    if not args.no_data:
        generate_test_data()
    
    # Run application
    run_application(args.host, args.port)

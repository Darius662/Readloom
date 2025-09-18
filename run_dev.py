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
    
    # Create database directory if it doesn't exist
    db_dir = Path("data/db")
    db_dir.mkdir(exist_ok=True)
    
    # Create empty database file if it doesn't exist
    db_file = db_dir / "mangarr.db"
    if not db_file.exists():
        try:
            db_file.touch()
            print(f"Created empty database file at {db_file}")
        except Exception as e:
            print(f"Error creating database file: {e}")
    
    print("Development environment set up successfully!")

def generate_test_data():
    """Generate test data."""
    try:
        # Make sure the database directory exists
        db_dir = Path("data/db")
        db_dir.mkdir(exist_ok=True)
        
        # Define the database path
        db_path = db_dir / "mangarr.db"
        
        # Run test data generator with the database path
        subprocess.run([sys.executable, "tests/test_data_generator.py", str(db_path)], check=True)
        print("Test data generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating test data: {e}")
        print("Continuing without test data...")

def run_application(host, port):
    """Run the MangaArr application.
    
    Args:
        host (str): Host to bind to.
        port (int): Port to bind to.
    """
    try:
        # Run simple app instead of full MangaArr
        cmd = [
            sys.executable, 
            "simple_app.py",
            "-d", "data/db",  # Use the db subdirectory for the database
            "-l", "data/logs",
            "-o", host,
            "-p", str(port)
        ]
        
        print(f"Starting MangaArr Simple App on {host}:{port}...")
        print(f"Command: {' '.join(cmd)}")
        print(f"\nOpen your browser and navigate to http://{host}:{port}/ to view the application")
        
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

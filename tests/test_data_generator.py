#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
import random

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.base.definitions import Constants, ReleaseStatus, SeriesStatus, ReadStatus, MetadataSource


def create_database_schema(cursor):
    """Create the database schema if it doesn't exist.
    
    Args:
        cursor: SQLite cursor object.
    """
    print("Creating database schema...")
    
    # Create series table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        author TEXT,
        publisher TEXT,
        cover_url TEXT,
        status TEXT,
        metadata_source TEXT,
        metadata_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create volumes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS volumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_number TEXT NOT NULL,
        title TEXT,
        description TEXT,
        cover_url TEXT,
        release_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE
    )
    """)
    
    # Create chapters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER NOT NULL,
        volume_id INTEGER,
        chapter_number TEXT NOT NULL,
        title TEXT,
        description TEXT,
        release_date TEXT,
        status TEXT,
        read_status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE SET NULL
    )
    """)
    
    # Create calendar_events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        series_id INTEGER,
        volume_id INTEGER,
        chapter_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        event_date TEXT NOT NULL,
        event_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (series_id) REFERENCES series (id) ON DELETE CASCADE,
        FOREIGN KEY (volume_id) REFERENCES volumes (id) ON DELETE CASCADE,
        FOREIGN KEY (chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
    )
    """)
    
    # Create settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    print("Database schema created successfully!")

def generate_test_data(db_path):
    """Generate test data for the Readloom database.
    
    Args:
        db_path (str): Path to the database file.
    """
    print(f"Generating test data in {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create database schema
    create_database_schema(cursor)
    
    # Sample data
    series_data = [
        {
            "title": "One Piece",
            "description": "The story follows the adventures of Monkey D. Luffy, a boy whose body gained the properties of rubber after unintentionally eating a Devil Fruit.",
            "author": "Eiichiro Oda",
            "publisher": "Shueisha",
            "cover_url": "https://upload.wikimedia.org/wikipedia/en/9/90/One_Piece%2C_Volume_61_Cover_%28Japanese%29.jpg",
            "status": SeriesStatus.ONGOING.name,
            "metadata_source": MetadataSource.MANUAL.name
        },
        {
            "title": "Attack on Titan",
            "description": "The story is set in a world where humanity lives within cities surrounded by enormous walls that protect them from gigantic man-eating humanoids referred to as Titans.",
            "author": "Hajime Isayama",
            "publisher": "Kodansha",
            "cover_url": "https://upload.wikimedia.org/wikipedia/en/d/d6/Shingeki_no_Kyojin_manga_volume_1.jpg",
            "status": SeriesStatus.COMPLETED.name,
            "metadata_source": MetadataSource.MANUAL.name
        },
        {
            "title": "Demon Slayer",
            "description": "The story follows Tanjiro Kamado, a young boy who becomes a demon slayer after his family is slaughtered and his younger sister Nezuko is turned into a demon.",
            "author": "Koyoharu Gotouge",
            "publisher": "Shueisha",
            "cover_url": "https://upload.wikimedia.org/wikipedia/en/0/09/Demon_Slayer_-_Kimetsu_no_Yaiba%2C_volume_1.jpg",
            "status": SeriesStatus.COMPLETED.name,
            "metadata_source": MetadataSource.MANUAL.name
        },
        {
            "title": "My Hero Academia",
            "description": "The story follows Izuku Midoriya, a boy born without superpowers in a world where they have become commonplace.",
            "author": "Kohei Horikoshi",
            "publisher": "Shueisha",
            "cover_url": "https://upload.wikimedia.org/wikipedia/en/5/5a/Boku_no_Hero_Academia_Volume_1.png",
            "status": SeriesStatus.ONGOING.name,
            "metadata_source": MetadataSource.MANUAL.name
        },
        {
            "title": "Solo Leveling",
            "description": "The story follows Sung Jin-Woo, a weak hunter who becomes the world's strongest after a mysterious system grants him the power to level up.",
            "author": "Chugong",
            "publisher": "D&C Media",
            "cover_url": "https://upload.wikimedia.org/wikipedia/en/9/99/Solo_Leveling_Webtoon.png",
            "status": SeriesStatus.COMPLETED.name,
            "metadata_source": MetadataSource.MANUAL.name
        }
    ]
    
    # Insert series
    series_ids = []
    for series in series_data:
        cursor.execute("""
        INSERT INTO series (
            title, description, author, publisher, cover_url, status, metadata_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            series["title"],
            series["description"],
            series["author"],
            series["publisher"],
            series["cover_url"],
            series["status"],
            series["metadata_source"]
        ))
        series_ids.append(cursor.lastrowid)
    
    # Generate volumes for each series
    for series_id in series_ids:
        # Get series info
        cursor.execute("SELECT title FROM series WHERE id = ?", (series_id,))
        series_title = cursor.fetchone()["title"]
        
        # Number of volumes depends on series
        num_volumes = random.randint(5, 20)
        
        for volume_num in range(1, num_volumes + 1):
            # Random release date between 2 years ago and 6 months in the future
            days_offset = random.randint(-730, 180)
            release_date = (datetime.now() + timedelta(days=days_offset)).strftime('%Y-%m-%d')
            
            cursor.execute("""
            INSERT INTO volumes (
                series_id, volume_number, title, description, release_date
            ) VALUES (?, ?, ?, ?, ?)
            """, (
                series_id,
                str(volume_num),
                f"Volume {volume_num}",
                f"The {volume_num}{'th' if volume_num > 3 else ['st', 'nd', 'rd'][volume_num-1]} volume of {series_title}",
                release_date
            ))
            volume_id = cursor.lastrowid
            
            # Generate chapters for this volume
            chapters_per_volume = random.randint(3, 8)
            for chapter_num in range(1, chapters_per_volume + 1):
                # Adjust chapter number based on volume
                adjusted_chapter_num = ((volume_num - 1) * 5) + chapter_num
                
                # Random release date close to volume release date
                chapter_days_offset = random.randint(-30, 30)
                chapter_release_date = (datetime.strptime(release_date, '%Y-%m-%d') + 
                                      timedelta(days=chapter_days_offset)).strftime('%Y-%m-%d')
                
                # Determine status based on release date
                today = datetime.now().strftime('%Y-%m-%d')
                if chapter_release_date > today:
                    status = ReleaseStatus.ANNOUNCED.name
                else:
                    status = ReleaseStatus.RELEASED.name
                
                # Determine read status based on release date
                if chapter_release_date > today:
                    read_status = ReadStatus.UNREAD.name
                else:
                    read_status = random.choice([ReadStatus.UNREAD.name, ReadStatus.READING.name, ReadStatus.READ.name])
                
                cursor.execute("""
                INSERT INTO chapters (
                    series_id, volume_id, chapter_number, title, release_date, status, read_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    series_id,
                    volume_id,
                    str(adjusted_chapter_num),
                    f"Chapter {adjusted_chapter_num}",
                    chapter_release_date,
                    status,
                    read_status
                ))
    
    # Commit changes
    conn.commit()
    
    # Generate calendar events
    cursor.execute("""
    SELECT id FROM series
    """)
    all_series_ids = [row["id"] for row in cursor.fetchall()]
    
    # Create some standalone calendar events
    for _ in range(10):
        series_id = random.choice(all_series_ids)
        
        # Get series info
        cursor.execute("SELECT title FROM series WHERE id = ?", (series_id,))
        series_title = cursor.fetchone()["title"]
        
        # Random date in the next 30 days
        days_offset = random.randint(1, 30)
        event_date = (datetime.now() + timedelta(days=days_offset)).strftime('%Y-%m-%d')
        
        # Random event type
        event_type = random.choice(["VOLUME_RELEASE", "CHAPTER_RELEASE"])
        
        cursor.execute("""
        INSERT INTO calendar_events (
            series_id, title, description, event_date, event_type
        ) VALUES (?, ?, ?, ?, ?)
        """, (
            series_id,
            f"Special Release - {series_title}",
            f"Special release for {series_title}",
            event_date,
            event_type
        ))
    
    # Commit changes
    conn.commit()
    
    # Close connection
    conn.close()
    
    print("Test data generation complete!")


if __name__ == "__main__":
    # Check if database path is provided
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Use default path
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "data", Constants.DEFAULT_DB_NAME)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    generate_test_data(db_path)

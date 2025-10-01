#!/usr/bin/env python3
"""
Refresh volumes for existing series in the database.
This script updates series that were imported before the volume detection fix.
"""

import sys
sys.path.insert(0, '.')

from backend.base.logging import setup_logging, LOGGER
from backend.internals.db import set_db_location, execute_query, get_db_connection
from backend.features.metadata_providers.base import metadata_provider_manager
from backend.features.metadata_providers.setup import initialize_providers
from datetime import datetime, timedelta

def refresh_series_volumes(series_id=None, series_name=None):
    """
    Refresh volumes for a specific series or all AniList series.
    
    Args:
        series_id: Specific series ID to refresh (optional)
        series_name: Series name to search for (optional)
    """
    # Set up
    setup_logging("data/logs", "refresh_volumes.log")
    set_db_location("data/db")
    initialize_providers()
    
    # Get the AniList provider
    anilist = metadata_provider_manager.get_provider("AniList")
    if not anilist:
        print("ERROR: Could not get AniList provider")
        return
    
    # Find series to refresh
    if series_id:
        series_list = execute_query(
            "SELECT id, title, metadata_source, metadata_id FROM series WHERE id = ?",
            (series_id,)
        )
    elif series_name:
        series_list = execute_query(
            "SELECT id, title, metadata_source, metadata_id FROM series WHERE title LIKE ?",
            (f"%{series_name}%",)
        )
    else:
        # Refresh all AniList series
        series_list = execute_query(
            "SELECT id, title, metadata_source, metadata_id FROM series WHERE metadata_source = 'AniList'"
        )
    
    if not series_list:
        print("No series found to refresh")
        return
    
    print(f"\nFound {len(series_list)} series to refresh\n")
    print("="*80)
    
    for series in series_list:
        print(f"\nRefreshing: {series['title']}")
        print("-" * 60)
        
        try:
            # Get current volume count
            current_volumes = execute_query(
                "SELECT COUNT(*) as count FROM volumes WHERE series_id = ?",
                (series['id'],)
            )[0]['count']
            
            print(f"  Current volumes in database: {current_volumes}")
            
            # Get manga details with accurate volume count
            if series['metadata_source'] == 'AniList':
                details = anilist.get_manga_details(series['metadata_id'])
                
                if not details:
                    print(f"  ❌ ERROR: Could not get details from AniList")
                    continue
                
                new_volume_count = details.get("volume_count", 0)
                volumes_list = details.get("volumes", [])
                
                print(f"  New volume count from scraper: {new_volume_count}")
                
                if new_volume_count == current_volumes:
                    print(f"  ✅ Volume count is already correct, skipping")
                    continue
                
                if new_volume_count == 0:
                    print(f"  ⚠️  WARNING: Scraper returned 0 volumes, skipping")
                    continue
                
                # Delete old volumes
                print(f"  Deleting {current_volumes} old volumes...")
                execute_query(
                    "DELETE FROM volumes WHERE series_id = ?",
                    (series['id'],)
                )
                
                # Insert new volumes
                print(f"  Creating {len(volumes_list)} new volumes...")
                conn = get_db_connection()
                cursor = conn.cursor()
                
                for volume in volumes_list:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO volumes (
                                series_id, volume_number, title, description, cover_url, release_date
                            ) VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                series['id'],
                                volume.get("number", "0"),
                                volume.get("title", f"Volume {volume.get('number', '0')}"),
                                volume.get("description", ""),
                                volume.get("cover_url", ""),
                                volume.get("release_date", "")
                            )
                        )
                    except Exception as e:
                        print(f"    ⚠️  Error inserting volume {volume.get('number')}: {e}")
                
                conn.commit()
                
                # Verify
                new_count = execute_query(
                    "SELECT COUNT(*) as count FROM volumes WHERE series_id = ?",
                    (series['id'],)
                )[0]['count']
                
                print(f"  ✅ SUCCESS: Updated from {current_volumes} to {new_count} volumes")
            else:
                print(f"  ⚠️  Skipping: Not an AniList series")
        
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("REFRESH COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Refresh volumes for existing series")
    parser.add_argument("--id", type=int, help="Specific series ID to refresh")
    parser.add_argument("--name", type=str, help="Series name to search for")
    parser.add_argument("--all", action="store_true", help="Refresh all AniList series")
    
    args = parser.parse_args()
    
    if args.id:
        refresh_series_volumes(series_id=args.id)
    elif args.name:
        refresh_series_volumes(series_name=args.name)
    elif args.all:
        refresh_series_volumes()
    else:
        print("Usage:")
        print("  python refresh_series_volumes.py --id <series_id>")
        print("  python refresh_series_volumes.py --name <series_name>")
        print("  python refresh_series_volumes.py --all")
        print("\nExamples:")
        print("  python refresh_series_volumes.py --name 'One Punch Man'")
        print("  python refresh_series_volumes.py --all")

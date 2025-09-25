#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data mapping utilities for the Jikan API provider.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from .constants import MAL_URL


def map_search_results(data: Dict[str, Any], provider_name: str) -> List[Dict[str, Any]]:
    """Map search results from Jikan API to standardized format.
    
    Args:
        data: The raw API response data
        provider_name: The name of the provider
        
    Returns:
        List of standardized manga search results
    """
    results = []
    
    if "data" in data:
        for item in data["data"]:
            try:
                manga_id = item["mal_id"]
                title = item["title"]
                
                # Get cover art
                cover_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")
                
                # Get author
                authors = []
                for author in item.get("authors", []):
                    authors.append(author.get("name", ""))
                author = ", ".join(authors) if authors else "Unknown"
                
                # Get status
                status = item.get("status", "Unknown").upper()
                
                # Get description
                description = item.get("synopsis", "")
                
                # Get genres
                genres = []
                for genre in item.get("genres", []):
                    genres.append(genre.get("name", ""))
                
                # Get rating
                rating = str(item.get("score", 0))
                
                manga_data = {
                    "id": str(manga_id),
                    "title": title,
                    "cover_url": cover_url,
                    "author": author,
                    "status": status,
                    "description": description,
                    "genres": genres,
                    "rating": rating,
                    "url": f"{MAL_URL}/{manga_id}",
                    "source": provider_name
                }
                
                results.append(manga_data)
            except Exception as e:
                # Log error in the provider class
                pass
    
    return results


def map_manga_details(item: Dict[str, Any], manga_id: str, provider_name: str) -> Dict[str, Any]:
    """Map manga details from Jikan API to standardized format.
    
    Args:
        item: The manga data from API
        manga_id: The manga ID
        provider_name: The name of the provider
        
    Returns:
        Standardized manga details
    """
    # Get title
    title = item["title"]
    
    # Get alternative titles
    alt_titles = []
    if "titles" in item:
        for title_obj in item["titles"]:
            if title_obj.get("type") != "Default":
                alt_titles.append(title_obj.get("title", ""))
    
    # Get cover art
    cover_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")
    
    # Get author
    authors = []
    for author in item.get("authors", []):
        authors.append(author.get("name", ""))
    author = ", ".join(authors) if authors else "Unknown"
    
    # Get status
    status = item.get("status", "Unknown").upper()
    
    # Get description
    description = item.get("synopsis", "")
    
    # Get genres
    genres = []
    for genre in item.get("genres", []):
        genres.append(genre.get("name", ""))
    
    # Get rating
    rating = str(item.get("score", 0))
    
    # Get volumes
    volumes = []
    volume_count = item.get("volumes", 0)
    if volume_count:
        for i in range(1, volume_count + 1):
            volumes.append({
                "number": str(i),
                "title": f"Volume {i}"
            })
    
    return {
        "id": str(manga_id),
        "title": title,
        "alternative_titles": alt_titles,
        "cover_url": cover_url,
        "author": author,
        "status": status,
        "description": description,
        "genres": genres,
        "rating": rating,
        "volumes": volumes,
        "url": f"{MAL_URL}/{manga_id}",
        "source": provider_name
    }


def map_latest_releases(data: Dict[str, Any], provider_name: str) -> List[Dict[str, Any]]:
    """Map latest releases from Jikan API to standardized format.
    
    Args:
        data: The raw API response data
        provider_name: The name of the provider
        
    Returns:
        List of standardized latest releases
    """
    results = []
    
    if "data" in data:
        for item in data["data"]:
            try:
                manga_id = item["mal_id"]
                manga_title = item["title"]
                
                # Get cover art
                cover_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")
                
                # For ongoing manga, try to estimate the most recent chapter release date
                release_date = ""
                
                # First try to get date from publishing info
                if item.get("published", {}).get("from"):
                    # Use from date as base date
                    start_date_str = item["published"]["from"].split("T")[0]
                    
                    try:
                        # For ongoing manga, estimate the most recent release
                        # Use the start date and assume biweekly releases up to current date
                        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                        today = datetime.now()
                        days_since_start = (today - start_date).days
                        
                        # Assume biweekly releases (14 days)
                        chapter_count = days_since_start // 14
                        if chapter_count > 0:
                            # Estimate the latest chapter release date
                            latest_release = start_date + timedelta(days=14 * chapter_count)
                            # If this would be in the future, use today's date
                            if latest_release > today:
                                latest_release = today
                            release_date = latest_release.strftime("%Y-%m-%d")
                        else:
                            release_date = start_date_str
                    except Exception:
                        release_date = start_date_str  # Fall back to start date
                else:
                    # No publication date, use today's date for ongoing manga
                    release_date = datetime.now().strftime("%Y-%m-%d")
                
                results.append({
                    "manga_id": str(manga_id),
                    "manga_title": manga_title,
                    "cover_url": cover_url,
                    "chapter": f"Latest Chapter",
                    "chapter_id": f"{manga_id}_latest",
                    "date": release_date,  # Always include a date
                    "url": f"{MAL_URL}/{manga_id}",
                    "source": provider_name
                })
            except Exception:
                # Log error in the provider class
                pass
    
    return results

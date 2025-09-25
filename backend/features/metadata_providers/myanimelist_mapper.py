#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MyAnimeList data mapping helpers.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .myanimelist_constants import MANGA_URL, STATUS_MAPPING


def map_search_results(data: Dict[str, Any], provider_name: str, logger=None) -> List[Dict[str, Any]]:
    """Map MyAnimeList search results to standard format.
    
    Args:
        data: The raw API response data.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A list of manga search results.
    """
    results = []
    
    try:
        if not data or "data" not in data:
            return results
        
        for item in data["data"]:
            try:
                node = item["node"]
                manga_id = str(node["id"])
                
                # Get title
                title = node.get("title", "")
                
                # Get alternative titles
                alt_titles = []
                if "alternative_titles" in node:
                    if "en" in node["alternative_titles"] and node["alternative_titles"]["en"]:
                        alt_titles.append(node["alternative_titles"]["en"])
                    if "ja" in node["alternative_titles"] and node["alternative_titles"]["ja"]:
                        alt_titles.append(node["alternative_titles"]["ja"])
                    if "synonyms" in node["alternative_titles"] and node["alternative_titles"]["synonyms"]:
                        alt_titles.extend(node["alternative_titles"]["synonyms"])
                
                # Get cover URL
                cover_url = ""
                if "main_picture" in node:
                    if "large" in node["main_picture"]:
                        cover_url = node["main_picture"]["large"]
                    elif "medium" in node["main_picture"]:
                        cover_url = node["main_picture"]["medium"]
                
                # Get description
                description = node.get("synopsis", "")
                
                # Get status
                status = "Unknown"
                if "status" in node and node["status"] in STATUS_MAPPING:
                    status = STATUS_MAPPING[node["status"]]
                
                # Get genres
                genres = []
                if "genres" in node:
                    for genre in node["genres"]:
                        if "name" in genre:
                            genres.append(genre["name"])
                
                # Get author
                author = "Unknown"
                if "authors" in node:
                    authors = []
                    for author_item in node["authors"]:
                        if "node" in author_item and "first_name" in author_item["node"] and "last_name" in author_item["node"]:
                            authors.append(f"{author_item['node']['last_name']}, {author_item['node']['first_name']}")
                    if authors:
                        author = ", ".join(authors)
                
                # Get volumes and chapters count
                volumes = node.get("num_volumes", 0)
                chapters = node.get("num_chapters", 0)
                
                # Get rating
                rating = "0"
                if "mean" in node and node["mean"]:
                    rating = str(node["mean"])
                
                # Format the result
                result = {
                    "id": manga_id,
                    "title": title,
                    "alternative_titles": alt_titles,
                    "cover_url": cover_url,
                    "author": author,
                    "status": status,
                    "description": description,
                    "genres": genres,
                    "volumes": volumes,
                    "chapters": chapters,
                    "rating": rating,
                    "url": f"{MANGA_URL}/{manga_id}",
                    "source": provider_name
                }
                
                results.append(result)
            except Exception as e:
                if logger:
                    logger.error(f"Error mapping manga item: {e}")
        
        return results
    except Exception as e:
        if logger:
            logger.error(f"Error mapping search results: {e}")
        return []


def map_manga_details(data: Dict[str, Any], provider_name: str, logger=None) -> Dict[str, Any]:
    """Map MyAnimeList manga details to standard format.
    
    Args:
        data: The raw API response data.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A dictionary containing manga details.
    """
    try:
        if not data:
            return {}
        
        manga_id = str(data["id"])
        
        # Get title
        title = data.get("title", "")
        
        # Get alternative titles
        alt_titles = []
        if "alternative_titles" in data:
            if "en" in data["alternative_titles"] and data["alternative_titles"]["en"]:
                alt_titles.append(data["alternative_titles"]["en"])
            if "ja" in data["alternative_titles"] and data["alternative_titles"]["ja"]:
                alt_titles.append(data["alternative_titles"]["ja"])
            if "synonyms" in data["alternative_titles"] and data["alternative_titles"]["synonyms"]:
                alt_titles.extend(data["alternative_titles"]["synonyms"])
        
        # Get cover URL
        cover_url = ""
        if "main_picture" in data:
            if "large" in data["main_picture"]:
                cover_url = data["main_picture"]["large"]
            elif "medium" in data["main_picture"]:
                cover_url = data["main_picture"]["medium"]
        
        # Get description
        description = data.get("synopsis", "")
        
        # Get status
        status = "Unknown"
        if "status" in data and data["status"] in STATUS_MAPPING:
            status = STATUS_MAPPING[data["status"]]
        
        # Get genres
        genres = []
        if "genres" in data:
            for genre in data["genres"]:
                if "name" in genre:
                    genres.append(genre["name"])
        
        # Get author
        author = "Unknown"
        if "authors" in data:
            authors = []
            for author_item in data["authors"]:
                if "node" in author_item and "first_name" in author_item["node"] and "last_name" in author_item["node"]:
                    authors.append(f"{author_item['node']['last_name']}, {author_item['node']['first_name']}")
            if authors:
                author = ", ".join(authors)
        
        # Get volumes and chapters count
        volumes = data.get("num_volumes", 0)
        chapters = data.get("num_chapters", 0)
        
        # Get rating
        rating = "0"
        if "mean" in data and data["mean"]:
            rating = str(data["mean"])
        
        # Get start and end dates
        start_date = ""
        if "start_date" in data and data["start_date"]:
            start_date = data["start_date"]
        
        end_date = ""
        if "end_date" in data and data["end_date"]:
            end_date = data["end_date"]
        
        # Get related manga
        related_manga = []
        if "related_manga" in data:
            for related in data["related_manga"]:
                if "node" in related and "id" in related["node"] and "title" in related["node"]:
                    related_manga.append({
                        "id": str(related["node"]["id"]),
                        "title": related["node"]["title"],
                        "relation_type": related.get("relation_type", ""),
                        "url": f"{MANGA_URL}/{related['node']['id']}"
                    })
        
        # Get recommendations
        recommendations = []
        if "recommendations" in data:
            for rec in data["recommendations"]:
                if "node" in rec and "id" in rec["node"] and "title" in rec["node"]:
                    recommendations.append({
                        "id": str(rec["node"]["id"]),
                        "title": rec["node"]["title"],
                        "url": f"{MANGA_URL}/{rec['node']['id']}"
                    })
        
        # Generate volumes list
        volumes_list = []
        if volumes:
            # Calculate a reasonable interval between volumes
            if start_date and end_date and start_date != end_date:
                try:
                    start = datetime.fromisoformat(start_date)
                    end = datetime.fromisoformat(end_date)
                    total_days = (end - start).days
                    interval_days = max(30, total_days // volumes)  # At least one month between volumes
                except (ValueError, TypeError):
                    # Default to 3-month intervals if date parsing fails
                    start = datetime.now() - timedelta(days=volumes * 90)
                    interval_days = 90
            else:
                # Default to 3-month intervals if we don't have proper dates
                start = datetime.now() - timedelta(days=volumes * 90)
                interval_days = 90
                
            for i in range(1, volumes + 1):
                # Calculate volume release date (evenly distributed)
                volume_date = start + timedelta(days=(i-1) * interval_days)
                volumes_list.append({
                    "number": str(i),
                    "title": f"Volume {i}",
                    "description": "",
                    "cover_url": "",
                    "release_date": volume_date.strftime("%Y-%m-%d")  # Use calculated date
                })
        
        # Format the result
        return {
            "id": manga_id,
            "title": title,
            "alternative_titles": alt_titles,
            "cover_url": cover_url,
            "author": author,
            "status": status,
            "description": description,
            "genres": genres,
            "volumes": volumes,
            "chapters": chapters,
            "rating": rating,
            "start_date": start_date,
            "end_date": end_date,
            "related_manga": related_manga,
            "recommendations": recommendations,
            "url": f"{MANGA_URL}/{manga_id}",
            "source": provider_name,
            "volumes": volumes_list
        }
    except Exception as e:
        if logger:
            logger.error(f"Error mapping manga details: {e}")
        return {}


def generate_chapter_list(manga_details: Dict[str, Any], provider_name: str, logger=None) -> Dict[str, List[Dict[str, Any]]]:
    """Generate synthetic chapter list based on manga details.
    
    Args:
        manga_details: The manga details.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A dictionary containing a list of chapters.
    """
    chapters = []
    
    try:
        manga_id = manga_details.get("id", "")
        total_chapters = manga_details.get("chapters", 0)
        status = manga_details.get("status", "")
        
        # If no chapters count, estimate based on status
        if not total_chapters or total_chapters <= 0:
            if status == "COMPLETED":
                total_chapters = 36  # Completed series - estimate 25-75 chapters
            elif status == "CANCELLED":
                total_chapters = 10  # Cancelled series - estimate 5-15 chapters
            else:
                total_chapters = 20  # Ongoing series - estimate 12-24 chapters so far
            
            if logger:
                logger.info(f"No chapter count from MyAnimeList for {manga_id}, estimating {total_chapters} chapters")
        
        # Get start and end dates
        start_date_str = manga_details.get("start_date", "")
        end_date_str = manga_details.get("end_date", "")
        
        # Parse start date
        start_date = None
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except (ValueError, TypeError):
                start_date = None
        
        # If no valid start date, use a default date 1 year ago
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        
        # Parse end date
        end_date = None
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
            except (ValueError, TypeError):
                end_date = None
        
        # Generate chapter dates
        if not end_date or status == "ONGOING":
            # For ongoing manga, distribute chapters between start date and now, with some future chapters
            future_chapters = max(3, int(total_chapters * 0.1))  # At least 3 future chapters or 10% of total
            past_chapters = total_chapters - future_chapters
            
            # Calculate intervals
            if past_chapters > 1:
                past_interval = (datetime.now() - start_date) / past_chapters
            else:
                past_interval = timedelta(days=14)  # Default to bi-weekly
            
            # Default publication schedule: weekly on Monday
            publication_day = 0  # Monday (0=Monday, 6=Sunday)
            future_interval = timedelta(days=7)  # Weekly
            
            for i in range(1, total_chapters + 1):
                if i <= past_chapters:
                    # Past chapter
                    chapter_date = start_date + (past_interval * (i - 1))
                    is_confirmed = True
                else:
                    # Future chapter
                    future_i = i - past_chapters
                    base_next_date = datetime.now() + (future_interval * future_i)
                    days_to_add = (publication_day - base_next_date.weekday()) % 7
                    chapter_date = base_next_date + timedelta(days=days_to_add)
                    is_confirmed = False
                
                chapters.append({
                    "id": f"{manga_id}_{i}",
                    "number": str(i),
                    "title": f"Chapter {i}",
                    "date": chapter_date.strftime("%Y-%m-%d"),
                    "source": provider_name,
                    "is_confirmed_date": 1 if is_confirmed else 0
                })
        else:
            # For completed manga, distribute chapters evenly between start and end dates
            interval = (end_date - start_date) / total_chapters
            for i in range(1, total_chapters + 1):
                chapter_date = start_date + (interval * (i - 1))
                chapters.append({
                    "id": f"{manga_id}_{i}",
                    "number": str(i),
                    "title": f"Chapter {i}",
                    "date": chapter_date.strftime("%Y-%m-%d"),
                    "source": provider_name,
                    "is_confirmed_date": 1  # All chapters in completed series are confirmed
                })
        
        return {"chapters": chapters}
    except Exception as e:
        if logger:
            logger.error(f"Error generating chapter list: {e}")
        return {"chapters": []}

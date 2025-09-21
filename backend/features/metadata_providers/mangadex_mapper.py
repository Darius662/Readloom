#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaDex data mapping helpers.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from .mangadex_constants import COVER_URL, MANGA_URL, CHAPTER_URL, STATUS_MAPPING


def map_search_results(data: Dict[str, Any], provider_name: str, logger=None) -> List[Dict[str, Any]]:
    """Map MangaDex search results to standard format.
    
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
                manga_id = item["id"]
                attributes = item["attributes"]
                
                # Get title
                title = ""
                if "title" in attributes:
                    if "en" in attributes["title"]:
                        title = attributes["title"]["en"]
                    elif attributes["title"] and len(attributes["title"]) > 0:
                        # Get first available title
                        title = next(iter(attributes["title"].values()))
                
                # Get alternative titles
                alt_titles = []
                if "altTitles" in attributes:
                    for alt_title_obj in attributes["altTitles"]:
                        for lang, alt_title in alt_title_obj.items():
                            if alt_title and alt_title not in alt_titles:
                                alt_titles.append(alt_title)
                
                # Get description
                description = ""
                if "description" in attributes:
                    if "en" in attributes["description"]:
                        description = attributes["description"]["en"]
                    elif attributes["description"] and len(attributes["description"]) > 0:
                        # Get first available description
                        description = next(iter(attributes["description"].values()))
                
                # Get status
                status = "Unknown"
                if "status" in attributes and attributes["status"] in STATUS_MAPPING:
                    status = STATUS_MAPPING[attributes["status"]]
                
                # Get cover URL
                cover_url = ""
                if "relationships" in item:
                    for rel in item["relationships"]:
                        if rel["type"] == "cover_art" and "attributes" in rel and "fileName" in rel["attributes"]:
                            cover_url = f"{COVER_URL}/{manga_id}/{rel['attributes']['fileName']}.512.jpg"
                
                # Get author
                author = "Unknown"
                if "relationships" in item:
                    authors = []
                    for rel in item["relationships"]:
                        if rel["type"] in ["author", "artist"] and "attributes" in rel and "name" in rel["attributes"]:
                            authors.append(rel["attributes"]["name"])
                    if authors:
                        author = ", ".join(authors)
                
                # Format the result
                result = {
                    "id": manga_id,
                    "title": title,
                    "alternative_titles": alt_titles,
                    "cover_url": cover_url,
                    "author": author,
                    "status": status,
                    "description": description,
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
    """Map MangaDex manga details to standard format.
    
    Args:
        data: The raw API response data.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A dictionary containing manga details.
    """
    try:
        if not data or "data" not in data:
            return {}
        
        item = data["data"]
        manga_id = item["id"]
        attributes = item["attributes"]
        
        # Get title
        title = ""
        if "title" in attributes:
            if "en" in attributes["title"]:
                title = attributes["title"]["en"]
            elif attributes["title"] and len(attributes["title"]) > 0:
                # Get first available title
                title = next(iter(attributes["title"].values()))
        
        # Get alternative titles
        alt_titles = []
        if "altTitles" in attributes:
            for alt_title_obj in attributes["altTitles"]:
                for lang, alt_title in alt_title_obj.items():
                    if alt_title and alt_title not in alt_titles:
                        alt_titles.append(alt_title)
        
        # Get description
        description = ""
        if "description" in attributes:
            if "en" in attributes["description"]:
                description = attributes["description"]["en"]
            elif attributes["description"] and len(attributes["description"]) > 0:
                # Get first available description
                description = next(iter(attributes["description"].values()))
        
        # Get status
        status = "Unknown"
        if "status" in attributes and attributes["status"] in STATUS_MAPPING:
            status = STATUS_MAPPING[attributes["status"]]
        
        # Get cover URL
        cover_url = ""
        if "relationships" in item:
            for rel in item["relationships"]:
                if rel["type"] == "cover_art" and "attributes" in rel and "fileName" in rel["attributes"]:
                    cover_url = f"{COVER_URL}/{manga_id}/{rel['attributes']['fileName']}.512.jpg"
        
        # Get author
        author = "Unknown"
        if "relationships" in item:
            authors = []
            for rel in item["relationships"]:
                if rel["type"] in ["author", "artist"] and "attributes" in rel and "name" in rel["attributes"]:
                    authors.append(rel["attributes"]["name"])
            if authors:
                author = ", ".join(authors)
        
        # Get genres
        genres = []
        if "tags" in attributes:
            for tag in attributes["tags"]:
                if "attributes" in tag and "name" in tag["attributes"] and "en" in tag["attributes"]["name"]:
                    genres.append(tag["attributes"]["name"]["en"])
        
        # Get volumes and chapters count
        volumes = attributes.get("lastVolume", "0")
        try:
            volumes = int(volumes) if volumes else 0
        except (ValueError, TypeError):
            volumes = 0
            
        chapters = attributes.get("lastChapter", "0")
        try:
            chapters = int(chapters) if chapters else 0
        except (ValueError, TypeError):
            chapters = 0
        
        # Get rating
        rating = "0"
        if "rating" in attributes and "bayesian" in attributes["rating"]:
            try:
                rating = str(round(attributes["rating"]["bayesian"] / 100, 1))
            except (ValueError, TypeError):
                rating = "0"
        
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
            "url": f"{MANGA_URL}/{manga_id}",
            "source": provider_name
        }
    except Exception as e:
        if logger:
            logger.error(f"Error mapping manga details: {e}")
        return {}


def map_chapter_list(data: Dict[str, Any], manga_id: str, provider_name: str, logger=None) -> List[Dict[str, Any]]:
    """Map MangaDex chapter list to standard format.
    
    Args:
        data: The raw API response data.
        manga_id: The manga ID.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A list of chapters.
    """
    chapters = []
    
    try:
        if not data or "data" not in data:
            return chapters
        
        for item in data["data"]:
            try:
                chapter_id = item["id"]
                attributes = item["attributes"]
                
                # Get chapter number
                chapter_number = attributes.get("chapter", "0")
                
                # Get chapter title
                chapter_title = attributes.get("title", f"Chapter {chapter_number}")
                if not chapter_title:
                    chapter_title = f"Chapter {chapter_number}"
                
                # Get chapter date
                chapter_date = ""
                if "publishAt" in attributes and attributes["publishAt"]:
                    try:
                        date_obj = datetime.fromisoformat(attributes["publishAt"].replace("Z", "+00:00"))
                        chapter_date = date_obj.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        pass
                
                if not chapter_date and "updatedAt" in attributes and attributes["updatedAt"]:
                    try:
                        date_obj = datetime.fromisoformat(attributes["updatedAt"].replace("Z", "+00:00"))
                        chapter_date = date_obj.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        pass
                
                if not chapter_date and "createdAt" in attributes and attributes["createdAt"]:
                    try:
                        date_obj = datetime.fromisoformat(attributes["createdAt"].replace("Z", "+00:00"))
                        chapter_date = date_obj.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        pass
                
                # Format the result
                chapters.append({
                    "id": chapter_id,
                    "number": chapter_number,
                    "title": chapter_title,
                    "date": chapter_date,
                    "url": f"{CHAPTER_URL}/{chapter_id}",
                    "manga_id": manga_id,
                    "source": provider_name
                })
            except Exception as e:
                if logger:
                    logger.error(f"Error mapping chapter item: {e}")
        
        return chapters
    except Exception as e:
        if logger:
            logger.error(f"Error mapping chapter list: {e}")
        return []


def map_chapter_images(data: Dict[str, Any], logger=None) -> List[str]:
    """Map MangaDex chapter images to standard format.
    
    Args:
        data: The raw API response data.
        logger: Optional logger for debug info.
        
    Returns:
        A list of image URLs.
    """
    images = []
    
    try:
        if not data or "baseUrl" not in data or "chapter" not in data or "data" not in data["chapter"]:
            return images
        
        base_url = data["baseUrl"]
        chapter_hash = data["chapter"]["hash"]
        image_files = data["chapter"]["data"]
        
        for image_file in image_files:
            image_url = f"{base_url}/data/{chapter_hash}/{image_file}"
            images.append(image_url)
        
        return images
    except Exception as e:
        if logger:
            logger.error(f"Error mapping chapter images: {e}")
        return []

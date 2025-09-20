#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AniList metadata provider.
"""

import json
from typing import Dict, List, Any, Optional, Union, Tuple
import requests
from datetime import datetime, timedelta, date
import re
import calendar

# Import the manga info provider
try:
    from backend.features.scrapers.mangafire_scraper import MangaInfoProvider
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False

from .base import MetadataProvider


class AniListProvider(MetadataProvider):
    """AniList metadata provider."""

    def __init__(self, enabled: bool = True):
        """Initialize the AniList provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("AniList", enabled)
        self.base_url = "https://graphql.anilist.co"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MangaArr/1.0.0"
        }
        self.session = requests.Session()
        
        # Initialize the manga info provider if available
        self.info_provider = None
        if PROVIDER_AVAILABLE:
            self.info_provider = MangaInfoProvider()
        
        # List of popular manga that should use the scraper for better chapter counts
        self.popular_manga_patterns = [
            re.compile(r'one\s*piece', re.IGNORECASE),
            re.compile(r'naruto', re.IGNORECASE),
            re.compile(r'bleach', re.IGNORECASE),
            re.compile(r'dragon\s*ball', re.IGNORECASE),
            re.compile(r'jujutsu\s*kaisen', re.IGNORECASE),
            re.compile(r'kimetsu\s*no\s*yaiba|demon\s*slayer', re.IGNORECASE),
            re.compile(r'attack\s*on\s*titan|shingeki\s*no\s*kyojin', re.IGNORECASE),
            re.compile(r'my\s*hero\s*academia|boku\s*no\s*hero', re.IGNORECASE),
            re.compile(r'hunter\s*x\s*hunter', re.IGNORECASE),
            re.compile(r'tokyo\s*ghoul', re.IGNORECASE)
        ]

    def _make_graphql_request(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Make a GraphQL request to the AniList API.
        
        Args:
            query: The GraphQL query.
            variables: The query variables.
            
        Returns:
            The JSON response.
        """
        try:
            payload = {
                "query": query,
                "variables": variables
            }
            
            response = self.session.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error making request to AniList API: {e}")
            return {}

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on AniList.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        # Define GraphQL query for searching manga
        graphql_query = """
        query ($search: String, $page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                media(search: $search, type: MANGA, sort: POPULARITY_DESC) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    description
                    coverImage {
                        large
                        medium
                    }
                    bannerImage
                    startDate {
                        year
                        month
                        day
                    }
                    endDate {
                        year
                        month
                        day
                    }
                    status
                    volumes
                    chapters
                    averageScore
                    genres
                    synonyms
                    staff {
                        edges {
                            role
                            node {
                                name {
                                    full
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        # Set variables for the query
        variables = {
            "search": query,
            "page": page,
            "perPage": 10  # Number of results per page
        }
        
        # Make the request
        data = self._make_graphql_request(graphql_query, variables)
        
        # Process and return the results
        results = []
        
        try:
            if data and "data" in data and "Page" in data["data"] and "media" in data["data"]["Page"]:
                for item in data["data"]["Page"]["media"]:
                    # Extract authors/staff information
                    authors = []
                    if "staff" in item and "edges" in item["staff"]:
                        for edge in item["staff"]["edges"]:
                            if "Story" in edge["role"] or "Art" in edge["role"]:
                                authors.append(edge["node"]["name"]["full"])
                    
                    # Determine status
                    status = "Unknown"
                    if "status" in item:
                        if item["status"] == "FINISHED":
                            status = "COMPLETED"
                        elif item["status"] == "RELEASING":
                            status = "ONGOING"
                        elif item["status"] == "NOT_YET_RELEASED":
                            status = "ANNOUNCED"
                        elif item["status"] == "CANCELLED":
                            status = "CANCELLED"
                        else:
                            status = item["status"]
                    
                    # Get alternative titles
                    alt_titles = []
                    if "synonyms" in item and item["synonyms"]:
                        alt_titles.extend(item["synonyms"])
                    
                    # Add English and native titles if different from romaji
                    if item["title"].get("english") and item["title"].get("english") != item["title"].get("romaji"):
                        alt_titles.append(item["title"]["english"])
                    if item["title"].get("native") and item["title"].get("native") != item["title"].get("romaji"):
                        alt_titles.append(item["title"]["native"])
                    
                    # Get cover URL
                    cover_url = ""
                    if "coverImage" in item:
                        if item["coverImage"].get("large"):
                            cover_url = item["coverImage"]["large"]
                        elif item["coverImage"].get("medium"):
                            cover_url = item["coverImage"]["medium"]
                    
                    # Format the result
                    result = {
                        "id": str(item["id"]),
                        "title": item["title"].get("romaji", item["title"].get("english", "")),
                        "alternative_titles": alt_titles,
                        "cover_url": cover_url,
                        "author": ", ".join(authors) if authors else "Unknown",
                        "status": status,
                        "description": item.get("description", "").replace("<br>", "\n").replace("<i>", "").replace("</i>", ""),
                        "genres": item.get("genres", []),
                        "rating": str(item.get("averageScore", 0) / 10) if item.get("averageScore") else "0",
                        "volumes": item.get("volumes", 0),
                        "chapters": item.get("chapters", 0),
                        "url": f"https://anilist.co/manga/{item['id']}",
                        "source": self.name
                    }
                    
                    results.append(result)
        except Exception as e:
            self.logger.error(f"Error parsing AniList search results: {e}")
        
        return results

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga on AniList.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            The manga details.
        """
        # Define GraphQL query for getting manga details
        graphql_query = """
        query ($id: Int) {
            Media(id: $id, type: MANGA) {
                id
                title {
                    romaji
                    english
                    native
                }
                description
                coverImage {
                    large
                    medium
                }
                bannerImage
                startDate {
                    year
                    month
                    day
                }
                endDate {
                    year
                    month
                    day
                }
                status
                volumes
                chapters
                averageScore
                genres
                synonyms
                staff {
                    edges {
                        role
                        node {
                            name {
                                full
                            }
                        }
                    }
                }
                relations {
                    edges {
                        relationType
                        node {
                            id
                            title {
                                romaji
                            }
                            type
                        }
                    }
                }
                recommendations {
                    nodes {
                        mediaRecommendation {
                            id
                            title {
                                romaji
                            }
                            type
                        }
                    }
                }
            }
        }
        """
        
        # Set variables for the query
        variables = {
            "id": int(manga_id)
        }
        
        # Make the request
        data = self._make_graphql_request(graphql_query, variables)
        
        # Process and return the results
        try:
            if data and "data" in data and "Media" in data["data"]:
                item = data["data"]["Media"]
                
                # Extract authors/staff information
                authors = []
                if "staff" in item and "edges" in item["staff"]:
                    for edge in item["staff"]["edges"]:
                        if "Story" in edge["role"] or "Art" in edge["role"]:
                            authors.append(edge["node"]["name"]["full"])
                
                # Determine status
                status = "Unknown"
                if "status" in item:
                    if item["status"] == "FINISHED":
                        status = "COMPLETED"
                    elif item["status"] == "RELEASING":
                        status = "ONGOING"
                    elif item["status"] == "NOT_YET_RELEASED":
                        status = "ANNOUNCED"
                    elif item["status"] == "CANCELLED":
                        status = "CANCELLED"
                    else:
                        status = item["status"]
                
                # Get alternative titles
                alt_titles = []
                if "synonyms" in item and item["synonyms"]:
                    alt_titles.extend(item["synonyms"])
                
                # Add English and native titles if different from romaji
                if item["title"].get("english") and item["title"].get("english") != item["title"].get("romaji"):
                    alt_titles.append(item["title"]["english"])
                if item["title"].get("native") and item["title"].get("native") != item["title"].get("romaji"):
                    alt_titles.append(item["title"]["native"])
                
                # Get cover URL
                cover_url = ""
                if "coverImage" in item:
                    if item["coverImage"].get("large"):
                        cover_url = item["coverImage"]["large"]
                    elif item["coverImage"].get("medium"):
                        cover_url = item["coverImage"]["medium"]
                
                # Format start and end dates
                start_date = ""
                if "startDate" in item and all(item["startDate"].values()):
                    start_date = f"{item['startDate']['year']}-{item['startDate']['month']}-{item['startDate']['day']}"
                
                end_date = ""
                if "endDate" in item and all(item["endDate"].values()):
                    end_date = f"{item['endDate']['year']}-{item['endDate']['month']}-{item['endDate']['day']}"
                
                # Get related manga
                related_manga = []
                if "relations" in item and "edges" in item["relations"]:
                    for edge in item["relations"]["edges"]:
                        if edge["node"]["type"] == "MANGA":
                            related_manga.append({
                                "id": str(edge["node"]["id"]),
                                "title": edge["node"]["title"].get("romaji", ""),
                                "relation_type": edge["relationType"],
                                "url": f"https://anilist.co/manga/{edge['node']['id']}"
                            })
                
                # Get recommendations
                recommendations = []
                if "recommendations" in item and "nodes" in item["recommendations"]:
                    for node in item["recommendations"]["nodes"]:
                        if node["mediaRecommendation"]["type"] == "MANGA":
                            recommendations.append({
                                "id": str(node["mediaRecommendation"]["id"]),
                                "title": node["mediaRecommendation"]["title"].get("romaji", ""),
                                "url": f"https://anilist.co/manga/{node['mediaRecommendation']['id']}"
                            })
                
                # Format the result
                # Create an empty volumes list since AniList doesn't provide detailed volume info
                # This is needed to prevent NoneType errors during import
                volumes_list = []
                
                # If we have volume count, create placeholder volume entries
                volume_count = item.get("volumes", 0)
                if volume_count and volume_count > 0:
                    for i in range(1, volume_count + 1):
                        volumes_list.append({
                            "number": str(i),
                            "title": f"Volume {i}",
                            "description": "",
                            "cover_url": "",
                            "release_date": start_date  # Use manga start date as fallback
                        })
                
                return {
                    "id": str(item["id"]),
                    "title": item["title"].get("romaji", item["title"].get("english", "")),
                    "alternative_titles": alt_titles,
                    "cover_url": cover_url,
                    "author": ", ".join(authors) if authors else "Unknown",
                    "status": status,
                    "description": item.get("description", "").replace("<br>", "\n").replace("<i>", "").replace("</i>", ""),
                    "genres": item.get("genres", []),
                    "rating": str(item.get("averageScore", 0) / 10) if item.get("averageScore") else "0",
                    "volumes": item.get("volumes", 0),
                    "chapters": item.get("chapters", 0),
                    "start_date": start_date,
                    "end_date": end_date,
                    "related_manga": related_manga,
                    "recommendations": recommendations,
                    "url": f"https://anilist.co/manga/{item['id']}",
                    "source": self.name,
                    # Add the volumes list to the response
                    "volumes": volumes_list
                }
                
        except Exception as e:
            self.logger.error(f"Error parsing AniList manga details: {e}")
        
        return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga on AniList.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A list of chapters or a dictionary with chapters.
        """
        # AniList API doesn't provide detailed chapter information
        # We need to generate synthetic chapter data
        
        try:
            # Get manga details to extract any available info
            manga_details = self.get_manga_details(manga_id)
            
            if not manga_details:
                return {"chapters": []}
            
            # Create a list of chapters
            chapters = []
            
            # Get chapter count from API, or from scraper, or estimate based on typical manga length
            total_chapters = manga_details.get("chapters", 0)
            total_volumes = manga_details.get("volumes", 0)
            manga_title = manga_details.get("title", "")
            
            # Try to get more accurate counts for any manga using our provider
            provider_data = False
            if self.info_provider and manga_title:
                self.logger.info(f"Getting accurate chapter counts for: {manga_title}")
                accurate_chapters, accurate_volumes = self.info_provider.get_chapter_count(manga_title)
                
                if accurate_chapters > 0:
                    total_chapters = accurate_chapters
                    total_volumes = accurate_volumes or total_volumes
                    provider_data = True
                    self.logger.info(f"Got accurate data for {manga_title}: {total_chapters} chapters, {total_volumes} volumes")
            
            # If no chapters count is provided by AniList API or our provider, estimate based on status and type
            if not provider_data and (not total_chapters or total_chapters <= 0):
                status = manga_details.get("status", "")
                # Generate a reasonable number of chapters based on manga status
                if status == "COMPLETED":
                    # Completed series - estimate 25-75 chapters
                    total_chapters = 36
                elif status == "CANCELLED":
                    # Cancelled series - estimate 5-15 chapters
                    total_chapters = 10
                else:  # ONGOING, RELEASING, etc.
                    # Ongoing series - estimate 12-24 chapters so far
                    total_chapters = 20
                
                self.logger.info(f"No chapter count from AniList for {manga_id}, estimating {total_chapters} chapters")
            
            # Now we have a reasonable chapter count to work with
            # Get start and end dates to distribute chapter releases
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
            
            # If manga is ongoing or has no end date, use current date + some future dates
            if not end_date or manga_details.get("status") == "ONGOING":
                # Use current date plus some buffer for future chapters
                future_chapters = max(3, int(total_chapters * 0.1))  # At least 3 future chapters or 10% of total
                if future_chapters > 0:
                    # For ongoing manga, make some recent chapters and some future ones
                    past_chapters = total_chapters - future_chapters
                    
                    # Calculate release intervals
                    if past_chapters > 1:
                        # Time between start and now for past chapters
                        past_interval = (datetime.now() - start_date) / past_chapters
                    else:
                        past_interval = timedelta(days=14)  # Default to bi-weekly
                        
                    # Determine publication schedule based on manga metadata
                    publication_day, future_interval = self._determine_publication_schedule(manga_details)
                    
                    # Create chapter dates
                    for i in range(1, total_chapters + 1):
                        if i <= past_chapters:
                            # Past chapter
                            chapter_date = start_date + (past_interval * (i - 1))
                        else:
                            # Future chapter - follow actual publication schedule
                            future_i = i - past_chapters
                            
                            # Calculate base next date
                            base_next_date = datetime.now() + (future_interval * future_i)
                            
                            # Adjust to the correct day of week based on publication schedule
                            days_to_add = (publication_day - base_next_date.weekday()) % 7
                            chapter_date = base_next_date + timedelta(days=days_to_add)
                        
                        # For future chapters, mark as unconfirmed (only predicted)
                        is_confirmed = False
                        if i <= past_chapters:
                            # Past chapters are considered "historical" data
                            is_confirmed = True
                        
                        chapters.append({
                            "id": f"{manga_id}_{i}",
                            "number": str(i),
                            "title": f"Chapter {i}",
                            "date": chapter_date.strftime("%Y-%m-%d"),
                            "source": self.name,
                            "is_confirmed_date": 1 if is_confirmed else 0
                        })
            else:
                # Completed manga - distribute chapters evenly between start and end date
                interval = (end_date - start_date) / total_chapters
                for i in range(1, total_chapters + 1):
                    chapter_date = start_date + (interval * (i - 1))
                    # For completed manga, all chapters are historical and considered confirmed
                    chapters.append({
                        "id": f"{manga_id}_{i}",
                        "number": str(i),
                        "title": f"Chapter {i}",
                        "date": chapter_date.strftime("%Y-%m-%d"),
                        "source": self.name,
                        "is_confirmed_date": 1  # All chapters in completed series are confirmed
                    })
            
            return {"chapters": chapters}
            
        except Exception as e:
            self.logger.error(f"Error getting chapter list from AniList: {e}")
            return {"chapters": []}

    def _determine_publication_schedule(self, manga_details: Dict[str, Any]) -> Tuple[int, timedelta]:
        """
        Determine the publication schedule based on manga metadata.
        
        Args:
            manga_details: The manga details.
            
        Returns:
            A tuple of (publication_day, interval) where publication_day is the day of week (0=Monday, 6=Sunday)
            and interval is the timedelta between chapters.
        """
        # Get relevant metadata
        title = str(manga_details.get("title", "")).lower()
        genres = [str(g).lower() for g in manga_details.get("genres", [])] if isinstance(manga_details.get("genres"), list) else []
        status = str(manga_details.get("status", "")).lower()
        
        # Default schedule: Monday release every 14 days (bi-weekly)
        default_day = 0  # Monday (0=Monday, 6=Sunday in Python's datetime)
        default_interval = timedelta(days=14)  # Bi-weekly
        
        # Detect if it's a Weekly Shonen Jump series (releases on Sunday in Japan, Monday in most Western countries)
        weekly_jump_patterns = ["one piece", "my hero academia", "black clover", "jujutsu kaisen", "chainsaw man"]
        if any(pattern in title for pattern in weekly_jump_patterns):
            return (0, timedelta(days=7))  # Monday, Weekly
        
        # Monthly seinen/josei magazines often release mid-month
        monthly_patterns = ["berserk", "vinland saga", "vagabond"]
        if any(pattern in title for pattern in monthly_patterns) or "seinen" in genres:
            return (3, timedelta(days=30))  # Thursday, Monthly
        
        # Detect manhwa (Korean comics) which often update on specific weekdays
        manhwa_patterns = ["solo leveling", "tower of god", "god of high school"]
        if any(pattern in title for pattern in manhwa_patterns):
            return (2, timedelta(days=7))  # Wednesday, Weekly
        
        # Detect if it's likely a weekly series based on genre and status
        if "shounen" in genres and status in ["ongoing", "releasing"]:
            # Many weekly shounen release on Sunday/Monday
            return (6, timedelta(days=7))  # Sunday, Weekly
        
        # Detect if it's likely a monthly series
        if any(g in genres for g in ["seinen", "josei"]) or "monthly" in title:
            # Monthly series, pick a consistent day (15th of month)
            return (4, timedelta(days=30))  # Friday, Monthly
            
        # Use default for everything else
        return (default_day, default_interval)
    
    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on AniList.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        # AniList API doesn't provide chapter images
        self.logger.warning("AniList API doesn't provide chapter images")
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on AniList.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        # Define GraphQL query for getting latest manga releases
        graphql_query = """
        query ($page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                media(type: MANGA, sort: TRENDING_DESC, status: RELEASING) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    coverImage {
                        large
                        medium
                    }
                    startDate {
                        year
                        month
                        day
                    }
                    status
                    volumes
                    chapters
                    averageScore
                    staff {
                        edges {
                            role
                            node {
                                name {
                                    full
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        # Set variables for the query
        variables = {
            "page": page,
            "perPage": 10  # Number of results per page
        }
        
        # Make the request
        data = self._make_graphql_request(graphql_query, variables)
        
        # Process and return the results
        results = []
        
        try:
            if data and "data" in data and "Page" in data["data"] and "media" in data["data"]["Page"]:
                for item in data["data"]["Page"]["media"]:
                    # Extract authors/staff information
                    authors = []
                    if "staff" in item and "edges" in item["staff"]:
                        for edge in item["staff"]["edges"]:
                            if "Story" in edge["role"] or "Art" in edge["role"]:
                                authors.append(edge["node"]["name"]["full"])
                    
                    # Get cover URL
                    cover_url = ""
                    if "coverImage" in item:
                        if item["coverImage"].get("large"):
                            cover_url = item["coverImage"]["large"]
                        elif item["coverImage"].get("medium"):
                            cover_url = item["coverImage"]["medium"]
                    
                    # Format the result
                    results.append({
                        "manga_id": str(item["id"]),
                        "manga_title": item["title"].get("romaji", item["title"].get("english", "")),
                        "cover_url": cover_url,
                        "author": ", ".join(authors) if authors else "Unknown",
                        "volumes": item.get("volumes", 0),
                        "chapters": item.get("chapters", 0),
                        "rating": str(item.get("averageScore", 0) / 10) if item.get("averageScore") else "0",
                        "url": f"https://anilist.co/manga/{item['id']}",
                        "source": self.name
                    })
        except Exception as e:
            self.logger.error(f"Error parsing AniList latest releases: {e}")
        
        return results

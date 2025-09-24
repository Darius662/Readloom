#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AniList metadata provider implementation.
"""

import json
import re
import calendar
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Union, Tuple

import requests

from ..base import MetadataProvider
from ..anilist_client import make_graphql_request
from ..anilist_constants import KNOWN_VOLUMES, POPULAR_MANGA_PATTERNS
from ..anilist_schedule import determine_publication_schedule

# Import the manga info provider
try:
    from backend.features.scrapers.mangafire_scraper import MangaInfoProvider
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False


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
            "User-Agent": "Readloom/1.0.0",
        }
        self.session = requests.Session()

        # Initialize the manga info provider if available
        self.info_provider = None
        if PROVIDER_AVAILABLE:
            self.info_provider = MangaInfoProvider()

        # Popular manga patterns for better chapter counts
        self.popular_manga_patterns = POPULAR_MANGA_PATTERNS

        # Known volume counts for manga where the API data might be incorrect
        self.known_volumes = KNOWN_VOLUMES

    def _make_graphql_request(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Make a GraphQL request to the AniList API."""
        return make_graphql_request(
            session=self.session,
            base_url=self.base_url,
            headers=self.headers,
            query=query,
            variables=variables,
            logger=self.logger,
        )

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on AniList."""
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

        variables = {"search": query, "page": page, "perPage": 10}

        data = self._make_graphql_request(graphql_query, variables)

        results: List[Dict[str, Any]] = []
        try:
            if data and "data" in data and "Page" in data["data"] and "media" in data["data"]["Page"]:
                for item in data["data"]["Page"]["media"]:
                    authors: List[str] = []
                    if "staff" in item and "edges" in item["staff"]:
                        for edge in item["staff"]["edges"]:
                            if "Story" in edge["role"] or "Art" in edge["role"]:
                                authors.append(edge["node"]["name"]["full"])

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

                    alt_titles: List[str] = []
                    if "synonyms" in item and item["synonyms"]:
                        alt_titles.extend(item["synonyms"])

                    if item["title"].get("english") and item["title"].get("english") != item["title"].get("romaji"):
                        alt_titles.append(item["title"]["english"])
                    if item["title"].get("native") and item["title"].get("native") != item["title"].get("romaji"):
                        alt_titles.append(item["title"]["native"])

                    cover_url = ""
                    if "coverImage" in item:
                        if item["coverImage"].get("large"):
                            cover_url = item["coverImage"]["large"]
                        elif item["coverImage"].get("medium"):
                            cover_url = item["coverImage"]["medium"]

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
                        "source": self.name,
                    }

                    results.append(result)
        except Exception as e:
            self.logger.error(f"Error parsing AniList search results: {e}")

        return results

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga on AniList."""
        graphql_query = """
        query ($id: Int) {
            Media(id: $id, type: MANGA) {
                id
                title { romaji english native }
                description
                coverImage { large medium }
                bannerImage
                startDate { year month day }
                endDate { year month day }
                status
                volumes
                chapters
                averageScore
                genres
                synonyms
                staff { edges { role node { name { full } } } }
                relations { edges { relationType node { id title { romaji } type } } }
                recommendations { nodes { mediaRecommendation { id title { romaji } type } } }
            }
        }
        """

        variables = {"id": int(manga_id)}
        data = self._make_graphql_request(graphql_query, variables)

        try:
            if data and "data" in data and "Media" in data["data"]:
                item = data["data"]["Media"]

                authors: List[str] = []
                if "staff" in item and "edges" in item["staff"]:
                    for edge in item["staff"]["edges"]:
                        if "Story" in edge["role"] or "Art" in edge["role"]:
                            authors.append(edge["node"]["name"]["full"])

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

                alt_titles: List[str] = []
                if "synonyms" in item and item["synonyms"]:
                    alt_titles.extend(item["synonyms"])

                if item["title"].get("english") and item["title"].get("english") != item["title"].get("romaji"):
                    alt_titles.append(item["title"]["english"])
                if item["title"].get("native") and item["title"].get("native") != item["title"].get("romaji"):
                    alt_titles.append(item["title"]["native"])

                cover_url = ""
                if "coverImage" in item:
                    if item["coverImage"].get("large"):
                        cover_url = item["coverImage"]["large"]
                    elif item["coverImage"].get("medium"):
                        cover_url = item["coverImage"]["medium"]

                start_date = ""
                if "startDate" in item and all(item["startDate"].values()):
                    start_date = f"{item['startDate']['year']}-{item['startDate']['month']}-{item['startDate']['day']}"

                end_date = ""
                if "endDate" in item and all(item["endDate"].values()):
                    end_date = f"{item['endDate']['year']}-{item['endDate']['month']}-{item['endDate']['day']}"

                related_manga = []
                if "relations" in item and "edges" in item["relations"]:
                    for edge in item["relations"]["edges"]:
                        if edge["node"]["type"] == "MANGA":
                            related_manga.append(
                                {
                                    "id": str(edge["node"]["id"]),
                                    "title": edge["node"]["title"].get("romaji", ""),
                                    "relation_type": edge["relationType"],
                                    "url": f"https://anilist.co/manga/{edge['node']['id']}",
                                }
                            )

                recommendations = []
                if "recommendations" in item and "nodes" in item["recommendations"]:
                    for node in item["recommendations"]["nodes"]:
                        if node["mediaRecommendation"]["type"] == "MANGA":
                            recommendations.append(
                                {
                                    "id": str(node["mediaRecommendation"]["id"]),
                                    "title": node["mediaRecommendation"]["title"].get("romaji", ""),
                                    "url": f"https://anilist.co/manga/{node['mediaRecommendation']['id']}",
                                }
                            )

                volumes_list: List[Dict[str, Any]] = []

                known_volume_count = self.known_volumes.get(str(item["id"]))
                if known_volume_count:
                    self.logger.info(
                        f"Using known volume count {known_volume_count} for {item['title'].get('romaji')}"
                    )
                    volume_count = known_volume_count
                else:
                    volume_count = item.get("volumes", 0)
                    if volume_count == 0 and item.get("status") == "FINISHED":
                        chapter_count = item.get("chapters", 0)
                        if chapter_count > 0:
                            volume_count = max(1, chapter_count // 9)
                            self.logger.info(
                                f"Estimated {volume_count} volumes for {item['title'].get('romaji')} based on {chapter_count} chapters"
                            )
                    if volume_count == 0 and item.get("status") != "NOT_YET_RELEASED":
                        volume_count = 1
                if volume_count and volume_count > 0:
                    if start_date and end_date and start_date != end_date:
                        try:
                            start = datetime.fromisoformat(start_date)
                            end = datetime.fromisoformat(end_date)
                            total_days = (end - start).days
                            interval_days = max(30, total_days // volume_count)
                        except (ValueError, TypeError):
                            start = datetime.now() - timedelta(days=volume_count * 90)
                            interval_days = 90
                    else:
                        start = datetime.now() - timedelta(days=volume_count * 90)
                        interval_days = 90

                    for i in range(1, volume_count + 1):
                        volume_date = start + timedelta(days=(i - 1) * interval_days)
                        volumes_list.append(
                            {
                                "number": str(i),
                                "title": f"Volume {i}",
                                "description": "",
                                "cover_url": "",
                                "release_date": volume_date.strftime("%Y-%m-%d"),
                            }
                        )

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
                    "volumes": volumes_list,
                }
        except Exception as e:
            self.logger.error(f"Error parsing AniList manga details: {e}")

        return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga on AniList."""
        try:
            manga_details = self.get_manga_details(manga_id)
            if not manga_details:
                return {"chapters": []}

            chapters: List[Dict[str, Any]] = []
            total_chapters = manga_details.get("chapters", 0)
            total_volumes = manga_details.get("volumes", 0)
            manga_title = manga_details.get("title", "")

            provider_data = False
            if self.info_provider and manga_title:
                self.logger.info(
                    f"Getting accurate volume and chapter counts for: {manga_title}"
                )
                accurate_chapters, accurate_volumes = self.info_provider.get_chapter_count(
                    manga_title
                )

                if accurate_volumes > 0:
                    total_volumes = accurate_volumes
                    provider_data = True
                    self.logger.info(
                        f"Using scraped volume count for {manga_title}: {total_volumes} volumes"
                    )

                if accurate_chapters > 0:
                    if total_chapters is None or accurate_chapters > total_chapters:
                        total_chapters = accurate_chapters
                        self.logger.info(
                            f"Using scraped chapter count for {manga_title}: {total_chapters} chapters"
                        )
                    provider_data = True

                if provider_data:
                    self.logger.info(
                        f"Final data for {manga_title}: {total_chapters} chapters, {total_volumes} volumes"
                    )

            if not provider_data and (not total_chapters or total_chapters <= 0):
                status = manga_details.get("status", "")
                if status == "COMPLETED":
                    total_chapters = 36
                elif status == "CANCELLED":
                    total_chapters = 10
                else:
                    total_chapters = 20

                self.logger.info(
                    f"No chapter count from AniList for {manga_id}, estimating {total_chapters} chapters"
                )

            start_date_str = manga_details.get("start_date", "")
            end_date_str = manga_details.get("end_date", "")

            start_date_dt: Optional[datetime] = None
            if start_date_str:
                try:
                    start_date_dt = datetime.fromisoformat(start_date_str)
                except (ValueError, TypeError):
                    start_date_dt = None

            if not start_date_dt:
                start_date_dt = datetime.now() - timedelta(days=365)

            end_date_dt: Optional[datetime] = None
            if end_date_str:
                try:
                    end_date_dt = datetime.fromisoformat(end_date_str)
                except (ValueError, TypeError):
                    end_date_dt = None

            if not end_date_dt or manga_details.get("status") == "ONGOING":
                future_chapters = max(3, int(total_chapters * 0.1))
                if future_chapters > 0:
                    past_chapters = total_chapters - future_chapters

                    if past_chapters > 1:
                        past_interval = (datetime.now() - start_date_dt) / past_chapters
                    else:
                        past_interval = timedelta(days=14)

                    publication_day, future_interval = determine_publication_schedule(
                        manga_details
                    )

                    for i in range(1, total_chapters + 1):
                        if i <= past_chapters:
                            chapter_date = start_date_dt + (past_interval * (i - 1))
                        else:
                            future_i = i - past_chapters
                            base_next_date = datetime.now() + (future_interval * future_i)
                            days_to_add = (publication_day - base_next_date.weekday()) % 7
                            chapter_date = base_next_date + timedelta(days=days_to_add)

                        is_confirmed = i <= past_chapters

                        chapters.append(
                            {
                                "id": f"{manga_id}_{i}",
                                "number": str(i),
                                "title": f"Chapter {i}",
                                "date": chapter_date.strftime("%Y-%m-%d"),
                                "source": self.name,
                                "is_confirmed_date": 1 if is_confirmed else 0,
                            }
                        )
            else:
                interval = (end_date_dt - start_date_dt) / total_chapters
                for i in range(1, total_chapters + 1):
                    chapter_date = start_date_dt + (interval * (i - 1))
                    chapters.append(
                        {
                            "id": f"{manga_id}_{i}",
                            "number": str(i),
                            "title": f"Chapter {i}",
                            "date": chapter_date.strftime("%Y-%m-%d"),
                            "source": self.name,
                            "is_confirmed_date": 1,
                        }
                    )

            return {"chapters": chapters}
        except Exception as e:
            self.logger.error(f"Error getting chapter list from AniList: {e}")
            return {"chapters": []}

    def _determine_publication_schedule(self, manga_details: Dict[str, Any]) -> Tuple[int, timedelta]:
        """Thin wrapper to the shared scheduling helper for backward compatibility."""
        return determine_publication_schedule(manga_details)

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on AniList."""
        self.logger.warning("AniList API doesn't provide chapter images")
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on AniList."""
        graphql_query = """
        query ($page: Int, $perPage: Int) {
            Page(page: $page, perPage: $perPage) {
                media(type: MANGA, sort: TRENDING_DESC, status: RELEASING) {
                    id
                    title { romaji english native }
                    coverImage { large medium }
                    startDate { year month day }
                    status
                    volumes
                    chapters
                    averageScore
                    staff { edges { role node { name { full } } } }
                }
            }
        }
        """

        variables = {"page": page, "perPage": 10}
        data = self._make_graphql_request(graphql_query, variables)

        results: List[Dict[str, Any]] = []
        try:
            if data and "data" in data and "Page" in data["data"] and "media" in data["data"]["Page"]:
                for item in data["data"]["Page"]["media"]:
                    authors = []
                    if "staff" in item and "edges" in item["staff"]:
                        for edge in item["staff"]["edges"]:
                            if "Story" in edge["role"] or "Art" in edge["role"]:
                                authors.append(edge["node"]["name"]["full"])

                    cover_url = ""
                    if "coverImage" in item:
                        if item["coverImage"].get("large"):
                            cover_url = item["coverImage"]["large"]
                        elif item["coverImage"].get("medium"):
                            cover_url = item["coverImage"]["medium"]

                    results.append(
                        {
                            "manga_id": str(item["id"]),
                            "manga_title": item["title"].get(
                                "romaji", item["title"].get("english", "")
                            ),
                            "cover_url": cover_url,
                            "author": ", ".join(authors) if authors else "Unknown",
                            "volumes": item.get("volumes", 0),
                            "chapters": item.get("chapters", 0),
                            "rating": str(item.get("averageScore", 0) / 10)
                            if item.get("averageScore")
                            else "0",
                            "url": f"https://anilist.co/manga/{item['id']}",
                            "source": self.name,
                        }
                    )
        except Exception as e:
            self.logger.error(f"Error parsing AniList latest releases: {e}")

        return results

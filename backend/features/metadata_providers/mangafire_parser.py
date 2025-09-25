#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MangaFire HTML parsing helpers.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup

from .mangafire_constants import BASE_URL


def parse_search_results(html_content: str, provider_name: str, logger=None) -> List[Dict[str, Any]]:
    """Parse search results from MangaFire HTML.
    
    Args:
        html_content: The HTML content to parse.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A list of manga search results.
    """
    results = []
    try:
        if logger:
            logger.info(f"HTML response length: {len(html_content)}")
            logger.info(f"First 500 chars of HTML: {html_content[:500]}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        manga_items = soup.select('.manga-detail')
        if logger:
            logger.info(f"Found {len(manga_items)} manga items with selector '.manga-detail'")
        
        # If no manga items found, try alternative selectors
        if not manga_items:
            if logger:
                logger.info("Trying alternative selectors...")
            manga_items = soup.select('.manga-item')
            if logger:
                logger.info(f"Found {len(manga_items)} manga items with selector '.manga-item'")
            
            if not manga_items:
                manga_items = soup.select('.manga')
                if logger:
                    logger.info(f"Found {len(manga_items)} manga items with selector '.manga'")
        
        for item in manga_items:
            try:
                title_elem = item.select_one('.manga-name a')
                title = title_elem.text.strip() if title_elem else "Unknown"
                
                manga_url = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                manga_id = manga_url.split('/')[-1] if manga_url else ""
                
                cover_elem = item.select_one('.manga-poster img')
                cover_url = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else ""
                
                author_elem = item.select_one('.manga-author')
                author = author_elem.text.strip() if author_elem else "Unknown"
                
                status_elem = item.select_one('.manga-status')
                status = status_elem.text.strip() if status_elem else "Unknown"
                
                latest_chapter_elem = item.select_one('.chapter-name')
                latest_chapter = latest_chapter_elem.text.strip() if latest_chapter_elem else "Unknown"
                
                results.append({
                    "id": manga_id,
                    "title": title,
                    "cover_url": cover_url,
                    "author": author,
                    "status": status,
                    "latest_chapter": latest_chapter,
                    "url": f"{BASE_URL}{manga_url}",
                    "source": provider_name
                })
            except Exception as e:
                if logger:
                    logger.error(f"Error parsing manga item: {e}")
        
        return results
    except Exception as e:
        if logger:
            logger.error(f"Error parsing search results: {e}")
        return []


def parse_manga_details(html_content: str, manga_id: str, provider_name: str, logger=None) -> Dict[str, Any]:
    """Parse manga details from MangaFire HTML.
    
    Args:
        html_content: The HTML content to parse.
        manga_id: The manga ID.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A dictionary containing manga details.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        title_elem = soup.select_one('.manga-name h1')
        title = title_elem.text.strip() if title_elem else "Unknown"
        
        cover_elem = soup.select_one('.manga-poster img')
        cover_url = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else ""
        
        author_elem = soup.select_one('.manga-author a')
        author = author_elem.text.strip() if author_elem else "Unknown"
        
        status_elem = soup.select_one('.manga-status')
        status = status_elem.text.strip() if status_elem else "Unknown"
        
        description_elem = soup.select_one('.manga-description')
        description = description_elem.text.strip() if description_elem else ""
        
        genres = []
        genre_elems = soup.select('.manga-genres a')
        for genre_elem in genre_elems:
            genres.append(genre_elem.text.strip())
        
        # Get alternative titles
        alt_titles = []
        alt_titles_elem = soup.select_one('.manga-alt-name')
        if alt_titles_elem:
            alt_titles_text = alt_titles_elem.text.strip()
            if alt_titles_text:
                alt_titles = [title.strip() for title in alt_titles_text.split(';')]
        
        # Get rating
        rating = "0.0"
        rating_elem = soup.select_one('.manga-rating .rating-num')
        if rating_elem:
            rating = rating_elem.text.strip()
        
        return {
            "id": manga_id,
            "title": title,
            "alternative_titles": alt_titles,
            "cover_url": cover_url,
            "author": author,
            "status": status,
            "description": description,
            "genres": genres,
            "rating": rating,
            "url": f"{BASE_URL}/manga/{manga_id}",
            "source": provider_name
        }
    except Exception as e:
        if logger:
            logger.error(f"Error parsing manga details: {e}")
        return {}


def parse_chapter_list(html_content: str, manga_id: str, provider_name: str, logger=None) -> List[Dict[str, Any]]:
    """Parse chapter list from MangaFire HTML.
    
    Args:
        html_content: The HTML content to parse.
        manga_id: The manga ID.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A list of chapters.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        chapters = []
        chapter_items = soup.select('.chapter-item')
        
        for item in chapter_items:
            try:
                chapter_elem = item.select_one('.chapter-name')
                chapter_title = chapter_elem.text.strip() if chapter_elem else "Unknown"
                
                chapter_url = chapter_elem['href'] if chapter_elem and 'href' in chapter_elem.attrs else ""
                chapter_id = chapter_url.split('/')[-1] if chapter_url else ""
                
                chapter_number_match = re.search(r'Chapter (\d+(\.\d+)?)', chapter_title)
                chapter_number = chapter_number_match.group(1) if chapter_number_match else "0"
                
                date_elem = item.select_one('.chapter-time')
                date = date_elem.text.strip() if date_elem else "Unknown"
                
                chapters.append({
                    "id": chapter_id,
                    "title": chapter_title,
                    "number": chapter_number,
                    "date": date,
                    "url": f"{BASE_URL}{chapter_url}",
                    "manga_id": manga_id
                })
            except Exception as e:
                if logger:
                    logger.error(f"Error parsing chapter item: {e}")
        
        return chapters
    except Exception as e:
        if logger:
            logger.error(f"Error parsing chapter list: {e}")
        return []


def parse_chapter_images(html_content: str, logger=None) -> List[str]:
    """Parse chapter images from MangaFire HTML.
    
    Args:
        html_content: The HTML content to parse.
        logger: Optional logger for debug info.
        
    Returns:
        A list of image URLs.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        images = []
        image_items = soup.select('.chapter-images img')
        
        for item in image_items:
            if 'src' in item.attrs:
                images.append(item['src'])
        
        return images
    except Exception as e:
        if logger:
            logger.error(f"Error parsing chapter images: {e}")
        return []


def parse_latest_releases(html_content: str, provider_name: str, logger=None) -> List[Dict[str, Any]]:
    """Parse latest releases from MangaFire HTML.
    
    Args:
        html_content: The HTML content to parse.
        provider_name: The provider name for source attribution.
        logger: Optional logger for debug info.
        
    Returns:
        A list of latest releases.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        results = []
        manga_items = soup.select('.manga-item')
        
        for item in manga_items:
            try:
                title_elem = item.select_one('.manga-name a')
                title = title_elem.text.strip() if title_elem else "Unknown"
                
                manga_url = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                manga_id = manga_url.split('/')[-1] if manga_url else ""
                
                cover_elem = item.select_one('.manga-poster img')
                cover_url = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else ""
                
                chapter_elem = item.select_one('.chapter-name')
                chapter = chapter_elem.text.strip() if chapter_elem else "Unknown"
                
                chapter_url = chapter_elem['href'] if chapter_elem and 'href' in chapter_elem.attrs else ""
                chapter_id = chapter_url.split('/')[-1] if chapter_url else ""
                
                date_elem = item.select_one('.chapter-time')
                date = date_elem.text.strip() if date_elem else "Unknown"
                
                results.append({
                    "manga_id": manga_id,
                    "manga_title": title,
                    "cover_url": cover_url,
                    "chapter": chapter,
                    "chapter_id": chapter_id,
                    "date": date,
                    "url": f"{BASE_URL}{chapter_url}",
                    "source": provider_name
                })
            except Exception as e:
                if logger:
                    logger.error(f"Error parsing latest release item: {e}")
        
        return results
    except Exception as e:
        if logger:
            logger.error(f"Error parsing latest releases: {e}")
        return []

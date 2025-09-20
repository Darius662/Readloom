#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Viz Media metadata provider.
"""

import re
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import threading

from .base import MetadataProvider


class VizMediaProvider(MetadataProvider):
    """Viz Media metadata provider that scrapes the Viz.com calendar."""

    def __init__(self, enabled: bool = True):
        """Initialize the Viz Media provider.
        
        Args:
            enabled: Whether the provider is enabled.
        """
        super().__init__("VizMedia", enabled)
        self.base_url = "https://www.viz.com"
        self.calendar_url = f"{self.base_url}/calendar"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": self.base_url,
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        self.session = requests.Session()
        # Add cache for cover images to avoid repeated requests
        self.cover_cache = {}
        
        # Rate limiting properties
        self.last_request_time = 0
        self.min_request_interval = 0.5  # Minimum time between requests in seconds
        self.request_lock = threading.Lock()  # Lock for thread safety

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a request to the Viz Media website with rate limiting.
        
        Args:
            url: The URL to request.
            params: The query parameters.
            
        Returns:
            The response.
        """
        try:
            # Apply rate limiting
            with self.request_lock:
                current_time = time.time()
                time_since_last_request = current_time - self.last_request_time
                
                if time_since_last_request < self.min_request_interval:
                    # Sleep to respect rate limit
                    sleep_time = self.min_request_interval - time_since_last_request
                    self.logger.info(f"Rate limiting: Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                
                self.last_request_time = time.time()
            
            self.logger.info(f"Making request to {url} with params {params}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            
            # If we get a 429 (too many requests), retry with backoff
            if response.status_code == 429:
                self.logger.warning(f"Received 429 Too Many Requests. Retrying with backoff...")
                time.sleep(2)  # Wait 2 seconds
                response = self.session.get(url, headers=self.headers, params=params, timeout=10)
            
            response.raise_for_status()
            self.logger.info(f"Request successful, status code: {response.status_code}")
            return response
        except requests.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            raise
            
    def _get_cover_image(self, link, manga_url: str = "") -> str:
        """Helper method to get a cover image from either the search results or the product page.
        
        Args:
            link: The BeautifulSoup link element from the search results.
            manga_url: The URL of the manga/product page.
            
        Returns:
            The cover image URL or an empty string if not found.
        """
        # If manga_url is empty, just try to get the image from the link
        if not manga_url:
            return self._extract_image_from_link(link)
            
        # Check if we've already cached this URL
        if manga_url in self.cover_cache:
            self.logger.info(f"Using cached cover image for {manga_url}")
            return self.cover_cache[manga_url]
        
        # Try method 1: Find image near the link in search results
        cover_url = ""
        parent = link.parent if link else None
        for _ in range(3):  # Look up to 3 levels up
            if parent:
                cover_elem = parent.select_one('img')
                if cover_elem and 'src' in cover_elem.attrs:
                    cover_url = cover_elem['src']
                    if cover_url.startswith('/'):
                        cover_url = urljoin(self.base_url, cover_url)
                    break
                parent = parent.parent
        
        # Try method 2: If no image found, make a request to the product page
        if not cover_url and manga_url:
            try:
                self.logger.info(f"Fetching cover image from product page: {manga_url}")
                product_response = self._make_request(manga_url)
                product_soup = BeautifulSoup(product_response.text, 'html.parser')
                
                # Try various selectors to find the cover image
                cover_selectors = [
                    '.product-image img', 
                    '.o_product-detail__image img',
                    'img.product-image',
                    '.book-image img', 
                    '.manga-cover img',
                    '.series-cover img',
                    'img[itemprop="image"]'
                ]
                
                for selector in cover_selectors:
                    img = product_soup.select_one(selector)
                    if img and 'src' in img.attrs:
                        cover_url = img['src']
                        if cover_url.startswith('/'):
                            cover_url = urljoin(self.base_url, cover_url)
                        break
                
                # Try meta tags if no image found yet
                if not cover_url:
                    meta = product_soup.select_one('meta[property="og:image"]')
                    if meta and 'content' in meta.attrs:
                        cover_url = meta['content']
                        if cover_url.startswith('/'):
                            cover_url = urljoin(self.base_url, cover_url)
            except Exception as e:
                self.logger.error(f"Error fetching cover image from product page: {e}")
        
        # Cache the result if we have a URL
        if manga_url and cover_url:
            self.cover_cache[manga_url] = cover_url
            self.logger.info(f"Cached cover image for {manga_url}")
            
            # Also try to cache by product ID for reuse across different methods
            product_id = manga_url.split('/')[-1] if manga_url else ""
            if product_id and product_id != manga_url:
                cache_key = f"{self.base_url}/product/{product_id}"
                self.cover_cache[cache_key] = cover_url
        
        return cover_url
        
    def _extract_image_from_link(self, link) -> str:
        """Extract image URL directly from a link element without making additional requests.
        
        Args:
            link: The BeautifulSoup link element from the search results.
            
        Returns:
            The cover image URL or an empty string if not found.
        """
        if not link:
            return ""
        
        cover_url = ""
        
        # Try to find image near the link
        parent = link.parent
        for _ in range(4):  # Look up to 4 levels up
            if parent:
                # Try direct img tag
                cover_elem = parent.select_one('img')
                if cover_elem and 'src' in cover_elem.attrs:
                    cover_url = cover_elem['src']
                    if cover_url.startswith('/'):
                        cover_url = urljoin(self.base_url, cover_url)
                    return cover_url
                    
                # Try data-src attribute which is common for lazy-loaded images
                cover_elem = parent.select_one('[data-src]')
                if cover_elem and 'data-src' in cover_elem.attrs:
                    cover_url = cover_elem['data-src']
                    if cover_url.startswith('/'):
                        cover_url = urljoin(self.base_url, cover_url)
                    return cover_url
                    
                # Move up one level
                parent = parent.parent
            else:
                break
                
        # Try to construct a cover URL based on product ID if available
        href = link.get('href', '')
        if href:
            parts = href.split('/')
            if len(parts) >= 2 and 'product' in parts:
                product_id = parts[-1]
                # Use a known pattern for Viz Media cover URLs
                predictive_url = f"https://dw9to29mmj727.cloudfront.net/products/{product_id}.jpg"
                return predictive_url
        
        return cover_url

    def search(self, query: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for manga on Viz Media.
        
        Args:
            query: The search query.
            page: The page number.
            
        Returns:
            A list of manga search results.
        """
        # For Viz Media, we'll use their internal search API
        search_url = f"{self.base_url}/search"
        params = {
            "search": query,
            "category": "manga",
            "page": page
        }
        
        try:
            self.logger.info(f"Searching for '{query}' on page {page}")
            response = self._make_request(search_url, params)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            # Viz Media's search page structure is different than expected
            # Look for links to manga titles
            manga_links = soup.select('a[href*="/manga-books/manga/"]')
            processed_urls = set()  # To avoid duplicates
            
            # Counter to limit product page requests
            product_page_requests = 0
            max_product_requests = 5  # Limit to avoid rate limiting
            
            for link in manga_links:
                try:
                    # Skip links without proper text or already processed
                    if not link.text.strip():
                        continue
                    
                    # Get manga URL
                    manga_url = link.get('href', "")
                    if not manga_url or manga_url in processed_urls:
                        continue
                    
                    processed_urls.add(manga_url)
                    
                    if manga_url.startswith('/'):
                        manga_url = urljoin(self.base_url, manga_url)
                    
                    # Extract manga ID and product ID
                    url_parts = manga_url.split('/')
                    if len(url_parts) >= 2:
                        product_id = url_parts[-1]
                        manga_id = url_parts[-2]
                    else:
                        product_id = ""
                        manga_id = ""
                    
                    # Get title (the link text)
                    title = link.text.strip()
                    
                    # Extract volume info from title
                    volume_match = re.search(r'Vol\.\s*(\d+)', title)
                    volume = volume_match.group(1) if volume_match else ""
                    
                    # Only fetch product pages for cover images if we haven't hit the limit
                    if product_page_requests < max_product_requests:
                        # Get cover image using the helper method
                        cover_url = self._get_cover_image(link, manga_url)
                        product_page_requests += 1
                    else:
                        # Skip product page request, just try to get image from search results
                        cover_url = self._get_cover_image(link, "")
                    
                    # Set author as unknown since it's not easily available in search results
                    author = "Unknown"
                    
                    # Set release date as empty since it's not easily available in search results
                    release_date = ""
                    
                    results.append({
                        "id": manga_id,
                        "product_id": product_id,
                        "title": title,
                        "volume": volume,
                        "cover_url": cover_url,
                        "author": author,
                        "release_date": release_date,
                        "url": manga_url,
                        "source": self.name
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing search result: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching manga on Viz Media: {e}")
            return []

    def get_manga_details(self, manga_id: str) -> Dict[str, Any]:
        """Get details for a manga on Viz Media.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            The manga details.
        """
        # Construct the manga detail URL based on the manga ID
        manga_url = f"{self.base_url}/manga/{manga_id}"
        
        try:
            response = self._make_request(manga_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title_elem = soup.select_one('h1.series-title')
            title = title_elem.text.strip() if title_elem else "Unknown"
            
            # Get cover image
            cover_elem = soup.select_one('.series-cover img')
            cover_url = cover_elem.get('src', "") if cover_elem else ""
            if cover_url and cover_url.startswith('/'):
                cover_url = urljoin(self.base_url, cover_url)
            
            # Get author
            author_elem = soup.select_one('.series-author')
            author = author_elem.text.strip() if author_elem else "Unknown"
            
            # Get description
            description_elem = soup.select_one('.series-description')
            description = description_elem.text.strip() if description_elem else ""
            
            # Get genres
            genres = []
            genre_elems = soup.select('.series-genre')
            for genre_elem in genre_elems:
                genres.append(genre_elem.text.strip())
            
            # Get publisher
            publisher_elem = soup.select_one('.series-publisher')
            publisher = publisher_elem.text.strip() if publisher_elem else "Viz Media"
            
            # Get status
            status_elem = soup.select_one('.series-status')
            status = status_elem.text.strip() if status_elem else "ONGOING"
            
            return {
                "id": manga_id,
                "title": title,
                "cover_url": cover_url,
                "author": author,
                "publisher": publisher,
                "description": description,
                "genres": genres,
                "status": status,
                "url": manga_url,
                "source": self.name
            }
        except Exception as e:
            self.logger.error(f"Error getting manga details on Viz Media: {e}")
            return {}

    def get_chapter_list(self, manga_id: str) -> List[Dict[str, Any]]:
        """Get the chapter list for a manga on Viz Media.
        
        Args:
            manga_id: The manga ID.
            
        Returns:
            A list of chapters.
        """
        # Viz Media typically doesn't provide chapter-by-chapter listings on their website
        # Instead, they list volumes. We'll use the manga detail page to get volume info
        manga_url = f"{self.base_url}/manga/{manga_id}"
        
        try:
            response = self._make_request(manga_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            chapters = []
            volume_items = soup.select('.volume-item')
            
            for item in volume_items:
                try:
                    volume_elem = item.select_one('.volume-number')
                    volume_number = volume_elem.text.strip() if volume_elem else "0"
                    
                    title_elem = item.select_one('.volume-title')
                    title = title_elem.text.strip() if title_elem else f"Volume {volume_number}"
                    
                    date_elem = item.select_one('.volume-release-date')
                    date = date_elem.text.strip() if date_elem else ""
                    
                    url_elem = item.select_one('a')
                    url = url_elem.get('href', "") if url_elem else ""
                    if url.startswith('/'):
                        url = urljoin(self.base_url, url)
                    
                    # Extract volume ID from URL
                    volume_id = url.split('/')[-1] if url else ""
                    
                    # For Viz, we'll represent volumes as chapters
                    chapters.append({
                        "id": volume_id,
                        "title": title,
                        "number": volume_number,
                        "date": date,
                        "url": url,
                        "manga_id": manga_id
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing volume item: {e}")
            
            return chapters
        except Exception as e:
            self.logger.error(f"Error getting chapter list on Viz Media: {e}")
            return []

    def get_chapter_images(self, manga_id: str, chapter_id: str) -> List[str]:
        """Get the images for a chapter on Viz Media.
        
        Args:
            manga_id: The manga ID.
            chapter_id: The chapter ID.
            
        Returns:
            A list of image URLs.
        """
        # Viz Media doesn't provide chapter images publicly
        self.logger.warning("Viz Media doesn't provide chapter images publicly")
        return []

    def get_latest_releases(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get the latest manga releases on Viz Media's calendar.
        
        Args:
            page: The page number.
            
        Returns:
            A list of latest releases.
        """
        # For Viz Media, we'll scrape their calendar page
        # The page parameter doesn't apply since we're getting the current month
        try:
            # Get the current month's calendar
            now = datetime.now()
            year = now.year
            month = now.month
            calendar_url = f"{self.calendar_url}/{year}/{month:02d}"
            
            response = self._make_request(calendar_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            # Look for manga items in the calendar
            manga_links = soup.select('a[href*="/manga-books/manga/"]')
            
            for link in manga_links:
                try:
                    # Skip links without proper text
                    if not link.text.strip():
                        continue
                        
                    # Get title (the link text)
                    title = link.text.strip()
                    
                    # Get URL
                    manga_url = link.get('href', "")
                    if manga_url.startswith('/'):
                        manga_url = urljoin(self.base_url, manga_url)
                    
                    # Extract manga ID from URL
                    manga_id = manga_url.split('/')[-2] if manga_url else ""
                    
                    # Extract volume info from title
                    volume_match = re.search(r'Vol\.\s*(\d+)', title)
                    volume = volume_match.group(1) if volume_match else ""
                    
                    # Get release date (use current month's date)
                    release_date = f"{year}-{month:02d}-01"  # Default to 1st of month
                    
                    # Get cover image using the helper method
                    cover_url = self._get_cover_image(link, manga_url)
                    
                    results.append({
                        "manga_id": manga_id,
                        "manga_title": title,
                        "cover_url": cover_url,
                        "volume": volume,
                        "release_date": release_date,
                        "url": manga_url,
                        "source": self.name
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing latest release: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting latest releases from Viz Media: {e}")
            return []

    def get_calendar_releases(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get the manga releases for a specific month from Viz Media's calendar.
        
        Args:
            year: The year.
            month: The month (1-12).
            
        Returns:
            A list of releases for the specified month.
        """
        try:
            # Format the calendar URL
            calendar_url = f"{self.calendar_url}/{year}/{month:02d}"
            
            response = self._make_request(calendar_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            # Look for manga items in the calendar
            manga_links = soup.select('a[href*="/manga-books/manga/"]')
            
            for link in manga_links:
                try:
                    # Skip links without proper text
                    if not link.text.strip():
                        continue
                        
                    # Get title (the link text)
                    title = link.text.strip()
                    
                    # Get URL
                    manga_url = link.get('href', "")
                    if manga_url.startswith('/'):
                        manga_url = urljoin(self.base_url, manga_url)
                    
                    # Extract manga ID from URL
                    manga_id = manga_url.split('/')[-2] if manga_url else ""
                    product_id = manga_url.split('/')[-1] if manga_url else ""
                    
                    # Extract volume info from title
                    volume_match = re.search(r'Vol\.\s*(\d+)', title)
                    volume = volume_match.group(1) if volume_match else ""
                    
                    # Get release date (use current month's date)
                    release_date = f"{year}-{month:02d}-01"  # Default to 1st of month
                    
                    # Try to find a more specific release date near this item
                    # This is challenging without knowing the exact HTML structure
                    
                    # Get cover image using the helper method
                    cover_url = self._get_cover_image(link, manga_url)
                    
                    # Try to extract format (paperback, hardcover, digital)
                    format_match = re.search(r'/(paperback|hardcover|digital)$', manga_url)
                    format_type = format_match.group(1) if format_match else "unknown"
                    
                    results.append({
                        "manga_id": manga_id,
                        "product_id": product_id,
                        "manga_title": title,
                        "cover_url": cover_url,
                        "volume": volume,
                        "release_date": release_date,
                        "format": format_type,
                        "url": manga_url,
                        "source": self.name
                    })
                except Exception as e:
                    self.logger.error(f"Error parsing calendar release: {e}")
            
            return results
        except Exception as e:
            self.logger.error(f"Error getting calendar releases from Viz Media: {e}")
            return []

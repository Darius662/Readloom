#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manga-specific service implementation.
Adapts existing manga handling into a service that implements the common interface.
"""

from typing import Dict, List, Any, Optional, Union

from backend.base.logging import LOGGER
from backend.features.content_service_base import ContentServiceBase
from backend.features.content_service_factory import ContentType
from backend.internals.db import execute_query


class MangaService(ContentServiceBase):
    """Service for handling manga-specific operations."""
    
    def __init__(self):
        """Initialize the manga service."""
        super().__init__()
        self.logger = LOGGER
    
    def search(self, query: str, search_type: str = "title", provider: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
        """Search for manga.
        
        Args:
            query: The search query.
            search_type: The type of search (title or author).
            provider: The provider to search with (optional).
            page: The page number.
            
        Returns:
            A dictionary containing search results.
        """
        from backend.features.metadata_service.facade import search_manga
        
        try:
            # Use the existing search function
            # Note: Most manga providers may not support author search
            results = search_manga(query, provider, page, search_type)
            
            # Add manga-specific processing here if needed
            if "results" in results and not provider:
                # Filter results to only include manga providers if no specific provider
                manga_providers = ["MangaDex", "AniList", "MyAnimeList", "Comick", "MangaUpdates"]
                filtered_results = {}
                
                for k, v in results["results"].items():
                    if k in manga_providers or any(p in k for p in manga_providers):
                        filtered_results[k] = v
                
                # If we have manga-specific results, use those, otherwise keep all results
                if filtered_results:
                    results["results"] = filtered_results
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching for manga: {e}")
            return {
                "query": query,
                "search_type": search_type,
                "page": page,
                "results": {},
                "error": str(e)
            }
    
    def get_details(self, content_id: str, provider: str) -> Dict[str, Any]:
        """Get manga details.
        
        Args:
            content_id: The manga ID.
            provider: The provider name.
            
        Returns:
            A dictionary containing manga details.
        """
        from backend.features.metadata_service.facade import get_manga_details
        
        try:
            # Use the existing details function
            details = get_manga_details(content_id, provider)
            return details
        except Exception as e:
            self.logger.error(f"Error getting manga details: {e}")
            return {"error": str(e)}
    
    def import_to_collection(self, content_id: str, provider: str, 
                            collection_id: Optional[int] = None,
                            content_type: Optional[str] = None,
                            root_folder_id: Optional[int] = None) -> Dict[str, Any]:
        """Import a manga to the collection.
        
        Args:
            content_id: The manga ID.
            provider: The provider name.
            collection_id: The collection ID (optional).
            content_type: The content type (optional).
            root_folder_id: The root folder ID (optional).
            
        Returns:
            A dictionary containing the result.
        """
        from backend.features.metadata_service.facade import import_manga_to_collection
        
        try:
            # Use the existing import function
            result = import_manga_to_collection(
                content_id,
                provider,
                collection_id=collection_id,
                content_type=content_type,
                root_folder_id=root_folder_id
            )
            
            # If import was successful, ensure it's marked as not a book
            if result.get("success") and "series_id" in result:
                series_id = result["series_id"]
                
                # Mark as manga content type
                execute_query("""
                    UPDATE series SET content_type = 'MANGA' WHERE id = ?
                """, (series_id,), commit=True)
            
            return result
        except Exception as e:
            self.logger.error(f"Error importing manga to collection: {e}")
            return {"success": False, "message": str(e)}
    
    def create_folder_structure(self, content_id: Union[int, str], title: str, 
                               content_type: str, collection_id: Optional[int] = None,
                               root_folder_id: Optional[int] = None,
                               author: Optional[str] = None) -> str:
        """Create series-based folder structure.
        
        Args:
            content_id: The manga ID.
            title: The manga title.
            content_type: The content type.
            collection_id: The collection ID (optional).
            root_folder_id: The root folder ID (optional).
            author: The author name (optional, not used for manga).
            
        Returns:
            The path to the created folder.
        """
        from backend.base.helpers import create_series_folder_structure
        
        try:
            # Use the existing folder creation function
            folder_path = create_series_folder_structure(
                content_id,
                title,
                content_type,
                collection_id,
                root_folder_id
            )
            
            return folder_path
        except Exception as e:
            self.logger.error(f"Error creating folder structure: {e}")
            return ""
    
    def get_series_by_publisher(self, publisher: str) -> List[Dict[str, Any]]:
        """Get manga series by publisher.
        
        Args:
            publisher: The publisher name.
            
        Returns:
            A list of manga series by the publisher.
        """
        try:
            series = execute_query("""
                SELECT * FROM series 
                WHERE publisher = ? AND UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC')
                ORDER BY title
            """, (publisher,))
            
            return series
        except Exception as e:
            self.logger.error(f"Error getting series by publisher: {e}")
            return []
    
    def get_all_publishers(self) -> List[Dict[str, Any]]:
        """Get all manga publishers.
        
        Returns:
            A list of all publishers.
        """
        try:
            publishers = execute_query("""
                SELECT publisher, COUNT(*) as series_count
                FROM series
                WHERE UPPER(content_type) IN ('MANGA', 'MANHWA', 'MANHUA', 'COMIC') 
                AND publisher IS NOT NULL AND publisher != ''
                GROUP BY publisher
                ORDER BY publisher
            """)
            
            return publishers
        except Exception as e:
            self.logger.error(f"Error getting all publishers: {e}")
            return []

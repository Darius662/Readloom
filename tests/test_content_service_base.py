#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the content service base class.
"""

import unittest
from unittest.mock import patch, MagicMock

from backend.features.content_service_base import ContentServiceBase


class ConcreteContentService(ContentServiceBase):
    """Concrete implementation of ContentServiceBase for testing."""
    
    def search(self, query, search_type="title", provider=None, page=1):
        """Implement abstract method."""
        return {"query": query, "implemented": True}
    
    def get_details(self, content_id, provider):
        """Implement abstract method."""
        return {"content_id": content_id, "implemented": True}
    
    def import_to_collection(self, content_id, provider, collection_id=None, content_type=None, root_folder_id=None):
        """Implement abstract method."""
        return {"success": True, "implemented": True}
    
    def create_folder_structure(self, content_id, title, content_type, collection_id=None, root_folder_id=None, author=None):
        """Implement abstract method."""
        return f"/path/to/{title}"


class TestContentServiceBase(unittest.TestCase):
    """Test the ContentServiceBase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = ConcreteContentService()
    
    def test_search(self):
        """Test the search method."""
        result = self.service.search("test query")
        self.assertEqual(result["query"], "test query")
        self.assertTrue(result["implemented"])
    
    def test_get_details(self):
        """Test the get_details method."""
        result = self.service.get_details("123", "test_provider")
        self.assertEqual(result["content_id"], "123")
        self.assertTrue(result["implemented"])
    
    def test_import_to_collection(self):
        """Test the import_to_collection method."""
        result = self.service.import_to_collection("123", "test_provider")
        self.assertTrue(result["success"])
        self.assertTrue(result["implemented"])
    
    def test_create_folder_structure(self):
        """Test the create_folder_structure method."""
        result = self.service.create_folder_structure(1, "Test Title", "BOOK")
        self.assertEqual(result, "/path/to/Test Title")
    
    @patch("backend.features.content_service_factory.ContentType")
    def test_get_content_type_group_book(self, mock_content_type):
        """Test getting the content type group for books."""
        mock_content_type.is_book_type.return_value = True
        mock_content_type.is_manga_type.return_value = False
        
        result = self.service.get_content_type_group("BOOK")
        self.assertEqual(result, "book")
        mock_content_type.is_book_type.assert_called_once_with("BOOK")
    
    @patch("backend.features.content_service_factory.ContentType")
    def test_get_content_type_group_manga(self, mock_content_type):
        """Test getting the content type group for manga."""
        mock_content_type.is_book_type.return_value = False
        mock_content_type.is_manga_type.return_value = True
        
        result = self.service.get_content_type_group("MANGA")
        self.assertEqual(result, "manga")
        mock_content_type.is_book_type.assert_called_once_with("MANGA")
        mock_content_type.is_manga_type.assert_called_once_with("MANGA")
    
    @patch("backend.features.content_service_factory.ContentType")
    def test_get_content_type_group_other(self, mock_content_type):
        """Test getting the content type group for other types."""
        mock_content_type.is_book_type.return_value = False
        mock_content_type.is_manga_type.return_value = False
        
        result = self.service.get_content_type_group("OTHER")
        self.assertEqual(result, "other")
        mock_content_type.is_book_type.assert_called_once_with("OTHER")
        mock_content_type.is_manga_type.assert_called_once_with("OTHER")


if __name__ == "__main__":
    unittest.main()

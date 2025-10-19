#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for the content service factory.
"""

import unittest
from unittest.mock import patch, MagicMock

from backend.features.content_service_factory import ContentType, get_content_service, get_service_for_content


class TestContentType(unittest.TestCase):
    """Test the ContentType enum."""
    
    def test_from_string(self):
        """Test converting strings to ContentType."""
        self.assertEqual(ContentType.from_string("BOOK"), ContentType.BOOK)
        self.assertEqual(ContentType.from_string("book"), ContentType.BOOK)
        self.assertEqual(ContentType.from_string("MANGA"), ContentType.MANGA)
        self.assertEqual(ContentType.from_string("manga"), ContentType.MANGA)
        self.assertEqual(ContentType.from_string("unknown"), ContentType.OTHER)
    
    def test_is_book_type(self):
        """Test checking if a content type is a book type."""
        self.assertTrue(ContentType.is_book_type(ContentType.BOOK))
        self.assertTrue(ContentType.is_book_type("BOOK"))
        self.assertTrue(ContentType.is_book_type("book"))
        self.assertTrue(ContentType.is_book_type(ContentType.NOVEL))
        self.assertTrue(ContentType.is_book_type("NOVEL"))
        self.assertFalse(ContentType.is_book_type(ContentType.MANGA))
        self.assertFalse(ContentType.is_book_type("MANGA"))
    
    def test_is_manga_type(self):
        """Test checking if a content type is a manga type."""
        self.assertTrue(ContentType.is_manga_type(ContentType.MANGA))
        self.assertTrue(ContentType.is_manga_type("MANGA"))
        self.assertTrue(ContentType.is_manga_type("manga"))
        self.assertTrue(ContentType.is_manga_type(ContentType.COMIC))
        self.assertTrue(ContentType.is_manga_type("COMIC"))
        self.assertFalse(ContentType.is_manga_type(ContentType.BOOK))
        self.assertFalse(ContentType.is_manga_type("BOOK"))


class TestGetContentService(unittest.TestCase):
    """Test the get_content_service function."""
    
    @patch("backend.features.content_service_factory.BookService")
    def test_get_book_service(self, mock_book_service):
        """Test getting a book service."""
        mock_instance = MagicMock()
        mock_book_service.return_value = mock_instance
        
        service = get_content_service(ContentType.BOOK)
        self.assertEqual(service, mock_instance)
        mock_book_service.assert_called_once()
        
        service = get_content_service("BOOK")
        self.assertEqual(service, mock_instance)
        self.assertEqual(mock_book_service.call_count, 2)
    
    @patch("backend.features.content_service_factory.MangaService")
    def test_get_manga_service(self, mock_manga_service):
        """Test getting a manga service."""
        mock_instance = MagicMock()
        mock_manga_service.return_value = mock_instance
        
        service = get_content_service(ContentType.MANGA)
        self.assertEqual(service, mock_instance)
        mock_manga_service.assert_called_once()
        
        service = get_content_service("MANGA")
        self.assertEqual(service, mock_instance)
        self.assertEqual(mock_manga_service.call_count, 2)
    
    @patch("backend.features.content_service_factory.BookService", side_effect=ImportError)
    @patch("backend.features.content_service_factory.ContentServiceBase")
    def test_fallback_when_service_not_available(self, mock_base_service, mock_book_service):
        """Test fallback to base service when specific service is not available."""
        mock_instance = MagicMock()
        mock_base_service.return_value = mock_instance
        
        service = get_content_service(ContentType.BOOK)
        self.assertEqual(service, mock_instance)
        mock_book_service.assert_called_once()
        mock_base_service.assert_called_once()


class TestGetServiceForContent(unittest.TestCase):
    """Test the get_service_for_content function."""
    
    @patch("backend.features.content_service_factory.execute_query")
    @patch("backend.features.content_service_factory.get_content_service")
    def test_get_service_with_content_type(self, mock_get_service, mock_execute_query):
        """Test getting a service with a provided content type."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        service = get_service_for_content(1, "BOOK")
        self.assertEqual(service, mock_service)
        mock_get_service.assert_called_once_with("BOOK")
        mock_execute_query.assert_not_called()
    
    @patch("backend.features.content_service_factory.execute_query")
    @patch("backend.features.content_service_factory.get_content_service")
    def test_get_service_without_content_type(self, mock_get_service, mock_execute_query):
        """Test getting a service without a provided content type."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_execute_query.return_value = [{"content_type": "MANGA"}]
        
        service = get_service_for_content(1)
        self.assertEqual(service, mock_service)
        mock_execute_query.assert_called_once()
        mock_get_service.assert_called_once_with("MANGA")
    
    @patch("backend.features.content_service_factory.execute_query")
    @patch("backend.features.content_service_factory.get_content_service")
    def test_get_service_with_unknown_content(self, mock_get_service, mock_execute_query):
        """Test getting a service for unknown content."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_execute_query.return_value = []
        
        service = get_service_for_content(999)
        self.assertEqual(service, mock_service)
        mock_execute_query.assert_called_once()
        mock_get_service.assert_called_once_with("MANGA")


if __name__ == "__main__":
    unittest.main()

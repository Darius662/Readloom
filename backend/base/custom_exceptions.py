#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class MangaArrException(Exception):
    """Base exception for MangaArr."""
    pass


class InvalidSettingValue(MangaArrException):
    """Exception raised when a setting value is invalid."""
    pass


class DatabaseError(MangaArrException):
    """Exception raised when there is a database error."""
    pass


class MetadataError(MangaArrException):
    """Exception raised when there is a metadata error."""
    pass


class APIError(MangaArrException):
    """Exception raised when there is an API error."""
    pass


class IntegrationError(MangaArrException):
    """Exception raised when there is an integration error."""
    pass

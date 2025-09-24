#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class ReadloomException(Exception):
    """Base exception for Readloom."""
    pass


class InvalidSettingValue(ReadloomException):
    """Exception raised when a setting value is invalid."""
    pass


class DatabaseError(ReadloomException):
    """Exception raised when there is a database error."""
    pass


class InvalidCollectionError(ReadloomException):
    """Exception raised for invalid collection operations."""
    pass


class MetadataError(ReadloomException):
    """Exception raised when there is a metadata error."""
    pass


class APIError(ReadloomException):
    """Exception raised when there is an API error."""
    pass


class IntegrationError(ReadloomException):
    """Exception raised when there is an integration error."""
    pass

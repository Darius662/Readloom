#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any
import requests


def make_graphql_request(session: requests.Session, base_url: str, headers: Dict[str, str], query: str, variables: Dict[str, Any], logger) -> Dict[str, Any]:
    """Make a GraphQL request using a provided session and parameters.

    Args:
        session: The requests session to use.
        base_url: The AniList GraphQL endpoint base URL.
        headers: HTTP headers to include.
        query: The GraphQL query string.
        variables: Variables for the GraphQL query.
        logger: Logger for error reporting.

    Returns:
        Parsed JSON dict or empty dict on error.
    """
    try:
        payload = {
            "query": query,
            "variables": variables,
        }
        response = session.post(base_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error making request to AniList API: {e}")
        return {}

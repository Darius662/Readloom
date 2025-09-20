#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to check manga releases from AniList for the current month.
"""

import requests
import json
from datetime import datetime

def get_this_month_releases():
    """
    Query AniList API for manga releases in the current month.
    """
    # Get current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # AniList GraphQL endpoint
    url = "https://graphql.anilist.co"
    
    # Define the GraphQL query for getting current manga releases
    # Simplified query with no variables
    query = """
    query {
        Page(perPage: 50) {
            media(type: MANGA, 
                  status: RELEASING,
                  sort: POPULARITY_DESC) {
                id
                title {
                    romaji
                    english
                    native
                }
                description
                coverImage {
                    large
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
                genres
                staff(perPage: 10) {
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
    
    # Make the request
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "MangaArr/1.0.0"
    }
    
    payload = {
        "query": query
    }
    
    # Debug - print the actual request
    print(f"Checking AniList for manga releases in {current_year}-{current_month:02d}...")
    print(f"\nQuery:\n{query}\n")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        
        # Debug - print the response
        print("Response:")
        print(json.dumps(response_json, indent=2))
        
        # Check for errors in the response
        if "errors" in response_json:
            print(f"Error from AniList: {response_json['errors']}")
            return []
            
        # If no errors, raise for other HTTP issues
        response.raise_for_status()
        data = response_json
        
        if "data" in data and "Page" in data["data"] and "media" in data["data"]["Page"]:
            releases = data["data"]["Page"]["media"]
            
            if not releases:
                print("No manga releases found for this month.")
                return []
            
            formatted_releases = []
            
            for item in releases:
                # Extract authors/staff information
                authors = []
                if "staff" in item and "edges" in item["staff"]:
                    for edge in item["staff"]["edges"]:
                        if "Story" in edge["role"] or "Art" in edge["role"]:
                            authors.append(edge["node"]["name"]["full"])
                
                # Format release date
                release_date = ""
                if "startDate" in item and all([item["startDate"].get("year"), 
                                               item["startDate"].get("month"), 
                                               item["startDate"].get("day")]):
                    release_date = f"{item['startDate']['year']}-{item['startDate']['month']:02d}-{item['startDate']['day']:02d}"
                
                formatted_release = {
                    "id": item["id"],
                    "title": item["title"].get("romaji", item["title"].get("english", "")),
                    "cover_url": item.get("coverImage", {}).get("large", ""),
                    "release_date": release_date,
                    "status": item.get("status", ""),
                    "volumes": item.get("volumes", 0),
                    "chapters": item.get("chapters", 0),
                    "genres": item.get("genres", []),
                    "authors": ", ".join(authors) if authors else "Unknown",
                    "score": item.get("averageScore", 0)
                }
                
                formatted_releases.append(formatted_release)
            
            return formatted_releases
        else:
            print("No data found in response.")
            return []
    
    except Exception as e:
        print(f"Error querying AniList API: {e}")
        return []

def filter_current_month_releases(releases):
    """
    Filter releases to only include those from the current month.
    """
    if not releases:
        return []
    
    # Get current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Filter releases
    current_month_releases = []
    
    for release in releases:
        # Check if release date exists
        if not release['release_date']:
            continue
            
        try:
            # Parse the release date
            release_date = datetime.fromisoformat(release['release_date'])
            
            # Check if it matches current month and year or is in the future this month
            if release_date.month == current_month:
                if release_date.year == current_year or release_date.year > current_year:
                    current_month_releases.append(release)
        except ValueError:
            # Skip releases with invalid dates
            continue
    
    return current_month_releases

def find_upcoming_releases(releases):
    """
    Find releases that are upcoming (future releases).
    """
    if not releases:
        return []
    
    # Get current date
    now = datetime.now()
    
    # Filter releases
    upcoming_releases = []
    
    for release in releases:
        # Check if release date exists
        if not release['release_date']:
            continue
            
        try:
            # Parse the release date
            release_date = datetime.fromisoformat(release['release_date'])
            
            # Check if it's in the future
            if release_date > now:
                upcoming_releases.append(release)
        except ValueError:
            # Skip releases with invalid dates
            continue
    
    return upcoming_releases

def display_releases(releases):
    """
    Display formatted release information.
    """
    if not releases:
        print("No releases to display.")
        return
    
    # Get month name for better display
    now = datetime.now()
    month_name = now.strftime("%B")
    
    print(f"\nFound {len(releases)} manga releases for {month_name} {now.year}:\n")
    print("-" * 80)
    
    # Sort by release date if available
    sorted_releases = sorted(releases, 
                             key=lambda x: x['release_date'] if x['release_date'] else '9999-99-99')
    
    for i, release in enumerate(sorted_releases, 1):
        print(f"{i}. {release['title']}")
        print(f"   Release Date: {release['release_date'] if release['release_date'] else 'Sometime in ' + month_name}")
        print(f"   Authors: {release['authors']}")
        print(f"   Status: {release['status']}")
        if release['volumes']:
            print(f"   Volumes: {release['volumes']}")
        print(f"   Genres: {', '.join(release['genres'])}")
        if release['score']:
            print(f"   Score: {release['score'] / 10:.1f}")
        print("-" * 80)

if __name__ == "__main__":
    # Get all currently releasing manga
    all_releases = get_this_month_releases()
    
    # Filter for this month's releases
    this_month_releases = filter_current_month_releases(all_releases)
    
    # Find upcoming releases
    upcoming_releases = find_upcoming_releases(all_releases)
    
    # Display the releases by category
    if this_month_releases:
        print(f"\n===== MANGA RELEASES FOR {datetime.now().strftime('%B %Y').upper()} =====")
        display_releases(this_month_releases)
    else:
        print(f"\nNo manga releases found specifically for {datetime.now().strftime('%B %Y')}.")
    
    # Show upcoming releases
    if upcoming_releases:
        print(f"\n===== UPCOMING MANGA RELEASES =====")
        display_releases(upcoming_releases[:10])  # Show only first 10 to avoid overwhelming
        
        if len(upcoming_releases) > 10:
            print(f"\n... and {len(upcoming_releases) - 10} more upcoming releases")
    else:
        print("\nNo upcoming manga releases found in the data.")
        
    # Summary
    print(f"\nTotal manga in the database: {len(all_releases)}")
    print(f"Releases this month: {len(this_month_releases)}")
    print(f"Upcoming releases: {len(upcoming_releases)}")
    
    # Display top 10 highest rated series
    top_series = sorted(all_releases, key=lambda x: x['score'] or 0, reverse=True)[:10]
    if top_series:
        print(f"\n===== TOP 10 HIGHEST RATED MANGA =====")
        for i, manga in enumerate(top_series, 1):
            print(f"{i}. {manga['title']} - Score: {manga['score'] / 10:.1f}")
            print(f"   Genres: {', '.join(manga['genres'])}")
            print(f"   Status: {manga['status']}")
            print()

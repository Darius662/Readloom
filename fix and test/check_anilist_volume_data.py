#!/usr/bin/env python3
import requests
import json

def fetch_manga_details(manga_id):
    """Fetch manga details directly from AniList API."""
    url = "https://graphql.anilist.co"
    
    # GraphQL query for manga details
    query = """
    query ($id: Int) {
        Media(id: $id, type: MANGA) {
            id
            title {
                romaji
                english
                native
            }
            description
            volumes
            chapters
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
    """
    
    # Variables for the query
    variables = {
        "id": manga_id
    }
    
    # Make the request
    response = requests.post(
        url, 
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    
    # Process response
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("Media", {})
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Check known series with expected volumes
series_to_check = [
    (86952, "Kumo desu ga, Nani ka?"),  # The series in question
    (30002, "Naruto"),  # A series we know has volumes
    (21, "One Piece"),  # Another popular series
    (31499, "Berserk")  # Another series with known volumes
]

print("Checking manga volume data from AniList API directly:\n")

for manga_id, title in series_to_check:
    print(f"Series: {title} (ID: {manga_id})")
    
    details = fetch_manga_details(manga_id)
    if details:
        volumes = details.get("volumes")
        chapters = details.get("chapters")
        print(f"  Volumes: {volumes}")
        print(f"  Chapters: {chapters}")
        print(f"  Title: {details.get('title', {}).get('romaji')}")
        
        # Get authors
        authors = []
        if "staff" in details and "edges" in details["staff"]:
            for edge in details["staff"]["edges"]:
                if "Story" in edge["role"] or "Art" in edge["role"]:
                    authors.append(edge["node"]["name"]["full"])
        
        print(f"  Authors: {', '.join(authors) if authors else 'Unknown'}")
        print()
    else:
        print("  Failed to fetch data\n")

# Now check Kumo desu ga with a manual search first
print("Searching for 'Kumo desu ga':")
search_query = """
query ($search: String) {
    Page {
        media(search: $search, type: MANGA) {
            id
            title {
                romaji
                english
            }
            volumes
            chapters
        }
    }
}
"""

search_variables = {
    "search": "Kumo desu ga"
}

response = requests.post(
    "https://graphql.anilist.co", 
    json={"query": search_query, "variables": search_variables},
    headers={"Content-Type": "application/json", "Accept": "application/json"}
)

if response.status_code == 200:
    results = response.json()
    if "data" in results and "Page" in results["data"] and "media" in results["data"]["Page"]:
        for item in results["data"]["Page"]["media"]:
            print(f"  ID: {item['id']}")
            print(f"  Title: {item['title']['romaji']}")
            print(f"  Volumes: {item.get('volumes')}")
            print(f"  Chapters: {item.get('chapters')}")
            print()
else:
    print(f"Search failed: {response.status_code}")
    print(response.text)

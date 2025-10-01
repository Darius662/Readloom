#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants for MangaInfo provider.
"""

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
]

# Base URLs for different manga sites
MANGAPARK_URL = "https://mangapark.net"
MANGADEX_URL = "https://api.mangadex.org"
MANGAFIRE_URL = "https://mangafire.to"

# Static database of popular manga for fallback
# Format: "search_key": {"chapters": X, "volumes": Y, "aliases": ["alt1", "alt2"], "status": "ONGOING/COMPLETED"}
# Note: For ongoing manga, this data may become outdated. The smart caching system will update it.
POPULAR_MANGA_DATA = {
    "one piece": {"chapters": 1130, "volumes": 115, "status": "ONGOING"},
    "naruto": {"chapters": 700, "volumes": 72},
    "bleach": {"chapters": 686, "volumes": 74},
    "dragon ball": {"chapters": 519, "volumes": 42},
    "jujutsu kaisen": {"chapters": 257, "volumes": 26},
    "demon slayer": {"chapters": 205, "volumes": 23, "aliases": ["kimetsu no yaiba"]},
    "attack on titan": {"chapters": 139, "volumes": 34, "aliases": ["shingeki no kyojin"]},
    "my hero academia": {"chapters": 430, "volumes": 40, "aliases": ["boku no hero academia"]},
    "hunter x hunter": {"chapters": 400, "volumes": 37},
    "tokyo ghoul": {"chapters": 144, "volumes": 14},
    "one punch man": {"chapters": 200, "volumes": 29, "aliases": ["onepunch-man", "onepunch man"]},
    "black clover": {"chapters": 368, "volumes": 36},
    "fairy tail": {"chapters": 545, "volumes": 63},
    "haikyu": {"chapters": 402, "volumes": 45, "aliases": ["haikyuu"]},
    "kingdom": {"chapters": 770, "volumes": 70},
    "vagabond": {"chapters": 327, "volumes": 37},
    "vinland saga": {"chapters": 208, "volumes": 26, "aliases": ["vinland saga"]},
    "berserk": {"chapters": 375, "volumes": 41},
    "slam dunk": {"chapters": 276, "volumes": 31},
    "fullmetal alchemist": {"chapters": 116, "volumes": 27, "aliases": ["hagane no renkinjutsushi"]},
    "death note": {"chapters": 108, "volumes": 12},
    "dr stone": {"chapters": 232, "volumes": 26, "aliases": ["dr. stone"]},
    "the promised neverland": {"chapters": 181, "volumes": 20, "aliases": ["yakusoku no neverland"]},
    "spy x family": {"chapters": 100, "volumes": 12, "aliases": ["spy family"]},
    "chainsaw man": {"chapters": 150, "volumes": 15},
    "shangri-la frontier": {"chapters": 100, "volumes": 17, "aliases": ["shangri-la frontier kusoge hunter"]},
    "dandadan": {"chapters": 211, "volumes": 24}
}

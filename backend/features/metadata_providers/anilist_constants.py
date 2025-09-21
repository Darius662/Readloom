#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# Popular manga patterns for better chapter counts
POPULAR_MANGA_PATTERNS = [
    re.compile(r'one\s*piece', re.IGNORECASE),
    re.compile(r'naruto', re.IGNORECASE),
    re.compile(r'bleach', re.IGNORECASE),
    re.compile(r'dragon\s*ball', re.IGNORECASE),
    re.compile(r'jujutsu\s*kaisen', re.IGNORECASE),
    re.compile(r'kimetsu\s*no\s*yaiba|demon\s*slayer', re.IGNORECASE),
    re.compile(r'attack\s*on\s*titan|shingeki\s*no\s*kyojin', re.IGNORECASE),
    re.compile(r'my\s*hero\s*academia|boku\s*no\s*hero', re.IGNORECASE),
    re.compile(r'hunter\s*x\s*hunter', re.IGNORECASE),
    re.compile(r'tokyo\s*ghoul', re.IGNORECASE),
]

# Known volume counts where API might be incorrect
KNOWN_VOLUMES = {
    "86952": 15,   # Kumo desu ga, Nani ka?
    "30002": 72,   # Naruto
    "31499": 41,   # Berserk
    "97720": 23,   # Kaguya-sama wa Kokurasetai
    "31478": 14,   # Monster
    "30013": 27,   # One Punch Man (ongoing)
    "31251": 13,   # Made in Abyss (ongoing)
}

import json
import random
import os


def load_countries(filepath="countries_data.json"):
    """Load countries data from JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    with open(full_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["countries"]


def get_random_country(countries, exclude_names=None):
    """Get a random country, excluding already-used ones."""
    if exclude_names is None:
        exclude_names = []
    available = [c for c in countries if c["name"] not in exclude_names]
    if not available:
        available = countries
        exclude_names.clear()
    return random.choice(available)


def get_countries_by_continent(countries, continent):
    """Filter countries by continent."""
    return [c for c in countries if c["continent"] == continent]


def get_all_continents(countries):
    """Get list of unique continents."""
    return sorted(set(c["continent"] for c in countries))

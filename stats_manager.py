import json
import os
from datetime import datetime


def create_default_stats(player_name="Player"):
    """Create default stats dictionary for a player."""
    return {
        "name": player_name,
        "total_questions": 0,
        "correct": 0,
        "wrong_guesses": 0,
        "give_ups": 0,
        "success_rate": 0.0,
        "current_streak": 0,
        "best_streak": 0,
        "stars": 0,
    }


def update_stats_correct(stats):
    """Update stats after a correct answer."""
    stats["total_questions"] += 1
    stats["correct"] += 1
    stats["current_streak"] += 1
    stats["stars"] += 1
    if stats["current_streak"] > stats["best_streak"]:
        stats["best_streak"] = stats["current_streak"]
    # Bonus stars for streak milestones
    if stats["current_streak"] % 5 == 0:
        stats["stars"] += 2
    _update_rate(stats)
    return stats


def update_stats_wrong(stats):
    """Record one wrong guess (does not end the question)."""
    stats["wrong_guesses"] += 1
    return stats


def update_stats_giveup(stats):
    """Update stats after giving up on a question."""
    stats["total_questions"] += 1
    stats["give_ups"] += 1
    stats["current_streak"] = 0
    _update_rate(stats)
    return stats


def _update_rate(stats):
    if stats["total_questions"] > 0:
        stats["success_rate"] = round(
            stats["correct"] / stats["total_questions"] * 100, 1
        )


def save_progress(stats_data, filepath="progress.json"):
    """Save progress to JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)

    existing = {}
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    timestamp = datetime.now().isoformat()
    if isinstance(stats_data, dict) and "name" in stats_data:
        existing[stats_data["name"]] = {**stats_data, "last_played": timestamp}
    elif isinstance(stats_data, dict):
        for name, stats in stats_data.items():
            existing[name] = {**stats, "last_played": timestamp}

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


def load_progress(filepath="progress.json"):
    """Load saved progress."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_leaderboard(multi_stats, mode="most_correct"):
    """Get sorted leaderboard based on game mode."""
    players = list(multi_stats.values())
    if mode == "longest_streak":
        players.sort(key=lambda p: p["best_streak"], reverse=True)
    else:
        players.sort(key=lambda p: p["correct"], reverse=True)
    return players

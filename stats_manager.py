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


# ── Competition history ──────────────────────────────────────────────────────

def save_competition(players_stats, mode, mode_label, winner_name, filepath="competitions.json"):
    """Save a completed competition to history."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)

    history = load_competitions(filepath)

    competition = {
        "id": len(history) + 1,
        "date": datetime.now().isoformat(),
        "mode": mode,
        "mode_label": mode_label,
        "winner": winner_name,
        "players": [],
    }
    for name, stats in players_stats.items():
        competition["players"].append({
            "name": name,
            "correct": stats.get("correct", 0),
            "total_questions": stats.get("total_questions", 0),
            "wrong_guesses": stats.get("wrong_guesses", 0),
            "give_ups": stats.get("give_ups", 0),
            "stars": stats.get("stars", 0),
            "best_streak": stats.get("best_streak", 0),
            "success_rate": stats.get("success_rate", 0.0),
        })

    history.append(competition)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return competition


def load_competitions(filepath="competitions.json"):
    """Load competition history."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_player_wins(filepath="competitions.json"):
    """Get a dict of player_name -> number of wins across all competitions."""
    history = load_competitions(filepath)
    wins = {}
    for comp in history:
        winner = comp.get("winner", "")
        if winner:
            wins[winner] = wins.get(winner, 0) + 1
    return wins


def get_player_competition_stats(filepath="competitions.json"):
    """Get cumulative competition stats per player."""
    history = load_competitions(filepath)
    stats = {}
    for comp in history:
        for p in comp.get("players", []):
            name = p["name"]
            if name not in stats:
                stats[name] = {
                    "name": name,
                    "games_played": 0,
                    "total_correct": 0,
                    "total_questions": 0,
                    "total_stars": 0,
                    "wins": 0,
                    "best_streak_ever": 0,
                }
            s = stats[name]
            s["games_played"] += 1
            s["total_correct"] += p.get("correct", 0)
            s["total_questions"] += p.get("total_questions", 0)
            s["total_stars"] += p.get("stars", 0)
            s["best_streak_ever"] = max(s["best_streak_ever"], p.get("best_streak", 0))
        winner = comp.get("winner", "")
        if winner and winner in stats:
            stats[winner]["wins"] += 1
    return stats

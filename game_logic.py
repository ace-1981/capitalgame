import difflib


def normalize_answer(answer):
    """Normalize an answer for comparison."""
    return answer.strip().lower()


def _best_ratio(guess, correct, alternatives):
    """Return the best similarity ratio across correct answer and alternatives."""
    best = difflib.SequenceMatcher(None, guess, correct).ratio()
    for alt in (alternatives or []):
        r = difflib.SequenceMatcher(None, guess, normalize_answer(alt)).ratio()
        if r > best:
            best = r
    return best


def check_answer(guess, correct_answer, alternatives=None):
    """Check answer with typo tolerance.

    Returns:
        "exact"  – perfect match
        "typo"   – 70%+ letters correct (accepted with spelling note)
        False    – wrong answer
    """
    if not guess:
        return False
    normalized_guess = normalize_answer(guess)
    normalized_correct = normalize_answer(correct_answer)

    # Exact match
    if normalized_guess == normalized_correct:
        return "exact"
    if alternatives:
        for alt in alternatives:
            if normalized_guess == normalize_answer(alt):
                return "exact"

    if len(normalized_guess) < 2:
        return False

    ratio = _best_ratio(normalized_guess, normalized_correct, alternatives)

    if ratio >= 0.70:
        return "typo"

    return False


def get_hint(capital, hint_level):
    """Get a progressively more helpful hint."""
    if hint_level == 1:
        return f"מתחיל באות **{capital[0]}**"
    elif hint_level == 2:
        return (
            f"מתחיל ב-**{capital[0]}** "
            f"ומסתיים ב-**{capital[-1]}**"
        )
    elif hint_level == 3:
        return (
            f"מכיל **{len(capital)}** אותיות "
            f"ומתחיל ב-**{capital[:2]}**"
        )
    else:
        hint_chars = []
        for i, ch in enumerate(capital):
            if ch == " ":
                hint_chars.append("  ")
            elif i == 0 or i == len(capital) - 1:
                hint_chars.append(ch)
            else:
                hint_chars.append(" _ ")
        return "השלם: **" + "".join(hint_chars) + "**"


# Game mode constants
MODE_MOST_CORRECT = "most_correct"
MODE_LONGEST_STREAK = "longest_streak"
MODE_FIXED_ROUNDS = "fixed_rounds"
MODE_TIMED = "timed"

GAME_MODES = {
    MODE_MOST_CORRECT: "🏆 הכי הרבה תשובות נכונות",
    MODE_LONGEST_STREAK: "🔥 הרצף הארוך ביותר",
    MODE_FIXED_ROUNDS: "🎯 סיבובים קבועים",
    MODE_TIMED: "⏱️ אתגר זמן",
}

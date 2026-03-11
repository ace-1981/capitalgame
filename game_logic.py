import difflib


def normalize_answer(answer):
    """Normalize an answer for comparison."""
    return answer.strip().lower()


def check_answer(guess, correct_answer, alternatives=None):
    """Check if the guess matches the correct answer (lenient for kids)."""
    if not guess:
        return False
    normalized_guess = normalize_answer(guess)
    normalized_correct = normalize_answer(correct_answer)

    if normalized_guess == normalized_correct:
        return True

    if alternatives:
        for alt in alternatives:
            if normalized_guess == normalize_answer(alt):
                return True

    # Allow close matches for typos (85%+ similarity, at least 3 chars typed)
    ratio = difflib.SequenceMatcher(
        None, normalized_guess, normalized_correct
    ).ratio()
    if ratio >= 0.85 and len(normalized_guess) >= 3:
        return True

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

import time

import streamlit as st

from data_loader import load_countries, get_random_country
from game_logic import check_answer, get_hint, GAME_MODES, MODE_TIMED, MODE_LONGEST_STREAK
from stats_manager import (
    create_default_stats,
    update_stats_correct,
    update_stats_wrong,
    update_stats_giveup,
    save_progress,
    load_progress,
    get_leaderboard,
    save_competition,
    load_competitions,
    get_player_competition_stats,
)
from ui_components import (
    inject_custom_css,
    render_info_card,
    render_country_map,
    render_maps,
    render_stats_sidebar,
    render_scoreboard,
    render_celebration,
    render_wrong_card,
    render_giveup_card,
    render_answer_prompt_html,
    render_hint_box,
    render_welcome,
    render_winner,
    render_player_banner,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="🌍 חידון ערי בירה", page_icon="🌍", layout="wide")
inject_custom_css()

# ── Session-state defaults ───────────────────────────────────────────────────
_DEFAULTS = dict(
    game_state="welcome",
    countries=None,
    current_country=None,
    turn_state="guessing",      # guessing | correct | wrong | gave_up
    hint_level=0,
    wrong_attempts=0,
    used_countries=[],
    # single-player
    player_name="חוקר",
    player_stats=None,
    # multiplayer
    players=[],
    current_player_idx=0,
    multi_stats={},
    game_mode="most_correct",
    total_rounds=10,
    time_limit=120,
    start_time=None,
    turns_played=0,
    celebrate=False,
    form_counter=0,
)

for key, val in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Load countries once
if st.session_state.countries is None:
    st.session_state.countries = load_countries()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _new_question():
    """Draw a new country card and reset per-turn state."""
    ss = st.session_state
    country = get_random_country(ss.countries, ss.used_countries)
    ss.current_country = country
    ss.used_countries.append(country["name"])
    ss.turn_state = "guessing"
    ss.hint_level = 0
    ss.wrong_attempts = 0
    ss.celebrate = False
    ss.typo_note = False
    ss.form_counter += 1


def _current_stats():
    """Return the stats dict for whoever is playing right now."""
    ss = st.session_state
    if ss.game_state == "single_play":
        return ss.player_stats
    name = ss.players[ss.current_player_idx]
    return ss.multi_stats[name]


def _check_game_over():
    """Return True if the multiplayer game has ended."""
    ss = st.session_state
    if ss.game_mode == MODE_TIMED:
        elapsed = time.time() - ss.start_time
        return elapsed >= ss.time_limit
    # rounds-based modes
    total_turns = ss.total_rounds * len(ss.players)
    return ss.turns_played >= total_turns


def _get_alternatives(country):
    """Get all acceptable answers including Hebrew capital."""
    alts = list(country.get("alternatives") or [])
    capital_he = country.get("capital_he", "")
    if capital_he and capital_he not in alts:
        alts.append(capital_he)
    return alts


# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

def welcome_page():
    render_welcome()

    # Show saved progress if any
    saved = load_progress()
    if saved:
        with st.expander("📂 התקדמות שמורה"):
            for name, data in saved.items():
                st.write(
                    f"**{name}** — ⭐ {data.get('stars',0)}  "
                    f"✅ {data.get('correct',0)}  "
                    f"🔥 שיא רצף {data.get('best_streak',0)}"
                )

    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            '<div style="background:rgba(255,255,255,.6);backdrop-filter:blur(8px);'
            'border-radius:24px;padding:28px 24px;text-align:center;'
            'box-shadow:0 8px 32px rgba(0,0,0,.06);border:2px solid rgba(99,102,241,.1)">'
            '<div style="font-size:20px;font-weight:800;color:#1e293b;margin-bottom:16px">'
            '🎮 בחרו מצב משחק</div></div>',
            unsafe_allow_html=True)
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧒 שחקן יחיד", use_container_width=True):
                st.session_state.game_state = "single_setup"
                st.rerun()
        with c2:
            if st.button("👫 מרובה משתתפים", use_container_width=True):
                st.session_state.game_state = "multi_setup"
                st.rerun()

    # ── Competition history ──
    competitions = load_competitions()
    if competitions:
        st.write("")
        st.markdown("### 🏆 היסטוריית תחרויות")

        # Overall leaderboard
        comp_stats = get_player_competition_stats()
        if comp_stats:
            sorted_players = sorted(comp_stats.values(), key=lambda p: p["wins"], reverse=True)
            st.markdown("#### 👑 טבלת אלופים")
            for i, p in enumerate(sorted_players):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "▪️"
                avg_rate = round(p["total_correct"] / p["total_questions"] * 100, 1) if p["total_questions"] > 0 else 0
                st.markdown(
                    f"{medal} **{p['name']}** — "
                    f"🏆 {p['wins']} ניצחונות | "
                    f"🎮 {p['games_played']} משחקים | "
                    f"⭐ {p['total_stars']} כוכבים | "
                    f"📈 {avg_rate}% הצלחה | "
                    f"🔥 שיא רצף: {p['best_streak_ever']}"
                )

        # Recent competitions
        with st.expander(f"📜 תחרויות אחרונות ({len(competitions)} סה\"כ)"):
            for comp in reversed(competitions[-10:]):
                date_str = comp["date"][:10]
                players_str = ", ".join(p["name"] for p in comp["players"])
                st.markdown(
                    f"**{date_str}** | {comp.get('mode_label', comp['mode'])} | "
                    f"שחקנים: {players_str} | "
                    f"🏆 מנצח: **{comp['winner']}**"
                )


# ──────────────────────────────────────────────────────────────────────────────
# Single-player setup & play
# ──────────────────────────────────────────────────────────────────────────────

def single_setup_page():
    render_welcome()
    st.markdown("### 🧒 הגדרת שחקן יחיד")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("מה השם שלך?", value="חוקר", max_chars=20)
        if st.button("🚀 התחילו ללמוד!", use_container_width=True):
            ss = st.session_state
            ss.player_name = name or "חוקר"
            saved = load_progress()
            if ss.player_name in saved:
                ss.player_stats = saved[ss.player_name]
                # keep name consistent
                ss.player_stats["name"] = ss.player_name
            else:
                ss.player_stats = create_default_stats(ss.player_name)
            ss.used_countries = []
            _new_question()
            ss.game_state = "single_play"
            st.rerun()

    if st.button("⬅️ חזרה"):
        st.session_state.game_state = "welcome"
        st.rerun()


def single_play_page():
    ss = st.session_state
    country = ss.current_country
    stats = ss.player_stats
    display_name = country.get("name_he", country["name"])

    render_stats_sidebar(stats)
    render_player_banner(stats["name"], stats["stars"], stats["current_streak"],
                         color="#6366f1", icon="🧒")

    # ── Two-card layout ─────────────────────────────────────────────────
    card_left, card_right = st.columns([3, 2])

    # LEFT: info card + world map
    with card_left:
        render_info_card(country)
        render_country_map(country)

    # RIGHT: answer card
    with card_right:
        if ss.turn_state in ("guessing", "wrong"):
            if ss.turn_state == "wrong":
                render_wrong_card(ss.wrong_attempts)
                hint_text = get_hint(country.get("capital_he", country["capital"]), ss.hint_level)
                extra = country["hint"] if ss.wrong_attempts >= 2 else None
                render_hint_box(hint_text, extra)
            else:
                render_answer_prompt_html(display_name)

            with st.form(f"answer_{ss.form_counter}", clear_on_submit=True):
                answer = st.text_input(
                    f"עיר הבירה של {display_name}? ✏️",
                    key=f"input_{ss.form_counter}",
                    label_visibility="collapsed",
                    placeholder="הקלידו את שם עיר הבירה פה...",
                )
                c1, c2 = st.columns(2)
                submitted = c1.form_submit_button("✅ שליחה", use_container_width=True)
                give_up = c2.form_submit_button("🏳️ ויתור", use_container_width=True)

            if submitted and answer:
                result = check_answer(answer, country["capital"], _get_alternatives(country))
                if result:
                    update_stats_correct(stats)
                    save_progress(stats)
                    ss.turn_state = "correct"
                    ss.celebrate = True
                    ss.typo_note = (result == "typo")
                    st.rerun()
                else:
                    update_stats_wrong(stats)
                    ss.wrong_attempts += 1
                    ss.hint_level += 1
                    ss.turn_state = "wrong"
                    ss.form_counter += 1
                    st.rerun()
            if give_up:
                update_stats_giveup(stats)
                save_progress(stats)
                ss.turn_state = "gave_up"
                st.rerun()

        elif ss.turn_state == "correct":
            render_celebration(country, stats)
            if st.button("➡️ מדינה הבאה", use_container_width=True):
                _new_question()
                st.rerun()

        elif ss.turn_state == "gave_up":
            render_giveup_card(country)
            if st.button("➡️ מדינה הבאה", use_container_width=True):
                _new_question()
                st.rerun()

    # Show capital map after answering (full width under both cards)
    if ss.turn_state in ("correct", "gave_up"):
        with st.expander("🗺️ ראו את עיר הבירה על המפה", expanded=ss.turn_state == "gave_up"):
            render_maps(country)

    # End session button
    st.write("")
    if st.button("🏠 סיום ושמירה"):
        save_progress(stats)
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.session_state.countries = load_countries()
        st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# Multiplayer setup & play
# ──────────────────────────────────────────────────────────────────────────────

def multi_setup_page():
    render_welcome()
    st.markdown("### 👫 הגדרת משחק מרובה משתתפים")

    num_players = st.slider("מספר שחקנים", 2, 4, 2)
    names = []
    cols = st.columns(num_players)
    for i, col in enumerate(cols):
        with col:
            n = st.text_input(f"שחקן {i+1}", value=f"שחקן {i+1}", key=f"pname_{i}", max_chars=20)
            names.append(n or f"שחקן {i+1}")

    st.markdown("---")
    mode_key = st.selectbox("מצב משחק", list(GAME_MODES.keys()), format_func=lambda k: GAME_MODES[k])

    if mode_key == MODE_TIMED:
        time_limit = st.slider("הגבלת זמן (שניות)", 60, 300, 120, step=30)
    else:
        rounds = st.slider("סיבובים לכל שחקן", 3, 20, 10)

    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 התחילו לשחק!", use_container_width=True):
            # make names unique
            seen = {}
            unique_names = []
            for n in names:
                if n in seen:
                    seen[n] += 1
                    unique_names.append(f"{n} ({seen[n]})")
                else:
                    seen[n] = 1
                    unique_names.append(n)

            ss = st.session_state
            ss.players = unique_names
            ss.multi_stats = {n: create_default_stats(n) for n in unique_names}
            ss.game_mode = mode_key
            ss.current_player_idx = 0
            ss.turns_played = 0
            ss.used_countries = []
            if mode_key == MODE_TIMED:
                ss.time_limit = time_limit
                ss.start_time = time.time()
            else:
                ss.total_rounds = rounds
            _new_question()
            ss.game_state = "multi_play"
            st.rerun()

    if st.button("⬅️ חזרה"):
        st.session_state.game_state = "welcome"
        st.rerun()


def multi_play_page():
    ss = st.session_state
    country = ss.current_country
    current_name = ss.players[ss.current_player_idx]
    stats = ss.multi_stats[current_name]
    display_name = country.get("name_he", country["name"])

    # Sidebar scoreboard
    with st.sidebar:
        render_scoreboard(ss.multi_stats, current_name, ss.game_mode)
        st.divider()
        if ss.game_mode == MODE_TIMED:
            remaining = max(0, ss.time_limit - (time.time() - ss.start_time))
            mins, secs = divmod(int(remaining), 60)
            st.markdown(f"### ⏱️ זמן שנותר: {mins}:{secs:02d}")
        else:
            total_turns = ss.total_rounds * len(ss.players)
            st.markdown(f"### 🎯 תור {ss.turns_played + 1} מתוך {total_turns}")

    # Check if game over (timed)
    if ss.game_mode == MODE_TIMED:
        remaining = ss.time_limit - (time.time() - ss.start_time)
        if remaining <= 0:
            save_progress(ss.multi_stats)
            leaderboard = get_leaderboard(ss.multi_stats, ss.game_mode)
            winner_name = leaderboard[0]["name"] if leaderboard else ""
            mode_label = GAME_MODES.get(ss.game_mode, ss.game_mode)
            save_competition(ss.multi_stats, ss.game_mode, mode_label, winner_name)
            ss.game_state = "results"
            st.rerun()

    # Player banner
    player_colors = ["#6366f1", "#dc2626", "#16a34a", "#ea580c"]
    color = player_colors[ss.current_player_idx % len(player_colors)]
    render_player_banner(current_name, stats["stars"], stats["current_streak"],
                         color=color, icon="🎮")

    # ── Two-card layout ─────────────────────────────────────────────────
    card_left, card_right = st.columns([3, 2])

    with card_left:
        render_info_card(country)
        render_country_map(country)

    with card_right:
        if ss.turn_state in ("guessing", "wrong"):
            if ss.turn_state == "wrong":
                render_wrong_card(ss.wrong_attempts)
                hint_text = get_hint(country.get("capital_he", country["capital"]), ss.hint_level)
                extra = country["hint"] if ss.wrong_attempts >= 2 else None
                render_hint_box(hint_text, extra)
            else:
                render_answer_prompt_html(display_name)

            with st.form(f"manswer_{ss.form_counter}", clear_on_submit=True):
                answer = st.text_input(
                    f"עיר הבירה של {display_name}? ✏️",
                    key=f"minput_{ss.form_counter}",
                    label_visibility="collapsed",
                    placeholder="הקלידו את שם עיר הבירה פה...",
                )
                c1, c2 = st.columns(2)
                submitted = c1.form_submit_button("✅ שליחה", use_container_width=True)
                give_up = c2.form_submit_button("🏳️ ויתור", use_container_width=True)

            if submitted and answer:
                result = check_answer(answer, country["capital"], _get_alternatives(country))
                if result:
                    update_stats_correct(stats)
                    ss.turn_state = "correct"
                    ss.celebrate = True
                    ss.typo_note = (result == "typo")
                    st.rerun()
                else:
                    update_stats_wrong(stats)
                    ss.wrong_attempts += 1
                    ss.hint_level += 1
                    ss.turn_state = "wrong"
                    ss.form_counter += 1
                    st.rerun()
            if give_up:
                update_stats_giveup(stats)
                ss.turn_state = "gave_up"
                st.rerun()

        elif ss.turn_state == "correct":
            render_celebration(country, stats)
            if st.button("➡️ תור הבא", use_container_width=True):
                _advance_multi_turn()

        elif ss.turn_state == "gave_up":
            render_giveup_card(country)
            if st.button("➡️ תור הבא", use_container_width=True):
                _advance_multi_turn()

    if ss.turn_state in ("correct", "gave_up"):
        with st.expander("🗺️ ראו את עיר הבירה על המפה", expanded=ss.turn_state == "gave_up"):
            render_maps(country)


def _advance_multi_turn():
    """Move to the next player / check end-of-game."""
    ss = st.session_state
    ss.turns_played += 1
    ss.current_player_idx = (ss.current_player_idx + 1) % len(ss.players)

    if _check_game_over():
        # Save all player stats
        save_progress(ss.multi_stats)
        # Save competition history
        leaderboard = get_leaderboard(ss.multi_stats, ss.game_mode)
        winner_name = leaderboard[0]["name"] if leaderboard else ""
        mode_label = GAME_MODES.get(ss.game_mode, ss.game_mode)
        save_competition(ss.multi_stats, ss.game_mode, mode_label, winner_name)
        ss.game_state = "results"
    else:
        _new_question()
    st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# Results page
# ──────────────────────────────────────────────────────────────────────────────

def results_page():
    st.markdown(
        '<div style="text-align:center;padding:10px 0">'
        '<div style="font-size:52px;font-weight:900;'
        'background:linear-gradient(135deg,#6366f1,#a78bfa,#ec4899,#f97316,#eab308);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent">'
        '🏆 המשחק נגמר! 🏆</div></div>',
        unsafe_allow_html=True,
    )
    st.write("")

    ss = st.session_state
    leaderboard = get_leaderboard(ss.multi_stats, ss.game_mode)

    if leaderboard:
        winner = leaderboard[0]
        render_winner(winner["name"], winner, ss.game_mode)
        st.balloons()

    st.markdown("### 📊 תוצאות סופיות")
    for i, p in enumerate(leaderboard):
        medal = ["🥇", "🥈", "🥉", "4️⃣"][i] if i < 4 else ""
        cols = st.columns([1, 2, 1, 1, 1, 1, 1])
        cols[0].markdown(f"### {medal}")
        cols[1].metric("שחקן", p["name"])
        cols[2].metric("⭐ כוכבים", p["stars"])
        cols[3].metric("✅ נכונות", p["correct"])
        cols[4].metric("🔥 שיא רצף", p["best_streak"])
        cols[5].metric("📈 אחוז", f"{p['success_rate']}%")
        cols[6].metric("🏳️ ויתורים", p["give_ups"])

    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 שחקו שוב", use_container_width=True):
            for k, v in _DEFAULTS.items():
                st.session_state[k] = v
            st.session_state.countries = load_countries()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Router
# ══════════════════════════════════════════════════════════════════════════════

_PAGES = {
    "welcome": welcome_page,
    "single_setup": single_setup_page,
    "single_play": single_play_page,
    "multi_setup": multi_setup_page,
    "multi_play": multi_play_page,
    "results": results_page,
}

_PAGES.get(st.session_state.game_state, welcome_page)()

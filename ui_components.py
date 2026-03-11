import os, base64, urllib.request
import streamlit as st
import streamlit.components.v1 as components


# ISO 2-letter → ISO numeric code mapping for our 25 countries
_ISO_NUM = {
    "fr": "250", "jp": "392", "br": "076", "eg": "818", "au": "036",
    "in": "356", "gb": "826", "it": "380", "mx": "484", "kr": "410",
    "ca": "124", "de": "276", "cn": "156", "ar": "032", "ke": "404",
    "es": "724", "tr": "792", "th": "764", "za": "710", "pe": "604",
    "gr": "300", "ru": "643", "no": "578", "ma": "504", "nz": "554",
}
_TOPO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"

FLAG_CDN = "https://flagcdn.com/w320"

# Wikimedia Commons landmark photo URLs  (400px thumbnails — allowed by Wikimedia)
_LANDMARK_IMG = {
    "fr": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/400px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
    "jp": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg/400px-View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg",
    "br": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Christ_the_Redeemer_-_Cristo_Redentor.jpg/400px-Christ_the_Redeemer_-_Cristo_Redentor.jpg",
    "eg": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Great_Pyramid_of_Giza_-_Pyramid_of_Khufu.jpg/400px-Great_Pyramid_of_Giza_-_Pyramid_of_Khufu.jpg",
    "au": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Sydney_Australia._%2821339175489%29.jpg/400px-Sydney_Australia._%2821339175489%29.jpg",
    "in": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Taj_Mahal_%28Edited%29.jpeg/400px-Taj_Mahal_%28Edited%29.jpeg",
    "gb": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Elizabeth_Tower%2C_June_2022.jpg/400px-Elizabeth_Tower%2C_June_2022.jpg",
    "it": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/400px-Colosseo_2020.jpg",
    "mx": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/400px-Chichen_Itza_3.jpg",
    "kr": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/%EA%B4%91%ED%99%94%EB%AC%B8_%EC%9B%94%EB%8C%80.jpg/400px-%EA%B4%91%ED%99%94%EB%AC%B8_%EC%9B%94%EB%8C%80.jpg",
    "ca": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg/400px-Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg",
    "de": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Brandenburger_Tor_abends.jpg/400px-Brandenburger_Tor_abends.jpg",
    "cn": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/400px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    "ar": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Buenos_Aires_%2820234294752%29.jpg/400px-Buenos_Aires_%2820234294752%29.jpg",
    "ke": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Masai_Mara_at_Sunset.jpg/400px-Masai_Mara_at_Sunset.jpg",
    "es": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/%CE%A3%CE%B1%CE%B3%CF%81%CE%AC%CE%B4%CE%B1_%CE%A6%CE%B1%CE%BC%CE%AF%CE%BB%CE%B9%CE%B1_2941.jpg/400px-%CE%A3%CE%B1%CE%B3%CF%81%CE%AC%CE%B4%CE%B1_%CE%A6%CE%B1%CE%BC%CE%AF%CE%BB%CE%B9%CE%B1_2941.jpg",
    "tr": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Hagia_Sophia_%28228968325%29.jpeg/400px-Hagia_Sophia_%28228968325%29.jpeg",
    "th": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/0005574_-_Wat_Phra_Kaew_006.jpg/400px-0005574_-_Wat_Phra_Kaew_006.jpg",
    "za": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Table_Mountain_DanieVDM.jpg/400px-Table_Mountain_DanieVDM.jpg",
    "pe": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/400px-Machu_Picchu%2C_2023_%28012%29.jpg",
    "gr": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/The_Parthenon_in_Athens.jpg/400px-The_Parthenon_in_Athens.jpg",
    "ru": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Moscow_Kremlin_%288281675670%29.jpg/400px-Moscow_Kremlin_%288281675670%29.jpg",
    "no": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Moragsoorm.jpg/400px-Moragsoorm.jpg",
    "ma": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Hassan_II_mosque%2C_Casablanca_2.jpg/400px-Hassan_II_mosque%2C_Casablanca_2.jpg",
    "nz": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/400px-Milford_Sound_%28New_Zealand%29.JPG",
}

# Continent-based color themes  (primary, mid, dark)
_CONTINENT_THEME = {
    "אירופה":       ("#4fc3f7", "#0288d1", "#01579b"),
    "אסיה":         ("#ef5350", "#c62828", "#7f0000"),
    "אפריקה":       ("#ffb74d", "#ef6c00", "#bf360c"),
    "דרום אמריקה":  ("#66bb6a", "#2e7d32", "#1b5e20"),
    "צפון אמריקה":  ("#ab47bc", "#7b1fa2", "#4a148c"),
    "אוקיאניה":     ("#26c6da", "#00838f", "#004d40"),
}


def _format_area(km2):
    if km2 >= 1_000_000:
        return f"{km2 / 1_000_000:.1f}M קמ״ר"
    return f"{km2:,} קמ״ר"


_IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_img_cache")


@st.cache_data(show_spinner=False)
def _photo_data_uri(code):
    """Download landmark photo, cache to disk, return as base64 data URI."""
    url = _LANDMARK_IMG.get(code)
    if not url:
        return ""
    os.makedirs(_IMG_DIR, exist_ok=True)
    path = os.path.join(_IMG_DIR, f"{code}.jpg")
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
    else:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "CapitalsQuiz/1.0 (educational project)"
            })
            data = urllib.request.urlopen(req, timeout=15).read()
            with open(path, "wb") as f:
                f.write(data)
        except Exception:
            return ""
    ext = "png" if url.lower().endswith(".png") else "jpeg"
    return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════════════

def inject_custom_css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700;800;900&display=swap');

    /* ── page ── */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(160deg, #f0f4ff 0%, #e0e7ff 50%, #dbeafe 100%);
        font-family: 'Rubik', 'Segoe UI', sans-serif;
    }
    [data-testid="stMainBlockContainer"] { max-width: 1200px; }

    /* ── sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(255,255,255,.06);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
        font-family: 'Rubik', sans-serif;
    }

    /* ── buttons ── */
    .stButton > button {
        border-radius: 16px; font-size: 16px; font-weight: 700;
        padding: 10px 28px; border: none;
        transition: all .2s ease;
        box-shadow: 0 4px 14px rgba(0,0,0,.10);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,.16);
    }
    .stButton > button:active { transform: translateY(0); }

    /* ── form submit buttons ── */
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #fff !important; font-weight: 800 !important;
        border-radius: 16px !important; font-size: 17px !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    }

    /* ── text input ── */
    .stTextInput > div > div > input {
        border-radius: 16px !important; padding: 14px 18px !important;
        font-size: 18px !important; font-weight: 600 !important;
        border: 2px solid #c7d2fe !important;
        background: rgba(255,255,255,.9) !important;
        text-align: center; direction: rtl;
        transition: border .2s, box-shadow .2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,.18) !important;
    }

    /* ── expander ── */
    details[data-testid="stExpander"] {
        background: rgba(255,255,255,.55); border-radius: 20px;
        border: 2px solid rgba(99,102,241,.10); padding: 4px;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 16px rgba(0,0,0,.04);
    }
    .streamlit-expanderHeader {
        font-weight: 700 !important; font-size: 16px !important;
    }

    /* ── selectbox / slider ── */
    .stSlider > div { padding: 0 8px; }
    .stSelectbox > div > div { border-radius: 14px !important; }

    /* ── scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 3px; }

    /* ── hide branding ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* tighten gap between card and map expander */
    [data-testid="stExpander"] { margin-top: -16px !important; }

    /* reduce general block gaps */
    [data-testid="stVerticalBlock"] > div { margin-top: -4px; }
    [data-testid="column"] [data-testid="stVerticalBlock"] > div:first-child { margin-top: 0; }
    </style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# COUNTRY INFO CARD  (collectible-card style via components.html)
# ═══════════════════════════════════════════════════════════════════════════════

def render_info_card(country):
    code = country.get("country_code", "")
    continent = country.get("continent", "")
    c1, c2, c3 = _CONTINENT_THEME.get(continent, ("#4fc3f7", "#0288d1", "#01579b"))
    display_name = country.get("name_he", country["name"])
    area = _format_area(country.get("area_km2", 0))
    photo_src = _photo_data_uri(code)
    flag_url = f"{FLAG_CDN}/{code}.png" if code else ""
    landmark = country.get("landmark", "")
    fun_fact = country.get("fun_fact", "")

    photo_block = (
        f'<img class="photo" src="{photo_src}" alt="{landmark}" '
        f'onerror="this.style.display=\'none\'">'
    ) if photo_src else ""

    flag_block = (
        f'<img class="flag" src="{flag_url}" alt="flag" '
        f'onerror="this.style.display=\'none\'">'
    ) if flag_url else ""

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
@keyframes cardIn{{0%{{opacity:0;transform:perspective(800px) rotateY(-6deg) translateY(16px) scale(.97)}}
  100%{{opacity:1;transform:none}}}}
@keyframes shimmer{{0%{{background-position:-200% 0}}100%{{background-position:200% 0}}}}
@keyframes glow{{0%,100%{{box-shadow:0 4px 16px rgba(0,0,0,.3)}}50%{{box-shadow:0 4px 16px rgba(0,0,0,.3),0 0 24px rgba(255,255,255,.2)}}}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:transparent;font-family:'Rubik','Segoe UI',sans-serif;direction:rtl}}

.card{{
  background:linear-gradient(165deg,{c1} 0%,{c2} 50%,{c3} 100%);
  border-radius:24px;color:#fff;text-align:center;
  position:relative;overflow:hidden;
  box-shadow:0 20px 60px rgba(0,0,0,.22), 0 2px 6px rgba(0,0,0,.08);
  border:2px solid rgba(255,255,255,.2);
  animation:cardIn .65s cubic-bezier(.22,.68,0,1.15) both;
}}

/* decorative background circles */
.card::before{{content:'';position:absolute;top:-50px;right:-50px;width:180px;height:180px;
  background:radial-gradient(circle,rgba(255,255,255,.1),transparent 60%);border-radius:50%;pointer-events:none}}
.card::after{{content:'';position:absolute;bottom:-30px;left:-30px;width:140px;height:140px;
  background:radial-gradient(circle,rgba(255,255,255,.06),transparent 60%);border-radius:50%;pointer-events:none}}

/* rarity stripe at top */
.rarity{{height:5px;background:linear-gradient(90deg,
  rgba(255,255,255,0),rgba(255,255,255,.5),rgba(255,255,255,0));
  background-size:200% 100%;animation:shimmer 2.5s ease-in-out infinite}}

/* photo area */
.photo-wrap{{position:relative;overflow:hidden}}
.photo{{width:100%;height:170px;object-fit:cover;display:block}}
.photo-overlay{{position:absolute;bottom:0;left:0;right:0;height:60px;
  background:linear-gradient(transparent,{c2})}}

/* flag */
.flag-wrap{{margin:-28px auto 0;position:relative;z-index:2;text-align:center}}
.flag{{width:76px;border-radius:10px;display:block;margin:0 auto;
  box-shadow:0 6px 20px rgba(0,0,0,.3);border:3px solid rgba(255,255,255,.45);
  animation:glow 3.5s ease-in-out infinite}}

/* body text */
.body{{padding:6px 18px 14px;position:relative;z-index:1}}
.name{{font-size:26px;font-weight:900;letter-spacing:1px;margin:6px 0 2px;
  text-shadow:0 2px 8px rgba(0,0,0,.25)}}
.continent{{display:inline-flex;align-items:center;gap:5px;
  background:rgba(255,255,255,.14);backdrop-filter:blur(6px);
  padding:4px 16px;border-radius:20px;font-size:13px;font-weight:700;
  color:rgba(255,255,255,.88);margin:4px 0 10px;border:1px solid rgba(255,255,255,.15)}}
.divider{{width:55%;height:1px;margin:0 auto 10px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent)}}
.landmark{{font-size:17px;font-weight:700;color:rgba(255,255,255,.85);margin:2px 0 8px}}
.chips{{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin:4px 0 8px}}
.chip{{display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,.1);
  border-radius:10px;padding:5px 14px;font-size:13px;font-weight:600;
  border:1px solid rgba(255,255,255,.1)}}
.funfact{{background:rgba(0,0,0,.14);border-radius:14px;padding:10px 14px;
  border-right:4px solid rgba(255,215,0,.65);text-align:right;font-size:14px;
  line-height:1.7;color:rgba(255,255,255,.9);direction:rtl;
  backdrop-filter:blur(4px)}}
.ff-label{{font-size:11px;font-weight:800;color:rgba(255,215,0,.75);
  letter-spacing:1px;margin-bottom:3px}}
.shimmer{{height:2px;margin:4px auto 4px;width:65%;border-radius:2px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent);
  background-size:200% 100%;animation:shimmer 2.5s ease-in-out infinite}}
</style></head><body>
<div class="card">
  <div class="rarity"></div>
  <div class="photo-wrap">
    {photo_block}
    <div class="photo-overlay"></div>
  </div>
  <div class="flag-wrap">{flag_block}</div>
  <div class="body">
    <div class="name">{display_name}</div>
    <div><span class="continent">🌍 {continent}</span></div>
    <div class="divider"></div>
    <div class="landmark">🏛️ {landmark}</div>
    <div class="chips">
      <span class="chip">📏 {area}</span>
    </div>
    <div class="shimmer"></div>
    <div class="funfact">
      <div class="ff-label">💡 הידעת?</div>
      {fun_fact}
    </div>
  </div>
</div>
</body></html>"""
    components.html(html, height=500, scrolling=False)


# ═══════════════════════════════════════════════════════════════════════════════
# LEAFLET MAP
# ═══════════════════════════════════════════════════════════════════════════════

def _leaflet_html(code, lat, lng, height=320, marker_lat=None, marker_lng=None, marker_label=""):
    numeric = _ISO_NUM.get(code.lower(), "")
    marker_js = ""
    if marker_lat is not None and marker_label:
        safe = marker_label.replace("'", "\\'")
        marker_js = (
            f"L.circleMarker([{marker_lat},{marker_lng}],"
            f"{{radius:6,color:'#c62828',fillColor:'#ef5350',fillOpacity:0.9,weight:2}})"
            f".addTo(map).bindTooltip('{safe}',"
            f"{{permanent:true,direction:'top',offset:[0,-8],className:'tip'}});"
        )
    html = """<!DOCTYPE html><html><head>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>
<style>body{margin:0}#m{width:100%;height:__H__px;border-radius:16px}
.tip{font-weight:700;font-size:13px;border:none;background:rgba(255,255,255,.92);
border-radius:10px;padding:4px 10px;box-shadow:0 3px 10px rgba(0,0,0,.15)}</style>
</head><body><div id="m"></div><script>
(function(){
var map=L.map('m',{scrollWheelZoom:false}).setView([__LAT__,__LNG__],3);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png',
{attribution:'\u00a9 OSM, \u00a9 CARTO',maxZoom:18}).addTo(map);
fetch('__TOPO__').then(function(r){return r.json();}).then(function(t){
var geo=topojson.feature(t,t.objects.countries);
var ff=geo.features.filter(function(f){return f.id==='__NUM__';});
if(ff.length){
var lyr=L.geoJSON(ff,{style:{color:'#6366f1',weight:2.5,
fillColor:'#818cf8',fillOpacity:0.18}}).addTo(map);
map.fitBounds(lyr.getBounds(),{padding:[30,30]});}
__MRK__
});
})();
</script></body></html>"""
    html = (html
        .replace("__H__", str(height))
        .replace("__LAT__", str(lat))
        .replace("__LNG__", str(lng))
        .replace("__NUM__", numeric)
        .replace("__TOPO__", _TOPO_URL)
        .replace("__MRK__", marker_js))
    return html


def render_country_map(country):
    code = country.get("country_code", "")
    html = _leaflet_html(code, country["country_lat"], country["country_lng"], height=250)
    components.html(html, height=260)


def render_maps(country):
    capital_display = country.get("capital_he", country["capital"])
    display_name = country.get("name_he", country["name"])
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div style="text-align:center;font-weight:700;font-size:15px;color:#475569;'
            f'margin-bottom:6px">🌍 מיקום — {display_name}</div>',
            unsafe_allow_html=True)
        html = _leaflet_html(country.get("country_code", ""),
                             country["country_lat"], country["country_lng"], height=280)
        components.html(html, height=300)
    with col2:
        st.markdown(
            f'<div style="text-align:center;font-weight:700;font-size:15px;color:#475569;'
            f'margin-bottom:6px">📍 עיר הבירה: {capital_display}</div>',
            unsafe_allow_html=True)
        html = _leaflet_html(country.get("country_code", ""),
                             country["capital_lat"], country["capital_lng"], height=280,
                             marker_lat=country["capital_lat"],
                             marker_lng=country["capital_lng"],
                             marker_label=capital_display)
        components.html(html, height=300)


# ═══════════════════════════════════════════════════════════════════════════════
# STATS SIDEBAR  (achievement-card style)
# ═══════════════════════════════════════════════════════════════════════════════

_STAT_ITEMS = [
    ("⭐", "stars",          "כוכבים",     "#eab308"),
    ("🔥", "current_streak", "רצף",        "#ef4444"),
    ("🏅", "best_streak",    "שיא רצף",    "#f97316"),
    ("✅", "correct",        "נכונות",     "#22c55e"),
    ("❌", "wrong_guesses",  "שגויות",     "#ef4444"),
    ("🏳️", "give_ups",       "ויתורים",    "#a1a1aa"),
    ("📈", "success_rate",   "אחוז הצלחה", "#6366f1"),
    ("🎯", "total_questions","שאלות",      "#0ea5e9"),
]


def render_stats_sidebar(stats):
    with st.sidebar:
        # Title
        st.markdown(
            '<div style="text-align:center;margin-bottom:14px">'
            '<div style="font-size:24px;font-weight:900;letter-spacing:1px">'
            '📊 הסטטיסטיקות שלך</div>'
            '<div style="height:3px;width:50%;margin:6px auto 0;border-radius:2px;'
            'background:linear-gradient(90deg,#6366f1,#a78bfa,#6366f1)"></div>'
            '</div>', unsafe_allow_html=True)

        # Top 3 highlight stats in columns
        c1, c2, c3 = st.columns(3)
        for col, (emoji, key, label, color) in zip(
            [c1, c2, c3], _STAT_ITEMS[:3]
        ):
            val = stats.get(key, 0)
            with col:
                st.markdown(
                    f"""<div style="background:linear-gradient(145deg,{color}22,{color}11);
                        border:2px solid {color}44;border-radius:16px;padding:10px 4px;
                        text-align:center;margin-bottom:4px">
                        <div style="font-size:11px;opacity:.6">{label}</div>
                        <div style="font-size:24px;font-weight:900">{emoji} {val}</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown(
            '<div style="height:1px;background:rgba(255,255,255,.08);margin:6px 0"></div>',
            unsafe_allow_html=True)

        # Remaining stats as compact rows
        for emoji, key, label, color in _STAT_ITEMS[3:]:
            val = stats.get(key, 0)
            suffix = "%" if key == "success_rate" else ""
            st.markdown(
                f"""<div style="display:flex;align-items:center;gap:10px;
                    background:rgba(255,255,255,.04);border-radius:12px;
                    padding:7px 12px;margin:3px 0;direction:rtl">
                    <div style="width:32px;height:32px;border-radius:9px;display:flex;
                        align-items:center;justify-content:center;font-size:16px;
                        background:{color}22;border:1px solid {color}33;flex-shrink:0">
                        {emoji}</div>
                    <div style="flex:1;text-align:right">
                        <div style="font-size:11px;opacity:.5;line-height:1">{label}</div>
                        <div style="font-size:18px;font-weight:800;line-height:1.2">{val}{suffix}</div>
                    </div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MULTIPLAYER SCOREBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render_scoreboard(multi_stats, current_player_name=None, mode="most_correct"):
    from stats_manager import get_leaderboard
    players = get_leaderboard(multi_stats, mode)

    st.markdown(
        '<div style="text-align:center;font-size:22px;font-weight:900;margin-bottom:10px">'
        '🏆 טבלת ניקוד</div>', unsafe_allow_html=True)

    medals = ["🥇", "🥈", "🥉"]
    for i, p in enumerate(players):
        medal = medals[i] if i < 3 else f"{i+1}."
        active = p["name"] == current_player_name
        border = "border-right:4px solid #6366f1;" if active else ""
        bg = "rgba(99,102,241,.12)" if active else "rgba(255,255,255,.05)"
        key_stat = p["best_streak"] if mode == "longest_streak" else p["correct"]
        key_label = "שיא רצף" if mode == "longest_streak" else "נכונות"
        st.markdown(
            f"""<div style="background:{bg};border-radius:16px;padding:12px 16px;
                margin:5px 0;{border};direction:rtl">
                <div style="font-size:16px;font-weight:800">{medal} {p['name']}</div>
                <div style="font-size:12px;opacity:.7;margin-top:3px;display:flex;
                    gap:10px;justify-content:center;flex-wrap:wrap">
                    <span>{key_label}: <b>{key_stat}</b></span>
                    <span>⭐ {p['stars']}</span>
                    <span>🔥 {p['current_streak']}</span>
                    <span>📈 {p['success_rate']}%</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# QUESTION / ANSWER PANEL
# ═══════════════════════════════════════════════════════════════════════════════

def render_answer_prompt_html(country_name_he):
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#ffffff,#f8fafc);
            border-radius:24px;padding:28px 24px 18px;text-align:center;
            box-shadow:0 8px 32px rgba(99,102,241,.08), 0 2px 8px rgba(0,0,0,.04);
            border:2px solid #e0e7ff;position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:5px;
                background:linear-gradient(90deg,#6366f1,#a78bfa,#ec4899)"></div>
            <div style="font-size:56px;line-height:1;margin-bottom:8px;opacity:.15">❓</div>
            <div style="font-size:24px;font-weight:900;
                background:linear-gradient(135deg,#312e81,#4f46e5);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:6px">מהי עיר הבירה?</div>
            <div style="font-size:16px;color:#64748b;font-weight:500">
                מהי עיר הבירה של <b style="color:#1e293b">{country_name_he}</b>?</div>
        </div>""", unsafe_allow_html=True)


def render_hint_box(hint_text, extra_hint=None):
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#eef2ff,#e0e7ff);
            border-radius:16px;padding:12px 16px;margin:10px 0;direction:rtl;
            border:1px solid #c7d2fe;display:flex;align-items:center;gap:10px;
            box-shadow:0 2px 8px rgba(99,102,241,.06)">
            <div style="width:34px;height:34px;border-radius:10px;background:#6366f1;
                display:flex;align-items:center;justify-content:center;font-size:16px;
                flex-shrink:0;color:#fff">💡</div>
            <div style="font-size:15px;font-weight:600;color:#312e81;line-height:1.5">
                {hint_text}</div>
        </div>""", unsafe_allow_html=True)
    if extra_hint:
        st.markdown(
            f"""<div style="background:linear-gradient(135deg,#fef3c7,#fde68a);
                border-radius:16px;padding:12px 16px;margin:8px 0;direction:rtl;
                border:1px solid #fbbf24;display:flex;align-items:center;gap:10px;
                box-shadow:0 2px 8px rgba(251,191,36,.08)">
                <div style="width:34px;height:34px;border-radius:10px;background:#f59e0b;
                    display:flex;align-items:center;justify-content:center;font-size:16px;
                    flex-shrink:0;color:#fff">🔎</div>
                <div style="font-size:15px;font-weight:600;color:#78350f;line-height:1.5">
                    {extra_hint}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CELEBRATION / WRONG / GIVEUP
# ═══════════════════════════════════════════════════════════════════════════════

def render_celebration(country, stats=None):
    st.balloons()
    capital_display = country.get("capital_he", country["capital"])
    streak_html = ""
    if stats:
        streak_html = (
            f'<div style="display:flex;gap:12px;justify-content:center;margin-top:14px">'
            f'<span style="background:rgba(255,255,255,.8);border-radius:12px;padding:6px 16px;'
            f'font-size:14px;font-weight:700;color:#15803d;'
            f'box-shadow:0 2px 8px rgba(0,0,0,.06)">⭐ +1 כוכב</span>'
            f'<span style="background:rgba(255,255,255,.8);border-radius:12px;padding:6px 16px;'
            f'font-size:14px;font-weight:700;color:#dc2626;'
            f'box-shadow:0 2px 8px rgba(0,0,0,.06)">🔥 רצף: {stats["current_streak"]}</span>'
            f'</div>'
        )
    st.markdown(
        f"""<div style="background:linear-gradient(145deg,#dcfce7,#bbf7d0,#86efac);
            border:3px solid #22c55e;border-radius:24px;padding:32px 24px;
            text-align:center;min-height:260px;display:flex;flex-direction:column;
            align-items:center;justify-content:center;
            box-shadow:0 12px 40px rgba(34,197,94,.15);
            position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:4px;
                background:linear-gradient(90deg,#22c55e,#86efac,#22c55e)"></div>
            <div style="font-size:52px;margin-bottom:8px">🎉</div>
            <div style="font-size:28px;font-weight:900;color:#15803d;margin-bottom:6px">
                !נכון מצוין</div>
            <div style="font-size:34px;font-weight:900;color:#166534;
                text-shadow:0 1px 3px rgba(0,0,0,.05)">{capital_display}</div>
            {streak_html}
        </div>""", unsafe_allow_html=True)


def render_wrong_card(attempts):
    msg = "לא בדיוק — נסו שוב! 💪" if attempts < 3 else "כמעט שם, המשיכו! 🌟"
    st.markdown(
        f"""<style>@keyframes shake{{0%,100%{{transform:translateX(0)}}
        25%{{transform:translateX(-5px)}}75%{{transform:translateX(5px)}}}}</style>
        <div style="background:linear-gradient(145deg,#fef2f2,#fecaca,#fca5a5);
            border:3px solid #ef4444;border-radius:24px;padding:26px 22px;
            text-align:center;min-height:150px;display:flex;flex-direction:column;
            align-items:center;justify-content:center;
            box-shadow:0 8px 28px rgba(239,68,68,.10);
            animation:shake .35s ease-in-out">
            <div style="font-size:42px;margin-bottom:6px">😅</div>
            <div style="font-size:19px;font-weight:800;color:#991b1b">{msg}</div>
            <div style="margin-top:6px;font-size:12px;color:#dc2626;font-weight:600;
                background:rgba(239,68,68,.08);padding:3px 12px;border-radius:8px">
                ניסיון {attempts}</div>
        </div>""", unsafe_allow_html=True)


def render_giveup_card(country):
    display_name = country.get("name_he", country["name"])
    capital_display = country.get("capital_he", country["capital"])
    st.markdown(
        f"""<div style="background:linear-gradient(145deg,#fffbeb,#fef3c7,#fde68a);
            border:3px solid #f59e0b;border-radius:24px;padding:28px 22px;
            text-align:center;min-height:210px;display:flex;flex-direction:column;
            align-items:center;justify-content:center;
            box-shadow:0 8px 28px rgba(245,158,11,.10);
            position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:4px;
                background:linear-gradient(90deg,#f59e0b,#fbbf24,#f59e0b)"></div>
            <div style="font-size:42px;margin-bottom:8px">🏳️</div>
            <div style="font-size:16px;font-weight:600;color:#92400e;margin-bottom:4px">
                עיר הבירה של {display_name} היא</div>
            <div style="font-size:32px;font-weight:900;color:#78350f;margin:4px 0;
                text-shadow:0 1px 2px rgba(0,0,0,.04)">{capital_display}</div>
            <div style="margin-top:12px;background:rgba(255,255,255,.55);border-radius:12px;
                padding:7px 16px;font-size:14px;font-weight:600;color:#92400e">
                בפעם הבאה תצליחו! 💪</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# WELCOME SCREEN
# ═══════════════════════════════════════════════════════════════════════════════

def render_welcome():
    st.markdown("""
        <div style="text-align:center;padding:10px 0 4px">
            <div style="font-size:54px;font-weight:900;letter-spacing:2px;
                background:linear-gradient(135deg,#6366f1,#a78bfa,#ec4899,#f97316,#eab308);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:2px">🌍 חידון ערי בירה 🏙️</div>
            <div style="font-size:19px;color:#64748b;font-weight:500;margin-bottom:4px">
                למדו את ערי הבירה של העולם — כרטיס אחרי כרטיס!</div>
            <div style="height:3px;width:100px;margin:8px auto 0;border-radius:2px;
                background:linear-gradient(90deg,#6366f1,#a78bfa,#ec4899)"></div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# WINNER BANNER
# ═══════════════════════════════════════════════════════════════════════════════

def render_winner(name, stats, mode):
    key = stats["best_streak"] if mode == "longest_streak" else stats["correct"]
    label = "שיא רצף" if mode == "longest_streak" else "תשובות נכונות"
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#fef3c7,#fde68a,#fbbf24);
            color:#78350f;border-radius:24px;padding:26px;text-align:center;
            font-size:28px;font-weight:900;margin:14px 0;
            box-shadow:0 12px 40px rgba(251,191,36,.2);
            border:3px solid rgba(245,158,11,.25);position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:4px;
                background:linear-gradient(90deg,#f59e0b,#fbbf24,#f59e0b)"></div>
            👑 {name} מנצח עם {key} {label}! 👑
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PLAYER HEADER BANNER  (reusable for single + multi)
# ═══════════════════════════════════════════════════════════════════════════════

def render_player_banner(name, stars, streak, color="#6366f1", icon="🧒"):
    st.markdown(
        f"""<div style="background:linear-gradient(135deg,{color},{color}cc);
            color:white;text-align:center;padding:8px 20px;
            border-radius:16px;font-size:16px;font-weight:800;margin-bottom:6px;
            box-shadow:0 8px 24px {color}22;display:flex;align-items:center;
            justify-content:center;gap:18px;border:2px solid rgba(255,255,255,.12);
            flex-wrap:wrap">
            <span>{icon} {name}</span>
            <span style="background:rgba(255,255,255,.15);padding:4px 14px;
                border-radius:12px;font-size:15px">⭐ {stars}</span>
            <span style="background:rgba(255,255,255,.15);padding:4px 14px;
                border-radius:12px;font-size:15px">🔥 רצף: {streak}</span>
        </div>""", unsafe_allow_html=True)

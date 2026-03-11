"""Build a standalone HTML file for the Capital Cities Quiz Game."""
import os, base64, json

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_img_cache")
DATA  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "countries_data.json")
OUT   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quiz.html")

# Load country data
with open(DATA, encoding="utf-8") as f:
    countries = json.load(f)["countries"]

# Load images as base64
images = {}
for c in countries:
    code = c["country_code"]
    path = os.path.join(CACHE, f"{code}.jpg")
    if os.path.exists(path):
        with open(path, "rb") as f:
            images[code] = base64.b64encode(f.read()).decode()
    else:
        images[code] = ""

# ISO numeric codes for TopoJSON
iso_num = {
    "fr":"250","jp":"392","br":"076","eg":"818","au":"036",
    "in":"356","gb":"826","it":"380","mx":"484","kr":"410",
    "ca":"124","de":"276","cn":"156","ar":"032","ke":"404",
    "es":"724","tr":"792","th":"764","za":"710","pe":"604",
    "gr":"300","ru":"643","no":"578","ma":"504","nz":"554",
}

# Continent themes
themes = {
    "אירופה":      ["#4fc3f7","#0288d1","#01579b"],
    "אסיה":        ["#ef5350","#c62828","#7f0000"],
    "אפריקה":      ["#ffb74d","#ef6c00","#bf360c"],
    "דרום אמריקה": ["#66bb6a","#2e7d32","#1b5e20"],
    "צפון אמריקה": ["#ab47bc","#7b1fa2","#4a148c"],
    "אוקיאניה":    ["#26c6da","#00838f","#004d40"],
}

# Build countries JSON for JS
js_countries = []
for c in countries:
    code = c["country_code"]
    js_countries.append({
        "name": c["name"],
        "name_he": c["name_he"],
        "capital": c["capital"],
        "capital_he": c["capital_he"],
        "alternatives": c.get("alternatives", []),
        "code": code,
        "area_km2": c["area_km2"],
        "continent": c["continent"],
        "country_lat": c["country_lat"],
        "country_lng": c["country_lng"],
        "capital_lat": c["capital_lat"],
        "capital_lng": c["capital_lng"],
        "landmark": c["landmark"],
        "fun_fact": c["fun_fact"],
        "hint": c["hint"],
        "img": images.get(code, ""),
        "iso_num": iso_num.get(code, ""),
        "theme": themes.get(c["continent"], ["#4fc3f7","#0288d1","#01579b"]),
    })

countries_json = json.dumps(js_countries, ensure_ascii=False)

html = r'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🌍 חידון ערי בירה</title>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Rubik','Segoe UI',sans-serif;background:linear-gradient(160deg,#f0f4ff,#e0e7ff,#dbeafe);
  min-height:100vh;direction:rtl;overflow-x:hidden}

/* Animations */
@keyframes cardIn{0%{opacity:0;transform:perspective(800px) rotateY(-6deg) translateY(16px) scale(.97)}100%{opacity:1;transform:none}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes glow{0%,100%{box-shadow:0 4px 16px rgba(0,0,0,.3)}50%{box-shadow:0 4px 16px rgba(0,0,0,.3),0 0 24px rgba(255,255,255,.2)}}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}
@keyframes fadeIn{0%{opacity:0;transform:translateY(10px)}100%{opacity:1;transform:none}}
@keyframes confetti{0%{transform:translateY(0) rotate(0);opacity:1}100%{transform:translateY(50vh) rotate(720deg);opacity:0}}

/* Welcome Screen */
.welcome{display:flex;flex-direction:column;align-items:center;justify-content:center;
  min-height:100vh;text-align:center;padding:20px}
.welcome h1{font-size:3.5rem;font-weight:900;background:linear-gradient(135deg,#6366f1,#a78bfa,#ec4899);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
.welcome p{font-size:1.3rem;color:#475569;margin-bottom:30px}
.welcome-card{background:white;border-radius:28px;padding:40px;box-shadow:0 20px 60px rgba(99,102,241,.12);
  max-width:500px;width:100%;border:2px solid #e0e7ff}
.welcome input[type="text"]{width:100%;padding:16px;border-radius:16px;border:2px solid #c7d2fe;
  font-size:20px;font-weight:600;text-align:center;font-family:inherit;direction:rtl;
  outline:none;transition:border .2s,box-shadow .2s;margin:14px 0}
.welcome input[type="text"]:focus{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.18)}
.btn{border:none;border-radius:16px;padding:14px 36px;font-size:18px;font-weight:800;
  cursor:pointer;transition:all .2s;box-shadow:0 4px 14px rgba(0,0,0,.1);font-family:inherit}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.16)}
.btn:active{transform:translateY(0)}
.btn-primary{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff}
.btn-success{background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff}
.btn-danger{background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff}

/* Game Layout */
.game-container{max-width:1200px;margin:0 auto;padding:10px 16px}
.banner{background:linear-gradient(135deg,#6366f1,#6366f1cc);color:white;text-align:center;
  padding:8px 20px;border-radius:16px;font-size:16px;font-weight:800;margin-bottom:6px;
  display:flex;align-items:center;justify-content:center;gap:18px;flex-wrap:wrap;
  box-shadow:0 8px 24px rgba(99,102,241,.12);border:2px solid rgba(255,255,255,.12)}
.banner span{background:rgba(255,255,255,.15);padding:4px 14px;border-radius:12px;font-size:15px}
.columns{display:grid;grid-template-columns:3fr 2fr;gap:12px;align-items:start}

/* Country Card */
.country-card{border-radius:24px;color:#fff;text-align:center;position:relative;overflow:hidden;
  box-shadow:0 20px 60px rgba(0,0,0,.22);border:2px solid rgba(255,255,255,.2);
  animation:cardIn .65s cubic-bezier(.22,.68,0,1.15) both}
.country-card .rarity{height:5px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.5),transparent);
  background-size:200% 100%;animation:shimmer 2.5s ease-in-out infinite}
.country-card .photo{width:100%;height:170px;object-fit:cover;display:block}
.country-card .photo-overlay{position:absolute;top:0;left:0;right:0;height:230px;
  background:linear-gradient(transparent 60%,var(--c2))}
.country-card .flag-wrap{margin:-28px auto 0;position:relative;z-index:2;text-align:center}
.country-card .flag{width:76px;border-radius:10px;display:block;margin:0 auto;
  box-shadow:0 6px 20px rgba(0,0,0,.3);border:3px solid rgba(255,255,255,.45);
  animation:glow 3.5s ease-in-out infinite}
.country-card .body{padding:6px 18px 14px;position:relative;z-index:1}
.country-card .name{font-size:26px;font-weight:900;letter-spacing:1px;margin:6px 0 2px;
  text-shadow:0 2px 8px rgba(0,0,0,.25)}
.country-card .continent{display:inline-flex;align-items:center;gap:5px;
  background:rgba(255,255,255,.14);backdrop-filter:blur(6px);
  padding:4px 16px;border-radius:20px;font-size:13px;font-weight:700;
  color:rgba(255,255,255,.88);margin:4px 0 10px;border:1px solid rgba(255,255,255,.15)}
.country-card .landmark{font-size:17px;font-weight:700;color:rgba(255,255,255,.85);margin:2px 0 8px}
.country-card .chip{display:inline-flex;align-items:center;gap:4px;background:rgba(255,255,255,.1);
  border-radius:10px;padding:5px 14px;font-size:13px;font-weight:600;border:1px solid rgba(255,255,255,.1)}
.country-card .funfact{background:rgba(0,0,0,.14);border-radius:14px;padding:10px 14px;
  border-right:4px solid rgba(255,215,0,.65);text-align:right;font-size:14px;
  line-height:1.7;color:rgba(255,255,255,.9);backdrop-filter:blur(4px);margin-top:8px}
.country-card .ff-label{font-size:11px;font-weight:800;color:rgba(255,215,0,.75);letter-spacing:1px;margin-bottom:3px}

/* Map */
.map-section{margin-top:-8px}
.map-toggle{background:rgba(255,255,255,.55);border-radius:20px;border:2px solid rgba(99,102,241,.10);
  padding:10px 16px;cursor:pointer;font-weight:700;font-size:16px;font-family:inherit;
  width:100%;text-align:right;display:flex;align-items:center;gap:8px;
  box-shadow:0 4px 16px rgba(0,0,0,.04);backdrop-filter:blur(8px)}
.map-container{border-radius:16px;overflow:hidden;margin-top:6px}
#map{width:100%;height:340px;border-radius:16px}
.leaflet-tooltip{font-weight:700;font-size:13px;border:none;background:rgba(255,255,255,.92);
  border-radius:10px;padding:4px 10px;box-shadow:0 3px 10px rgba(0,0,0,.15)}

/* Answer Panel */
.answer-panel{animation:fadeIn .4s ease-out}
.answer-card{background:linear-gradient(135deg,#ffffff,#f8fafc);border-radius:24px;
  padding:34px 24px 28px;text-align:center;box-shadow:0 8px 32px rgba(99,102,241,.08);
  border:2px solid #e0e7ff;position:relative;overflow:hidden;
  min-height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.answer-card .top-bar{position:absolute;top:0;left:0;right:0;height:5px;
  background:linear-gradient(90deg,#6366f1,#a78bfa,#ec4899)}
.answer-card .q-icon{font-size:56px;line-height:1;margin-bottom:10px;opacity:.15}
.answer-card .q-title{font-size:26px;font-weight:900;background:linear-gradient(135deg,#312e81,#4f46e5);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
.answer-card .q-sub{font-size:18px;color:#64748b;font-weight:500}
.answer-input{width:100%;padding:16px 20px;border-radius:16px;border:2px solid #c7d2fe;
  font-size:20px;font-weight:600;text-align:center;font-family:inherit;direction:rtl;
  outline:none;transition:border .2s,box-shadow .2s;margin:14px 0;background:rgba(255,255,255,.9)}
.answer-input:focus{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.18)}
.btn-row{display:flex;gap:10px;width:100%;margin-top:6px}
.btn-row .btn{flex:1;padding:12px 24px;font-size:18px}

/* Hint Box */
.hint-box{background:linear-gradient(135deg,#eef2ff,#e0e7ff);border-radius:16px;
  padding:12px 16px;margin:10px 0;direction:rtl;border:1px solid #c7d2fe;
  display:flex;align-items:center;gap:10px;box-shadow:0 2px 8px rgba(99,102,241,.06)}
.hint-icon{width:34px;height:34px;border-radius:10px;background:#6366f1;
  display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;color:#fff}
.hint-text{font-size:15px;font-weight:600;color:#312e81;line-height:1.5}
.hint-box.extra{background:linear-gradient(135deg,#fef3c7,#fde68a);border-color:#fbbf24}
.hint-box.extra .hint-icon{background:#f59e0b}
.hint-box.extra .hint-text{color:#78350f}

/* Wrong Card */
.wrong-card{background:linear-gradient(145deg,#fef2f2,#fecaca,#fca5a5);border:3px solid #ef4444;
  border-radius:24px;padding:26px 22px;text-align:center;min-height:150px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  box-shadow:0 8px 28px rgba(239,68,68,.1);animation:shake .35s ease-in-out}
.wrong-card .emoji{font-size:42px;margin-bottom:6px}
.wrong-card .msg{font-size:19px;font-weight:800;color:#991b1b}

/* Celebration Card */
.celebration-card{background:linear-gradient(145deg,#dcfce7,#bbf7d0,#86efac);border:3px solid #22c55e;
  border-radius:24px;padding:32px 24px;text-align:center;min-height:260px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  box-shadow:0 12px 40px rgba(34,197,94,.15);position:relative;overflow:hidden}
.celebration-card .top-bar{position:absolute;top:0;left:0;right:0;height:4px;
  background:linear-gradient(90deg,#22c55e,#86efac,#22c55e)}
.celebration-card .emoji{font-size:52px;margin-bottom:8px}
.celebration-card .title{font-size:28px;font-weight:900;color:#15803d;margin-bottom:6px}
.celebration-card .capital{font-size:34px;font-weight:900;color:#166534}
.celebration-card .badges{display:flex;gap:12px;justify-content:center;margin-top:14px}
.celebration-card .badge{background:rgba(255,255,255,.8);border-radius:12px;padding:6px 16px;
  font-size:14px;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,.06)}

/* Giveup Card */
.giveup-card{background:linear-gradient(145deg,#fefce8,#fef08a,#fde047);border:3px solid #eab308;
  border-radius:24px;padding:28px 22px;text-align:center;min-height:220px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  box-shadow:0 8px 28px rgba(234,179,8,.1)}

/* Stats Sidebar (left side on desktop) */
.stats-panel{position:fixed;top:10px;left:10px;width:180px;background:linear-gradient(180deg,#0f172a,#1e293b);
  border-radius:20px;padding:16px;color:#e2e8f0;z-index:100;
  box-shadow:0 12px 40px rgba(0,0,0,.2);display:none}
.stats-panel.visible{display:block}
.stats-title{text-align:center;font-size:16px;font-weight:900;margin-bottom:10px}
.stats-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-bottom:8px}
.stat-cell{background:rgba(255,255,255,.06);border-radius:12px;padding:6px 2px;text-align:center}
.stat-cell .val{font-size:18px;font-weight:900}
.stat-cell .label{font-size:9px;opacity:.6}
.stat-row{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.04);
  border-radius:10px;padding:5px 10px;margin:3px 0;direction:rtl}
.stat-row .icon{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;
  justify-content:center;font-size:14px;flex-shrink:0}
.stat-row .info{flex:1;text-align:right}
.stat-row .info .label{font-size:10px;opacity:.5}
.stat-row .info .val{font-size:15px;font-weight:800}

/* Confetti */
.confetti-piece{position:fixed;top:-20px;z-index:9999;pointer-events:none;font-size:24px}

/* Responsive */
@media(max-width:900px){
  .columns{grid-template-columns:1fr}
  .stats-panel{position:static;width:100%;margin-bottom:10px;display:none}
  .stats-panel.visible{display:block}
}
</style>
</head>
<body>

<div id="app"></div>

<script>
const COUNTRIES = ''' + countries_json + r''';

const TOPO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";
const FLAG_CDN = "https://flagcdn.com/w320";

// ── Game State ──
let state = {
  screen: "welcome",
  playerName: "חוקר",
  countries: [],
  usedCodes: [],
  current: null,
  turnState: "guessing", // guessing | wrong | correct | gave_up
  hintLevel: 0,
  wrongAttempts: 0,
  stars: 0,
  correct: 0,
  wrong_guesses: 0,
  give_ups: 0,
  total_questions: 0,
  current_streak: 0,
  best_streak: 0,
  success_rate: 0,
};

function loadStats(){
  try{
    const s = JSON.parse(localStorage.getItem("capitalQuizStats")||"{}");
    if(s.stars !== undefined){
      state.stars=s.stars; state.correct=s.correct; state.wrong_guesses=s.wrong_guesses;
      state.give_ups=s.give_ups; state.total_questions=s.total_questions;
      state.current_streak=s.current_streak; state.best_streak=s.best_streak;
      state.success_rate=s.success_rate; state.playerName=s.playerName||"חוקר";
    }
  }catch(e){}
}
function saveStats(){
  try{
    localStorage.setItem("capitalQuizStats", JSON.stringify({
      stars:state.stars, correct:state.correct, wrong_guesses:state.wrong_guesses,
      give_ups:state.give_ups, total_questions:state.total_questions,
      current_streak:state.current_streak, best_streak:state.best_streak,
      success_rate:state.success_rate, playerName:state.playerName
    }));
  }catch(e){}
}
function updateSuccessRate(){
  const t = state.correct + state.wrong_guesses + state.give_ups;
  state.success_rate = t > 0 ? Math.round(state.correct / t * 100) : 0;
}

// ── Helpers ──
function formatArea(km2){
  if(km2>=1000000) return (km2/1000000).toFixed(1)+"M קמ״ר";
  return km2.toLocaleString()+" קמ״ר";
}

function normalize(s){ return s.trim().toLowerCase(); }

function similarity(a,b){
  const la=a.length, lb=b.length;
  const dp=Array.from({length:la+1},()=>Array(lb+1).fill(0));
  for(let i=1;i<=la;i++) for(let j=1;j<=lb;j++)
    dp[i][j]=a[i-1]===b[j-1]?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]);
  return 2*dp[la][lb]/(la+lb);
}

function checkAnswer(guess, country){
  if(!guess) return false;
  const ng = normalize(guess);
  const nc = normalize(country.capital_he);
  if(ng===nc) return true;
  for(const alt of country.alternatives||[]){
    if(ng===normalize(alt)) return true;
  }
  if(ng===normalize(country.capital)) return true;
  if(similarity(ng,nc)>=0.85 && ng.length>=3) return true;
  return false;
}

function getHint(capital, level){
  if(level===1) return "מתחיל באות <b>"+capital[0]+"</b>";
  if(level===2) return "מתחיל ב-<b>"+capital[0]+"</b> ומסתיים ב-<b>"+capital[capital.length-1]+"</b>";
  if(level===3) return "מכיל <b>"+capital.length+"</b> אותיות ומתחיל ב-<b>"+capital.slice(0,2)+"</b>";
  let h="";
  for(let i=0;i<capital.length;i++){
    if(capital[i]===" ") h+="  ";
    else if(i===0||i===capital.length-1) h+=capital[i];
    else h+=" _ ";
  }
  return "השלם: <b>"+h+"</b>";
}

function pickCountry(){
  const available = COUNTRIES.filter(c => !state.usedCodes.includes(c.code));
  if(available.length===0){
    state.usedCodes=[];
    return COUNTRIES[Math.floor(Math.random()*COUNTRIES.length)];
  }
  return available[Math.floor(Math.random()*available.length)];
}

function newQuestion(){
  state.current = pickCountry();
  state.usedCodes.push(state.current.code);
  state.turnState = "guessing";
  state.hintLevel = 0;
  state.wrongAttempts = 0;
  render();
  setTimeout(()=>initMap(),100);
}

// ── Confetti ──
function showConfetti(){
  const pieces = ["🎉","⭐","🌟","🎊","✨","🎈","💫"];
  for(let i=0;i<30;i++){
    const el=document.createElement("div");
    el.className="confetti-piece";
    el.textContent=pieces[Math.floor(Math.random()*pieces.length)];
    el.style.left=Math.random()*100+"vw";
    el.style.animationDuration=(2+Math.random()*2)+"s";
    el.style.animation=`confetti ${2+Math.random()*2}s ease-out forwards`;
    el.style.animationDelay=Math.random()*0.5+"s";
    document.body.appendChild(el);
    setTimeout(()=>el.remove(),4000);
  }
}

// ── Map ──
let mapInstance = null;
function initMap(){
  const c = state.current;
  if(!c) return;
  const el = document.getElementById("map");
  if(!el) return;
  if(mapInstance){ mapInstance.remove(); mapInstance=null; }
  mapInstance = L.map("map",{scrollWheelZoom:false}).setView([c.country_lat,c.country_lng],3);
  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
    {attribution:"© OSM, © CARTO",maxZoom:18}).addTo(mapInstance);
  fetch(TOPO_URL).then(r=>r.json()).then(t=>{
    const geo = topojson.feature(t, t.objects.countries);
    const ff = geo.features.filter(f=>f.id===c.iso_num);
    if(ff.length){
      const lyr = L.geoJSON(ff,{style:{color:"#6366f1",weight:2.5,fillColor:"#818cf8",fillOpacity:0.18}}).addTo(mapInstance);
      mapInstance.fitBounds(lyr.getBounds(),{padding:[30,30]});
    }
  });
}

// ── Render ──
function render(){
  const app = document.getElementById("app");
  if(state.screen==="welcome"){
    app.innerHTML = renderWelcome();
  } else if(state.screen==="playing"){
    app.innerHTML = renderGame();
  }
}

function renderWelcome(){
  return `<div class="welcome">
    <h1>🌍 חידון ערי בירה</h1>
    <p>כמה ערי בירה אתם מכירים?</p>
    <div class="welcome-card">
      <div style="font-size:80px;margin-bottom:10px">🗺️</div>
      <div style="font-size:20px;font-weight:700;color:#1e293b;margin-bottom:4px">הכניסו את שמכם</div>
      <input type="text" id="nameInput" value="${state.playerName}" placeholder="השם שלך...">
      <div style="margin-top:16px">
        <button class="btn btn-primary" onclick="startGame()" style="width:100%;font-size:22px;padding:16px">
          🚀 יאללה, בואו נשחק!
        </button>
      </div>
    </div>
  </div>`;
}

function renderGame(){
  const c = state.current;
  const [c1,c2,c3] = c.theme;
  const imgSrc = c.img ? "data:image/jpeg;base64,"+c.img : "";
  const flagUrl = FLAG_CDN+"/"+c.code+".png";

  const photoBlock = imgSrc ? `<img class="photo" src="${imgSrc}" alt="${c.landmark}" onerror="this.style.display='none'">` : "";

  let rightPanel = "";
  if(state.turnState==="guessing"){
    rightPanel = renderAnswerPrompt(c);
  } else if(state.turnState==="wrong"){
    rightPanel = renderWrongPanel(c);
  } else if(state.turnState==="correct"){
    rightPanel = renderCelebration(c);
  } else if(state.turnState==="gave_up"){
    rightPanel = renderGiveup(c);
  }

  return `
  ${renderStats()}
  <div class="game-container">
    <div class="banner">
      <span>🧒 ${state.playerName}</span>
      <span>⭐ ${state.stars}</span>
      <span>🔥 רצף: ${state.current_streak}</span>
    </div>
    <div class="columns">
      <div>
        <div class="country-card" style="background:linear-gradient(165deg,${c1},${c2},${c3});--c2:${c2}">
          <div class="rarity"></div>
          <div style="position:relative;overflow:hidden">
            ${photoBlock}
            <div class="photo-overlay"></div>
          </div>
          <div class="flag-wrap"><img class="flag" src="${flagUrl}" alt="flag" onerror="this.style.display='none'"></div>
          <div class="body">
            <div class="name">${c.name_he}</div>
            <div><span class="continent">🌍 ${c.continent}</span></div>
            <div style="width:55%;height:1px;margin:0 auto 10px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent)"></div>
            <div class="landmark">🏛️ ${c.landmark}</div>
            <div style="margin:4px 0 8px"><span class="chip">📏 ${formatArea(c.area_km2)}</span></div>
            <div class="funfact">
              <div class="ff-label">💡 הידעת?</div>
              ${c.fun_fact}
            </div>
          </div>
        </div>
        <div class="map-section">
          <div class="map-toggle" onclick="toggleMap()">🌍 איפה בעולם? ▼</div>
          <div class="map-container" id="mapContainer" style="display:block">
            <div id="map"></div>
          </div>
        </div>
      </div>
      <div class="answer-panel">
        ${rightPanel}
      </div>
    </div>
    <div style="text-align:center;margin-top:14px">
      <button class="btn" onclick="endGame()" style="background:linear-gradient(135deg,#94a3b8,#64748b);color:#fff;font-size:14px;padding:10px 24px">
        🏠 סיום ושמירה
      </button>
    </div>
  </div>`;
}

function renderAnswerPrompt(c){
  return `<div class="answer-card">
    <div class="top-bar"></div>
    <div class="q-icon">❓</div>
    <div class="q-title">מהי עיר הבירה?</div>
    <div class="q-sub">מהי עיר הבירה של <b style="color:#1e293b">${c.name_he}</b>?</div>
  </div>
  <input type="text" class="answer-input" id="answerInput" placeholder="הקלידו את שם עיר הבירה פה..."
    onkeydown="if(event.key==='Enter')submitAnswer()">
  <div class="btn-row">
    <button class="btn btn-primary" onclick="submitAnswer()">✅ שליחה</button>
    <button class="btn btn-danger" onclick="giveUp()">🏳️ ויתור</button>
  </div>`;
}

function renderWrongPanel(c){
  const msg = state.wrongAttempts<3 ? "לא בדיוק — נסו שוב! 💪" : "כמעט שם, המשיכו! 🌟";
  const capital = c.capital_he;
  let hints = "";
  for(let i=1;i<=state.hintLevel;i++){
    hints += `<div class="hint-box"><div class="hint-icon">💡</div><div class="hint-text">${getHint(capital,i)}</div></div>`;
  }
  if(state.wrongAttempts>=2 && c.hint){
    hints += `<div class="hint-box extra"><div class="hint-icon">🔎</div><div class="hint-text">${c.hint}</div></div>`;
  }
  return `<div class="wrong-card">
    <div class="emoji">😅</div>
    <div class="msg">${msg}</div>
    <div style="font-size:14px;color:#7f1d1d;margin-top:4px">ניסיונות: ${state.wrongAttempts}</div>
  </div>
  ${hints}
  <input type="text" class="answer-input" id="answerInput" placeholder="נסו שוב..."
    onkeydown="if(event.key==='Enter')submitAnswer()">
  <div class="btn-row">
    <button class="btn btn-primary" onclick="submitAnswer()">✅ שליחה</button>
    <button class="btn btn-danger" onclick="giveUp()">🏳️ ויתור</button>
  </div>`;
}

function renderCelebration(c){
  return `<div class="celebration-card">
    <div class="top-bar"></div>
    <div class="emoji">🎉</div>
    <div class="title">!נכון מצוין</div>
    <div class="capital">${c.capital_he}</div>
    <div class="badges">
      <span class="badge" style="color:#15803d">⭐ +1 כוכב</span>
      <span class="badge" style="color:#dc2626">🔥 רצף: ${state.current_streak}</span>
    </div>
  </div>
  <div style="margin-top:14px">
    <button class="btn btn-success" onclick="newQuestion()" style="width:100%;font-size:20px;padding:14px">
      ➡️ מדינה הבאה
    </button>
  </div>`;
}

function renderGiveup(c){
  return `<div class="giveup-card">
    <div style="font-size:46px;margin-bottom:8px">🏳️</div>
    <div style="font-size:22px;font-weight:900;color:#854d0e">:התשובה הנכונה היא</div>
    <div style="font-size:36px;font-weight:900;color:#713f12;margin:8px 0">${c.capital_he}</div>
    <div style="font-size:14px;color:#92400e;line-height:1.8">
      אל תדאגו, בפעם הבאה תזכרו! 💪
    </div>
  </div>
  <div style="margin-top:14px">
    <button class="btn btn-success" onclick="newQuestion()" style="width:100%;font-size:20px;padding:14px">
      ➡️ מדינה הבאה
    </button>
  </div>`;
}

function renderStats(){
  return `<div class="stats-panel visible">
    <div class="stats-title">📊 הסטטיסטיקות שלך</div>
    <div style="height:3px;width:50%;margin:0 auto 8px;border-radius:2px;background:linear-gradient(90deg,#6366f1,#a78bfa,#6366f1)"></div>
    <div class="stats-grid">
      <div class="stat-cell"><div class="label">כוכבים</div><div class="val">⭐ ${state.stars}</div></div>
      <div class="stat-cell"><div class="label">רצף</div><div class="val">🔥 ${state.current_streak}</div></div>
      <div class="stat-cell"><div class="label">שיא רצף</div><div class="val">🏅 ${state.best_streak}</div></div>
    </div>
    <div style="height:1px;background:rgba(255,255,255,.08);margin:4px 0"></div>
    <div class="stat-row"><div class="icon" style="background:#22c55e22;border:1px solid #22c55e33">✅</div><div class="info"><div class="label">נכונות</div><div class="val">${state.correct}</div></div></div>
    <div class="stat-row"><div class="icon" style="background:#ef444422;border:1px solid #ef444433">❌</div><div class="info"><div class="label">שגויות</div><div class="val">${state.wrong_guesses}</div></div></div>
    <div class="stat-row"><div class="icon" style="background:#a1a1aa22;border:1px solid #a1a1aa33">🏳️</div><div class="info"><div class="label">ויתורים</div><div class="val">${state.give_ups}</div></div></div>
    <div class="stat-row"><div class="icon" style="background:#6366f122;border:1px solid #6366f133">📈</div><div class="info"><div class="label">אחוז הצלחה</div><div class="val">${state.success_rate}%</div></div></div>
    <div class="stat-row"><div class="icon" style="background:#0ea5e922;border:1px solid #0ea5e933">🎯</div><div class="info"><div class="label">שאלות</div><div class="val">${state.total_questions}</div></div></div>
  </div>`;
}

// ── Actions ──
function startGame(){
  const input = document.getElementById("nameInput");
  if(input && input.value.trim()) state.playerName = input.value.trim();
  state.screen = "playing";
  state.usedCodes = [];
  newQuestion();
}

function submitAnswer(){
  const input = document.getElementById("answerInput");
  if(!input || !input.value.trim()) return;
  const guess = input.value.trim();
  if(checkAnswer(guess, state.current)){
    state.correct++;
    state.stars++;
    state.total_questions++;
    state.current_streak++;
    if(state.current_streak > state.best_streak) state.best_streak = state.current_streak;
    updateSuccessRate();
    saveStats();
    state.turnState = "correct";
    render();
    showConfetti();
    setTimeout(()=>initMap(),100);
  } else {
    state.wrong_guesses++;
    state.wrongAttempts++;
    state.hintLevel++;
    state.turnState = "wrong";
    render();
    setTimeout(()=>{
      const inp = document.getElementById("answerInput");
      if(inp) inp.focus();
      initMap();
    },100);
  }
}

function giveUp(){
  state.give_ups++;
  state.total_questions++;
  state.current_streak = 0;
  updateSuccessRate();
  saveStats();
  state.turnState = "gave_up";
  render();
  setTimeout(()=>initMap(),100);
}

function toggleMap(){
  const mc = document.getElementById("mapContainer");
  if(mc) mc.style.display = mc.style.display==="none" ? "block" : "none";
  setTimeout(()=>{if(mapInstance) mapInstance.invalidateSize();},200);
}

function endGame(){
  saveStats();
  state.screen = "welcome";
  render();
}

// ── Init ──
loadStats();
render();
</script>
</body>
</html>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size = os.path.getsize(OUT)
print(f"Created quiz.html: {size:,} bytes = {size/1024/1024:.2f} MB")

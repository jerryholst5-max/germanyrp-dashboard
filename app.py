import os, requests
from flask import Flask, redirect, request, session, jsonify, Response
from pymongo import MongoClient
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "grp2026")
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://germanyrp-dashboard-production.up.railway.app/callback")
BOT_OWNER_ID = "1408144132966322407"
DISCORD_API = "https://discord.com/api/v10"
mongo_client = MongoClient(os.environ.get("MONGODB_URL"))
db = mongo_client["germanyrp"]

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f0f0f;--bg2:#1a1a1a;--bg3:#242424;--border:#2e2e2e;--text:#e8e8e8;--text2:#999;--accent:#f0a500;--red:#e05252;--green:#52c078;--radius:10px}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh}
.layout{display:flex;min-height:100vh}
.sidebar{width:250px;background:var(--bg2);border-right:1px solid var(--border);padding:1.25rem 1rem;display:flex;flex-direction:column;gap:.25rem;flex-shrink:0;overflow-y:auto}
.logo{display:flex;align-items:center;gap:10px;padding:.5rem;margin-bottom:.75rem;font-size:15px;font-weight:700;color:var(--accent)}
.logo img{width:32px;height:32px;border-radius:50%;object-fit:cover}
.back-btn{display:flex;align-items:center;gap:6px;padding:.4rem .6rem;border-radius:6px;color:var(--text2);font-size:12px;text-decoration:none;margin-bottom:.5rem;transition:all .15s}
.back-btn:hover{background:var(--bg3);color:var(--text)}
.nav-section{font-size:10px;color:var(--text2);padding:.75rem .6rem .25rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600}
.nav-item{display:flex;align-items:center;gap:8px;padding:.55rem .7rem;border-radius:8px;color:var(--text2);font-size:13px;text-decoration:none;transition:all .15s;cursor:pointer;border:none;background:none;width:100%;text-align:left}
.nav-item:hover,.nav-item.active{background:var(--bg3);color:var(--text)}
.main{flex:1;padding:2rem;overflow-y:auto;max-width:900px}
.page-title{font-size:22px;font-weight:700;margin-bottom:.3rem}
.page-sub{color:var(--text2);font-size:13px;margin-bottom:2rem}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-bottom:1.25rem}
.card-title{font-size:14px;font-weight:700;margin-bottom:1.25rem;display:flex;align-items:center;gap:8px;color:var(--text);letter-spacing:.3px}
.section-divider{border:none;border-top:1px solid var(--border);margin:1.25rem 0}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}
.form-grid.cols3{grid-template-columns:1fr 1fr 1fr}
.form-grid.full{grid-template-columns:1fr}
.form-group{display:flex;flex-direction:column;gap:5px}
.form-label{font-size:12px;color:var(--text2);font-weight:500;letter-spacing:.3px}
.form-input,.form-select,.form-textarea{background:var(--bg3);border:1px solid var(--border);border-radius:8px;color:var(--text);padding:.6rem .8rem;font-size:13px;width:100%;outline:none;transition:border-color .15s;font-family:inherit}
.form-textarea{resize:vertical;min-height:80px}
.form-input:focus,.form-select:focus,.form-textarea:focus{border-color:var(--accent)}
.toggle-row{display:flex;align-items:center;justify-content:space-between;padding:.9rem 0;border-bottom:1px solid var(--border)}
.toggle-row:last-of-type{border-bottom:none}
.toggle-info .tl{font-size:14px;font-weight:500;margin-bottom:2px}
.toggle-info .td{font-size:12px;color:var(--text2)}
.toggle{position:relative;width:44px;height:24px;flex-shrink:0}
.toggle input{opacity:0;width:0;height:0}
.slider{position:absolute;inset:0;background:var(--border);border-radius:24px;cursor:pointer;transition:.2s}
.slider:before{content:"";position:absolute;height:18px;width:18px;left:3px;top:3px;background:white;border-radius:50%;transition:.2s}
input:checked+.slider{background:var(--accent)}
input:checked+.slider:before{transform:translateX(20px)}
.btn{padding:.6rem 1.25rem;border-radius:8px;border:none;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:var(--accent);color:#000}
.btn-primary:hover{opacity:.9}
.btn-danger{background:var(--red);color:white}
.btn-danger:hover{opacity:.85}
.btn-ghost{background:var(--bg3);color:var(--text);border:1px solid var(--border)}
.btn-ghost:hover{border-color:var(--accent)}
.alert{padding:.8rem 1rem;border-radius:8px;font-size:13px;margin-bottom:1rem;display:none}
.alert-success{background:rgba(82,192,120,.15);border:1px solid rgba(82,192,120,.3);color:var(--green)}
.alert-error{background:rgba(224,82,82,.15);border:1px solid rgba(224,82,82,.3);color:var(--red)}
.page{display:none}
.page.active{display:block}
.partner-card{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:1rem;display:flex;align-items:center;justify-content:space-between;margin-bottom:.75rem}
.partner-info .pname{font-weight:600;font-size:14px;margin-bottom:3px}
.partner-info .pkat{font-size:11px;color:var(--accent);background:rgba(240,165,0,.15);padding:2px 8px;border-radius:4px;display:inline-block;margin-bottom:4px}
.partner-info .plink{font-size:12px;color:var(--text2)}
.partner-info .pap{font-size:12px;color:var(--text2)}
.ticket-kat-card{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:.75rem 1rem;display:flex;align-items:center;justify-content:space-between;margin-bottom:.5rem}
.overview-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:1rem}
.ov-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.25rem;text-align:center;cursor:pointer;transition:all .2s}
.ov-card:hover{border-color:var(--accent);transform:translateY(-2px)}
.ov-icon{font-size:28px;margin-bottom:.5rem}
.ov-label{font-size:13px;font-weight:600}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;background:rgba(240,165,0,.15);color:var(--accent)}
.tag{display:inline-flex;align-items:center;gap:5px;padding:.3rem .7rem;border-radius:6px;font-size:12px;background:var(--bg3);border:1px solid var(--border);margin:.25rem}
@media(max-width:768px){.sidebar{display:none}.form-grid{grid-template-columns:1fr}}
"""

def html_page(title, body):
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"""

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if "user" not in session: return redirect("/")
        if str(session["user"]["id"]) != BOT_OWNER_ID:
            return redirect("/logout")
        return f(*a, **kw)
    return dec

def get_cfg():
    doc = db["config"].find_one({"_id": "main"}) or {}
    doc.pop("_id", None)
    return doc

def save_cfg(cfg):
    db["config"].update_one({"_id": "main"}, {"$set": cfg}, upsert=True)

def bot_headers():
    return {"Authorization": f"Bot {os.environ.get('DISCORD_BOT_TOKEN')}"}

def get_channels(guild_id):
    r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=bot_headers())
    if not r.ok: return [], []
    all_ch = r.json()
    text = [{"id": c["id"], "name": c["name"]} for c in sorted(all_ch, key=lambda x: x.get("position",0)) if c.get("type") == 0]
    voice = [{"id": c["id"], "name": c["name"]} for c in sorted(all_ch, key=lambda x: x.get("position",0)) if c.get("type") == 2]
    return text, voice

def get_roles(guild_id):
    r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/roles", headers=bot_headers())
    if not r.ok: return []
    return [{"id": ro["id"], "name": ro["name"]} for ro in sorted(r.json(), key=lambda x: -x["position"]) if ro["name"] != "@everyone"]

# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user" in session: return redirect("/servers")
    OAUTH = f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify+guilds"
    body = f"""<div style="min-height:100vh;display:flex;align-items:center;justify-content:center">
      <div style="background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:3rem 2.5rem;text-align:center;max-width:400px;width:100%">
        <div style="font-size:52px;margin-bottom:1rem">🇩🇪</div>
        <h1 style="font-size:24px;font-weight:700;margin-bottom:.5rem">GermanyRP Dashboard</h1>
        <p style="color:var(--text2);font-size:14px;margin-bottom:2rem">Melde dich mit Discord an um den Bot zu konfigurieren.</p>
        <a href="{OAUTH}" style="background:#5865F2;color:white;display:inline-flex;align-items:center;gap:10px;padding:.85rem 2rem;border-radius:10px;font-size:15px;font-weight:600;text-decoration:none">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057c.002.022.015.043.032.056a19.9 19.9 0 0 0 5.993 3.03.077.077 0 0 0 .083-.026c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>
          Mit Discord anmelden
        </a>
      </div>
    </div>"""
    return Response(html_page("GermanyRP Dashboard", body), content_type="text/html")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code: return redirect("/")
    r = requests.post(f"{DISCORD_API}/oauth2/token", data={"client_id": DISCORD_CLIENT_ID, "client_secret": DISCORD_CLIENT_SECRET, "grant_type": "authorization_code", "code": code, "redirect_uri": DISCORD_REDIRECT_URI})
    token = r.json().get("access_token")
    if not token: return redirect("/")
    user = requests.get(f"{DISCORD_API}/users/@me", headers={"Authorization": f"Bearer {token}"}).json()
    if str(user.get("id")) != BOT_OWNER_ID: return redirect("/")
    session["user"] = user
    session["token"] = token
    return redirect("/servers")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ── Server Selection ──────────────────────────────────────────────────────────

@app.route("/servers")
@login_required
def servers():
    user = session["user"]
    guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers={"Authorization": f"Bearer {session['token']}"})
    guilds = guilds_r.json() if guilds_r.ok else []
    bot_guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers=bot_headers())
    bot_ids = {g["id"] for g in (bot_guilds_r.json() if bot_guilds_r.ok else [])}
    guilds = [g for g in guilds if g["id"] in bot_ids]
    avatar = f"https://cdn.discordapp.com/avatars/{user['id']}/{user.get('avatar','')}.png"

    cards = ""
    for g in guilds:
        icon_url = f"https://cdn.discordapp.com/icons/{g['id']}/{g['icon']}.png" if g.get("icon") else ""
        icon_html = f'<img src="{icon_url}" style="width:72px;height:72px;border-radius:50%;object-fit:cover;margin-bottom:.75rem">' if icon_url else f'<div style="width:72px;height:72px;border-radius:50%;background:var(--bg3);display:flex;align-items:center;justify-content:center;font-size:26px;margin:0 auto .75rem">{g["name"][0]}</div>'
        cards += f"""<a href="/dashboard/{g['id']}" style="text-decoration:none">
          <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.5rem 1rem;text-align:center;cursor:pointer;transition:all .2s" onmouseover="this.style.borderColor='#f0a500';this.style.transform='translateY(-3px)'" onmouseout="this.style.borderColor='var(--border)';this.style.transform='none'">
            {icon_html}
            <div style="color:var(--text);font-weight:600;font-size:13px;margin-bottom:.5rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{g['name']}</div>
            <div style="background:rgba(82,192,120,.15);color:#52c078;font-size:11px;font-weight:600;padding:3px 10px;border-radius:4px;display:inline-block">Bot aktiv</div>
          </div>
        </a>"""

    body = f"""
      <div style="background:var(--bg2);border-bottom:1px solid var(--border);padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between">
        <div style="font-size:17px;font-weight:700;color:var(--accent)">🇩🇪 GermanyRP Dashboard</div>
        <div style="display:flex;align-items:center;gap:12px">
          <img src="{avatar}" style="width:32px;height:32px;border-radius:50%" onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
          <span style="font-size:14px;font-weight:500">{user['username']}</span>
          <a href="/logout" style="color:var(--red);font-size:13px;text-decoration:none;padding:.4rem .8rem;border:1px solid var(--red);border-radius:6px">Abmelden</a>
        </div>
      </div>
      <div style="padding:3rem 2rem">
        <h1 style="font-size:26px;font-weight:700;text-align:center;margin-bottom:.5rem">Server Ubersicht</h1>
        <p style="color:var(--text2);text-align:center;margin-bottom:2.5rem;font-size:14px">Wahle einen Server aus den du verwalten mochtest.</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:1.25rem;max-width:1000px;margin:0 auto">
          {cards or '<p style="color:var(--text2);text-align:center;grid-column:1/-1">Keine Server gefunden.</p>'}
        </div>
      </div>"""
    return Response(html_page("GermanyRP - Server", body), content_type="text/html")

# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard_root():
    return redirect("/servers")

@app.route("/dashboard/<guild_id>")
@login_required
def dashboard(guild_id):
    user = session["user"]
    guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers={"Authorization": f"Bearer {session['token']}"})
    guilds = guilds_r.json() if guilds_r.ok else []
    bot_guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers=bot_headers())
    bot_ids = {g["id"] for g in (bot_guilds_r.json() if bot_guilds_r.ok else [])}
    guilds = [g for g in guilds if g["id"] in bot_ids]
    sel = next((g for g in guilds if g["id"] == guild_id), None)
    if not sel: return redirect("/servers")

    avatar = f"https://cdn.discordapp.com/avatars/{user['id']}/{user.get('avatar','')}.png"
    sel_icon = f"https://cdn.discordapp.com/icons/{sel['id']}/{sel['icon']}.png" if sel.get("icon") else ""
    logo_img = f'<img src="{sel_icon}" style="width:28px;height:28px;border-radius:50%;object-fit:cover">' if sel_icon else '<span>&#x1F1E9;&#x1F1EA;</span>'

    sidebar = f"""<nav class="sidebar">
      <div class="logo">{logo_img}<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{sel['name'][:20]}</span></div>
      <a href="/servers" class="back-btn">&#8592; Server wechseln</a>
      <span class="nav-section">Allgemein</span>
      <button class="nav-item active" onclick="show('overview',this)">&#128202; Ubersicht</button>
      <span class="nav-section">Bot Einstellungen</span>
      <button class="nav-item" onclick="show('automod',this)">&#128737;&#65039; Automod</button>
      <button class="nav-item" onclick="show('level',this)">&#11014;&#65039; Level-System</button>
      <button class="nav-item" onclick="show('abmeldung',this)">&#128203; Abmeldung</button>
      <button class="nav-item" onclick="show('voicesupport',this)">&#127897;&#65039; Voice-Support</button>
      <button class="nav-item" onclick="show('logs',this)">&#128441; Log-System</button>
      <button class="nav-item" onclick="show('tickets',this)">&#127915; Tickets</button>
      <button class="nav-item" onclick="show('partner',this)">&#129309; Partner</button>
      <span class="nav-section">Server Setup</span>
      <button class="nav-item" onclick="show('willkommen',this)">&#128075; Willkommen/Abschied</button>
      <button class="nav-item" onclick="show('teamliste',this)">&#128101; Teamliste</button>
      <button class="nav-item" onclick="show('ingamelog',this)">&#127918; Ingame-Log</button>
      <button class="nav-item" onclick="show('autorole',this)">&#129302; Auto-Rolle</button>
      <button class="nav-item" onclick="show('backup',this)">&#128190; Backup</button>
      <button class="nav-item" onclick="show('ranklog',this)">&#128200; Ranklog</button>
      <div style="margin-top:auto;padding-top:1rem;border-top:1px solid var(--border)">
        <div style="display:flex;align-items:center;gap:8px;padding:.5rem .6rem;margin-bottom:.25rem">
          <img src="{avatar}" style="width:28px;height:28px;border-radius:50%" onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
          <span style="font-size:13px;font-weight:600">{user['username']}</span>
        </div>
        <a href="/logout" class="nav-item" style="color:var(--red)">&#128682; Abmelden</a>
      </div>
    </nav>"""

    pages = f"""
    <div id="page-overview" class="page active">
      <h1 class="page-title">Ubersicht</h1>
      <p class="page-sub">Wahle eine Kategorie um die Einstellungen zu bearbeiten.</p>
      <div class="overview-grid">
        <div class="ov-card" onclick="show('automod',null)"><div class="ov-icon">&#128737;</div><div class="ov-label">Automod</div></div>
        <div class="ov-card" onclick="show('level',null)"><div class="ov-icon">&#11014;</div><div class="ov-label">Level-System</div></div>
        <div class="ov-card" onclick="show('abmeldung',null)"><div class="ov-icon">&#128203;</div><div class="ov-label">Abmeldung</div></div>
        <div class="ov-card" onclick="show('voicesupport',null)"><div class="ov-icon">&#127897;</div><div class="ov-label">Voice-Support</div></div>
        <div class="ov-card" onclick="show('logs',null)"><div class="ov-icon">&#128441;</div><div class="ov-label">Log-System</div></div>
        <div class="ov-card" onclick="show('tickets',null)"><div class="ov-icon">&#127915;</div><div class="ov-label">Tickets</div></div>
        <div class="ov-card" onclick="show('partner',null)"><div class="ov-icon">&#129309;</div><div class="ov-label">Partner</div></div>
        <div class="ov-card" onclick="show('willkommen',null)"><div class="ov-icon">&#128075;</div><div class="ov-label">Willkommen</div></div>
        <div class="ov-card" onclick="show('teamliste',null)"><div class="ov-icon">&#128101;</div><div class="ov-label">Teamliste</div></div>
        <div class="ov-card" onclick="show('ingamelog',null)"><div class="ov-icon">&#127918;</div><div class="ov-label">Ingame-Log</div></div>
        <div class="ov-card" onclick="show('autorole',null)"><div class="ov-icon">&#129302;</div><div class="ov-label">Auto-Rolle</div></div>
        <div class="ov-card" onclick="show('backup',null)"><div class="ov-icon">&#128190;</div><div class="ov-label">Backup</div></div>
        <div class="ov-card" onclick="show('ranklog',null)"><div class="ov-icon">&#128200;</div><div class="ov-label">Ranklog</div></div>
      </div>
    </div>

    <!-- AUTOMOD -->
    <div id="page-automod" class="page">
      <h1 class="page-title">Automod</h1>
      <p class="page-sub">Schimpfworter und Scam-Werbung automatisch filtern.</p>
      <div id="alert-automod" class="alert"></div>
      <div class="card">
        <div class="card-title">&#9881; Allgemeine Einstellungen</div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Automod aktiv</div><div class="td">Nachrichten automatisch filtern</div></div><label class="toggle"><input type="checkbox" id="am-enabled"><span class="slider"></span></label></div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Scam-Erkennung</div><div class="td">Krypto/Werbung automatisch loschen</div></div><label class="toggle"><input type="checkbox" id="am-scam"><span class="slider"></span></label></div>
      </div>
      <div class="card">
        <div class="card-title">&#9876; Aktion & Kanal</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Aktion bei Verstoss</label><select class="form-select" id="am-action"><option value="delete">Nur loschen</option><option value="warn">Loschen + warnen</option><option value="mute">Loschen + muten</option></select></div>
          <div class="form-group"><label class="form-label">Mute-Dauer (Minuten)</label><input type="number" class="form-input" id="am-mute" min="1" max="1440" value="5"></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="am-channel"><option value="">Kanal wahlen...</option></select></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">&#128683; Ausnahmen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Ausnahme-Rolle (wird nicht gefiltert)</label><select class="form-select" id="am-exempt-role"><option value="">Rolle wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Ausnahme-Kanal</label><select class="form-select" id="am-exempt-ch"><option value="">Kanal wahlen...</option></select></div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="save('automod')">&#128190; Speichern</button>
    </div>

    <!-- LEVEL -->
    <div id="page-level" class="page">
      <h1 class="page-title">Level-System</h1>
      <p class="page-sub">XP, Rollen und Level-Up Kanal konfigurieren.</p>
      <div id="alert-level" class="alert"></div>
      <div class="card">
        <div class="card-title">&#9881; Einstellungen</div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Level-System aktiv</div><div class="td">XP durch Nachrichten und Voice sammeln</div></div><label class="toggle"><input type="checkbox" id="lv-enabled"><span class="slider"></span></label></div>
        <div class="form-grid" style="margin-top:1rem">
          <div class="form-group"><label class="form-label">Level-Up Kanal</label><select class="form-select" id="lv-channel"><option value="">Kanal wahlen...</option></select></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">&#127942; Level-Rollen (werden beim Setup automatisch erstellt)</div>
        <div style="display:flex;flex-wrap:wrap;gap:.5rem">
          <span class="tag">Level 5 - Aktiv</span><span class="tag">Level 10 - Erfahren</span><span class="tag">Level 20 - Veteran</span><span class="tag">Level 30 - Elite</span><span class="tag">Level 50 - Legende</span><span class="tag">Level 75 - Meister</span><span class="tag">Level 100 - Grandmaster</span><span class="tag">Level 125 - Unsterblich</span><span class="tag">Level 150 - Mythisch</span><span class="tag">Level 200 - Gottlich</span>
        </div>
        <p style="color:var(--text2);font-size:12px;margin-top:.75rem">Hinweis: Rollen werden beim ersten /level-setup Befehl automatisch erstellt.</p>
      </div>
      <button class="btn btn-primary" onclick="save('level')">&#128190; Speichern</button>
    </div>

    <!-- ABMELDUNG -->
    <div id="page-abmeldung" class="page">
      <h1 class="page-title">Abmeldungs-System</h1>
      <p class="page-sub">Abwesenheitsrolle, Bestatigungsrolle, Log-Kanal und Panel konfigurieren.</p>
      <div id="alert-abmeldung" class="alert"></div>
      <div class="card">
        <div class="card-title">&#128203; Panel & Log</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Panel-Kanal</label><select class="form-select" id="ab-panel"><option value="">Kanal wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="ab-log"><option value="">Kanal wahlen...</option></select></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">&#127922; Rollen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Abwesenheitsrolle</label><select class="form-select" id="ab-role"><option value="">Rolle wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Bestatigungsrolle</label><select class="form-select" id="ab-confirm-role"><option value="">Rolle wahlen...</option></select></div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="save('abmeldung')">&#128190; Speichern</button>
    </div>

    <!-- VOICE SUPPORT -->
    <div id="page-voicesupport" class="page">
      <h1 class="page-title">Voice-Support System</h1>
      <p class="page-sub">Warteraum, Benachrichtigungs-Kanal und Support-Rollen konfigurieren.</p>
      <div id="alert-voicesupport" class="alert"></div>
      <div class="card">
        <div class="card-title">&#127897; System 1</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Warteraum (Voice-Channel)</label><select class="form-select" id="vs1-wait"><option value="">Voice-Channel wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Benachrichtigungs-Kanal</label><select class="form-select" id="vs1-notif"><option value="">Kanal wahlen...</option></select></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Support-Rolle</label><select class="form-select" id="vs1-suprole"><option value="">Rolle wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Ping-Rolle</label><select class="form-select" id="vs1-pingrole"><option value="">Rolle wahlen...</option></select></div>
        </div>
        <button class="btn btn-primary" onclick="saveVS(1)">&#128190; System 1 speichern</button>
      </div>
      <div class="card">
        <div class="card-title">&#127897; System 2</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Warteraum (Voice-Channel)</label><select class="form-select" id="vs2-wait"><option value="">Voice-Channel wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Benachrichtigungs-Kanal</label><select class="form-select" id="vs2-notif"><option value="">Kanal wahlen...</option></select></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Support-Rolle</label><select class="form-select" id="vs2-suprole"><option value="">Rolle wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Ping-Rolle</label><select class="form-select" id="vs2-pingrole"><option value="">Rolle wahlen...</option></select></div>
        </div>
        <button class="btn btn-primary" onclick="saveVS(2)">&#128190; System 2 speichern</button>
      </div>
    </div>

    <!-- LOGS -->
    <div id="page-logs" class="page">
      <h1 class="page-title">Log-System</h1>
      <p class="page-sub">Lege fest welche Ereignisse in welchem Kanal geloggt werden.</p>
      <div id="alert-logs" class="alert"></div>
      <div class="card">
        <div class="card-title">&#128441; Log-Kanal</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Kanal fur alle Logs</label><select class="form-select" id="log-channel"><option value="">Kanal wahlen...</option></select></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">&#127381; Kategorien aktivieren</div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Moderation</div><div class="td">Ban, Kick, Mute, Warn, Uprank, Downrank</div></div><label class="toggle"><input type="checkbox" id="log-moderation"><span class="slider"></span></label></div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Nachrichten</div><div class="td">Geloschte und bearbeitete Nachrichten</div></div><label class="toggle"><input type="checkbox" id="log-messages"><span class="slider"></span></label></div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Server-Anderungen</div><div class="td">Rollen und Kanale erstellt/geloscht</div></div><label class="toggle"><input type="checkbox" id="log-server"><span class="slider"></span></label></div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Voice-Aktivitat</div><div class="td">Join, Leave, Switch</div></div><label class="toggle"><input type="checkbox" id="log-voice"><span class="slider"></span></label></div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Mitglieder</div><div class="td">Join, Leave, Nickname geandert</div></div><label class="toggle"><input type="checkbox" id="log-members"><span class="slider"></span></label></div>
      </div>
      <button class="btn btn-primary" onclick="save('logs')">&#128190; Speichern</button>
    </div>

    <!-- TICKETS -->
    <div id="page-tickets" class="page">
      <h1 class="page-title">Ticket-System</h1>
      <p class="page-sub">Panel, Rollen und Kategorien fur das Ticket-System konfigurieren.</p>
      <div id="alert-tickets" class="alert"></div>
      <div class="card">
        <div class="card-title">&#127915; Panel & Kanale</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Panel-Kanal</label><select class="form-select" id="tk-panel"><option value="">Kanal wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Transcript-Kanal</label><select class="form-select" id="tk-transcript"><option value="">Kanal wahlen...</option></select></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Support-Rolle</label><select class="form-select" id="tk-role"><option value="">Rolle wahlen...</option></select></div>
        </div>
        <button class="btn btn-primary" onclick="save('ticketsetup')">&#128190; Speichern</button>
      </div>
      <hr class="section-divider">
      <div class="card">
        <div class="card-title">&#10133; Kategorie hinzufugen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Name</label><input type="text" class="form-input" id="tk-kat-name" placeholder="z.B. Beschwerde"></div>
          <div class="form-group"><label class="form-label">Emoji</label><input type="text" class="form-input" id="tk-kat-emoji" placeholder="z.B. &#128542;" style="max-width:100px"></div>
        </div>
        <button class="btn btn-primary" onclick="addTicketKat()">&#10133; Hinzufugen</button>
      </div>
      <div class="card">
        <div class="card-title">&#128203; Aktuelle Kategorien</div>
        <div id="tk-kat-list"><p style="color:var(--text2);font-size:13px">Wird geladen...</p></div>
      </div>
    </div>

    <!-- PARTNER -->
    <div id="page-partner" class="page">
      <h1 class="page-title">Partner</h1>
      <p class="page-sub">Partnerliste verwalten - wird automatisch im Discord-Kanal aktualisiert.</p>
      <div id="alert-partner" class="alert"></div>
      <div class="card">
        <div class="card-title">&#9881; Panel-Kanal</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Kanal fur die Partnerliste</label><select class="form-select" id="pt-channel"><option value="">Kanal wahlen...</option></select></div>
        </div>
        <button class="btn btn-primary" onclick="savePartnerSetup()">&#128190; Kanal speichern</button>
      </div>
      <div class="card">
        <div class="card-title">&#10133; Partner hinzufugen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Server-Name</label><input type="text" class="form-input" id="pt-name" placeholder="z.B. Notruf Hamburg"></div>
          <div class="form-group"><label class="form-label">Einladungslink</label><input type="text" class="form-input" id="pt-link" placeholder="discord.gg/..."></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Kategorie</label><input type="text" class="form-input" id="pt-kat" placeholder="z.B. Grosse Partner"></div>
          <div class="form-group"><label class="form-label">Ansprechpartner (optional)</label><input type="text" class="form-input" id="pt-ap" placeholder="z.B. @Jeremy"></div>
        </div>
        <button class="btn btn-primary" onclick="addPartner()">&#10133; Partner hinzufugen</button>
      </div>
      <div class="card">
        <div class="card-title">&#129309; Aktuelle Partner</div>
        <div id="pt-list"><p style="color:var(--text2);font-size:13px">Wird geladen...</p></div>
      </div>
    </div>

    <!-- WILLKOMMEN -->
    <div id="page-willkommen" class="page">
      <h1 class="page-title">Willkommen & Abschied</h1>
      <p class="page-sub">Begrussungs- und Abschiedsnachrichten konfigurieren.</p>
      <div id="alert-willkommen" class="alert"></div>
      <div class="card">
        <div class="card-title">&#128075; Willkommensnachricht</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Kanal</label><select class="form-select" id="wc-channel"><option value="">Kanal wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Bild-URL (optional)</label><input type="text" class="form-input" id="wc-image" placeholder="https://..."></div>
        </div>
        <div class="form-grid full">
          <div class="form-group"><label class="form-label">Nachricht (optional - nutze {{user}} fur Mention)</label><input type="text" class="form-input" id="wc-msg" placeholder="Willkommen auf dem Server, {{user}}!"></div>
        </div>
        <button class="btn btn-primary" onclick="saveWillkommen()">&#128190; Speichern</button>
      </div>
      <div class="card">
        <div class="card-title">&#128682; Abschiedsnachricht</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Kanal</label><select class="form-select" id="gb-channel"><option value="">Kanal wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Bild-URL (optional)</label><input type="text" class="form-input" id="gb-image" placeholder="https://..."></div>
        </div>
        <div class="form-grid full">
          <div class="form-group"><label class="form-label">Nachricht (optional)</label><input type="text" class="form-input" id="gb-msg" placeholder="Auf Wiedersehen, {{user}}!"></div>
        </div>
        <button class="btn btn-primary" onclick="saveAbschied()">&#128190; Speichern</button>
      </div>
    </div>

    <!-- TEAMLISTE -->
    <div id="page-teamliste" class="page">
      <h1 class="page-title">Teamliste</h1>
      <p class="page-sub">Kanal und Titel fur die automatische Teamliste konfigurieren.</p>
      <div id="alert-teamliste" class="alert"></div>
      <div class="card">
        <div class="card-title">&#128101; Einstellungen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Kanal</label><select class="form-select" id="tl-channel"><option value="">Kanal wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Titel</label><input type="text" class="form-input" id="tl-titel" placeholder="Teamliste" value="Teamliste"></div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="save('teamliste')">&#128190; Speichern</button>
    </div>

    <!-- INGAME LOG -->
    <div id="page-ingamelog" class="page">
      <h1 class="page-title">Ingame-Log System</h1>
      <p class="page-sub">Panel und Log-Kanal fur In-Game Bans/Kicks konfigurieren.</p>
      <div id="alert-ingamelog" class="alert"></div>
      <div class="card">
        <div class="card-title">&#127918; Einstellungen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Panel-Kanal</label><select class="form-select" id="ig-panel"><option value="">Kanal wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="ig-log"><option value="">Kanal wahlen...</option></select></div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="save('ingamelog')">&#128190; Speichern</button>
    </div>

    <!-- AUTO ROLLE -->
    <div id="page-autorole" class="page">
      <h1 class="page-title">Auto-Rolle</h1>
      <p class="page-sub">Rolle die neue Mitglieder automatisch beim Beitritt erhalten.</p>
      <div id="alert-autorole" class="alert"></div>
      <div class="card">
        <div class="card-title">&#129302; Einstellungen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Auto-Rolle</label><select class="form-select" id="ar-role"><option value="">Rolle wahlen...</option></select></div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="save('autorole')">&#128190; Speichern</button>
    </div>

    <!-- BACKUP -->
    <div id="page-backup" class="page">
      <h1 class="page-title">Backup-System</h1>
      <p class="page-sub">Automatische Backups aktivieren und Log-Kanal konfigurieren.</p>
      <div id="alert-backup" class="alert"></div>
      <div class="card">
        <div class="card-title">&#128190; Einstellungen</div>
        <div class="toggle-row"><div class="toggle-info"><div class="tl">Auto-Backup aktiv</div><div class="td">Taglich um 03:00 UTC automatisch sichern</div></div><label class="toggle"><input type="checkbox" id="bk-auto"><span class="slider"></span></label></div>
        <div class="form-grid" style="margin-top:1rem">
          <div class="form-group"><label class="form-label">Log-Kanal (optional)</label><select class="form-select" id="bk-channel"><option value="">Kanal wahlen...</option></select></div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="save('backup')">&#128190; Speichern</button>
    </div>

    <!-- RANKLOG -->
    <div id="page-ranklog" class="page">
      <h1 class="page-title">Ranklog</h1>
      <p class="page-sub">Kanal und Rollen-Range fur Up/Downrank Logs konfigurieren.</p>
      <div id="alert-ranklog" class="alert"></div>
      <div class="card">
        <div class="card-title">&#128200; Einstellungen</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="rl-channel"><option value="">Kanal wahlen...</option></select></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Von Rolle (unterste Stufe)</label><select class="form-select" id="rl-von"><option value="">Rolle wahlen...</option></select></div>
          <div class="form-group"><label class="form-label">Bis Rolle (oberste Stufe)</label><select class="form-select" id="rl-bis"><option value="">Rolle wahlen...</option></select></div>
        </div>
      </div>
      <button class="btn btn-primary" onclick="save('ranklog')">&#128190; Speichern</button>
    </div>"""

    script = f"""<script>
const GUILD_ID = "{guild_id}";
let channels = [], voices = [], roles = [];

function show(id, el) {{
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  if (el) el.classList.add('active');
}}

function alert2(id, msg, t='success') {{
  const e = document.getElementById('alert-' + id);
  if (!e) return;
  e.textContent = msg;
  e.className = 'alert alert-' + t;
  e.style.display = 'block';
  setTimeout(() => e.style.display = 'none', 3500);
}}

async function api(p, m='GET', b=null) {{
  const o = {{method: m, headers: {{'Content-Type': 'application/json'}}}};
  if (b) o.body = JSON.stringify(b);
  const r = await fetch(p, o);
  return r.json();
}}

function fillSelect(id, items, val='', prefix='') {{
  const s = document.getElementById(id);
  if (!s) return;
  const cur = val || s.value;
  s.innerHTML = `<option value="">${{prefix || 'Wahlen...'}}</option>` + items.map(x => `<option value="${{x.id}}" ${{x.id==cur?'selected':''}}>#${{x.name}}</option>`).join('');
}}

function fillRoleSelect(id, items, val='') {{
  const s = document.getElementById(id);
  if (!s) return;
  const cur = val || s.value;
  s.innerHTML = '<option value="">Wahlen...</option>' + items.map(x => `<option value="${{x.id}}" ${{x.id==cur?'selected':''}}>@${{x.name}}</option>`).join('');
}}

function fillVoiceSelect(id, items, val='') {{
  const s = document.getElementById(id);
  if (!s) return;
  const cur = val || s.value;
  s.innerHTML = '<option value="">Voice-Channel wahlen...</option>' + items.map(x => `<option value="${{x.id}}" ${{x.id==cur?'selected':''}}>&#128266; ${{x.name}}</option>`).join('');
}}

async function loadChannelsAndRoles() {{
  const [ch, ro] = await Promise.all([
    api('/api/channels?guild_id=' + GUILD_ID),
    api('/api/roles?guild_id=' + GUILD_ID)
  ]);
  channels = ch.text || [];
  voices = ch.voice || [];
  roles = ro || [];

  // Fill all text channel selects
  ['am-channel','am-exempt-ch','lv-channel','ab-panel','ab-log','vs1-notif','vs2-notif','log-channel','tk-panel','tk-transcript','pt-channel','wc-channel','gb-channel','tl-channel','ig-panel','ig-log','bk-channel','rl-channel'].forEach(id => fillSelect(id, channels, '', 'Kanal wahlen...'));
  // Fill voice selects
  ['vs1-wait','vs2-wait'].forEach(id => fillVoiceSelect(id, voices));
  // Fill role selects
  ['am-exempt-role','ab-role','ab-confirm-role','vs1-suprole','vs1-pingrole','vs2-suprole','vs2-pingrole','tk-role','ar-role','rl-von','rl-bis'].forEach(id => fillRoleSelect(id, roles));
}}

async function loadAll() {{
  await loadChannelsAndRoles();
  await Promise.all([loadAutomod(), loadLevel(), loadAbmeldung(), loadVS(), loadLogs(), loadTicketSetup(), loadTicketKat(), loadPartner(), loadWillkommen(), loadTeamliste(), loadIngamelog(), loadAutorole(), loadBackup(), loadRanklog()]);
}}

// AUTOMOD
async function loadAutomod() {{
  const c = await api('/api/automod?guild_id=' + GUILD_ID);
  document.getElementById('am-enabled').checked = c.enabled || false;
  document.getElementById('am-scam').checked = c.scam_detection !== false;
  document.getElementById('am-action').value = c.action || 'warn';
  document.getElementById('am-mute').value = c.mute_duration || 5;
  if (c.log_channel_id) fillSelect('am-channel', channels, c.log_channel_id);
  if (c.exempt_role) fillRoleSelect('am-exempt-role', roles, c.exempt_role);
  if (c.exempt_channel) fillSelect('am-exempt-ch', channels, c.exempt_channel);
}}

// LEVEL
async function loadLevel() {{
  const c = (await api('/api/cfg?guild_id=' + GUILD_ID + '&key=level_config')) || {{}};
  document.getElementById('lv-enabled').checked = c.enabled || false;
  if (c.levelup_channel_id) fillSelect('lv-channel', channels, c.levelup_channel_id);
}}

// ABMELDUNG
async function loadAbmeldung() {{
  const c = await api('/api/abmeldung?guild_id=' + GUILD_ID);
  if (c.log_channel_id) fillSelect('ab-log', channels, c.log_channel_id);
  if (c.panel_channel_id) fillSelect('ab-panel', channels, c.panel_channel_id);
  if (c.abwesenheitsrolle_id) fillRoleSelect('ab-role', roles, c.abwesenheitsrolle_id);
  if (c.bestaetigung_rolle_id) fillRoleSelect('ab-confirm-role', roles, c.bestaetigung_rolle_id);
}}

// VOICE SUPPORT
async function loadVS() {{
  const [c1, c2] = await Promise.all([api('/api/voicesupport?guild_id=' + GUILD_ID + '&system=1'), api('/api/voicesupport?guild_id=' + GUILD_ID + '&system=2')]);
  if (c1.warteraum_id) fillVoiceSelect('vs1-wait', voices, c1.warteraum_id);
  if (c1.notif_channel_id) fillSelect('vs1-notif', channels, c1.notif_channel_id);
  if (c1.support_role_id) fillRoleSelect('vs1-suprole', roles, c1.support_role_id);
  if (c1.ping_role_id) fillRoleSelect('vs1-pingrole', roles, c1.ping_role_id);
  if (c2.warteraum_id) fillVoiceSelect('vs2-wait', voices, c2.warteraum_id);
  if (c2.notif_channel_id) fillSelect('vs2-notif', channels, c2.notif_channel_id);
  if (c2.support_role_id) fillRoleSelect('vs2-suprole', roles, c2.support_role_id);
  if (c2.ping_role_id) fillRoleSelect('vs2-pingrole', roles, c2.ping_role_id);
}}
async function saveVS(s) {{
  await api('/api/voicesupport', 'POST', {{guild_id: GUILD_ID, system: String(s), warteraum_id: document.getElementById('vs'+s+'-wait').value, notif_channel_id: document.getElementById('vs'+s+'-notif').value, support_role_id: document.getElementById('vs'+s+'-suprole').value, ping_role_id: document.getElementById('vs'+s+'-pingrole').value}});
  alert2('voicesupport', '&#10003; System ' + s + ' gespeichert!');
}}

// LOGS
async function loadLogs() {{
  const c = (await api('/api/cfg?guild_id=' + GUILD_ID + '&key=unified_log_config')) || {{}};
  if (c.channel_id) fillSelect('log-channel', channels, c.channel_id);
  ['moderation','messages','server','voice','members'].forEach(x => document.getElementById('log-'+x).checked = (c.categories||[]).includes(x));
}}

// TICKETS
async function loadTicketSetup() {{
  const c = (await api('/api/cfg?guild_id=' + GUILD_ID + '&key=ticket_setup')) || {{}};
  if (c.panel_kanal_id) fillSelect('tk-panel', channels, c.panel_kanal_id);
  if (c.transcript_kanal_id) fillSelect('tk-transcript', channels, c.transcript_kanal_id);
  if (c.support_role_id) fillRoleSelect('tk-role', roles, c.support_role_id);
}}
async function loadTicketKat() {{
  const k = await api('/api/tickets?guild_id=' + GUILD_ID);
  const el = document.getElementById('tk-kat-list');
  if (!k || !k.length) {{ el.innerHTML = '<p style="color:var(--text2);font-size:13px">Noch keine Kategorien.</p>'; return; }}
  el.innerHTML = k.map(x => `<div class="ticket-kat-card"><span style="font-size:16px">${{x.emoji}}</span><span style="font-weight:600;flex:1;margin-left:.75rem">${{x.name}}</span><button class="btn btn-danger" style="padding:.3rem .7rem;font-size:12px" onclick="delTicketKat('${{x.name}}')">Loschen</button></div>`).join('');
}}
async function addTicketKat() {{
  const n = document.getElementById('tk-kat-name').value.trim();
  const e = document.getElementById('tk-kat-emoji').value.trim() || '&#127915;';
  if (!n) return alert2('tickets', '&#9888; Name eingeben!', 'error');
  await api('/api/tickets', 'POST', {{guild_id: GUILD_ID, name: n, emoji: e}});
  document.getElementById('tk-kat-name').value = ''; document.getElementById('tk-kat-emoji').value = '';
  alert2('tickets', '&#10003; Kategorie hinzugefugt!'); await loadTicketKat();
}}
async function delTicketKat(n) {{
  await api('/api/tickets', 'DELETE', {{guild_id: GUILD_ID, name: n}});
  alert2('tickets', '&#10003; Geloscht!'); await loadTicketKat();
}}

// PARTNER
async function loadPartner() {{
  const c = await api('/api/partner?guild_id=' + GUILD_ID);
  if (c.channel_id) fillSelect('pt-channel', channels, c.channel_id);
  const p = c.partners || [];
  const el = document.getElementById('pt-list');
  if (!p.length) {{ el.innerHTML = '<p style="color:var(--text2);font-size:13px">Noch keine Partner.</p>'; return; }}
  el.innerHTML = p.map(x => `<div class="partner-card">
    <div class="partner-info">
      <div class="pkat">${{x.kategorie}}</div>
      <div class="pname">${{x.name}}</div>
      ${{x.ansprechpartner ? `<div class="pap">Ansprechpartner: ${{x.ansprechpartner}}</div>` : ''}}
      <div class="plink"><a href="${{x.link.startsWith('http')?x.link:'https://'+x.link}}" target="_blank" style="color:var(--accent)">${{x.link}}</a></div>
    </div>
    <button class="btn btn-danger" style="padding:.3rem .75rem;font-size:12px" onclick="delPartner('${{x.name}}')">Loschen</button>
  </div>`).join('');
}}
async function savePartnerSetup() {{
  const c = await api('/api/partner?guild_id=' + GUILD_ID);
  c.channel_id = document.getElementById('pt-channel').value;
  c.guild_id = GUILD_ID;
  await api('/api/partner-setup', 'POST', c);
  alert2('partner', '&#10003; Kanal gespeichert!');
}}
async function addPartner() {{
  const n = document.getElementById('pt-name').value.trim();
  const l = document.getElementById('pt-link').value.trim();
  if (!n || !l) return alert2('partner', '&#9888; Name und Link eingeben!', 'error');
  await api('/api/partner', 'POST', {{guild_id: GUILD_ID, name: n, link: l, kategorie: document.getElementById('pt-kat').value.trim() || '&#129309; Partner', ansprechpartner: document.getElementById('pt-ap').value.trim()}});
  ['pt-name','pt-link','pt-kat','pt-ap'].forEach(id => document.getElementById(id).value = '');
  alert2('partner', '&#10003; Partner hinzugefugt!'); await loadPartner();
}}
async function delPartner(n) {{
  await api('/api/partner?guild_id=' + GUILD_ID, 'DELETE', {{guild_id: GUILD_ID, name: n}});
  alert2('partner', '&#10003; Geloscht!'); await loadPartner();
}}

// WILLKOMMEN
async function loadWillkommen() {{
  const [wc, gb] = await Promise.all([api('/api/cfg?guild_id=' + GUILD_ID + '&key=welcome'), api('/api/cfg?guild_id=' + GUILD_ID + '&key=goodbye')]);
  if (wc && wc.channel_id) fillSelect('wc-channel', channels, wc.channel_id);
  document.getElementById('wc-msg').value = (wc && wc.message) || '';
  document.getElementById('wc-image').value = (wc && wc.image_url) || '';
  if (gb && gb.channel_id) fillSelect('gb-channel', channels, gb.channel_id);
  document.getElementById('gb-msg').value = (gb && gb.message) || '';
  document.getElementById('gb-image').value = (gb && gb.image_url) || '';
}}
async function saveWillkommen() {{
  await api('/api/welcome', 'POST', {{guild_id: GUILD_ID, channel_id: document.getElementById('wc-channel').value, message: document.getElementById('wc-msg').value, image_url: document.getElementById('wc-image').value}});
  alert2('willkommen', '&#10003; Willkommensnachricht gespeichert!');
}}
async function saveAbschied() {{
  await api('/api/goodbye', 'POST', {{guild_id: GUILD_ID, channel_id: document.getElementById('gb-channel').value, message: document.getElementById('gb-msg').value, image_url: document.getElementById('gb-image').value}});
  alert2('willkommen', '&#10003; Abschiedsnachricht gespeichert!');
}}

// TEAMLISTE
async function loadTeamliste() {{
  const c = (await api('/api/cfg?guild_id=' + GUILD_ID + '&key=teamliste')) || {{}};
  if (c.channel_id) fillSelect('tl-channel', channels, c.channel_id);
  document.getElementById('tl-titel').value = c.title || 'Teamliste';
}}

// INGAMELOG
async function loadIngamelog() {{
  const c = await api('/api/ingamelog?guild_id=' + GUILD_ID);
  if (c.panel_kanal_id) fillSelect('ig-panel', channels, c.panel_kanal_id);
  if (c.log_kanal_id) fillSelect('ig-log', channels, c.log_kanal_id);
}}

// AUTOROLE
async function loadAutorole() {{
  const c = await api('/api/cfg?guild_id=' + GUILD_ID + '&key=auto_role_id');
  if (c) fillRoleSelect('ar-role', roles, c);
}}

// BACKUP
async function loadBackup() {{
  const c = await api('/api/backup?guild_id=' + GUILD_ID);
  document.getElementById('bk-auto').checked = c.auto_backup || false;
  if (c.log_kanal_id) fillSelect('bk-channel', channels, c.log_kanal_id);
}}

// RANKLOG
async function loadRanklog() {{
  const c = (await api('/api/cfg?guild_id=' + GUILD_ID + '&key=ranklog')) || {{}};
  if (c.channel_id) fillSelect('rl-channel', channels, c.channel_id);
  if (c.von_role_id) fillRoleSelect('rl-von', roles, c.von_role_id);
  if (c.bis_role_id) fillRoleSelect('rl-bis', roles, c.bis_role_id);
}}

// GENERIC SAVE
async function save(system) {{
  let data = {{guild_id: GUILD_ID}};
  if (system === 'automod') {{
    data = {{guild_id: GUILD_ID, enabled: document.getElementById('am-enabled').checked, scam_detection: document.getElementById('am-scam').checked, action: document.getElementById('am-action').value, mute_duration: parseInt(document.getElementById('am-mute').value), log_channel_id: document.getElementById('am-channel').value, exempt_role: document.getElementById('am-exempt-role').value, exempt_channel: document.getElementById('am-exempt-ch').value}};
  }} else if (system === 'level') {{
    data = {{guild_id: GUILD_ID, enabled: document.getElementById('lv-enabled').checked, levelup_channel_id: document.getElementById('lv-channel').value}};
  }} else if (system === 'abmeldung') {{
    data = {{guild_id: GUILD_ID, log_channel_id: document.getElementById('ab-log').value, panel_channel_id: document.getElementById('ab-panel').value, abwesenheitsrolle_id: document.getElementById('ab-role').value, bestaetigung_rolle_id: document.getElementById('ab-confirm-role').value}};
  }} else if (system === 'logs') {{
    const cats = ['moderation','messages','server','voice','members'].filter(x => document.getElementById('log-'+x).checked);
    data = {{guild_id: GUILD_ID, channel_id: document.getElementById('log-channel').value, categories: cats}};
  }} else if (system === 'ticketsetup') {{
    data = {{guild_id: GUILD_ID, panel_kanal_id: document.getElementById('tk-panel').value, transcript_kanal_id: document.getElementById('tk-transcript').value, support_role_id: document.getElementById('tk-role').value}};
  }} else if (system === 'teamliste') {{
    data = {{guild_id: GUILD_ID, kanal_id: document.getElementById('tl-channel').value, titel: document.getElementById('tl-titel').value || 'Teamliste'}};
  }} else if (system === 'ingamelog') {{
    data = {{guild_id: GUILD_ID, panel_kanal_id: document.getElementById('ig-panel').value, log_kanal_id: document.getElementById('ig-log').value}};
  }} else if (system === 'autorole') {{
    data = {{guild_id: GUILD_ID, role_id: document.getElementById('ar-role').value}};
  }} else if (system === 'backup') {{
    data = {{guild_id: GUILD_ID, auto_backup: document.getElementById('bk-auto').checked, log_kanal_id: document.getElementById('bk-channel').value}};
  }} else if (system === 'ranklog') {{
    data = {{guild_id: GUILD_ID, kanal_id: document.getElementById('rl-channel').value, von_id: document.getElementById('rl-von').value, bis_id: document.getElementById('rl-bis').value}};
  }}
  await api('/api/' + system, 'POST', data);
  alert2(system, '&#10003; Gespeichert!');
}}

window.addEventListener('load', loadAll);
</script>"""

    main = f'<main class="main">{pages}</main>'
    body = f'<div class="layout">{sidebar}{main}</div>{script}'
    return Response(html_page(f"GermanyRP - {sel['name']}", body), content_type="text/html")

# ── API Routes ────────────────────────────────────────────────────────────────

@app.route("/api/channels")
@login_required
def api_channels():
    gid = request.args.get("guild_id")
    text, voice = get_channels(gid)
    return jsonify({"text": text, "voice": voice})

@app.route("/api/roles")
@login_required
def api_roles():
    gid = request.args.get("guild_id")
    return jsonify(get_roles(gid))

@app.route("/api/cfg")
@login_required
def api_cfg_get():
    gid = request.args.get("guild_id")
    key = request.args.get("key")
    cfg = get_cfg()
    val = cfg.get(key, {})
    if isinstance(val, dict):
        return jsonify(val.get(gid, {}))
    return jsonify(val)

@app.route("/api/automod", methods=["GET", "POST"])
@login_required
def api_automod():
    if request.method == "POST":
        d = request.json; gid = d.get("guild_id")
        db["automod_config"].update_one({"guild_id": gid}, {"$set": {**d, "guild_id": gid}}, upsert=True)
        return jsonify({"ok": True})
    gid = request.args.get("guild_id")
    doc = db["automod_config"].find_one({"guild_id": gid}) or {}
    doc.pop("_id", None); return jsonify(doc)

@app.route("/api/level", methods=["POST"])
@login_required
def api_level():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    cfg.setdefault("level_config", {})[gid] = {"enabled": d.get("enabled"), "levelup_channel_id": d.get("levelup_channel_id", "")}
    save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/abmeldung", methods=["GET", "POST"])
@login_required
def api_abmeldung():
    if request.method == "POST":
        d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
        cfg.setdefault("abmeldung_log_channel", {})[gid] = d.get("log_channel_id", "")
        cfg.setdefault("abmeldung_abwesenheitsrolle", {})[gid] = d.get("abwesenheitsrolle_id", "")
        cfg.setdefault("abmeldung_bestaetigung_rolle", {})[gid] = d.get("bestaetigung_rolle_id", "")
        cfg.setdefault("abmeldung_panel_channel", {})[gid] = d.get("panel_channel_id", "")
        save_cfg(cfg); return jsonify({"ok": True})
    gid = request.args.get("guild_id"); cfg = get_cfg()
    return jsonify({"log_channel_id": cfg.get("abmeldung_log_channel", {}).get(gid, ""), "abwesenheitsrolle_id": cfg.get("abmeldung_abwesenheitsrolle", {}).get(gid, ""), "bestaetigung_rolle_id": cfg.get("abmeldung_bestaetigung_rolle", {}).get(gid, ""), "panel_channel_id": cfg.get("abmeldung_panel_channel", {}).get(gid, "")})

@app.route("/api/voicesupport", methods=["GET", "POST"])
@login_required
def api_voicesupport():
    if request.method == "POST":
        d = request.json; gid = d.get("guild_id"); s = d.get("system", "1")
        key = "voice_support" if s == "1" else "voice_support_2"; cfg = get_cfg()
        cfg.setdefault(key, {})[gid] = {"warteraum_id": d.get("warteraum_id", ""), "notif_channel_id": d.get("notif_channel_id", ""), "support_role_id": d.get("support_role_id", ""), "ping_role_id": d.get("ping_role_id", "")}
        save_cfg(cfg); return jsonify({"ok": True})
    gid = request.args.get("guild_id"); s = request.args.get("system", "1")
    key = "voice_support" if s == "1" else "voice_support_2"; cfg = get_cfg()
    return jsonify(cfg.get(key, {}).get(gid, {}))

@app.route("/api/logs", methods=["POST"])
@login_required
def api_logs():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    cfg.setdefault("unified_log_config", {})[gid] = {"channel_id": d.get("channel_id", ""), "categories": d.get("categories", [])}
    save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/ticketsetup", methods=["POST"])
@login_required
def api_ticketsetup():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    cfg.setdefault("ticket_setup", {})[gid] = {"panel_kanal_id": d.get("panel_kanal_id", ""), "transcript_kanal_id": d.get("transcript_kanal_id", ""), "support_role_id": d.get("support_role_id", "")}
    save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/tickets", methods=["GET", "POST", "DELETE"])
@login_required
def api_tickets():
    gid = request.args.get("guild_id") or (request.json or {}).get("guild_id")
    if request.method == "GET":
        cfg = get_cfg(); return jsonify(cfg.get("ticket_kategorien", {}).get(gid, []))
    if request.method == "POST":
        d = request.json; cfg = get_cfg()
        cfg.setdefault("ticket_kategorien", {}).setdefault(gid, []).append({"name": d.get("name"), "emoji": d.get("emoji", "&#127915;")})
        save_cfg(cfg); return jsonify({"ok": True})
    if request.method == "DELETE":
        d = request.json; cfg = get_cfg()
        kat = cfg.get("ticket_kategorien", {}).get(gid, [])
        cfg["ticket_kategorien"][gid] = [k for k in kat if k["name"] != d.get("name")]
        save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/partner", methods=["GET", "POST", "DELETE"])
@login_required
def api_partner():
    gid = request.args.get("guild_id") or (request.json or {}).get("guild_id")
    if request.method == "GET":
        doc = db["partner_config"].find_one({"guild_id": gid}) or {}; doc.pop("_id", None); return jsonify(doc)
    if request.method == "POST":
        d = request.json
        doc = db["partner_config"].find_one({"guild_id": gid}) or {"guild_id": gid, "partners": []}
        doc["partners"].append({"name": d.get("name"), "link": d.get("link"), "kategorie": d.get("kategorie", "Partner"), "ansprechpartner": d.get("ansprechpartner", "")})
        db["partner_config"].update_one({"guild_id": gid}, {"$set": {"partners": doc["partners"]}}, upsert=True); return jsonify({"ok": True})
    if request.method == "DELETE":
        d = request.json
        doc = db["partner_config"].find_one({"guild_id": gid}) or {}
        db["partner_config"].update_one({"guild_id": gid}, {"$set": {"partners": [p for p in doc.get("partners", []) if p["name"] != d.get("name")]}}, upsert=True); return jsonify({"ok": True})

@app.route("/api/partner-setup", methods=["POST"])
@login_required
def api_partner_setup():
    d = request.json; gid = d.get("guild_id")
    db["partner_config"].update_one({"guild_id": gid}, {"$set": {"channel_id": d.get("channel_id", "")}}, upsert=True)
    return jsonify({"ok": True})

@app.route("/api/welcome", methods=["POST"])
@login_required
def api_welcome():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    cfg.setdefault("welcome", {})[gid] = {"channel_id": d.get("channel_id", ""), "message": d.get("message", ""), "image_url": d.get("image_url", "")}
    save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/goodbye", methods=["POST"])
@login_required
def api_goodbye():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    cfg.setdefault("goodbye", {})[gid] = {"channel_id": d.get("channel_id", ""), "message": d.get("message", ""), "image_url": d.get("image_url", "")}
    save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/teamliste", methods=["POST"])
@login_required
def api_teamliste():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    tl = cfg.get("teamliste", {}).get(gid, {})
    tl["channel_id"] = d.get("kanal_id", ""); tl["title"] = d.get("titel", "Teamliste")
    cfg.setdefault("teamliste", {})[gid] = tl; save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/ingamelog", methods=["GET", "POST"])
@login_required
def api_ingamelog():
    if request.method == "POST":
        d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
        cfg.setdefault("ingame_panel_channel", {})[gid] = d.get("panel_kanal_id", "")
        cfg.setdefault("ingame_log_channel", {})[gid] = d.get("log_kanal_id", "")
        save_cfg(cfg); return jsonify({"ok": True})
    gid = request.args.get("guild_id"); cfg = get_cfg()
    return jsonify({"panel_kanal_id": cfg.get("ingame_panel_channel", {}).get(gid, ""), "log_kanal_id": cfg.get("ingame_log_channel", {}).get(gid, "")})

@app.route("/api/autorole", methods=["POST"])
@login_required
def api_autorole():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    cfg.setdefault("auto_role", {})[gid] = d.get("role_id", ""); save_cfg(cfg); return jsonify({"ok": True})

@app.route("/api/backup", methods=["GET", "POST"])
@login_required
def api_backup():
    if request.method == "POST":
        d = request.json; gid = d.get("guild_id")
        db["backup_config"].update_one({"guild_id": gid}, {"$set": {"guild_id": gid, "auto_backup": d.get("auto_backup", False), "log_kanal_id": d.get("log_kanal_id", "")}}, upsert=True)
        return jsonify({"ok": True})
    gid = request.args.get("guild_id"); doc = db["backup_config"].find_one({"guild_id": gid}) or {}; doc.pop("_id", None); return jsonify(doc)

@app.route("/api/ranklog", methods=["POST"])
@login_required
def api_ranklog():
    d = request.json; gid = d.get("guild_id"); cfg = get_cfg()
    cfg.setdefault("ranklog", {})[gid] = {"channel_id": d.get("kanal_id", ""), "von_role_id": d.get("von_id", ""), "bis_role_id": d.get("bis_id", "")}
    save_cfg(cfg); return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

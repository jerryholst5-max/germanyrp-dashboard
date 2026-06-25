import os
import requests
from flask import Flask, redirect, request, session, jsonify, Response
from pymongo import MongoClient
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "germanyrp-secret-key-2026")

DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://germanyrp-dashboard-production.up.railway.app/callback")
BOT_OWNER_ID = "1408144132966322407"
MONGODB_URL = os.environ.get("MONGODB_URL")
mongo_client = MongoClient(MONGODB_URL)
db = mongo_client["germanyrp"]
DISCORD_API = "https://discord.com/api/v10"

CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root { --bg:#0f0f0f;--bg2:#1a1a1a;--bg3:#242424;--border:#2e2e2e;--text:#e8e8e8;--text2:#999;--accent:#f0a500;--accent2:#c47d00;--red:#e05252;--green:#52c078;--radius:10px; }
body { background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh; }
.layout { display:flex;min-height:100vh; }
.sidebar { width:240px;background:var(--bg2);border-right:1px solid var(--border);padding:1.5rem 1rem;display:flex;flex-direction:column;gap:.5rem;flex-shrink:0; }
.logo { display:flex;align-items:center;gap:10px;padding:.5rem;margin-bottom:1rem;font-size:15px;font-weight:600;color:var(--accent); }
.nav-item { display:flex;align-items:center;gap:10px;padding:.6rem .8rem;border-radius:8px;color:var(--text2);font-size:14px;text-decoration:none;transition:all .15s;cursor:pointer;border:none;background:none;width:100%;text-align:left; }
.nav-item:hover,.nav-item.active { background:var(--bg3);color:var(--text); }
.nav-section { font-size:11px;color:var(--text2);padding:.8rem .8rem .3rem;text-transform:uppercase;letter-spacing:.5px; }
.main { flex:1;padding:2rem;overflow-y:auto; }
.page-title { font-size:22px;font-weight:600;margin-bottom:.4rem; }
.page-sub { color:var(--text2);font-size:14px;margin-bottom:2rem; }
.card { background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-bottom:1.5rem; }
.card-title { font-size:15px;font-weight:600;margin-bottom:1rem; }
.form-row { display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem; }
.form-group { display:flex;flex-direction:column;gap:6px; }
.form-label { font-size:13px;color:var(--text2); }
.form-input,.form-select { background:var(--bg3);border:1px solid var(--border);border-radius:8px;color:var(--text);padding:.6rem .8rem;font-size:14px;width:100%;outline:none; }
.form-input:focus,.form-select:focus { border-color:var(--accent); }
.toggle-row { display:flex;align-items:center;justify-content:space-between;padding:.8rem 0;border-bottom:1px solid var(--border); }
.toggle-row:last-child { border-bottom:none; }
.toggle-info { display:flex;flex-direction:column;gap:3px; }
.toggle-label { font-size:14px;font-weight:500; }
.toggle-desc { font-size:12px;color:var(--text2); }
.toggle { position:relative;width:44px;height:24px;flex-shrink:0; }
.toggle input { opacity:0;width:0;height:0; }
.slider { position:absolute;inset:0;background:var(--border);border-radius:24px;cursor:pointer;transition:.2s; }
.slider:before { content:"";position:absolute;height:18px;width:18px;left:3px;top:3px;background:white;border-radius:50%;transition:.2s; }
input:checked+.slider { background:var(--accent); }
input:checked+.slider:before { transform:translateX(20px); }
.btn { padding:.6rem 1.2rem;border-radius:8px;border:none;font-size:14px;font-weight:500;cursor:pointer; }
.btn-primary { background:var(--accent);color:#000; }
.btn-danger { background:var(--red);color:white; }
.btn-ghost { background:var(--bg3);color:var(--text);border:1px solid var(--border); }
.alert { padding:.8rem 1rem;border-radius:8px;font-size:14px;margin-bottom:1rem;display:none; }
.alert-success { background:rgba(82,192,120,.15);border:1px solid rgba(82,192,120,.3);color:var(--green); }
.alert-error { background:rgba(224,82,82,.15);border:1px solid rgba(224,82,82,.3);color:var(--red); }
.guild-bar { display:flex;align-items:center;gap:1rem;margin-bottom:2rem;padding:1rem 1.25rem;background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius); }
.table { width:100%;border-collapse:collapse;font-size:14px; }
.table th { text-align:left;padding:.6rem 1rem;color:var(--text2);font-size:12px;text-transform:uppercase;border-bottom:1px solid var(--border); }
.table td { padding:.75rem 1rem;border-bottom:1px solid var(--border); }
.page { display:none; }
.page.active { display:block; }
.login-wrap { min-height:100vh;display:flex;align-items:center;justify-content:center; }
.login-card { background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:3rem 2.5rem;text-align:center;max-width:400px;width:100%; }
.btn-discord { background:#5865F2;color:white;display:inline-flex;align-items:center;gap:10px;padding:.8rem 1.8rem;border-radius:10px;font-size:15px;font-weight:600;text-decoration:none; }
.overview-grid { display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem; }
.overview-card { background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;text-align:center;cursor:pointer; }
.overview-card:hover { border-color:var(--accent); }
.overview-icon { font-size:32px;margin-bottom:.5rem; }
@media(max-width:768px){.sidebar{display:none}.form-row{grid-template-columns:1fr}}
"""

def html(title, body, user=None):
    user_html = ""
    if user:
        avatar = f"https://cdn.discordapp.com/avatars/{user['id']}/{user.get('avatar','')}.png"
        user_html = f"""
        <div style="margin-top:auto;padding-top:1rem;border-top:1px solid var(--border)">
          <div style="display:flex;align-items:center;gap:10px;padding:.5rem">
            <img src="{avatar}" style="width:32px;height:32px;border-radius:50%" onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
            <div><div style="font-size:13px;font-weight:600">{user['username']}</div><div style="font-size:11px;color:var(--text2)">Owner</div></div>
          </div>
          <a href="/logout" class="nav-item" style="color:var(--red)">🚪 Abmelden</a>
        </div>"""
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>"""

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if "user" not in session: return redirect("/")
        if str(session["user"]["id"]) != BOT_OWNER_ID:
            return Response(html("Kein Zugriff", '<div class="login-wrap"><div class="login-card"><div style="font-size:48px">❌</div><h1 style="margin:1rem 0 .5rem">Kein Zugriff</h1><p style="color:var(--text2)">Nur der Bot-Owner kann das Dashboard nutzen.</p><a href="/logout" class="btn btn-ghost" style="display:inline-block;margin-top:1rem">Zurück</a></div></div>'), content_type="text/html")
        return f(*a, **kw)
    return dec

def get_config():
    doc = db["config"].find_one({"_id": "main"}) or {}
    doc.pop("_id", None)
    return doc

def save_config(cfg):
    db["config"].update_one({"_id": "main"}, {"$set": cfg}, upsert=True)

@app.route("/")
def index():
    if "user" in session: return redirect("/servers")
    OAUTH = f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify+guilds"
    body = f"""<div class="login-wrap"><div class="login-card">
      <div style="font-size:48px;margin-bottom:1rem">🇩🇪</div>
      <h1 style="font-size:24px;font-weight:700;margin-bottom:.5rem">GermanyRP Dashboard</h1>
      <p style="color:var(--text2);font-size:14px;margin-bottom:2rem">Melde dich mit Discord an um den Bot zu konfigurieren.</p>
      <a href="{OAUTH}" class="btn-discord">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057c.002.022.015.043.032.056a19.9 19.9 0 0 0 5.993 3.03.077.077 0 0 0 .083-.026c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03z"/></svg>
        Mit Discord anmelden
      </a>
    </div></div>"""
    return Response(html("GermanyRP Dashboard", body), content_type="text/html")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code: return redirect("/")
    r = requests.post(f"{DISCORD_API}/oauth2/token", data={"client_id":DISCORD_CLIENT_ID,"client_secret":DISCORD_CLIENT_SECRET,"grant_type":"authorization_code","code":code,"redirect_uri":DISCORD_REDIRECT_URI})
    token = r.json().get("access_token")
    if not token: return redirect("/")
    user = requests.get(f"{DISCORD_API}/users/@me", headers={"Authorization":f"Bearer {token}"}).json()
    if str(user.get("id")) != BOT_OWNER_ID: return redirect("/")
    session["user"] = user
    session["token"] = token
    return redirect("/servers")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/servers")
@login_required
def servers():
    user = session["user"]
    guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers={"Authorization":f"Bearer {session['token']}"})
    guilds = guilds_r.json() if guilds_r.ok else []
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    bot_guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers={"Authorization":f"Bot {bot_token}"})
    bot_guild_ids = {g["id"] for g in (bot_guilds_r.json() if bot_guilds_r.ok else [])}
    guilds = [g for g in guilds if g["id"] in bot_guild_ids]
    avatar = f"https://cdn.discordapp.com/avatars/{user['id']}/{user.get('avatar','')}.png"

    guild_cards = ""
    for g in guilds:
        icon = f"https://cdn.discordapp.com/icons/{g['id']}/{g.get('icon')}.png" if g.get("icon") else ""
        icon_html = f'<img src="{icon}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;margin-bottom:1rem">' if icon else f'<div style="width:80px;height:80px;border-radius:50%;background:var(--bg3);display:flex;align-items:center;justify-content:center;font-size:28px;margin:0 auto 1rem">{g["name"][0]}</div>'
        guild_cards += f"""<a href="/dashboard/{g['id']}" style="text-decoration:none">
          <div class="server-card" onmouseover="this.style.borderColor='var(--accent)';this.style.transform='translateY(-3px)'" onmouseout="this.style.borderColor='var(--border)';this.style.transform='none'">
            {icon_html}
            <div style="color:var(--text);font-weight:600;font-size:14px;margin-bottom:.25rem">{g['name']}</div>
            <div style="color:var(--text2);font-size:11px;margin-bottom:.75rem">{g['id']}</div>
            <div style="background:var(--accent);color:#000;padding:.35rem .9rem;border-radius:6px;font-size:12px;font-weight:700;display:inline-block">Verwalten</div>
          </div>
        </a>"""

    body = f"""<style>
    .server-card {{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:1.5rem;text-align:center;cursor:pointer;transition:all .2s;}}
    </style>
    <div style="min-height:100vh">
      <div style="background:var(--bg2);border-bottom:1px solid var(--border);padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between">
        <div style="font-size:18px;font-weight:700;color:var(--accent)">GermanyRP Dashboard</div>
        <div style="display:flex;align-items:center;gap:12px">
          <img src="{avatar}" style="width:32px;height:32px;border-radius:50%" onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
          <span style="font-size:14px;font-weight:500">{user['username']}</span>
          <a href="/logout" style="color:var(--red);font-size:13px;text-decoration:none">Abmelden</a>
        </div>
      </div>
      <div style="padding:3rem 2rem">
        <h1 style="font-size:28px;font-weight:700;text-align:center;margin-bottom:.5rem">Server Ubersicht</h1>
        <p style="color:var(--text2);text-align:center;margin-bottom:2.5rem">Wahle einen Server aus den du verwalten mochtest.</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1.25rem;max-width:1000px;margin:0 auto">
          {guild_cards if guild_cards else '<p style="color:var(--text2);text-align:center">Keine Server gefunden.</p>'}
        </div>
      </div>
    </div>"""
    return Response(html("GermanyRP Dashboard", body), content_type="text/html")

@app.route("/dashboard")
@app.route("/dashboard/<guild_id>")
@login_required
def dashboard(guild_id=None):
    if not guild_id:
        return redirect("/servers")
    user = session["user"]
    guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers={"Authorization":f"Bearer {session['token']}"})
    guilds = guilds_r.json() if guilds_r.ok else []
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    bot_guilds_r = requests.get(f"{DISCORD_API}/users/@me/guilds", headers={"Authorization":f"Bot {bot_token}"})
    bot_guild_ids = {g["id"] for g in (bot_guilds_r.json() if bot_guilds_r.ok else [])}
    guilds = [g for g in guilds if g["id"] in bot_guild_ids]
    selected = next((g for g in guilds if g["id"] == guild_id), None)
    if not selected:
        return redirect("/servers")
    guild_opts = "".join(f'<option value="{g["id"]}">{g["name"]}</option>' for g in guilds)
    avatar = f"https://cdn.discordapp.com/avatars/{user['id']}/{user.get('avatar','')}.png"

    sel_icon = f"https://cdn.discordapp.com/icons/{selected['id']}/{selected.get('icon')}.png" if selected.get("icon") else ""
    sel_icon_html = f'<img src="{sel_icon}" style="width:28px;height:28px;border-radius:50%;object-fit:cover">' if sel_icon else '<span style="font-size:20px">&#x1F1E9;&#x1F1EA;</span>'
    sidebar = f"""<nav class="sidebar">
      <div class="logo">{sel_icon_html} {selected.get('name','GermanyRP')[:18]}</div>
      <a href="/servers" class="nav-item" style="color:var(--text2);font-size:12px;margin-bottom:.25rem">&#8592; Server wechseln</a>
      <span class="nav-section">Allgemein</span>
      <button class="nav-item active" onclick="show('uebersicht',this)">📊 Übersicht</button>
      <span class="nav-section">Bot Einstellungen</span>
      <button class="nav-item" onclick="show('logs',this)">📋 Log-System</button>
      <button class="nav-item" onclick="show('automod',this)">🛡️ Automod</button>
      <button class="nav-item" onclick="show('level',this)">⬆️ Level-System</button>
      <button class="nav-item" onclick="show('tickets',this)">🎫 Tickets</button>
      <button class="nav-item" onclick="show('partner',this)">🤝 Partner</button>
      <button class="nav-item" onclick="show('abmeldung',this)">📋 Abmeldung</button>
      <button class="nav-item" onclick="show('voicesupport',this)">🎙️ Voice-Support</button>
      <span class="nav-section">Server Setup</span>
      <button class="nav-item" onclick="show('willkommen',this)">👋 Willkommen/Abschied</button>
      <button class="nav-item" onclick="show('ticketsetup',this)">🎫 Ticket-Setup</button>
      <button class="nav-item" onclick="show('teamliste',this)">👥 Teamliste</button>
      <button class="nav-item" onclick="show('ranklog',this)">📈 Ranklog</button>
      <button class="nav-item" onclick="show('ingamelog',this)">🎮 Ingame-Log</button>
      <button class="nav-item" onclick="show('backup',this)">💾 Backup</button>
      <button class="nav-item" onclick="show('autorole',this)">🤖 Auto-Rolle</button>
      <div style="margin-top:auto;padding-top:1rem;border-top:1px solid var(--border)">
        <div style="display:flex;align-items:center;gap:10px;padding:.5rem">
          <img src="{avatar}" style="width:32px;height:32px;border-radius:50%" onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
          <div><div style="font-size:13px;font-weight:600">{user['username']}</div><div style="font-size:11px;color:var(--text2)">Owner</div></div>
        </div>
        <a href="/logout" class="nav-item" style="color:var(--red)">🚪 Abmelden</a>
      </div>
    </nav>"""

    main = f"""<main class="main">
      <div class="guild-bar">
        <label style="font-size:13px;color:var(--text2)">Server:</label>
        <select class="form-select" style="max-width:300px" onchange="onGuild(this.value)">
          <option value="">Server auswählen...</option>{guild_opts}
        </select>
      </div>

      <div class="page active" id="page-uebersicht">
        <h1 class="page-title">Willkommen, {user['username']}! 👋</h1>
        <p class="page-sub">Wähle oben deinen Server aus und dann eine Kategorie in der Sidebar.</p>
        <div class="overview-grid">
          <div class="overview-card" onclick="show('logs',null)"><div class="overview-icon">📋</div><div style="font-weight:600">Log-System</div></div>
          <div class="overview-card" onclick="show('automod',null)"><div class="overview-icon">🛡️</div><div style="font-weight:600">Automod</div></div>
          <div class="overview-card" onclick="show('level',null)"><div class="overview-icon">⬆️</div><div style="font-weight:600">Level-System</div></div>
          <div class="overview-card" onclick="show('tickets',null)"><div class="overview-icon">🎫</div><div style="font-weight:600">Tickets</div></div>
          <div class="overview-card" onclick="show('partner',null)"><div class="overview-icon">🤝</div><div style="font-weight:600">Partner</div></div>
          <div class="overview-card" onclick="show('abmeldung',null)"><div class="overview-icon">📋</div><div style="font-weight:600">Abmeldung</div></div>
          <div class="overview-card" onclick="show('voicesupport',null)"><div class="overview-icon">🎙️</div><div style="font-weight:600">Voice-Support</div></div>
        </div>
      </div>

      <div class="page" id="page-logs">
        <h1 class="page-title">Log-System</h1>
        <p class="page-sub">Lege fest welche Ereignisse geloggt werden.</p>
        <div id="alert-logs" class="alert"></div>
        <div class="card">
          <div class="card-title">Log-Kanal & Kategorien</div>
          <div class="form-row"><div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="log-channel"><option>Kanal laden...</option></select></div></div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">🔨 Moderation</div><div class="toggle-desc">Ban, Kick, Mute, Warn</div></div><label class="toggle"><input type="checkbox" id="log-moderation"><span class="slider"></span></label></div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">📝 Nachrichten</div><div class="toggle-desc">Gelöscht & bearbeitet</div></div><label class="toggle"><input type="checkbox" id="log-messages"><span class="slider"></span></label></div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">🛠️ Server-Änderungen</div><div class="toggle-desc">Rollen & Kanäle</div></div><label class="toggle"><input type="checkbox" id="log-server"><span class="slider"></span></label></div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">🎙️ Voice-Aktivität</div><div class="toggle-desc">Join, Leave, Switch</div></div><label class="toggle"><input type="checkbox" id="log-voice"><span class="slider"></span></label></div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">👤 Mitglieder</div><div class="toggle-desc">Join, Leave, Nickname</div></div><label class="toggle"><input type="checkbox" id="log-members"><span class="slider"></span></label></div>
          <div style="margin-top:1.5rem"><button class="btn btn-primary" onclick="saveLogs()">💾 Speichern</button></div>
        </div>
      </div>

      <div class="page" id="page-automod">
        <h1 class="page-title">Automod</h1>
        <p class="page-sub">Schimpfwörter und Scam-Werbung automatisch filtern.</p>
        <div id="alert-automod" class="alert"></div>
        <div class="card">
          <div class="card-title">Einstellungen</div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">Automod aktiv</div><div class="toggle-desc">Nachrichten filtern</div></div><label class="toggle"><input type="checkbox" id="automod-enabled"><span class="slider"></span></label></div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">Scam-Erkennung</div><div class="toggle-desc">Krypto/Werbung löschen</div></div><label class="toggle"><input type="checkbox" id="automod-scam"><span class="slider"></span></label></div>
          <div class="form-row" style="margin-top:1rem">
            <div class="form-group"><label class="form-label">Aktion</label><select class="form-select" id="automod-action"><option value="delete">Nur löschen</option><option value="warn">Löschen + warnen</option><option value="mute">Löschen + muten</option></select></div>
            <div class="form-group"><label class="form-label">Mute-Dauer (Min)</label><input type="number" class="form-input" id="automod-mute" min="1" max="60" value="5"></div>
          </div>
          <div class="form-row"><div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="automod-channel"><option value="">Kanal wählen...</option></select></div></div>
          <div style="margin-top:1rem"><button class="btn btn-primary" onclick="saveAutomod()">💾 Speichern</button></div>
        </div>
      </div>

      <div class="page" id="page-level">
        <h1 class="page-title">Level-System</h1>
        <p class="page-sub">XP und Level-Up Kanal konfigurieren.</p>
        <div id="alert-level" class="alert"></div>
        <div class="card">
          <div class="card-title">Einstellungen</div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">Level-System aktiv</div><div class="toggle-desc">XP durch Nachrichten und Voice</div></div><label class="toggle"><input type="checkbox" id="level-enabled"><span class="slider"></span></label></div>
          <div class="form-row" style="margin-top:1rem"><div class="form-group"><label class="form-label">Level-Up Kanal</label><select class="form-select" id="level-channel"><option value="">Kanal wählen...</option></select></div></div>
          <div style="margin-top:1rem"><button class="btn btn-primary" onclick="saveLevel()">💾 Speichern</button></div>
        </div>
      </div>

      <div class="page" id="page-tickets">
        <h1 class="page-title">Ticket-Kategorien</h1>
        <p class="page-sub">Kategorien für das Ticket-Dropdown verwalten.</p>
        <div id="alert-tickets" class="alert"></div>
        <div class="card">
          <div class="card-title">Neue Kategorie</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Name</label><input type="text" class="form-input" id="ticket-name" placeholder="z.B. Beschwerde"></div>
            <div class="form-group"><label class="form-label">Emoji</label><input type="text" class="form-input" id="ticket-emoji" placeholder="z.B. 😤"></div>
          </div>
          <button class="btn btn-primary" onclick="addTicketKat()">➕ Hinzufügen</button>
        </div>
        <div class="card"><div class="card-title">Aktuelle Kategorien</div><div id="ticket-list"><p style="color:var(--text2)">Server auswählen...</p></div></div>
      </div>

      <div class="page" id="page-partner">
        <h1 class="page-title">Partner</h1>
        <p class="page-sub">Partnerliste verwalten.</p>
        <div id="alert-partner" class="alert"></div>
        <div class="card">
          <div class="card-title">Partner hinzufügen</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Name</label><input type="text" class="form-input" id="partner-name" placeholder="Server-Name"></div>
            <div class="form-group"><label class="form-label">Link</label><input type="text" class="form-input" id="partner-link" placeholder="discord.gg/..."></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Kategorie</label><input type="text" class="form-input" id="partner-kat" placeholder="🌟 Große Partner"></div>
            <div class="form-group"><label class="form-label">Ansprechpartner</label><input type="text" class="form-input" id="partner-ap" placeholder="@Jeremy"></div>
          </div>
          <button class="btn btn-primary" onclick="addPartner()">➕ Hinzufügen</button>
        </div>
        <div class="card"><div class="card-title">Aktuelle Partner</div><div id="partner-list"><p style="color:var(--text2)">Server auswählen...</p></div></div>
      </div>

      <div class="page" id="page-voicesupport">
        <h1 class="page-title">Voice-Support System</h1>
        <p class="page-sub">Warteraum, Benachrichtigungs-Kanal und Support-Rolle konfigurieren.</p>
        <div id="alert-voicesupport" class="alert"></div>
        <div class="card">
          <div class="card-title">🎙️ System 1</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Warteraum (Voice)</label><select class="form-select" id="vs1-warteraum"><option value="">Voice-Channel wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Benachrichtigungs-Kanal</label><select class="form-select" id="vs1-notif"><option value="">Kanal wählen...</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Support-Rolle</label><select class="form-select" id="vs1-support-role"><option value="">Rolle wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Ping-Rolle</label><select class="form-select" id="vs1-ping-role"><option value="">Rolle wählen...</option></select></div>
          </div>
          <div style="margin-top:1rem"><button class="btn btn-primary" onclick="saveVS(1)">💾 System 1 Speichern</button></div>
        </div>
        <div class="card">
          <div class="card-title">🎙️ System 2</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Warteraum (Voice)</label><select class="form-select" id="vs2-warteraum"><option value="">Voice-Channel wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Benachrichtigungs-Kanal</label><select class="form-select" id="vs2-notif"><option value="">Kanal wählen...</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Support-Rolle</label><select class="form-select" id="vs2-support-role"><option value="">Rolle wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Ping-Rolle</label><select class="form-select" id="vs2-ping-role"><option value="">Rolle wählen...</option></select></div>
          </div>
          <div style="margin-top:1rem"><button class="btn btn-primary" onclick="saveVS(2)">💾 System 2 Speichern</button></div>
        </div>
      </div>

      <!-- Willkommen/Abschied -->
      <div class="page" id="page-willkommen">
        <h1 class="page-title">Willkommen & Abschied</h1>
        <p class="page-sub">Begrüßungs- und Abschiedsnachrichten konfigurieren.</p>
        <div id="alert-willkommen" class="alert"></div>
        <div class="card">
          <div class="card-title">👋 Willkommensnachricht</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Kanal</label><select class="form-select" id="welcome-channel"><option value="">Kanal wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Bild-URL (optional)</label><input type="text" class="form-input" id="welcome-image" placeholder="https://..."></div>
          </div>
          <div class="form-group" style="margin-bottom:1rem"><label class="form-label">Nachricht (optional, {user} = Mention)</label><input type="text" class="form-input" id="welcome-msg" placeholder="Willkommen {user}!"></div>
          <button class="btn btn-primary" onclick="saveWillkommen()">💾 Speichern</button>
        </div>
        <div class="card">
          <div class="card-title">🚪 Abschiedsnachricht</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Kanal</label><select class="form-select" id="goodbye-channel"><option value="">Kanal wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Bild-URL (optional)</label><input type="text" class="form-input" id="goodbye-image" placeholder="https://..."></div>
          </div>
          <div class="form-group" style="margin-bottom:1rem"><label class="form-label">Nachricht (optional)</label><input type="text" class="form-input" id="goodbye-msg" placeholder="Auf Wiedersehen {user}!"></div>
          <button class="btn btn-primary" onclick="saveAbschied()">💾 Speichern</button>
        </div>
      </div>

      <!-- Ticket Setup -->
      <div class="page" id="page-ticketsetup">
        <h1 class="page-title">Ticket-Setup</h1>
        <p class="page-sub">Ticket-Panel, Support-Rolle und Transcript-Kanal konfigurieren.</p>
        <div id="alert-ticketsetup" class="alert"></div>
        <div class="card">
          <div class="card-title">🎫 Einstellungen</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Panel-Kanal</label><select class="form-select" id="ticket-panel-ch"><option value="">Kanal wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Transcript-Kanal</label><select class="form-select" id="ticket-transcript-ch"><option value="">Kanal wählen...</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Support-Rolle</label><select class="form-select" id="ticket-support-role"><option value="">Rolle wählen...</option></select></div>
          </div>
          <button class="btn btn-primary" onclick="saveTicketSetup()">💾 Speichern</button>
        </div>
      </div>

      <!-- Teamliste -->
      <div class="page" id="page-teamliste">
        <h1 class="page-title">Teamliste</h1>
        <p class="page-sub">Kanal und Titel für die automatische Teamliste konfigurieren.</p>
        <div id="alert-teamliste" class="alert"></div>
        <div class="card">
          <div class="card-title">👥 Einstellungen</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Kanal</label><select class="form-select" id="teamliste-channel"><option value="">Kanal wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Titel</label><input type="text" class="form-input" id="teamliste-titel" placeholder="Teamliste"></div>
          </div>
          <button class="btn btn-primary" onclick="saveTeamliste()">💾 Speichern</button>
        </div>
      </div>

      <!-- Ranklog -->
      <div class="page" id="page-ranklog">
        <h1 class="page-title">Ranklog</h1>
        <p class="page-sub">Kanal und Rollen-Range für den Ranklog konfigurieren.</p>
        <div id="alert-ranklog" class="alert"></div>
        <div class="card">
          <div class="card-title">📈 Einstellungen</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="ranklog-channel"><option value="">Kanal wählen...</option></select></div>
          </div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Von Rolle</label><select class="form-select" id="ranklog-von"><option value="">Rolle wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Bis Rolle</label><select class="form-select" id="ranklog-bis"><option value="">Rolle wählen...</option></select></div>
          </div>
          <button class="btn btn-primary" onclick="saveRanklog()">💾 Speichern</button>
        </div>
      </div>

      <!-- Ingame Log -->
      <div class="page" id="page-ingamelog">
        <h1 class="page-title">Ingame-Log</h1>
        <p class="page-sub">Panel-Kanal und Log-Kanal für In-Game Bans/Kicks konfigurieren.</p>
        <div id="alert-ingamelog" class="alert"></div>
        <div class="card">
          <div class="card-title">🎮 Einstellungen</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Panel-Kanal</label><select class="form-select" id="ingame-panel-ch"><option value="">Kanal wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="ingame-log-ch"><option value="">Kanal wählen...</option></select></div>
          </div>
          <button class="btn btn-primary" onclick="saveIngamelog()">💾 Speichern</button>
        </div>
      </div>

      <!-- Backup -->
      <div class="page" id="page-backup">
        <h1 class="page-title">Backup-System</h1>
        <p class="page-sub">Auto-Backup aktivieren und Log-Kanal konfigurieren.</p>
        <div id="alert-backup" class="alert"></div>
        <div class="card">
          <div class="card-title">💾 Einstellungen</div>
          <div class="toggle-row"><div class="toggle-info"><div class="toggle-label">Auto-Backup aktiv</div><div class="toggle-desc">Täglich um 03:00 UTC</div></div><label class="toggle"><input type="checkbox" id="backup-auto"><span class="slider"></span></label></div>
          <div class="form-row" style="margin-top:1rem">
            <div class="form-group"><label class="form-label">Log-Kanal (optional)</label><select class="form-select" id="backup-log-ch"><option value="">Kanal wählen...</option></select></div>
          </div>
          <button class="btn btn-primary" onclick="saveBackup()">💾 Speichern</button>
        </div>
      </div>

      <!-- Auto-Rolle -->
      <div class="page" id="page-autorole">
        <h1 class="page-title">Auto-Rolle</h1>
        <p class="page-sub">Rolle die neue Mitglieder automatisch erhalten.</p>
        <div id="alert-autorole" class="alert"></div>
        <div class="card">
          <div class="card-title">🤖 Einstellungen</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Auto-Rolle</label><select class="form-select" id="autorole-role"><option value="">Rolle wählen...</option></select></div>
          </div>
          <button class="btn btn-primary" onclick="saveAutorole()">💾 Speichern</button>
        </div>
      </div>

      <div class="page" id="page-abmeldung">
        <h1 class="page-title">Abmeldung</h1>
        <p class="page-sub">Abwesenheitsrolle und Log-Kanal konfigurieren.</p>
        <div id="alert-abmeldung" class="alert"></div>
        <div class="card">
          <div class="card-title">Einstellungen</div>
          <div class="form-row">
            <div class="form-group"><label class="form-label">Abwesenheitsrolle</label><select class="form-select" id="abmeldung-rolle"><option value="">Rolle wählen...</option></select></div>
            <div class="form-group"><label class="form-label">Bestätigungsrolle</label><select class="form-select" id="abmeldung-bestaetigung"><option value="">Rolle wählen...</option></select></div>
          </div>
          <div class="form-row"><div class="form-group"><label class="form-label">Log-Kanal</label><select class="form-select" id="abmeldung-log"><option value="">Kanal wählen...</option></select></div></div>
          <div style="margin-top:1rem"><button class="btn btn-primary" onclick="saveAbmeldung()">💾 Speichern</button></div>
        </div>
      </div>
    </main>"""

    script = """<script>
let guild="{guild_id_placeholder}";
const guildName="{guild_name_placeholder}";
window.addEventListener('load',()=>{if(guild)onGuild(guild);});
function show(id,el){document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));document.getElementById('page-'+id).classList.add('active');if(el)el.classList.add('active');}
function alert2(id,msg,t='success'){const e=document.getElementById('alert-'+id);e.textContent=msg;e.className='alert alert-'+t;e.style.display='block';setTimeout(()=>e.style.display='none',3000);}
async function api(p,m='GET',b=null){const o={method:m,headers:{'Content-Type':'application/json'}};if(b)o.body=JSON.stringify(b);return(await fetch(p,o)).json();}
async function onGuild(id){if(!id)return;guild=id;const ch=await api('/api/channels?guild_id='+id);const ro=await api('/api/roles?guild_id='+id);const co=ch.text.map(c=>`<option value="${c.id}">#${c.name}</option>`).join('');const vo=ch.voice.map(c=>`<option value="${c.id}">🔊 ${c.name}</option>`).join('');const ro2=ro.map(r=>`<option value="${r.id}">@${r.name}</option>`).join('');['log-channel','automod-channel','level-channel','abmeldung-log','vs1-notif','vs2-notif','welcome-channel','goodbye-channel','ticket-panel-ch','ticket-transcript-ch','teamliste-channel','ranklog-channel','ingame-panel-ch','ingame-log-ch','backup-log-ch'].forEach(x=>{const s=document.getElementById(x);if(s)s.innerHTML='<option value="">Kanal wählen...</option>'+co;});['vs1-warteraum','vs2-warteraum'].forEach(x=>{const s=document.getElementById(x);if(s)s.innerHTML='<option value="">Voice-Channel wählen...</option>'+vo;});['abmeldung-rolle','abmeldung-bestaetigung','vs1-support-role','vs1-ping-role','vs2-support-role','vs2-ping-role','ticket-support-role','ranklog-von','ranklog-bis','autorole-role'].forEach(x=>{const s=document.getElementById(x);if(s)s.innerHTML='<option value="">Rolle wählen...</option>'+ro2;});await loadLogs();await loadAutomod();await loadLevel();await loadPartner();await loadTickets();await loadAbmeldung();await loadVS(1);await loadVS(2);await loadWillkommen();await loadAbschied();await loadTicketSetup();await loadTeamliste();await loadRanklog();await loadIngamelog();await loadBackup();await loadAutorole();}
async function loadLogs(){const c=await api('/api/logs?guild_id='+guild);if(c.channel_id)document.getElementById('log-channel').value=c.channel_id;['moderation','messages','server','voice','members'].forEach(x=>document.getElementById('log-'+x).checked=(c.categories||[]).includes(x));}
async function saveLogs(){if(!guild)return alert2('logs','⚠️ Server auswählen!','error');const cats=['moderation','messages','server','voice','members'].filter(x=>document.getElementById('log-'+x).checked);await api('/api/logs','POST',{guild_id:guild,channel_id:document.getElementById('log-channel').value,categories:cats});alert2('logs','✅ Gespeichert!');}
async function loadAutomod(){const c=await api('/api/automod?guild_id='+guild);document.getElementById('automod-enabled').checked=c.enabled||false;document.getElementById('automod-scam').checked=c.scam_detection!==false;document.getElementById('automod-action').value=c.action||'warn';document.getElementById('automod-mute').value=c.mute_duration||5;if(c.log_channel_id)document.getElementById('automod-channel').value=c.log_channel_id;}
async function saveAutomod(){if(!guild)return alert2('automod','⚠️ Server auswählen!','error');await api('/api/automod','POST',{guild_id:guild,enabled:document.getElementById('automod-enabled').checked,scam_detection:document.getElementById('automod-scam').checked,action:document.getElementById('automod-action').value,mute_duration:document.getElementById('automod-mute').value,log_channel_id:document.getElementById('automod-channel').value});alert2('automod','✅ Gespeichert!');}
async function loadLevel(){const c=await api('/api/level?guild_id='+guild);document.getElementById('level-enabled').checked=c.enabled||false;if(c.levelup_channel_id)document.getElementById('level-channel').value=c.levelup_channel_id;}
async function saveLevel(){if(!guild)return alert2('level','⚠️ Server auswählen!','error');await api('/api/level','POST',{guild_id:guild,enabled:document.getElementById('level-enabled').checked,levelup_channel_id:document.getElementById('level-channel').value});alert2('level','✅ Gespeichert!');}
async function loadTickets(){const k=await api('/api/tickets?guild_id='+guild);const el=document.getElementById('ticket-list');if(!k.length){el.innerHTML='<p style="color:var(--text2)">Noch keine Kategorien.</p>';return;}el.innerHTML='<table class="table"><thead><tr><th>Emoji</th><th>Name</th><th></th></tr></thead><tbody>'+k.map(x=>`<tr><td>${x.emoji}</td><td>${x.name}</td><td><button class="btn btn-danger" style="padding:.3rem .7rem;font-size:12px" onclick="delTicket('${x.name}')">Löschen</button></td></tr>`).join('')+'</tbody></table>';}
async function addTicketKat(){if(!guild)return alert2('tickets','⚠️ Server auswählen!','error');const n=document.getElementById('ticket-name').value.trim();const e=document.getElementById('ticket-emoji').value.trim()||'🎫';if(!n)return alert2('tickets','⚠️ Name eingeben!','error');await api('/api/tickets','POST',{guild_id:guild,name:n,emoji:e});document.getElementById('ticket-name').value='';document.getElementById('ticket-emoji').value='';alert2('tickets','✅ Hinzugefügt!');await loadTickets();}
async function delTicket(n){await api('/api/tickets','DELETE',{guild_id:guild,name:n});alert2('tickets','✅ Gelöscht!');await loadTickets();}
async function loadPartner(){const c=await api('/api/partner?guild_id='+guild);const p=c.partners||[];const el=document.getElementById('partner-list');if(!p.length){el.innerHTML='<p style="color:var(--text2)">Noch keine Partner.</p>';return;}el.innerHTML='<table class="table"><thead><tr><th>Name</th><th>Kategorie</th><th>Link</th><th></th></tr></thead><tbody>'+p.map(x=>`<tr><td>${x.name}</td><td>${x.kategorie}</td><td><a href="${x.link.startsWith('http')?x.link:'https://'+x.link}" target="_blank" style="color:var(--accent)">${x.link}</a></td><td><button class="btn btn-danger" style="padding:.3rem .7rem;font-size:12px" onclick="delPartner('${x.name}')">Löschen</button></td></tr>`).join('')+'</tbody></table>';}
async function addPartner(){if(!guild)return alert2('partner','⚠️ Server auswählen!','error');const n=document.getElementById('partner-name').value.trim();const l=document.getElementById('partner-link').value.trim();if(!n||!l)return alert2('partner','⚠️ Name und Link eingeben!','error');await api('/api/partner','POST',{guild_id:guild,name:n,link:l,kategorie:document.getElementById('partner-kat').value.trim()||'🤝 Partner',ansprechpartner:document.getElementById('partner-ap').value.trim()});['partner-name','partner-link','partner-kat','partner-ap'].forEach(x=>document.getElementById(x).value='');alert2('partner','✅ Hinzugefügt!');await loadPartner();}
async function delPartner(n){await api('/api/partner?guild_id='+guild,'DELETE',{guild_id:guild,name:n});alert2('partner','✅ Gelöscht!');await loadPartner();}
async function loadAbmeldung(){const c=await api('/api/abmeldung?guild_id='+guild);if(c.abwesenheitsrolle_id)document.getElementById('abmeldung-rolle').value=c.abwesenheitsrolle_id;if(c.bestaetigung_rolle_id)document.getElementById('abmeldung-bestaetigung').value=c.bestaetigung_rolle_id;if(c.log_channel_id)document.getElementById('abmeldung-log').value=c.log_channel_id;}
async function saveAbmeldung(){if(!guild)return alert2('abmeldung','⚠️ Server auswählen!','error');await api('/api/abmeldung','POST',{guild_id:guild,abwesenheitsrolle_id:document.getElementById('abmeldung-rolle').value,bestaetigung_rolle_id:document.getElementById('abmeldung-bestaetigung').value,log_channel_id:document.getElementById('abmeldung-log').value});alert2('abmeldung','✅ Gespeichert!');}
async function loadVS(s){const c=await api('/api/voicesupport?guild_id='+guild+'&system='+s);if(c.warteraum_id)document.getElementById('vs'+s+'-warteraum').value=c.warteraum_id;if(c.notif_channel_id)document.getElementById('vs'+s+'-notif').value=c.notif_channel_id;if(c.support_role_id)document.getElementById('vs'+s+'-support-role').value=c.support_role_id;if(c.ping_role_id)document.getElementById('vs'+s+'-ping-role').value=c.ping_role_id;}
async function saveVS(s){if(!guild)return alert2('voicesupport','⚠️ Server auswählen!','error');await api('/api/voicesupport','POST',{guild_id:guild,system:String(s),warteraum_id:document.getElementById('vs'+s+'-warteraum').value,notif_channel_id:document.getElementById('vs'+s+'-notif').value,support_role_id:document.getElementById('vs'+s+'-support-role').value,ping_role_id:document.getElementById('vs'+s+'-ping-role').value});alert2('voicesupport','✅ System '+s+' gespeichert!');}
async function loadWillkommen(){const c=await api('/api/willkommen-setup?guild_id='+guild);if(c.channel_id)document.getElementById('welcome-channel').value=c.channel_id;document.getElementById('welcome-msg').value=c.message||'';document.getElementById('welcome-image').value=c.image_url||'';}
async function saveWillkommen(){if(!guild)return alert2('willkommen','⚠️ Server auswählen!','error');await api('/api/willkommen-setup','POST',{guild_id:guild,channel_id:document.getElementById('welcome-channel').value,message:document.getElementById('welcome-msg').value,image_url:document.getElementById('welcome-image').value});alert2('willkommen','✅ Willkommensnachricht gespeichert!');}
async function loadAbschied(){const c=await api('/api/abschied-setup?guild_id='+guild);if(c.channel_id)document.getElementById('goodbye-channel').value=c.channel_id;document.getElementById('goodbye-msg').value=c.message||'';document.getElementById('goodbye-image').value=c.image_url||'';}
async function saveAbschied(){if(!guild)return alert2('willkommen','⚠️ Server auswählen!','error');await api('/api/abschied-setup','POST',{guild_id:guild,channel_id:document.getElementById('goodbye-channel').value,message:document.getElementById('goodbye-msg').value,image_url:document.getElementById('goodbye-image').value});alert2('willkommen','✅ Abschiedsnachricht gespeichert!');}
async function loadTicketSetup(){const c=await api('/api/ticket-setup?guild_id='+guild);if(c.panel_kanal_id)document.getElementById('ticket-panel-ch').value=c.panel_kanal_id;if(c.transcript_kanal_id)document.getElementById('ticket-transcript-ch').value=c.transcript_kanal_id;if(c.support_role_id)document.getElementById('ticket-support-role').value=c.support_role_id;}
async function saveTicketSetup(){if(!guild)return alert2('ticketsetup','⚠️ Server auswählen!','error');await api('/api/ticket-setup','POST',{guild_id:guild,panel_kanal_id:document.getElementById('ticket-panel-ch').value,transcript_kanal_id:document.getElementById('ticket-transcript-ch').value,support_role_id:document.getElementById('ticket-support-role').value});alert2('ticketsetup','✅ Ticket-Setup gespeichert!');}
async function loadTeamliste(){const c=await api('/api/teamliste-setup?guild_id='+guild);if(c.channel_id)document.getElementById('teamliste-channel').value=c.channel_id;document.getElementById('teamliste-titel').value=c.title||'Teamliste';}
async function saveTeamliste(){if(!guild)return alert2('teamliste','⚠️ Server auswählen!','error');await api('/api/teamliste-setup','POST',{guild_id:guild,kanal_id:document.getElementById('teamliste-channel').value,titel:document.getElementById('teamliste-titel').value||'Teamliste'});alert2('teamliste','✅ Teamliste gespeichert!');}
async function loadRanklog(){const c=await api('/api/ranklog-setup?guild_id='+guild);if(c.channel_id)document.getElementById('ranklog-channel').value=c.channel_id;if(c.von_role_id)document.getElementById('ranklog-von').value=c.von_role_id;if(c.bis_role_id)document.getElementById('ranklog-bis').value=c.bis_role_id;}
async function saveRanklog(){if(!guild)return alert2('ranklog','⚠️ Server auswählen!','error');await api('/api/ranklog-setup','POST',{guild_id:guild,kanal_id:document.getElementById('ranklog-channel').value,von_id:document.getElementById('ranklog-von').value,bis_id:document.getElementById('ranklog-bis').value});alert2('ranklog','✅ Ranklog gespeichert!');}
async function loadIngamelog(){const c=await api('/api/ingamelog-setup?guild_id='+guild);if(c.panel_kanal_id)document.getElementById('ingame-panel-ch').value=c.panel_kanal_id;if(c.log_kanal_id)document.getElementById('ingame-log-ch').value=c.log_kanal_id;}
async function saveIngamelog(){if(!guild)return alert2('ingamelog','⚠️ Server auswählen!','error');await api('/api/ingamelog-setup','POST',{guild_id:guild,panel_kanal_id:document.getElementById('ingame-panel-ch').value,log_kanal_id:document.getElementById('ingame-log-ch').value});alert2('ingamelog','✅ Ingame-Log gespeichert!');}
async function loadBackup(){const c=await api('/api/backup-setup?guild_id='+guild);document.getElementById('backup-auto').checked=c.auto_backup||false;if(c.log_kanal_id)document.getElementById('backup-log-ch').value=c.log_kanal_id;}
async function saveBackup(){if(!guild)return alert2('backup','⚠️ Server auswählen!','error');await api('/api/backup-setup','POST',{guild_id:guild,auto_backup:document.getElementById('backup-auto').checked,log_kanal_id:document.getElementById('backup-log-ch').value});alert2('backup','✅ Backup gespeichert!');}
async function loadAutorole(){const c=await api('/api/autorole-setup?guild_id='+guild);if(c.role_id)document.getElementById('autorole-role').value=c.role_id;}
async function saveAutorole(){if(!guild)return alert2('autorole','⚠️ Server auswählen!','error');await api('/api/autorole-setup','POST',{guild_id:guild,role_id:document.getElementById('autorole-role').value});alert2('autorole','✅ Auto-Rolle gespeichert!');}
</script>"""

    script_final = script.replace("{guild_id_placeholder}", guild_id).replace("{guild_name_placeholder}", selected.get("name",""))
    body = f'<div class="layout">{sidebar}{main}</div>{script_final}'
    return Response(html(f"GermanyRP Dashboard - {selected.get('name','')}", body), content_type="text/html")

# API Routes
@app.route("/api/channels")
@login_required
def api_channels():
    gid = request.args.get("guild_id")
    r = requests.get(f"{DISCORD_API}/guilds/{gid}/channels", headers={"Authorization":f"Bot {os.environ.get('DISCORD_BOT_TOKEN')}"})
    if not r.ok: return jsonify([])
    all_ch = r.json()
    text = [{"id":c["id"],"name":c["name"],"type":"text"} for c in all_ch if c.get("type")==0]
    voice = [{"id":c["id"],"name":c["name"],"type":"voice"} for c in all_ch if c.get("type")==2]
    return jsonify({"text": text, "voice": voice})

@app.route("/api/roles")
@login_required
def api_roles():
    gid = request.args.get("guild_id")
    r = requests.get(f"{DISCORD_API}/guilds/{gid}/roles", headers={"Authorization":f"Bot {os.environ.get('DISCORD_BOT_TOKEN')}"})
    if not r.ok: return jsonify([])
    return jsonify([{"id":ro["id"],"name":ro["name"]} for ro in sorted(r.json(), key=lambda x:-x["position"]) if ro["name"]!="@everyone"])

@app.route("/api/logs", methods=["GET","POST"])
@login_required
def api_logs():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("unified_log_config",{})[gid]={"channel_id":d.get("channel_id"),"categories":d.get("categories",[])}
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify(cfg.get("unified_log_config",{}).get(gid,{}))

@app.route("/api/automod", methods=["GET","POST"])
@login_required
def api_automod():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id")
        db["automod_config"].update_one({"guild_id":gid},{"$set":{**d,"guild_id":gid}},upsert=True)
        return jsonify({"ok":True})
    gid=request.args.get("guild_id"); doc=db["automod_config"].find_one({"guild_id":gid}) or {}; doc.pop("_id",None)
    return jsonify(doc)

@app.route("/api/level", methods=["GET","POST"])
@login_required
def api_level():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("level_config",{})[gid]={"enabled":d.get("enabled"),"levelup_channel_id":d.get("levelup_channel_id","")}
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify(cfg.get("level_config",{}).get(gid,{}))

@app.route("/api/tickets", methods=["GET","POST","DELETE"])
@login_required
def api_tickets():
    gid=request.args.get("guild_id") or (request.json or {}).get("guild_id")
    if request.method=="GET":
        cfg=get_config(); return jsonify(cfg.get("ticket_kategorien",{}).get(gid,[]))
    if request.method=="POST":
        d=request.json; cfg=get_config(); kat=cfg.setdefault("ticket_kategorien",{}).setdefault(gid,[])
        kat.append({"name":d.get("name"),"emoji":d.get("emoji","🎫")}); save_config(cfg); return jsonify({"ok":True})
    if request.method=="DELETE":
        d=request.json; cfg=get_config(); kat=cfg.get("ticket_kategorien",{}).get(gid,[])
        cfg["ticket_kategorien"][gid]=[k for k in kat if k["name"]!=d.get("name")]; save_config(cfg); return jsonify({"ok":True})

@app.route("/api/partner", methods=["GET","POST","DELETE"])
@login_required
def api_partner():
    gid=request.args.get("guild_id") or (request.json or {}).get("guild_id")
    if request.method=="GET":
        doc=db["partner_config"].find_one({"guild_id":gid}) or {}; doc.pop("_id",None); return jsonify(doc)
    if request.method=="POST":
        d=request.json; doc=db["partner_config"].find_one({"guild_id":gid}) or {"guild_id":gid,"partners":[]}
        doc["partners"].append({"name":d.get("name"),"link":d.get("link"),"kategorie":d.get("kategorie","🤝 Partner"),"ansprechpartner":d.get("ansprechpartner","")})
        db["partner_config"].update_one({"guild_id":gid},{"$set":{"partners":doc["partners"]}},upsert=True); return jsonify({"ok":True})
    if request.method=="DELETE":
        d=request.json; doc=db["partner_config"].find_one({"guild_id":gid}) or {}
        db["partner_config"].update_one({"guild_id":gid},{"$set":{"partners":[p for p in doc.get("partners",[]) if p["name"]!=d.get("name")]}},upsert=True); return jsonify({"ok":True})

@app.route("/api/ticket-setup", methods=["GET","POST"])
@login_required
def api_ticket_setup():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("ticket_setup",{})[gid]={"support_role_id":d.get("support_role_id",""),"transcript_kanal_id":d.get("transcript_kanal_id",""),"panel_kanal_id":d.get("panel_kanal_id","")}
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify(cfg.get("ticket_setup",{}).get(gid,{}))

@app.route("/api/willkommen-setup", methods=["GET","POST"])
@login_required
def api_willkommen():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("welcome",{})[gid]={"channel_id":d.get("channel_id",""),"message":d.get("message",""),"image_url":d.get("image_url","")}
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify(cfg.get("welcome",{}).get(gid,{}))

@app.route("/api/abschied-setup", methods=["GET","POST"])
@login_required
def api_abschied():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("goodbye",{})[gid]={"channel_id":d.get("channel_id",""),"message":d.get("message",""),"image_url":d.get("image_url","")}
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify(cfg.get("goodbye",{}).get(gid,{}))

@app.route("/api/modlog-setup", methods=["GET","POST"])
@login_required
def api_modlog():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        logs=cfg.get("logs",{}); logs.setdefault(gid,{})["ban_log"]=d.get("kanal_id","")
        cfg["logs"]=logs; save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify({"kanal_id":cfg.get("logs",{}).get(gid,{}).get("ban_log","")})

@app.route("/api/ingamelog-setup", methods=["GET","POST"])
@login_required
def api_ingamelog():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("ingame_log_channel",{})[gid]=d.get("log_kanal_id","")
        cfg.setdefault("ingame_panel_channel",{})[gid]=d.get("panel_kanal_id","")
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify({"log_kanal_id":cfg.get("ingame_log_channel",{}).get(gid,""),"panel_kanal_id":cfg.get("ingame_panel_channel",{}).get(gid,"")})

@app.route("/api/ranklog-setup", methods=["GET","POST"])
@login_required
def api_ranklog():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("ranklog",{})[gid]={"channel_id":d.get("kanal_id",""),"von_role_id":d.get("von_id",""),"bis_role_id":d.get("bis_id","")}
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify(cfg.get("ranklog",{}).get(gid,{}))

@app.route("/api/teamliste-setup", methods=["GET","POST"])
@login_required
def api_teamliste():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        tl=cfg.get("teamliste",{}).get(gid,{})
        tl["channel_id"]=d.get("kanal_id",""); tl["title"]=d.get("titel","Teamliste")
        cfg.setdefault("teamliste",{})[gid]=tl; save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify(cfg.get("teamliste",{}).get(gid,{}))

@app.route("/api/backup-setup", methods=["GET","POST"])
@login_required
def api_backup():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id")
        db["backup_config"].update_one({"guild_id":gid},{"$set":{"guild_id":gid,"auto_backup":d.get("auto_backup",False),"log_kanal_id":d.get("log_kanal_id","")}},upsert=True)
        return jsonify({"ok":True})
    gid=request.args.get("guild_id"); doc=db["backup_config"].find_one({"guild_id":gid}) or {}; doc.pop("_id",None)
    return jsonify(doc)

@app.route("/api/autorole-setup", methods=["GET","POST"])
@login_required
def api_autorole():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("auto_role",{})[gid]=d.get("role_id","")
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify({"role_id":cfg.get("auto_role",{}).get(gid,"")})

@app.route("/api/voicesupport", methods=["GET","POST"])
@login_required
def api_voicesupport():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        system = d.get("system", "1")
        key = "voice_support" if system == "1" else "voice_support_2"
        cfg.setdefault(key, {})[gid] = {
            "warteraum_id": d.get("warteraum_id",""),
            "notif_channel_id": d.get("notif_channel_id",""),
            "support_role_id": d.get("support_role_id",""),
            "ping_role_id": d.get("ping_role_id",""),
        }
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); system=request.args.get("system","1"); cfg=get_config()
    key = "voice_support" if system == "1" else "voice_support_2"
    return jsonify(cfg.get(key,{}).get(gid,{}))

@app.route("/api/abmeldung", methods=["GET","POST"])
@login_required
def api_abmeldung():
    if request.method=="POST":
        d=request.json; gid=d.get("guild_id"); cfg=get_config()
        cfg.setdefault("abmeldung_abwesenheitsrolle",{})[gid]=d.get("abwesenheitsrolle_id","")
        cfg.setdefault("abmeldung_bestaetigung_rolle",{})[gid]=d.get("bestaetigung_rolle_id","")
        cfg.setdefault("abmeldung_log_channel",{})[gid]=d.get("log_channel_id","")
        save_config(cfg); return jsonify({"ok":True})
    gid=request.args.get("guild_id"); cfg=get_config()
    return jsonify({"abwesenheitsrolle_id":cfg.get("abmeldung_abwesenheitsrolle",{}).get(gid,""),"bestaetigung_rolle_id":cfg.get("abmeldung_bestaetigung_rolle",{}).get(gid,""),"log_channel_id":cfg.get("abmeldung_log_channel",{}).get(gid,"")})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))

import os
import json
import requests
from flask import Flask, redirect, request, session, render_template, jsonify
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
OAUTH_URL = (
    f"https://discord.com/oauth2/authorize"
    f"?client_id={DISCORD_CLIENT_ID}"
    f"&redirect_uri={DISCORD_REDIRECT_URI}"
    f"&response_type=code"
    f"&scope=identify+guilds"
)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        if str(session["user"]["id"]) != BOT_OWNER_ID:
            return render_template("error.html", message="Kein Zugriff – nur der Bot-Owner kann das Dashboard nutzen.")
        return f(*args, **kwargs)
    return decorated

def get_config():
    doc = db["config"].find_one({"_id": "main"})
    return doc or {}

def save_config(cfg):
    db["config"].update_one({"_id": "main"}, {"$set": cfg}, upsert=True)

# ─── Auth Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user" in session:
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/login")
def login():
    return redirect(OAUTH_URL)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect("/")
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }
    r = requests.post(f"{DISCORD_API}/oauth2/token", data=data)
    token = r.json().get("access_token")
    if not token:
        return redirect("/")
    headers = {"Authorization": f"Bearer {token}"}
    user = requests.get(f"{DISCORD_API}/users/@me", headers=headers).json()
    session["user"] = user
    session["token"] = token
    if str(user.get("id")) != BOT_OWNER_ID:
        session.clear()
        return render_template("error.html", message="Kein Zugriff – nur der Bot-Owner kann das Dashboard nutzen.")
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.route("/dashboard")
@owner_required
def dashboard():
    cfg = get_config()
    guilds_r = requests.get(
        f"{DISCORD_API}/users/@me/guilds",
        headers={"Authorization": f"Bearer {session['token']}"}
    )
    guilds = guilds_r.json() if guilds_r.ok else []
    return render_template("dashboard.html", user=session["user"], cfg=cfg, guilds=guilds)

# ─── API Routes ──────────────────────────────────────────────────────────────

@app.route("/api/logs", methods=["GET", "POST"])
@owner_required
def api_logs():
    if request.method == "POST":
        data = request.json
        guild_id = data.get("guild_id")
        cfg = get_config()
        if "unified_log_config" not in cfg:
            cfg["unified_log_config"] = {}
        cfg["unified_log_config"][guild_id] = {
            "channel_id": data.get("channel_id"),
            "categories": data.get("categories", [])
        }
        save_config(cfg)
        return jsonify({"ok": True})
    guild_id = request.args.get("guild_id")
    cfg = get_config()
    return jsonify(cfg.get("unified_log_config", {}).get(guild_id, {}))

@app.route("/api/automod", methods=["GET", "POST"])
@owner_required
def api_automod():
    if request.method == "POST":
        data = request.json
        guild_id = data.get("guild_id")
        db["automod_config"].update_one(
            {"guild_id": guild_id},
            {"$set": {
                "guild_id": guild_id,
                "enabled": data.get("enabled", False),
                "action": data.get("action", "warn"),
                "mute_duration": int(data.get("mute_duration", 5)),
                "scam_detection": data.get("scam_detection", True),
                "log_channel_id": data.get("log_channel_id", ""),
            }},
            upsert=True
        )
        return jsonify({"ok": True})
    guild_id = request.args.get("guild_id")
    doc = db["automod_config"].find_one({"guild_id": guild_id}) or {}
    doc.pop("_id", None)
    return jsonify(doc)

@app.route("/api/level", methods=["GET", "POST"])
@owner_required
def api_level():
    if request.method == "POST":
        data = request.json
        guild_id = data.get("guild_id")
        cfg = get_config()
        if "level_config" not in cfg:
            cfg["level_config"] = {}
        cfg["level_config"][guild_id] = {
            "enabled": data.get("enabled", False),
            "levelup_channel_id": data.get("levelup_channel_id", ""),
            "role_ids": cfg.get("level_config", {}).get(guild_id, {}).get("role_ids", {})
        }
        save_config(cfg)
        return jsonify({"ok": True})
    guild_id = request.args.get("guild_id")
    cfg = get_config()
    return jsonify(cfg.get("level_config", {}).get(guild_id, {}))

@app.route("/api/partner", methods=["GET", "POST", "DELETE"])
@owner_required
def api_partner():
    guild_id = request.args.get("guild_id") or (request.json or {}).get("guild_id")
    if request.method == "GET":
        doc = db["partner_config"].find_one({"guild_id": guild_id}) or {}
        doc.pop("_id", None)
        return jsonify(doc)
    if request.method == "POST":
        data = request.json
        doc = db["partner_config"].find_one({"guild_id": guild_id}) or {"guild_id": guild_id, "partners": []}
        partners = doc.get("partners", [])
        partners.append({
            "name": data.get("name"),
            "link": data.get("link"),
            "kategorie": data.get("kategorie", "🤝 Partner"),
            "ansprechpartner": data.get("ansprechpartner", ""),
        })
        db["partner_config"].update_one(
            {"guild_id": guild_id},
            {"$set": {"partners": partners}},
            upsert=True
        )
        return jsonify({"ok": True})
    if request.method == "DELETE":
        data = request.json
        doc = db["partner_config"].find_one({"guild_id": guild_id}) or {}
        partners = [p for p in doc.get("partners", []) if p["name"] != data.get("name")]
        db["partner_config"].update_one(
            {"guild_id": guild_id},
            {"$set": {"partners": partners}},
            upsert=True
        )
        return jsonify({"ok": True})

@app.route("/api/ticket-kategorien", methods=["GET", "POST", "DELETE"])
@owner_required
def api_ticket_kategorien():
    guild_id = request.args.get("guild_id") or (request.json or {}).get("guild_id")
    if request.method == "GET":
        cfg = get_config()
        kategorien = cfg.get("ticket_kategorien", {}).get(guild_id, [])
        return jsonify(kategorien)
    if request.method == "POST":
        data = request.json
        cfg = get_config()
        if "ticket_kategorien" not in cfg:
            cfg["ticket_kategorien"] = {}
        kat = cfg["ticket_kategorien"].get(guild_id, [])
        kat.append({"name": data.get("name"), "emoji": data.get("emoji", "🎫")})
        cfg["ticket_kategorien"][guild_id] = kat
        save_config(cfg)
        return jsonify({"ok": True})
    if request.method == "DELETE":
        data = request.json
        cfg = get_config()
        kat = cfg.get("ticket_kategorien", {}).get(guild_id, [])
        kat = [k for k in kat if k["name"] != data.get("name")]
        cfg["ticket_kategorien"][guild_id] = kat
        save_config(cfg)
        return jsonify({"ok": True})

@app.route("/api/abmeldung", methods=["GET", "POST"])
@owner_required
def api_abmeldung():
    if request.method == "POST":
        data = request.json
        guild_id = data.get("guild_id")
        cfg = get_config()
        cfg.setdefault("abmeldung_abwesenheitsrolle", {})[guild_id] = data.get("abwesenheitsrolle_id", "")
        cfg.setdefault("abmeldung_bestaetigung_rolle", {})[guild_id] = data.get("bestaetigung_rolle_id", "")
        cfg.setdefault("abmeldung_log_channel", {})[guild_id] = data.get("log_channel_id", "")
        save_config(cfg)
        return jsonify({"ok": True})
    guild_id = request.args.get("guild_id")
    cfg = get_config()
    return jsonify({
        "abwesenheitsrolle_id": cfg.get("abmeldung_abwesenheitsrolle", {}).get(guild_id, ""),
        "bestaetigung_rolle_id": cfg.get("abmeldung_bestaetigung_rolle", {}).get(guild_id, ""),
        "log_channel_id": cfg.get("abmeldung_log_channel", {}).get(guild_id, ""),
    })

@app.route("/api/guild-channels")
@owner_required
def api_guild_channels():
    guild_id = request.args.get("guild_id")
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    r = requests.get(
        f"{DISCORD_API}/guilds/{guild_id}/channels",
        headers={"Authorization": f"Bot {bot_token}"}
    )
    if not r.ok:
        return jsonify([])
    channels = [c for c in r.json() if c.get("type") == 0]
    return jsonify([{"id": c["id"], "name": c["name"]} for c in channels])

@app.route("/api/guild-roles")
@owner_required
def api_guild_roles():
    guild_id = request.args.get("guild_id")
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    r = requests.get(
        f"{DISCORD_API}/guilds/{guild_id}/roles",
        headers={"Authorization": f"Bot {bot_token}"}
    )
    if not r.ok:
        return jsonify([])
    roles = [ro for ro in r.json() if ro["name"] != "@everyone"]
    return jsonify([{"id": ro["id"], "name": ro["name"]} for ro in sorted(roles, key=lambda x: -x["position"])])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

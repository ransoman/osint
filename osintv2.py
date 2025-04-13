from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import json
import phonenumbers
from phonenumbers import geocoder, carrier
import hashlib

# === TOKEN BOT TELEGRAM ===
TOKEN = "7857304059:AAEcD9efRQWiNA73QAs1-QyjV6mBm0Yx_Oo"

# === SCAN MODULES ===
async def run_email_scan(update, email):
    await update.message.reply_text(f"🔍 Scan Email: `{email}`", parse_mode="Markdown")
    gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower().encode()).hexdigest()
    await update.message.reply_text(f"🖼️ *Gravatar:* {gravatar_url}", parse_mode="Markdown")

    hibp_resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                             headers={"hibp-api-key": "ISI_API_KALO_PUNYA", "User-Agent": "XIDENT-BOT"})
    if hibp_resp.status_code == 200:
        leaks = [x["Name"] for x in hibp_resp.json()]
        await update.message.reply_text(f"💀 *Breached on:* {', '.join(leaks)}", parse_mode="Markdown")
    else:
        await update.message.reply_text("✅ Tidak ditemukan di HIBP atau API tidak aktif.")

    rep = requests.get(f"https://emailrep.io/{email}").json()
    await update.message.reply_text(f"⚠️ *EmailRep:* `{rep.get('reputation', '-')}`\n"
                                    f"Blacklist: {rep.get('details', {}).get('blacklisted')}", parse_mode="Markdown")

async def run_number_scan(update, phone):
    await update.message.reply_text(f"📱 Scan Nomor: `{phone}`", parse_mode="Markdown")
    try:
        no = phonenumbers.parse(phone, None)
        country = geocoder.description_for_number(no, "en")
        provider = carrier.name_for_number(no, "en")
        await update.message.reply_text(f"🌎 Lokasi: {country}\n📡 Provider: {provider}", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Format nomor tidak valid.")

    await update.message.reply_text(f"🟢 Cek WhatsApp: https://wa.me/{phone.lstrip('+')}", parse_mode="Markdown")

async def run_username_scan(update, uname):
    await update.message.reply_text(f"🔎 Scan Username: `{uname}`", parse_mode="Markdown")
    social_sites = [
        f"https://instagram.com/{uname}",
        f"https://twitter.com/{uname}",
        f"https://github.com/{uname}",
        f"https://tiktok.com/@{uname}",
        f"https://www.reddit.com/user/{uname}",
        f"https://www.facebook.com/{uname}",
    ]
    for site in social_sites:
        try:
            r = requests.get(site, timeout=5)
            if r.status_code == 200:
                await update.message.reply_text(f"✅ Terdaftar: {site}")
        except:
            pass

async def run_ip_scan(update, ip):
    await update.message.reply_text(f"🌐 Scan IP: `{ip}`", parse_mode="Markdown")
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}").json()
        await update.message.reply_text(
            f"🌍 Negara: {data['country']}\n"
            f"🏙️ Kota: {data['city']}\n"
            f"📡 ISP: {data['isp']}\n"
            f"🧠 ASN: {data['as']}\n"
            f"🧭 Koordinat: {data['lat']}, {data['lon']}", parse_mode="Markdown"
        )
        await update.message.reply_text(f"📍 Google Maps: https://www.google.com/maps?q={data['lat']},{data['lon']}")
    except:
        await update.message.reply_text("❌ IP tidak valid atau gagal ambil data.")

async def run_dox(update, target):
    def detect_type(t):
        if "@" in t and "." in t:
            return "email"
        elif t.replace("+", "").isdigit():
            return "number"
        elif t.count(".") == 3:
            return "ip"
        else:
            return "username"

    t_type = detect_type(target)
    await update.message.reply_text(f"💣 Brutal DOX aktif untuk `{target}` ({t_type})", parse_mode="Markdown")
    if t_type == "email":
        await run_email_scan(update, target)
        uname = target.split("@")[0]
        await run_username_scan(update, uname)
    elif t_type == "number":
        await run_number_scan(update, target)
        await run_email_scan(update, f"{target}@gmail.com")
    elif t_type == "username":
        await run_username_scan(update, target)
    elif t_type == "ip":
        await run_ip_scan(update, target)
    else:
        await update.message.reply_text("🚫 Format tidak dikenali, tidak bisa DOX.")

# === COMMAND HANDLERS ===
async def start(update, context):
    await update.message.reply_text("👋 Selamat datang di X-IDENT Bot\n\nGunakan perintah berikut:\n/start - Petunjuk\n/osint [target] - Auto ident\n/email [email] - Scan Email\n/number [nomor] - Scan Nomor\n/username [uname] - Scan Username\n/ip [IP] - Scan IP\n/dox [target] - Brutal Combo")

async def osint_handler(update, context):
    if context.args:
        await run_dox(update, context.args[0])
    else:
        await update.message.reply_text("❌ Contoh: /osint khan@example.com")

async def email_handler(update, context):
    if context.args:
        await run_email_scan(update, context.args[0])
    else:
        await update.message.reply_text("❌ Contoh: /email khan@example.com")

async def number_handler(update, context):
    if context.args:
        await run_number_scan(update, context.args[0])
    else:
        await update.message.reply_text("❌ Contoh: /number +62812345678")

async def username_handler(update, context):
    if context.args:
        await run_username_scan(update, context.args[0])
    else:
        await update.message.reply_text("❌ Contoh: /username khan123")

async def ip_handler(update, context):
    if context.args:
        await run_ip_scan(update, context.args[0])
    else:
        await update.message.reply_text("❌ Contoh: /ip 8.8.8.8")

async def dox_handler(update, context):
    if context.args:
        await run_dox(update, context.args[0])
    else:
        await update.message.reply_text("❌ Contoh: /dox khan@example.com")

# === BOT SETUP ===
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("osint", osint_handler))
app.add_handler(CommandHandler("email", email_handler))
app.add_handler(CommandHandler("number", number_handler))
app.add_handler(CommandHandler("username", username_handler))
app.add_handler(CommandHandler("ip", ip_handler))
app.add_handler(CommandHandler("dox", dox_handler))

app.run_polling()

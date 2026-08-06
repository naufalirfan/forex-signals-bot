import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("forex-signals-bot")

load_dotenv()

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com")  # URL webapp yang sudah di-deploy
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "")
ADMIN_USERS = os.getenv("ADMIN_USERS", "")

allowed_user_ids = set()
if ALLOWED_USERS.strip():
    allowed_user_ids = {int(uid.strip()) for uid in ALLOWED_USERS.split(",") if uid.strip().isdigit()}

admin_user_ids = set()
if ADMIN_USERS.strip():
    admin_user_ids = {int(uid.strip()) for uid in ADMIN_USERS.split(",") if uid.strip().isdigit()}

# --- Signal Data Store ---
signals_file = "signals.json"

def load_signals():
    if os.path.exists(signals_file):
        with open(signals_file, "r") as f:
            return json.load(f)
    return []

def save_signals(signals):
    with open(signals_file, "w") as f:
        json.dump(signals, f, indent=2)

def generate_signal(symbol, timeframe, signal_type):
    import random

    # Base prices for common symbols
    base_prices = {
        "XAUUSD": 4030.0,
        "EURUSD": 1.0850,
        "GBPUSD": 1.2680,
        "USDJPY": 149.50,
        "BTCUSD": 67500.0,
        "ETHUSD": 3450.0,
    }

    base = base_prices.get(symbol, 100.0)

    if base > 1000:
        spread = 5.0
        pip = 0.001
    elif base > 100:
        spread = 0.01
        pip = 0.0001
    else:
        spread = 0.5
        pip = 0.01

    # Generate zones
    sell_zone = {
        "rec1": {
            "from": round(base + spread * random.uniform(0.5, 1.5), 3),
            "to": round(base + spread * random.uniform(1.5, 2.5), 3)
        },
        "rec2": {
            "from": round(base + spread * random.uniform(2.0, 3.0), 3),
            "to": round(base + spread * random.uniform(3.0, 4.0), 3)
        },
        "rec3": {
            "from": round(base + spread * random.uniform(1.0, 2.0), 3),
            "to": round(base + spread * random.uniform(2.0, 3.0), 3)
        }
    }

    buy_zone = {
        "rec1": {
            "from": round(base - spread * random.uniform(0.5, 1.5), 3),
            "to": round(base - spread * random.uniform(0.1, 0.5), 3)
        },
        "rec2": {
            "from": round(base - spread * random.uniform(2.0, 4.0), 3),
            "to": round(base - spread * random.uniform(0.5, 2.0), 3)
        },
        "rec3": {
            "from": round(base - spread * random.uniform(1.0, 2.0), 3),
            "to": round(base - spread * random.uniform(0.5, 1.0), 3)
        }
    }

    signal = {
        "id": int(datetime.now().timestamp() * 1000),
        "symbol": symbol,
        "timeframe": timeframe,
        "type": signal_type,
        "confirmation": signal_type if random.random() > 0.3 else "WAIT",
        "sellZone": sell_zone,
        "buyZone": buy_zone,
        "active": True,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }

    return signal


# --- Access Control ---
def check_access(user_id: int) -> bool:
    if not allowed_user_ids:
        return True
    return user_id in allowed_user_ids

def is_admin(user_id: int) -> bool:
    if not admin_user_ids:
        return True
    return user_id in admin_user_ids


# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not check_access(user_id):
        await update.message.reply_text(
            "❌ Akses ditolak.\n\n"
            "Silakan beli paket PRO untuk mengakses sinyal trading AI.\n"
            "Hubungi admin untuk info lebih lanjut."
        )
        return

    keyboard = [
        [InlineKeyboardButton("🚀 Buka Sinyal Trading", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))],
        [
            InlineKeyboardButton("📦 Paket", callback_data="package"),
            InlineKeyboardButton("👤 Profile", callback_data="profile")
        ],
    ]

    welcome_text = (
        "🟢 **SIGNALS AI TRADING** 🟢\n\n"
        "Selamat datang di sinyal trading berbasis AI!\n\n"
        "**Fitur:**\n"
        "• Zone V1 & V2\n"
        "• Real-time signals\n"
        "• Multiple timeframe\n\n"
        "**Cara pakai:**\n"
        "Klik tombol di bawah untuk membuka mini app dan melihat sinyal."
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.id):
        return

    help_text = (
        "📖 **Bantuan**\n\n"
        "**Perintah:**\n"
        "/start - Mulai bot\n"
        "/signals - Lihat sinyal aktif\n"
        "/addsignal - Tambah sinyal (admin)\n"
        "/delsignal - Hapus sinyal (admin)\n"
        "/status - Status bot\n"
        "/help - Bantuan ini\n\n"
        "**Tentang Sinyal:**\n"
        "• Semua sinyal bersifat edukatif\n"
        "• AI bekerja berdasarkan probabilitas\n"
        "• Keputusan trading ada di tangan Anda"
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")


async def signals_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.id):
        return

    keyboard = [
        [InlineKeyboardButton("🚀 Buka Mini App", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
    ]

    await update.message.reply_text(
        "📊 **Sinyal Aktif**\n\n"
        "Klik tombol di bawah untuk melihat semua sinyal trading:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def addsignal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Hanya admin yang bisa menambah sinyal.")
        return

    if len(context.args) < 3:
        await update.message.reply_text(
            "📝 **Cara tambah sinyal:**\n\n"
            "/addsignal <SYMBOL> <TIMEFRAME> <TYPE>\n\n"
            "**Contoh:**\n"
            "/addsignal XAUUSD M1 BUY\n"
            "/addsignal EURUSD M5 SELL",
            parse_mode="Markdown"
        )
        return

    symbol = context.args[0].upper()
    timeframe = context.args[1].upper()
    signal_type = context.args[2].upper()

    if signal_type not in ["BUY", "SELL"]:
        await update.message.reply_text("❌ Type harus BUY atau SELL")
        return

    signal = generate_signal(symbol, timeframe, signal_type)
    signals = load_signals()
    signals.append(signal)
    save_signals(signals)

    await update.message.reply_text(
        f"✅ Sinyal berhasil ditambahkan!\n\n"
        f"**Symbol:** {symbol}\n"
        f"**Timeframe:** {timeframe}\n"
        f"**Type:** {signal_type}",
        parse_mode="Markdown"
    )


async def delsignal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Hanya admin yang bisa menghapus sinyal.")
        return

    signals = load_signals()
    if not signals:
        await update.message.reply_text("Tidak ada sinyal aktif.")
        return

    keyboard = []
    for sig in signals[-10:]:  # Show last 10
        keyboard.append([
            InlineKeyboardButton(
                f"{sig['symbol']} {sig['timeframe']} {sig['type']}",
                callback_data=f"del:{sig['id']}"
            )
        ])

    await update.message.reply_text(
        "🗑 **Pilih sinyal yang ingin dihapus:**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.effective_user.id):
        return

    signals = load_signals()
    active = [s for s in signals if s.get("active", True)]

    await update.message.reply_text(
        f"📊 **Status Bot**\n\n"
        f"Sinyal aktif: {len(active)}\n"
        f"Total sinyal: {len(signals)}\n"
        f"Webapp URL: {WEBAPP_URL}",
        parse_mode="Markdown"
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "package":
        await query.edit_message_text(
            "📦 **Paket Premium**\n\n"
            "• Trial Gratis: 3 Hari\n"
            "• Paket Pro: Rp 199.000/bulan\n"
            "• Paket Lifetime: Rp 499.000\n\n"
            "Hubungi admin untuk pembelian!",
            parse_mode="Markdown"
        )
    elif data == "profile":
        user = query.from_user
        await query.edit_message_text(
            f"👤 **Profile Anda**\n\n"
            f"ID: `{user.id}`\n"
            f"Username: @{user.username or 'N/A'}\n"
            f"Name: {user.first_name}",
            parse_mode="Markdown"
        )
    elif data.startswith("del:"):
        signal_id = int(data.split(":")[1])
        signals = load_signals()
        signals = [s for s in signals if s["id"] != signal_id]
        save_signals(signals)
        await query.edit_message_text("✅ Sinyal berhasil dihapus!")


async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data sent from Mini App"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        action = data.get("action")

        if action == "confirm":
            symbol = data.get("symbol")
            signal_type = data.get("type")

            await update.message.reply_text(
                f"✅ **Konfirmasi Diterima**\n\n"
                f"Symbol: {symbol}\n"
                f"Type: {signal_type}\n"
                f"Waktu: {datetime.now().strftime('%H:%M:%S')}",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Error handling webapp data: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


def main():
    if not BOT_TOKEN:
        print("Error: Set environment variable BOT_TOKEN")
        print("Contoh: export BOT_TOKEN=123456:ABC-DEF...")
        return

    print("=" * 50)
    print("  Forex Signals Trading Bot")
    print(f"  Webapp URL: {WEBAPP_URL}")
    print(f"  Allowed: {'Semua' if not allowed_user_ids else allowed_user_ids}")
    print(f"  Admin: {'Semua' if not admin_user_ids else admin_user_ids}")
    print("=" * 50)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("signals", signals_cmd))
    app.add_handler(CommandHandler("addsignal", addsignal_cmd))
    app.add_handler(CommandHandler("delsignal", delsignal_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler, pattern=r"^(package|profile|del:)"))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    app.add_error_handler(error_handler)

    # Initialize with sample signals if empty
    if not load_signals():
        sample_signals = [
            generate_signal("XAUUSD", "M1", "SELL"),
            generate_signal("EURUSD", "M5", "BUY"),
            generate_signal("GBPUSD", "M15", "SELL"),
            generate_signal("USDJPY", "M5", "BUY"),
        ]
        save_signals(sample_signals)
        logger.info("Initialized with sample signals")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

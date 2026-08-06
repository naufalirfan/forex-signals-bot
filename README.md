# 🚀 SIGNALS AI TRADING - Telegram Mini App

Sinyal trading forex berbasis AI dengan interface Telegram Mini App.

![Signals AI](https://img.shields.io/badge/Signals-AI-00d26a?style=for-the-badge)
![Telegram](https://img.shields.io/badge/Telegram-Mini%20App-26A5E4?style=for-the-badge)

## ✨ Fitur

- 📊 Real-time trading signals
- 🎯 Zone V1 & V2
- 🔄 Multiple timeframe (M1, M5, M15, H1, H4, D1)
- 💱 Multiple symbols (Forex, Gold, Crypto)
- 🌙 Dark theme UI
- 📱 Mobile-friendly design

## 🌐 Live Demo

**[Buka Mini App di Telegram](https://t.me/YOUR_BOT_USERNAME)**

## 📦 Deployment

### GitHub Pages (Static Webapp)

1. Fork/Clone repo ini
2. Push ke GitHub
3. Buka **Settings > Pages**
4. Pilih source: **Deploy from a branch**
5. Branch: **master**, Folder: **/ (root)**
6. Klik **Save**

Webapp akan live di: `https://YOUR_USERNAME.github.io/REPO_NAME/`

### Bot Server (Optional)

Untuk data real-time, jalankan bot server:

```bash
cd bot
pip install -r requirements.txt

# Copy dan edit .env
cp .env.example .env

# Jalankan bot
python bot.py
```

## 🛠 Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Telegram Bot API)
- **Hosting:** GitHub Pages

## 📱 Commands Bot

| Command | Description |
|---------|-------------|
| `/start` | Mulai bot |
| `/signals` | Buka mini app |
| `/addsignal XAUUSD M1 BUY` | Tambah sinyal (admin) |
| `/delsignal` | Hapus sinyal (admin) |
| `/status` | Status bot |

## ⚠️ Disclaimer

Semua sinyal bersifat edukatif dan informatif, bukan ajakan untuk transaksi. AI bekerja berdasarkan probabilitas statistik, bukan kepastian pasar. Keputusan entry, exit, dan manajemen risiko sepenuhnya ada di tangan Anda sebagai trader.

## 📄 License

MIT License

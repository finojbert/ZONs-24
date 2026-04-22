import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ===================== KONFIGURASI =====================
BOT_TOKEN = "MASUKKAN_TOKEN_BOT_KAMU_DI_SINI"  # Dari @BotFather
CS_CONTACT = "https://wa.me/628123456789"        # Ganti dengan WA/Telegram CS kamu
NAMA_TOKO = "DigiStore ID"
TAGLINE = "Produk Digital Terpercaya 🚀"

# ===================== DATA PRODUK =====================
# Tambah/edit produk di sini
PRODUK = {
    "1": {
        "nama": "📘 Ebook Marketing Digital 2025",
        "harga": 75000,
        "deskripsi": "Panduan lengkap marketing digital dari nol sampai mahir. 200+ halaman, bonus template Canva.",
        "preview": "✅ Strategi Instagram & TikTok\n✅ Email Marketing\n✅ SEO Dasar\n✅ Bonus: 10 Template Canva",
        "format": "PDF",
    },
    "2": {
        "nama": "🎨 Pack Template Canva Premium",
        "harga": 49000,
        "deskripsi": "50+ template Canva siap pakai untuk konten media sosial. Feed Instagram, Story, Reels Cover.",
        "preview": "✅ 50+ Template Editable\n✅ Feed & Story Instagram\n✅ Cover Reels & YouTube\n✅ Update Seumur Hidup",
        "format": "Link Canva",
    },
    "3": {
        "nama": "💻 Kursus Video Editing Pemula",
        "harga": 125000,
        "deskripsi": "Belajar edit video dari nol pakai CapCut & Adobe Premiere. 5 jam video pembelajaran.",
        "preview": "✅ 5 Jam Video HD\n✅ CapCut & Premiere Pro\n✅ Project File Latihan\n✅ Akses Selamanya",
        "format": "Video + PDF",
    },
    "4": {
        "nama": "📊 Template Excel Keuangan Bisnis",
        "harga": 35000,
        "deskripsi": "Template Excel otomatis untuk catat keuangan bisnis, laporan laba rugi, dan cash flow.",
        "preview": "✅ Laporan Laba Rugi Auto\n✅ Cash Flow Tracker\n✅ Dashboard Visual\n✅ Panduan Penggunaan",
        "format": "Excel (.xlsx)",
    },
    "5": {
        "nama": "🤖 Prompt ChatGPT Bisnis (500+ Prompt)",
        "harga": 59000,
        "deskripsi": "Koleksi 500+ prompt ChatGPT siap pakai untuk copywriting, konten, email marketing, dan bisnis.",
        "preview": "✅ 500+ Prompt Siap Pakai\n✅ Kategori Copywriting\n✅ Konten Sosmed\n✅ Email & Customer Service",
        "format": "PDF + Notion",
    },
}

# ===================== CARA PEMBAYARAN =====================
CARA_BAYAR = """
💳 *Metode Pembayaran:*

🏦 Transfer Bank:
• BCA: 1234567890 (a.n. DigiStore ID)
• BNI: 0987654321 (a.n. DigiStore ID)

📱 E-Wallet:
• GoPay / OVO / DANA: 0812-3456-7890
• ShopeePay: DigiStoreID

₿ QRIS: Tersedia (scan di saat checkout)

📌 *Langkah Order:*
1. Pilih produk & masukkan keranjang
2. Ketik /keranjang untuk lihat pesanan
3. Hubungi CS untuk konfirmasi bayar
4. Produk dikirim otomatis setelah pembayaran dikonfirmasi ✅
"""

# ===================== LOGGING =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== KERANJANG (disimpan per user) =====================
keranjang_user = {}  # {user_id: {"1": qty, "2": qty, ...}}

def get_keranjang(user_id):
    return keranjang_user.get(user_id, {})

def format_harga(harga):
    return f"Rp {harga:,.0f}".replace(",", ".")

def total_keranjang(user_id):
    keranjang = get_keranjang(user_id)
    total = sum(PRODUK[pid]["harga"] * qty for pid, qty in keranjang.items() if pid in PRODUK)
    return total

# ===================== KEYBOARD UTAMA =====================
def keyboard_utama():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Lihat Katalog", callback_data="katalog")],
        [InlineKeyboardButton("🛒 Keranjang Saya", callback_data="keranjang"),
         InlineKeyboardButton("💬 Hubungi CS", url=CS_CONTACT)],
        [InlineKeyboardButton("💳 Cara Pembayaran", callback_data="cara_bayar")],
    ])

# ===================== COMMAND /start =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.effective_user.first_name
    teks = (
        f"Halo, *{nama}!* 👋\n\n"
        f"Selamat datang di *{NAMA_TOKO}*\n"
        f"_{TAGLINE}_\n\n"
        f"Kami menyediakan produk digital berkualitas dengan harga terjangkau.\n"
        f"Pilih menu di bawah untuk mulai belanja! ✨"
    )
    await update.message.reply_text(teks, parse_mode="Markdown", reply_markup=keyboard_utama())

# ===================== COMMAND /katalog =====================
async def katalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tampilkan_katalog(update.message, update.effective_user.id)

async def tampilkan_katalog(message, user_id):
    teks = f"🛍️ *Katalog Produk {NAMA_TOKO}*\n\n"
    teks += "Pilih produk untuk melihat detail:\n"
    tombol = []
    for pid, produk in PRODUK.items():
        label = f"{produk['nama']} — {format_harga(produk['harga'])}"
        tombol.append([InlineKeyboardButton(label, callback_data=f"produk_{pid}")])
    tombol.append([InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="menu_utama")])
    await message.reply_text(teks, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(tombol))

# ===================== COMMAND /keranjang =====================
async def keranjang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tampilkan_keranjang(update.message, update.effective_user.id)

async def tampilkan_keranjang(message, user_id):
    keranjang = get_keranjang(user_id)
    if not keranjang:
        teks = "🛒 Keranjang kamu masih kosong!\n\nYuk lihat katalog produk kami."
        tombol = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ Lihat Katalog", callback_data="katalog")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
        ])
    else:
        teks = "🛒 *Keranjang Belanja Kamu:*\n\n"
        for pid, qty in keranjang.items():
            if pid in PRODUK:
                p = PRODUK[pid]
                subtotal = p["harga"] * qty
                teks += f"• {p['nama']}\n  {qty}x {format_harga(p['harga'])} = *{format_harga(subtotal)}*\n\n"
        teks += f"━━━━━━━━━━━━━━\n"
        teks += f"💰 *Total: {format_harga(total_keranjang(user_id))}*\n\n"
        teks += f"Hubungi CS untuk konfirmasi pembayaran!"
        tombol = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Pesan Sekarang via CS", url=CS_CONTACT)],
            [InlineKeyboardButton("🗑️ Kosongkan Keranjang", callback_data="kosongkan_keranjang")],
            [InlineKeyboardButton("🛍️ Lanjut Belanja", callback_data="katalog")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
        ])
    await message.reply_text(teks, parse_mode="Markdown", reply_markup=tombol)

# ===================== HANDLER CALLBACK =====================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "menu_utama":
        nama = query.from_user.first_name
        teks = (
            f"Halo, *{nama}!* 👋\n\n"
            f"Selamat datang di *{NAMA_TOKO}*\n"
            f"_{TAGLINE}_\n\n"
            f"Pilih menu di bawah untuk mulai belanja! ✨"
        )
        await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=keyboard_utama())

    elif data == "katalog":
        teks = f"🛍️ *Katalog Produk {NAMA_TOKO}*\n\nPilih produk untuk melihat detail:\n"
        tombol = []
        for pid, produk in PRODUK.items():
            label = f"{produk['nama']} — {format_harga(produk['harga'])}"
            tombol.append([InlineKeyboardButton(label, callback_data=f"produk_{pid}")])
        tombol.append([InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="menu_utama")])
        await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(tombol))

    elif data.startswith("produk_"):
        pid = data.split("_")[1]
        if pid in PRODUK:
            p = PRODUK[pid]
            teks = (
                f"*{p['nama']}*\n\n"
                f"💰 Harga: *{format_harga(p['harga'])}*\n"
                f"📦 Format: {p['format']}\n\n"
                f"📝 Deskripsi:\n{p['deskripsi']}\n\n"
                f"✨ Yang kamu dapat:\n{p['preview']}"
            )
            tombol = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Tambah ke Keranjang", callback_data=f"tambah_{pid}")],
                [InlineKeyboardButton("💬 Tanya CS", url=CS_CONTACT)],
                [InlineKeyboardButton("⬅️ Kembali ke Katalog", callback_data="katalog")],
            ])
            await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=tombol)

    elif data.startswith("tambah_"):
        pid = data.split("_")[1]
        if pid in PRODUK:
            if user_id not in keranjang_user:
                keranjang_user[user_id] = {}
            keranjang_user[user_id][pid] = keranjang_user[user_id].get(pid, 0) + 1
            p = PRODUK[pid]
            teks = (
                f"✅ *{p['nama']}* berhasil ditambahkan ke keranjang!\n\n"
                f"🛒 Total keranjang: *{format_harga(total_keranjang(user_id))}*"
            )
            tombol = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Lihat Keranjang", callback_data="keranjang")],
                [InlineKeyboardButton("🛍️ Lanjut Belanja", callback_data="katalog")],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
            ])
            await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=tombol)

    elif data == "keranjang":
        keranjang = get_keranjang(user_id)
        if not keranjang:
            teks = "🛒 Keranjang kamu masih kosong!\n\nYuk lihat katalog produk kami."
            tombol = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍️ Lihat Katalog", callback_data="katalog")],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
            ])
        else:
            teks = "🛒 *Keranjang Belanja Kamu:*\n\n"
            for pid, qty in keranjang.items():
                if pid in PRODUK:
                    p = PRODUK[pid]
                    subtotal = p["harga"] * qty
                    teks += f"• {p['nama']}\n  {qty}x {format_harga(p['harga'])} = *{format_harga(subtotal)}*\n\n"
            teks += f"━━━━━━━━━━━━━━\n"
            teks += f"💰 *Total: {format_harga(total_keranjang(user_id))}*\n\n"
            teks += f"Hubungi CS untuk konfirmasi pembayaran!"
            tombol = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Pesan Sekarang via CS", url=CS_CONTACT)],
                [InlineKeyboardButton("🗑️ Kosongkan Keranjang", callback_data="kosongkan_keranjang")],
                [InlineKeyboardButton("🛍️ Lanjut Belanja", callback_data="katalog")],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
            ])
        await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=tombol)

    elif data == "kosongkan_keranjang":
        keranjang_user[user_id] = {}
        teks = "🗑️ Keranjang berhasil dikosongkan."
        tombol = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ Lihat Katalog", callback_data="katalog")],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
        ])
        await query.edit_message_text(teks, parse_mode="Markdown", reply_markup=tombol)

    elif data == "cara_bayar":
        tombol = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Hubungi CS", url=CS_CONTACT)],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
        ])
        await query.edit_message_text(CARA_BAYAR, parse_mode="Markdown", reply_markup=tombol)

# ===================== AUTO REPLY PESAN BIASA =====================
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teks_masuk = update.message.text.lower()
    nama = update.effective_user.first_name

    # Kata kunci yang dikenali
    if any(k in teks_masuk for k in ["halo", "hai", "hi", "hello", "selamat"]):
        balas = f"Halo *{nama}*! 👋 Selamat datang di *{NAMA_TOKO}*! Ada yang bisa kami bantu?"
        await update.message.reply_text(balas, parse_mode="Markdown", reply_markup=keyboard_utama())

    elif any(k in teks_masuk for k in ["produk", "katalog", "jual", "ada apa"]):
        await tampilkan_katalog(update.message, update.effective_user.id)

    elif any(k in teks_masuk for k in ["harga", "berapa", "price"]):
        teks = "💰 Harga produk kami mulai dari *Rp 35.000*!\n\nLihat katalog lengkap untuk detail harga:"
        await update.message.reply_text(teks, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ Lihat Katalog", callback_data="katalog")]
        ]))

    elif any(k in teks_masuk for k in ["bayar", "transfer", "payment", "beli"]):
        tombol = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Hubungi CS", url=CS_CONTACT)],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")],
        ])
        await update.message.reply_text(CARA_BAYAR, parse_mode="Markdown", reply_markup=tombol)

    elif any(k in teks_masuk for k in ["cs", "admin", "bantuan", "help", "kontak"]):
        teks = f"💬 Hubungi CS kami yang siap membantu!\n\n📱 Klik tombol di bawah untuk chat langsung:"
        tombol = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Chat CS Sekarang", url=CS_CONTACT)]])
        await update.message.reply_text(teks, parse_mode="Markdown", reply_markup=tombol)

    elif any(k in teks_masuk for k in ["keranjang", "cart", "pesanan"]):
        await tampilkan_keranjang(update.message, update.effective_user.id)

    else:
        # Default reply
        teks = (
            f"Halo *{nama}*! 😊\n\n"
            f"Maaf, saya belum paham pesanmu. Gunakan menu di bawah atau hubungi CS kami:"
        )
        await update.message.reply_text(teks, parse_mode="Markdown", reply_markup=keyboard_utama())

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("katalog", katalog_command))
    app.add_handler(CommandHandler("keranjang", keranjang_command))

    # Callback handler (tombol inline)
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Auto reply pesan teks biasa
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    print(f"🤖 Bot {NAMA_TOKO} aktif! Tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()
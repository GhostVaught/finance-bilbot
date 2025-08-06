
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime
import json
import os
import nest_asyncio
from keep_alive import keep_alive

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("USER_ID"))

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = config["GOOGLE_CREDS"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open("Bilal Finance").sheet1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Maaf Ini Bot Pribadi")
        return
    await update.message.reply_text("Halo Selamat Datang!\nGunakan Tombol (/) untuk memulai")

async def catat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Akses Ditolak")
        return
    try:
        args = context.args
        Tipe, Jumlah, *Keterangan = args
        Jumlah = int(Jumlah)
        Keterangan = " ".join(Keterangan)
        Tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([Tanggal, Tipe, Jumlah, Keterangan])
        await update.message.reply_text("Catatan Berhasil Disimpan")
    except:
        await update.message.reply_text("Format Salah")

async def laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Akses Ditolak")
        return
    records = sheet.get_all_records()
    masuk = keluar = 0
    for row in records:
        if row['Tipe'].lower() == 'pemasukan': masuk += int(row['Jumlah'])
        elif row['Tipe'].lower() == 'pengeluaran': keluar += int(row['Jumlah'])
    saldo = masuk - keluar
    await update.message.reply_text(f"📊 Laporan Keuangan:\n\n💰 Pemasukan: Rp{masuk:,}\n💸 Pengeluaran: Rp{keluar:,}\n🧮 Saldo: Rp{saldo:,}")

async def hariini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Akses Ditolak")
        return
    today = datetime.now().strftime("%Y-%m-%d")
    records = sheet.get_all_records()
    masuk = keluar = 0
    for row in records:
        if row['Tanggal'].startswith(today):
            if row['Tipe'].lower() == 'pemasukan': masuk += int(row['Jumlah'])
            elif row['Tipe'].lower() == 'pengeluaran': keluar += int(row['Jumlah'])
    saldo = masuk - keluar
    await update.message.reply_text(f"📆 Keuangan Hari Ini:\n\n💰 Masuk: Rp{masuk:,}\n💸 Keluar: Rp{keluar:,}\n🧮 Saldo: Rp{saldo:,}")

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("Akses Ditolak")
        return
    await update.message.reply_text("/catat [tipe] [jumlah] [keterangan]\n/laporan - Lihat ringkasan saldo\n/hariini - Laporan hari ini\n/bantuan - Daftar perintah")

async def blok_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    await update.message.reply_text("⚠️ Gunakan perintah dari menu (/)")

async def set_commands(app):
    commands = [
        BotCommand("catat", "Catat Transaksi"),
        BotCommand("laporan", "Lihat Laporan Saldo"),
        BotCommand("hariini", "Lihat Laporan Hari Ini"),
        BotCommand("bantuan", "Tampilkan Menu Bantuan")
    ]
    await app.bot.set_my_commands(commands)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catat", catat))
    app.add_handler(CommandHandler("laporan", laporan))
    app.add_handler(CommandHandler("hariini", hariini))
    app.add_handler(CommandHandler("bantuan", bantuan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, blok_pesan))
    await set_commands(app)
    print("Bot Aktif")
    await app.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    keep_alive()
    import asyncio
    asyncio.run(main())

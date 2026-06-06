from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

import os
import sqlite3

# ambil token dari Railway (bukan ditulis langsung)
TOKEN = os.getenv("BOT_TOKEN")

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("reksagg.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT
)
""")

conn.commit()

# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Reksagg Bot aktif\n\n"
        "/todo <tugas>\n/list\n/done <id>"
    )

# =========================
# TODO
# =========================

async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Contoh: /todo belajar python")
        return

    task = " ".join(context.args)

    cursor.execute(
        "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
        (update.effective_user.id, task)
    )

    conn.commit()

    await update.message.reply_text("✅ Tugas ditambah")

# =========================
# LIST
# =========================

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute(
        "SELECT id, task FROM tasks WHERE user_id=?",
        (update.effective_user.id,)
    )

    data = cursor.fetchall()

    if not data:
        await update.message.reply_text("Kosong")
        return

    text = "📝 TASK:\n\n"

    for i, t in data:
        text += f"{i}. {t}\n"

    await update.message.reply_text(text)

# =========================
# DONE
# =========================

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Contoh: /done 1")
        return

    task_id = int(context.args[0])

    cursor.execute(
        "DELETE FROM tasks WHERE id=? AND user_id=?",
        (task_id, update.effective_user.id)
    )

    conn.commit()

    await update.message.reply_text("✅ Selesai")

# =========================
# BOT RUN
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("todo", todo))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CommandHandler("done", done))

print("BOT AKTIF")
app.run_polling()
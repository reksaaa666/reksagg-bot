from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import sqlite3

# =====================
# TOKEN
# =====================
TOKEN = os.getenv("BOT_TOKEN")

# =====================
# DATABASE
# =====================
conn = sqlite3.connect("reksagg.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    note TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS finance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type TEXT,
    amount INTEGER,
    description TEXT
)
""")

conn.commit()

# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Reksagg Manager Bot\n\n"
        "/todo <tugas>\n/list\n/done <id>\n\n"
        "/note <catatan>\n/notes\n\n"
        "/masuk <jumlah> <keterangan>\n"
        "/keluar <jumlah> <keterangan>\n"
        "/saldo"
    )

# =====================
# TODO
# =====================
async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Contoh: /todo belajar python")

    task = " ".join(context.args)

    cursor.execute(
        "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
        (update.effective_user.id, task)
    )
    conn.commit()

    await update.message.reply_text("✅ Task ditambah")

# =====================
# LIST TASK
# =====================
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute(
        "SELECT id, task FROM tasks WHERE user_id=?",
        (update.effective_user.id,)
    )
    data = cursor.fetchall()

    if not data:
        return await update.message.reply_text("Kosong")

    text = "📝 TASK:\n\n"
    for i, t in data:
        text += f"{i}. {t}\n"

    await update.message.reply_text(text)

# =====================
# DONE
# =====================
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Contoh: /done 1")

    task_id = int(context.args[0])

    cursor.execute(
        "DELETE FROM tasks WHERE id=? AND user_id=?",
        (task_id, update.effective_user.id)
    )
    conn.commit()

    await update.message.reply_text("✅ Selesai")

# =====================
# NOTE
# =====================
async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Contoh: /note ganti oli")

    text = " ".join(context.args)

    cursor.execute(
        "INSERT INTO notes (user_id, note) VALUES (?, ?)",
        (update.effective_user.id, text)
    )
    conn.commit()

    await update.message.reply_text("📝 Tersimpan")

# =====================
# NOTES LIST
# =====================
async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute(
        "SELECT id, note FROM notes WHERE user_id=?",
        (update.effective_user.id,)
    )

    data = cursor.fetchall()

    if not data:
        return await update.message.reply_text("Kosong")

    text = "📝 NOTES:\n\n"
    for i, n in data:
        text += f"{i}. {n}\n"

    await update.message.reply_text(text)

# =====================
# MASUK
# =====================
async def masuk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        return await update.message.reply_text("Contoh: /masuk 100000 gaji")

    amount = int(context.args[0])
    desc = " ".join(context.args[1:])

    cursor.execute("""
        INSERT INTO finance (user_id, type, amount, description)
        VALUES (?, ?, ?, ?)
    """, (update.effective_user.id, "masuk", amount, desc))

    conn.commit()

    await update.message.reply_text(f"💰 +Rp{amount:,}")

# =====================
# KELUAR
# =====================
async def keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        return await update.message.reply_text("Contoh: /keluar 50000 bensin")

    amount = int(context.args[0])
    desc = " ".join(context.args[1:])

    cursor.execute("""
        INSERT INTO finance (user_id, type, amount, description)
        VALUES (?, ?, ?, ?)
    """, (update.effective_user.id, "keluar", amount, desc))

    conn.commit()

    await update.message.reply_text(f"💸 -Rp{amount:,}")

# =====================
# SALDO
# =====================
async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute(
        "SELECT type, amount FROM finance WHERE user_id=?",
        (update.effective_user.id,)
    )

    data = cursor.fetchall()

    total = 0
    for t, a in data:
        if t == "masuk":
            total += a
        else:
            total -= a

    await update.message.reply_text(f"💰 SALDO: Rp{total:,}")

# =====================
# RUN BOT
# =====================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("todo", todo))
app.add_handler(CommandHandler("list", list_tasks))
app.add_handler(CommandHandler("done", done))

app.add_handler(CommandHandler("note", note))
app.add_handler(CommandHandler("notes", notes))

app.add_handler(CommandHandler("masuk", masuk))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("saldo", saldo))

print("BOT AKTIF")
app.run_polling()

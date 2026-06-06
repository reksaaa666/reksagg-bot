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

cursor.execute("""
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    count INTEGER DEFAULT 0
)
""")

conn.commit()

# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 REKSAGG BOT AKTIF\n\n"
        "/todo <tugas>\n/list\n/done <id>\n\n"
        "/note <catatan>\n/notes\n\n"
        "/masuk <jumlah> <keterangan>\n"
        "/keluar <jumlah> <keterangan>\n\n"
        "/habit <nama>\n/checkin <nama>\n\n"
        "/summary"
    )

# =====================
# TODO
# =====================
async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("contoh: /todo belajar python")

    task = " ".join(context.args)

    cursor.execute(
        "INSERT INTO tasks (user_id, task) VALUES (?, ?)",
        (update.effective_user.id, task)
    )
    conn.commit()

    await update.message.reply_text("✅ task ditambah")

# =====================
# LIST
# =====================
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute(
        "SELECT id, task FROM tasks WHERE user_id=?",
        (update.effective_user.id,)
    )
    data = cursor.fetchall()

    if not data:
        return await update.message.reply_text("kosong")

    text = "📝 TASK:\n\n"
    for i, t in data:
        text += f"{i}. {t}\n"

    await update.message.reply_text(text)

# =====================
# DONE
# =====================
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("contoh: /done 1")

    task_id = int(context.args[0])

    cursor.execute(
        "DELETE FROM tasks WHERE id=? AND user_id=?",
        (task_id, update.effective_user.id)
    )
    conn.commit()

    await update.message.reply_text("✅ selesai")

# =====================
# NOTE
# =====================
async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("contoh: /note ganti oli")

    text = " ".join(context.args)

    cursor.execute(
        "INSERT INTO notes (user_id, note) VALUES (?, ?)",
        (update.effective_user.id, text)
    )
    conn.commit()

    await update.message.reply_text("📝 tersimpan")

# =====================
# NOTES
# =====================
async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute(
        "SELECT id, note FROM notes WHERE user_id=?",
        (update.effective_user.id,)
    )
    data = cursor.fetchall()

    if not data:
        return await update.message.reply_text("kosong")

    text = "📝 NOTES:\n\n"
    for i, n in data:
        text += f"{i}. {n}\n"

    await update.message.reply_text(text)

# =====================
# MASUK
# =====================
async def masuk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        return await update.message.reply_text("contoh: /masuk 100000 gaji")

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
        return await update.message.reply_text("contoh: /keluar 50000 bensin")

    amount = int(context.args[0])
    desc = " ".join(context.args[1:])

    cursor.execute("""
        INSERT INTO finance (user_id, type, amount, description)
        VALUES (?, ?, ?, ?)
    """, (update.effective_user.id, "keluar", amount, desc))

    conn.commit()

    await update.message.reply_text(f"💸 -Rp{amount:,}")

# =====================
# HABIT + CHECKIN
# =====================
async def habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)

    cursor.execute(
        "INSERT INTO habits (user_id, name) VALUES (?, ?)",
        (update.effective_user.id, name)
    )
    conn.commit()

    await update.message.reply_text("🔥 habit ditambah")

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)

    cursor.execute("""
        UPDATE habits
        SET count = count + 1
        WHERE user_id=? AND name=?
    """, (update.effective_user.id, name))

    conn.commit()

    await update.message.reply_text("✔ checkin")

# =====================
# SUMMARY (DASHBOARD UTAMA)
# =====================
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id=?", (uid,))
    task_count = cursor.fetchone()[0]

    cursor.execute("SELECT task FROM tasks WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,))
    tasks = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id=?", (uid,))
    notes_count = cursor.fetchone()[0]

    cursor.execute("SELECT type, amount FROM finance WHERE user_id=?", (uid,))
    finance = cursor.fetchall()

    saldo = sum(a if t == "masuk" else -a for t, a in finance)

    cursor.execute("SELECT name, count FROM habits WHERE user_id=? ORDER BY count DESC LIMIT 3", (uid,))
    habits = cursor.fetchall()

    text = "📊 SUMMARY REKSAGG\n━━━━━━━━━━━━━━\n\n"

    text += f"📝 TASK ({task_count})\n"
    for t in tasks:
        text += f"• {t[0]}\n"

    text += f"\n💰 SALDO\nRp{saldo:,}\n"
    text += f"\n🧾 NOTES: {notes_count}\n\n"

    text += "🔥 HABITS\n"
    for h in habits:
        text += f"• {h[0]} ({h[1]}x)\n"

    await update.message.reply_text(text)

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

app.add_handler(CommandHandler("habit", habit))
app.add_handler(CommandHandler("checkin", checkin))

app.add_handler(CommandHandler("summary", summary))

print("BOT AKTIF")
app.run_polling()

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from receipt import generate_receipt

API_ID = 21189715
API_HASH = "988a9111105fd2f0c5e21c2c2449edfd"
BOT_TOKEN = "8149415790:AAE9L3ew6ENxgs7S9yYAXYGXej-NeAbunS4"

app = Client("bank_receipt_bot",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN)

users = {}

@app.on_message(filters.command("start"))
async def start(_, m):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧾 Create Receipt", callback_data="create")]
    ])
    await m.reply("💸 **Bank Receipt Generator Bot**", reply_markup=kb)

@app.on_callback_query()
async def cb_handler(_, cq):
    uid = cq.from_user.id
    data = users.get(uid)
    
    if cq.data == "create":
        users[uid] = {}
        await cq.message.edit("👉 Enter **Paid To Name**:")

    elif cq.data in ["light", "dark"]:
        if not data:
            await cq.answer("⚠ Please start receipt creation first with /start", show_alert=True)
            return
        theme = cq.data
        file = generate_receipt(data, theme)
        await cq.message.edit("✅ **Receipt Generated**")
        await cq.message.reply_photo(file)
        users.pop(uid, None)

@app.on_message(filters.text & filters.private)
async def text_handler(_, m):
    uid = m.from_user.id
    if uid not in users:
        return
    data = users[uid]

    if "to" not in data:
        data["to"] = m.text
        return await m.reply("👉 Enter **Paid By Name**:")

    if "from" not in data:
        data["from"] = m.text
        return await m.reply("👉 Enter **Amount**:")

    if "amount" not in data:
        data["amount"] = m.text
        return await m.reply("👉 Enter **UTR Number**:")

    if "utr" not in data:
        data["utr"] = m.text
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌞 Light Theme", callback_data="light"),
                InlineKeyboardButton("🌙 Dark Theme", callback_data="dark")
            ]
        ])
        return await m.reply("🎨 Choose Receipt Theme:", reply_markup=kb)

app.run()

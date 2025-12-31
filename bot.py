from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from receipt import generate_receipt

API_ID = 12345678
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_TOKEN"

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
async def cb(_, cq):
    uid = cq.from_user.id

    if cq.data == "create":
        users[uid] = {}
        await cq.message.edit("👉 Enter **Paid To Name**:")

    elif cq.data in ["light", "dark"]:
        theme = cq.data
        data = users[uid]
        file = generate_receipt(data, theme)
        await cq.message.edit("✅ **Receipt Generated**")
        await cq.message.reply_photo(file)
        users.pop(uid)

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

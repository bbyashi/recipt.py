from pyrogram import Client, filters
from receipt import generate_receipt

API_ID = 21189715
API_HASH = "988a9111105fd2f0c5e21c2c2449edfd"
BOT_TOKEN = "8149415790:AAE9L3ew6ENxgs7S9yYAXYGXej-NeAbunS4"

app = Client(
    "bank_receipt_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("gen") & filters.private)
async def gen_receipt(_, m):
    try:
        _, name, acc, amount = m.text.split(maxsplit=3)
    except ValueError:
        return await m.reply(
            "❌ Format wrong\n\n"
            "**Use:**\n"
            "`/gen name account/upi amount`\n\n"
            "**Example:**\n"
            "`/gen chiky 788787887887 250`\n"
            "`/gen chiky chiky@upi 250`"
        )

    file = generate_receipt(
        paid_to=name,
        account_or_upi=acc,
        amount=amount
    )

    await m.reply_photo(file, caption="✅ Receipt Generated")

app.run()

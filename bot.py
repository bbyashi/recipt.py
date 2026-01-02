import os, re, unicodedata
from pyrogram import Client, filters
from receipt import generate_receipt

API_ID = 21189715
API_HASH = "988a9111105fd2f0c5e21c2c2449edfd"
BOT_TOKEN = "8149415790:AAE9L3ew6ENxgs7S9yYAXYGXej-NeAbunS4"

app = Client("receipt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


INDIAN_BANKS = {
    "sbi","state bank","hdfc","icici","axis","canara","pnb","punjab national",
    "bank of baroda","bob","union bank","ubi","indian bank","idbi","yes bank",
    "kotak","bank of india","boi","central bank","uco","indusind","rbl",
    "federal","south indian","karnataka bank","karur vysya","kvb"
}

def normalize(text):
    import unicodedata, re
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w@\n ]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)   # preserve newline
    return text.lower()
    
def extract_from_text(text):
    text = normalize(text)

    # ---------- ACCOUNT / UPI ----------
    upi = re.search(r"\b[a-z0-9._-]+@[a-z]+\b", text)
    if upi:
        account = upi.group()
    else:
        nums = re.findall(r"\b\d{9,18}\b", text)
        account = nums[0] if nums else None

    # ---------- IFSC ----------
    ifsc = re.search(r"\b[a-z]{4}0\d{6}\b", text)
    ifsc = ifsc.group().upper() if ifsc else None

    # ---------- NAME ----------
    name = None
    for line in text.split("\n"):
        line = line.strip()
        if len(line.split()) < 2:  # ignore very short lines or numbers
            continue

        # ignore lines with bank/account/ifsc/upi keywords
        if any(k in line for k in ["bank", "account", "ifsc", "@"]):
            continue

        # ignore lines having Indian bank names
        if any(b in line.lower() for b in INDIAN_BANKS):
            continue

        # remove unwanted keywords like 'name', 'account holder', 'beneficiary'
        line = re.sub(r"^(name|account holder|beneficiary)\s+", "", line, flags=re.IGNORECASE)

        # match 2–5 word person name
        m = re.fullmatch(r"[a-z]{3,}(?:\s+[a-z]{3,}){1,4}", line.lower())
        if m:
            name = m.group()
            break

    name = name.title() if name else None
    return name, account, ifsc



@app.on_message(filters.command("done"))
async def done_cmd(_, m):
    await m.delete()
    parts = m.text.split()
    if len(parts) < 2:
        return await m.reply("❌ /done <amount>")

    amount = parts[1]

    if not m.reply_to_message or not m.reply_to_message.text:
        return await m.reply("❌ Reply to bank message")

    name, account, ifsc = extract_from_text(m.reply_to_message.text)

    if not name or not account:
        return await m.reply("❌ Name / Account detect nahi hua")

    file = generate_receipt(paid_to=name, account_or_upi=account,
                            amount=amount, status="SUCCESS")

    await m.reply_photo(file, caption=f"✅ Receipt for {name}")


@app.on_message(filters.command("fail"))
async def fail_cmd(_, m):
    await m.delete()
    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        return await m.reply("❌ /fail <amount> <reason>")

    amount = parts[1]
    reason = parts[2]

    if not m.reply_to_message or not m.reply_to_message.text:
        return await m.reply("❌ Reply to bank message")

    name, account, ifsc = extract_from_text(m.reply_to_message.text)

    if not name or not account:
        return await m.reply("❌ Name / Account detect nahi hua")

    file = generate_receipt(paid_to=name, account_or_upi=account,
                            amount=amount, status="FAILED", fail_reason=reason)

    await m.reply_photo(file, caption=f"❌ Payment Failed for {name}")


print("🤖 Receipt Bot Running...")
app.run()

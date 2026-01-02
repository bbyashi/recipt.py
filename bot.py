import os, re, unicodedata
from pyrogram import Client, filters
from receipt import generate_receipt

API_ID = 21189715
API_HASH = "988a9111105fd2f0c5e21c2c2449edfd"
BOT_TOKEN = "7947877880:AAEn3SB0pAoyDq2AYeYkkv0i05AF6zykT24"

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

    # ---------- ACCOUNT ----------
    account_match = re.search(r"(?:account\s*(?:no|number)?\s*[:\-,]?\s*|(?<!\d))(\d{9,18})", text, flags=re.IGNORECASE)
    account = account_match.group(1) if account_match else None

    # ---------- IFSC ----------
    ifsc_match = re.search(r"\b[a-z]{4}0\d{6}\b", text, flags=re.IGNORECASE)
    ifsc = ifsc_match.group().upper() if ifsc_match else None

    # ---------- NAME ----------
    name = None
    for line in text.split("\n"):
        line = line.strip()
        if len(line.split()) < 1:
            continue

        # ignore lines with bank/account/ifsc/upi keywords
        if any(k in line.lower() for k in ["bank", "ifsc", "@"]):
            continue

        # ignore lines having Indian bank names
        if any(b in line.lower() for b in INDIAN_BANKS):
            continue

        line = line.strip()

        # remove leading numbering or emojis (like 1️⃣, 1., *, -)
        line = re.sub(r"^[\d\W]*", "", line)
        # remove unwanted prefixes like 'name', 'holder name', 'account holder', 'beneficiary'
        line = re.sub(r"^(name|holder name|1️⃣ Name:|account holder|beneficiary)\s*[:\-,]?\s*", "", line, flags=re.IGNORECASE)

        # match 1–5 word person name
        m = re.search(r"[a-z]{3,}(?:\s+[a-z]{2,}){0,4}", line.lower())
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

    # Extract details
    name, account, ifsc = extract_from_text(m.reply_to_message.text)
    if not name or not account:
        return await m.reply("❌ Name / Account detect nahi hua")

    # Generate receipt
    file = generate_receipt(paid_to=name, account_or_upi=account, amount=amount, status="SUCCESS")

    # Reply to original message (no username tagging)
    await m.reply_to_message.reply_photo(file, caption=f"✅ Receipt for {name}")



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

    # Extract details
    name, account, ifsc = extract_from_text(m.reply_to_message.text)
    if not name or not account:
        return await m.reply("❌ Name / Account detect nahi hua")

    # Generate failed receipt
    file = generate_receipt(paid_to=name, account_or_upi=account,
                            amount=amount, status="FAILED", fail_reason=reason)

    # Reply to original message (no username tagging)
    await m.reply_to_message.reply_photo(file, caption=f"❌ Payment Failed for {name}")



print("🤖 Receipt Bot Running...")
app.run()

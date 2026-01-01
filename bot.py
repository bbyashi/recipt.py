import re
from pyrogram import Client, filters
from receipt import generate_receipt  # tera receipt.py

API_ID = 21189715
API_HASH = "988a9111105fd2f0c5e21c2c2449edfd"
BOT_TOKEN = "8149415790:AAE9L3ew6ENxgs7S9yYAXYGXej-NeAbunS4"

app = Client(
    "receipt_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- NAME + ACCOUNT/UPI EXTRACTOR ----------------
def extract_details(text: str):
    """
    Robust Name + Account/UPI extractor for all provided formats
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = None
    account = None

    for l in lines:
        low = l.lower()

        # ----- UPI detection -----
        upi = re.search(r"\b[\w\.-]+@[\w-]+\b", l)
        if upi:
            account = upi.group()
            continue

        # ----- Account with keywords -----
        if re.search(r"\b(ac|a/c|account|account no|a/c no)\b", low):
            digits = re.search(r"\d{4,18}", l.replace(" ", ""))
            if digits:
                account = digits.group()
                continue

        # ----- Pure digit line (9-18 digits) -----
        digits = re.fullmatch(r"\d{9,18}", l.replace(" ", ""))
        if digits:
            account = l.replace(" ", "")
            continue

        # ----- Name detection -----
        if not name:
            # Name: X / Holder name: X / Account holder: X / Paid to X
            m = re.search(
                r"(?i)(name|holder name|account holder|paid to|credited to)[:\- ]*\s*([A-Za-z ]{2,60})",
                l
            )
            if m:
                name = m.group(2).strip()
                continue

            # Pure line with letters only (2+ words)
            if re.fullmatch(r"[A-Za-z ]{3,60}", l) and len(l.split()) >= 2:
                name = l.strip()

    return name, account


# ---------------- /done COMMAND ----------------
@app.on_message(filters.command("done") & (filters.private | filters.group))
async def done_cmd(_, m):
    await m.delete()

    # Get amount from command
    parts = m.text.split(maxsplit=1)
    amount = parts[1].strip() if len(parts) > 1 else None

    # Get source text (reply or inline)
    source_text = ""
    if m.reply_to_message and m.reply_to_message.text:
        source_text = m.reply_to_message.text
    else:
        if amount:
            source_text = m.text.replace(f"/done {amount}", "").strip()
        else:
            return await m.reply("❌ Reply to payment text or paste it after /done <amount>")

    # Extract Name + Account/UPI
    name, account = extract_details(source_text)
    if not name or not account:
        return await m.reply("❌ Name / Account / UPI detect nahi hua")

    # Generate receipt
    file = generate_receipt(
        paid_to=name,
        account_or_upi=account,
        amount=amount if amount else "0",
        status="SUCCESS"
    )

    await m.reply_photo(file, caption=f"✅ Payment Receipt for {name}")


# ---------------- /fail COMMAND ----------------
@app.on_message(filters.command("fail") & (filters.private | filters.group))
async def fail_cmd(_, m):
    await m.delete()

    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        return await m.reply("❌ Format: /fail <amount> <reason>")

    amount = parts[1].strip()
    reason = parts[2].strip()

    # Get source text (reply or inline)
    source_text = ""
    if m.reply_to_message and m.reply_to_message.text:
        source_text = m.reply_to_message.text
    else:
        source_text = m.text.replace(f"/fail {amount} {reason}", "").strip()
        if not source_text:
            return await m.reply("❌ Reply to payment text or paste it after /fail <amount> <reason>")

    # Extract Name + Account/UPI
    name, account = extract_details(source_text)
    if not name or not account:
        return await m.reply("❌ Name / Account / UPI detect nahi hua")

    # Generate failed receipt
    file = generate_receipt(
        paid_to=name,
        account_or_upi=account,
        amount=amount,
        status="FAILED",
        fail_reason=reason
    )

    await m.reply_photo(file, caption=f"❌ Payment Failed for {name}\nReason: {reason}")


print("🤖 Receipt Bot Started...")
app.run()

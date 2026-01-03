import re
import unicodedata
from pyrogram import Client, filters
from pymongo import MongoClient
from receipt import generate_receipt

# ---------------- TELEGRAM BOT CONFIG ----------------
API_ID = 21189715
API_HASH = "988a9111105fd2f0c5e21c2c2449edfd"
BOT_TOKEN = "7947877880:AAEn3SB0pAoyDq2AYeYkkv0i05AF6zykT24"
OWNER_ID = 7932059238  # <-- apna telegram ID (owner)

app = Client("receipt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------- MONGO SETUP ----------------
MONGO_URI = "mongodb+srv://Ashiku:ashachiku123@cluster0.wu7maqj.mongodb.net/?appName=Cluster0"  # <-- apna URI
mongo = MongoClient(MONGO_URI)
db = mongo["receiptbot"]
sudo_db = db["sudo_users"]
users_db = db["users"]


# ---------------- SUDO / OWNER SYSTEM ----------------
def is_sudo(user_id: int):
    if user_id == OWNER_ID:  # owner always sudo
        return True
    return sudo_db.find_one({"user_id": user_id}) is not None

def add_sudo(user_id: int):
    sudo_db.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

def remove_sudo(user_id: int):
    sudo_db.delete_one({"user_id": user_id})

# ---------------- INDIAN BANKS ----------------
INDIAN_BANKS = {
    "sbi","state bank","hdfc","icici","axis","canara","canara bank","pnb","punjab national",
    "bank of baroda","bob","union bank","ubi","indian bank","idbi","yes bank",
    "kotak","bank of india","boi","central bank","uco","indusind","rbl",
    "federal","south indian","karnataka bank","karur vysya","kvb"
}

def normalize(text):
    text = unicodedata.normalize("NFKD", text)
    # allow letters, numbers, dash, underscore, @, space, newline
    text = re.sub(r"[^\w@\n \-]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.lower()

# ---------- EXTRACT NAME / ACCOUNT / IFSC ----------
def extract_from_text(text):
    text = normalize(text)

    # ---------- ACCOUNT / UPI ----------
    account = None
    upi_match = re.search(r"[a-z0-9._-]+@[a-z0-9._-]+", text, flags=re.IGNORECASE)
    if upi_match:
        account = upi_match.group()
    else:
        nums = re.findall(r"\b\d{9,18}\b", text)
        if nums:
            account = nums[0]

    # ---------- IFSC ----------
    ifsc_match = re.search(r"\b[a-z]{4}0[a-z0-9]{6}\b", text, flags=re.IGNORECASE)
    ifsc = ifsc_match.group().upper() if ifsc_match else None

    # ---------- NAME ----------
    name = None

    # 1️⃣ key-value format
    kv_name = re.search(
        r"(account holder name|account holder|holder name|beneficiary|name)\s*[:\-]\s*([a-z ]{4,40})",
        text, flags=re.IGNORECASE
    )
    if kv_name:
        name = kv_name.group(2).strip()

    # 2️⃣ clean-line fallback
    if not name:
        for line in text.split("\n"):
            raw = line.strip()
            low = raw.lower()

            if not raw:
                continue

            # ❌ skip bank / account / ifsc lines
            if any(w in low for w in ["bank", "ifsc", "account", "number", "@"]):
                continue

            # ❌ skip indian bank words
            if any(b in low for b in BANK_WORDS):
                continue

            raw = re.sub(r"^[\d\W]+", "", raw)

            if re.fullmatch(r"[A-Za-z ]{4,40}", raw):
                name = raw
                break

    name = name.title() if name else None
    return name, account, ifsc




# ---------------- /start COMMAND ----------------
@app.on_message(filters.command("start"))
async def start_cmd(_, m):
    user = m.from_user
    if not user:
        return

    users_db.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "first_name": user.first_name,
            "username": user.username,
        }},
        upsert=True
    )
    await m.reply(f"👋 Hello {user.first_name}! You are registered for updates.")

# ---------------- /done COMMAND ----------------
@app.on_message(filters.command("done"))
async def done_cmd(_, m):
    if not is_sudo(m.from_user.id):
        return await m.reply("❌ You are not authorized")

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

    file = generate_receipt(paid_to=name, account_or_upi=account, amount=amount, status="SUCCESS")
    await m.reply_to_message.reply_photo(file, caption=f"✅ Receipt for {name}")

# ---------------- /fail COMMAND ----------------
@app.on_message(filters.command("fail"))
async def fail_cmd(_, m):
    if not is_sudo(m.from_user.id):
        return await m.reply("❌ You are not authorized")

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
    await m.reply_to_message.reply_photo(file, caption=f"❌ Payment Failed for {name}")

# ---------------- /add COMMAND ----------------
@app.on_message(filters.command("add"))
async def add_cmd(_, m):
    if not is_sudo(m.from_user.id):
        return await m.reply("❌ You are not authorized")

    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await m.reply("❌ Usage: /add <user_id>")

    uid = int(parts[1])
    add_sudo(uid)
    await m.reply(f"✅ User {uid} added as sudo")

# ---------------- /remove COMMAND ----------------
@app.on_message(filters.command("remove"))
async def remove_cmd(_, m):
    if m.from_user.id != OWNER_ID:  # only owner can remove
        return await m.reply("❌ Only owner can remove sudo users")

    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await m.reply("❌ Usage: /remove <user_id>")

    uid = int(parts[1])
    remove_sudo(uid)
    await m.reply(f"🗑 User {uid} removed from sudo")

# ---------------- /broadcast COMMAND ----------------
@app.on_message(filters.command("broadcast"))
async def broadcast_cmd(_, m):
    if not is_sudo(m.from_user.id):
        return await m.reply("❌ You are not authorized")
    
    msg = m.text.split(maxsplit=1)
    if len(msg) < 2:
        return await m.reply("❌ Usage: /broadcast <message>")

    text = msg[1]
    count = 0
    for user in users_db.find({}):
        try:
            await app.send_message(user["user_id"], f"📢 Broadcast:\n\n{text}")
            count += 1
        except:
            continue

    await m.reply(f"✅ Broadcast sent to {count} users")

# ---------- COMMAND: /authlist ----------
@app.on_message(filters.command("authlist"))
async def authlist_cmd(_, m):
    user = m.from_user
    if user.id != OWNER_ID and not sudo_db.find_one({"user_id": user.id}):
        return await m.reply("❌ You are not authorized to view the auth list.")

    sudoers_list = list(sudo_db.find())
    if len(sudoers_list) == 0:
        return await m.reply("No sudoers found.")

    text = "👑 Current Sudoers:\n"
    for s in sudoers_list:
        text += f"- `{s['user_id']}`\n"

    await m.reply(text)

# ---------------- RUN BOT ----------------
print("🤖 Receipt Bot Running...")
app.run()

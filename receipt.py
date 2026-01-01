import os
import uuid
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "assets/pariwesh.png")

# FONTS
FONT_BOLD = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
FONT_AMOUNT = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
FONT_STATUS = ImageFont.truetype("DejaVuSans-Bold.ttf", 38)
FONT_NORMAL = ImageFont.truetype("DejaVuSans.ttf", 34)  # ✅ normal font

# COLORS
GOLD = (255, 200, 90)
GREEN = (120, 255, 120)


def format_account_or_upi(value: str) -> str:
    value = value.strip()

    # ✅ UPI case
    if "@" in value:
        return f"( UPI : {value} )"

    # ✅ Account number case (mask all except last 4)
    last4 = value[-4:]
    return f"( Acc No - XXXX XXXX {last4} )"


def generate_receipt(paid_to: str, account_or_upi: str, amount: str):
    img = Image.open(BG_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # IST Date & Time
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    date = now.strftime("%d %b %Y")
    time = now.strftime("%I:%M %p")

    # Auto UTR
    utr = str(random.randint(100000000000, 999999999999))

    acc_text = format_account_or_upi(account_or_upi)

    positions = {
        "paid_to": (540, 335),
        "account": (470, 390),   # 👈 name ke just niche
        "paid_by": (520, 470),
        "amount": (510, 554),
        "utr": (520, 655),
        "date": (520, 740),
        "time": (520, 825),
        "status": (520, 920),
    }

    # DRAW TEXT
    draw.text(positions["paid_to"], paid_to, font=FONT_BOLD, fill=GOLD)
    draw.text(positions["account"], acc_text, font=FONT_NORMAL, fill=GOLD)  # ✅ normal
    draw.text(positions["paid_by"], "Prishwave Team", font=FONT_BOLD, fill=GOLD)
    draw.text(positions["amount"], f"₹{amount}", font=FONT_AMOUNT, fill=GOLD)
    draw.text(positions["utr"], utr, font=FONT_BOLD, fill=GOLD)
    draw.text(positions["date"], date, font=FONT_BOLD, fill=GOLD)
    draw.text(positions["time"], time, font=FONT_BOLD, fill=GOLD)
    draw.text(positions["status"], "SUCCESS", font=FONT_STATUS, fill=GREEN)

    out = f"/tmp/receipt_{uuid.uuid4().hex}.png"
    img.save(out)
    return out

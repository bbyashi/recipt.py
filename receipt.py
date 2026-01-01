# receipt.py
import os
import uuid
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BG_PATH = os.path.join(BASE_DIR, "assets/dark_bg1.png")

FONT_VALUE = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)
FONT_AMOUNT = ImageFont.truetype("DejaVuSans-Bold.ttf", 35)
FONT_STATUS = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)

GOLD = (255, 200, 90)
GREEN = (120, 255, 120)
RED = (255, 120, 120)


def mask_account(acc: str):
    acc = acc.strip()

    # UPI
    if "@" in acc:
        return f"UPI - {acc}"

    digits = "".join(filter(str.isdigit, acc))
    if len(digits) >= 4:
        return f"Acc No - XXXX XXXX {digits[-4:]}"
    return acc


def generate_receipt(
    *,
    paid_to: str,
    account_or_upi: str,
    amount: str,
    status: str = "SUCCESS",
    fail_reason: str | None = None
):
    img = Image.open(BG_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    date = now.strftime("%d %b %Y")
    time = now.strftime("%I:%M %p")

    utr = str(random.randint(100000000000, 999999999999))
    acc_text = mask_account(account_or_upi)

    positions = {
        "paid_to": (470, 360),
        "account": (470, 420),
        "paid_by": (470, 530),
        "amount": (470, 620),
        "utr": (470, 720),
        "date": (470, 810),
        "time": (470, 890),
        "status": (470, 970),
        "reason": (470, 1000),
    }

    draw.text(positions["paid_to"], paid_to, font=FONT_VALUE, fill=GOLD)
    draw.text(positions["account"], acc_text, font=FONT_VALUE, fill=GOLD)
    draw.text(positions["paid_by"], "Prishwave Team", font=FONT_VALUE, fill=GOLD)
    draw.text(positions["amount"], f"₹{amount}", font=FONT_AMOUNT, fill=GOLD)
    draw.text(positions["utr"], utr, font=FONT_VALUE, fill=GOLD)
    draw.text(positions["date"], date, font=FONT_VALUE, fill=GOLD)
    draw.text(positions["time"], time, font=FONT_VALUE, fill=GOLD)

    if status == "SUCCESS":
        draw.text(positions["status"], "SUCCESS", font=FONT_STATUS, fill=GREEN)
    else:
        draw.text(positions["status"], "FAILED", font=FONT_STATUS, fill=RED)
        if fail_reason:
            draw.text(
                positions["reason"],
                f"Reason - {fail_reason}",
                font=FONT_VALUE,
                fill=RED
            )

    out = f"/tmp/receipt_{uuid.uuid4().hex}.png"
    img.save(out)
    return out

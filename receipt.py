# receipt.py
import os
import uuid
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
from num2words import num2words

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "assets/22222.png")  # your template

# ================= FONTS =================
FONT = ImageFont.truetype("DejaVuSans-Bold.ttf", 30)
FONT_STATUS = ImageFont.truetype("DejaVuSans-Bold.ttf", 32)

# ================= COLORS =================
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
RED = (220, 0, 0)

# ==================================================
# 🔥 FULL CONTROL SECTIONS (EDIT ONLY THESE NUMBERS)
# ==================================================

# ---- LABEL POSITIONS (independent) ----
LABEL_POS = {
    "transaction_date": (150, 250),
    "paid_to": (150, 325),
    "paid_by": (150, 395),
    "account": (150, 466),
    "amount": (150, 535),
    "amount_words": (150, 611),
    "utr": (150, 682),
    "time": (150, 747),
    "status": (150, 820),
}

# ---- VALUE POSITIONS (independent) ----
VALUE_POS = {
    "transaction_date": (620, 250),
    "paid_to": (620, 325),
    "paid_by": (620, 395),
    "account": (620, 466),
    "amount": (620, 535),
    "amount_words": (620, 611),
    "utr": (620, 682),
    "time": (620, 747),
    "status": (620, 820),
}

# ==================================================


def mask_account(acc: str):
    acc = acc.strip()
    if "@" in acc:
        return acc
    digits = "".join(filter(str.isdigit, acc))
    if len(digits) >= 4:
        return f"XXXX XXXX {digits[-4:]}"
    return acc


def generate_receipt(
    paid_to: str,
    account_or_upi: str,
    amount: str,
    status: str = "SUCCESS",
    fail_reason: str | None = None,
):
    img = Image.open(BG_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ================= DATE / TIME =================
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    date = now.strftime("%d %b %Y")
    time = now.strftime("%I:%M %p")

    # ================= DATA =================
    utr = str(random.randint(100000000000, 999999999999))
    acc_text = mask_account(account_or_upi)

    # Convert to Indian currency words (integer rupees only)
    amount_float = float(amount)
    rupees = int(amount_float)
    amount_words = num2words(rupees, lang="en_IN").replace("-", " ").title() + " Rupees"

    # ================= DRAW LABELS & VALUES =================
    draw.text(LABEL_POS["transaction_date"], "Transaction Date:", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["transaction_date"], date, font=FONT, fill=BLACK)

    draw.text(LABEL_POS["paid_to"], "Paid To:", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["paid_to"], paid_to, font=FONT, fill=BLACK)

    draw.text(LABEL_POS["paid_by"], "Paid By:", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["paid_by"], "Imps Pvt Ltd", font=FONT, fill=BLACK)

    draw.text(LABEL_POS["account"], "Account / UPI:", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["account"], acc_text, font=FONT, fill=BLACK)

    draw.text(LABEL_POS["amount"], "Amount:", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["amount"], f"₹{amount}", font=FONT, fill=BLACK)

    draw.text(LABEL_POS["amount_words"], "Amount (in words):", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["amount_words"], amount_words, font=FONT, fill=BLACK)

    draw.text(LABEL_POS["utr"], "UTR No:", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["utr"], utr, font=FONT, fill=BLACK)

    draw.text(LABEL_POS["time"], "Time:", font=FONT, fill=BLACK)
    draw.text(VALUE_POS["time"], time, font=FONT, fill=BLACK)

    # ================= STATUS =================
    draw.text(LABEL_POS["status"], "Status:", font=FONT_STATUS, fill=BLACK)

    if status.upper() == "SUCCESS":
        draw.text(VALUE_POS["status"], "SUCCESS", font=FONT_STATUS, fill=GREEN)
    else:
        # Draw "FAILED"
        draw.text(VALUE_POS["status"], "FAILED", font=FONT_STATUS, fill=RED)

        # Draw reason right next to "FAILED"
        if fail_reason:
            bbox = FONT_STATUS.getbbox("FAILED")  # (x0, y0, x1, y1)
            failed_width = bbox[2] - bbox[0]
            reason_pos = (VALUE_POS["status"][0] + failed_width + 10, VALUE_POS["status"][1])
            draw.text(reason_pos, f": {fail_reason}", font=FONT, fill=RED)

    # ================= SAVE =================
    out = f"/tmp/receipt_{uuid.uuid4().hex}.png"
    img.save(out)
    return out

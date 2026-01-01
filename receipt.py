from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

BG_PATH = "assets/dark_bg.png"

FONT_REG = ImageFont.truetype("DejaVuSans.ttf", 34)
FONT_BOLD = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
FONT_SMALL = ImageFont.truetype("DejaVuSans.ttf", 30)

def generate_receipt(
    paid_to: str,
    paid_by: str,
    amount: str,
    utr: str,
    status: str = "SUCCESS"
):
    # Load background
    img = Image.open(BG_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 🔥 AUTO DATE & TIME (IST)
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    date = now.strftime("%d %b %Y")     # 06 Jan 2026
    time = now.strftime("%I:%M %p")     # 09:15 PM

    # Colors
    WHITE = (245, 245, 245)
    GOLD = (255, 200, 90)
    GREEN = (120, 255, 120)

    # Layout positions (matched to your template)
    x_label = 140
    x_value = 520
    y = 360
    gap = 85

    fields = [
        ("Paid To", paid_to),
        ("Paid By", paid_by),
        ("Amount", f"₹{amount}"),
        ("UTR Number", utr),
        ("Date", date),   # ← automatic
        ("Time", time),   # ← automatic
        ("Status", status),
    ]

    for label, value in fields:
        draw.text((x_label, y), label, font=FONT_SMALL, fill=WHITE)
        draw.text(
            (x_value, y),
            value,
            font=FONT_BOLD if label == "Amount" else FONT_REG,
            fill=GREEN if label == "Status" else GOLD
        )
        y += gap

    out = f"/tmp/receipt_{uuid.uuid4().hex}.png"
    img.save(out)
    return out

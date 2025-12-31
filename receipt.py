from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
import os

def generate_receipt(data, theme="light", output="receipt.png"):
    # Background
    bg_file = "assets/12.png" if theme=="light" else "assets/dark_bg.png"
    if not os.path.exists(bg_file):
        raise FileNotFoundError(f"Background file not found: {bg_file}")
    
    img = Image.open(bg_file).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Fonts
    font_title = ImageFont.truetype("assets/font.ttf", 50)
    font_label = ImageFont.truetype("assets/font.ttf", 32)
    font_value = ImageFont.truetype("assets/font.ttf", 36)
    font_small = ImageFont.truetype("assets/font.ttf", 24)

    # Auto date & time (IST)
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%H:%M:%S")

    # Title
    draw.text((250, 40), "BANK PAYMENT RECEIPT", font=font_title, fill="#1e3a8a")

    y_start = 180
    gap = 85
    fields = [
        ("Paid To", data["to"]),
        ("Paid By", data["from"]),
        ("Amount", f"₹ {data['amount']}"),
        ("UTR Number", data["utr"]),
        ("Date", date),
        ("Time", time),
        ("Status", "SUCCESS")
    ]

    for i, (label, value) in enumerate(fields):
        draw.text((120, y_start + i*gap), label, font=font_label, fill="#6b7280")
        draw.text((430, y_start + i*gap), value, font=font_value, fill="#111827")

    # Footer logos
    logos = ["assets/gpay.png", "assets/paytm.png", "assets/upi.png"]
    x = 160
    for logo in logos:
        if not os.path.exists(logo):
            continue
        icon = Image.open(logo).convert("RGBA").resize((100, 100))
        img.paste(icon, (x, 940), icon)
        x += 240

    # Footer note
    draw.text((240, 880), "This is a system generated receipt", font=font_small, fill="#6b7280")

    img.save(output)
    return output

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def generate_receipt(data, theme="light", output="receipt.png"):
    bg = "assets/light_bg.png" if theme == "light" else "assets/dark_bg.png"
    img = Image.open(bg).convert("RGBA")
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.truetype("assets/font.ttf", 48)
    label_font = ImageFont.truetype("assets/font.ttf", 32)
    value_font = ImageFont.truetype("assets/font.ttf", 36)
    small_font = ImageFont.truetype("assets/font.ttf", 24)

    # Auto date & time
    now = datetime.now()
    date = now.strftime("%d %b %Y")
    time = now.strftime("%I:%M %p")

    # Title
    draw.text((260, 40), "BANK PAYMENT RECEIPT", font=title_font, fill="#1e3a8a")

    y = 180
    gap = 85

    fields = [
        ("Paid To", data["to"]),
        ("Paid By", data["from"]),
        ("Amount", f"₹ {data['amount']}"),
        ("UTR Number", data["utr"]),
        ("Date", date),
        ("Time", time),
        ("Status", "SUCCESS"),
    ]

    for label, value in fields:
        draw.text((120, y), label, font=label_font, fill="#6b7280")
        draw.text((430, y), value, font=value_font, fill="#111827")
        y += gap

    # Footer note
    draw.text((240, 880), "This is a system generated receipt",
              font=small_font, fill="#6b7280")

    # Logos
    logos = ["assets/gpay.png", "assets/paytm.png", "assets/upi.png"]
    x = 160
    for l in logos:
        icon = Image.open(l).resize((100, 100))
        img.paste(icon, (x, 940), icon)
        x += 240

    img.save(output)
    return output

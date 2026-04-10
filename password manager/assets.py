import os
from PIL import Image, ImageDraw, ImageFont
from constants import ASSETS_DIR, LOGO_PATH, LOGIN_BG, REGISTER_BG, HOME_BG, PRIMARY, SECONDARY, ACCENT, WHITE

def _generate_and_save_logo(path, size=128, bg=PRIMARY, accent=ACCENT, fg=WHITE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new("RGBA", (size, size), bg)
    draw = ImageDraw.Draw(img)
    try:
        fnt = ImageFont.truetype("arial.ttf", int(size * 0.55))
    except Exception:
        fnt = ImageFont.load_default()
    text = "P"
    w, h = draw.textsize(text, font=fnt)
    draw.text(((size - w) / 2, (size - h) / 2), text, font=fnt, fill=fg)
    draw.rectangle([size - int(size*0.16), size - int(size*0.3), size - int(size*0.06), size - int(size*0.06)], fill=accent)
    img.save(path, format="PNG")
    return img

def load_ctk_logo(size=(36,36)):
    from customtkinter import CTkImage
    if not os.path.exists(LOGO_PATH):
        _generate_and_save_logo(LOGO_PATH, size=128, bg=PRIMARY, accent=ACCENT, fg=WHITE)
    pil_img = Image.open(LOGO_PATH).convert("RGBA")
    pil_img = pil_img.resize((size[0], size[1]), Image.LANCZOS)
    return CTkImage(light_image=pil_img, size=size)

def ensure_files():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    # create salt file if missing
    from constants import KEY_FILE
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'wb') as f:
            f.write(os.urandom(16))
    if not os.path.exists(LOGO_PATH):
        _generate_and_save_logo(LOGO_PATH, size=128, bg=PRIMARY, accent=ACCENT, fg=WHITE)
    if not os.path.exists(LOGIN_BG):
        img = Image.new("RGBA", (1600, 1000), PRIMARY)
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 1600, 200], fill=SECONDARY)
        img.save(LOGIN_BG)
    if not os.path.exists(REGISTER_BG):
        img = Image.new("RGBA", (1600, 1000), SECONDARY)
        draw = ImageDraw.Draw(img)
        draw.ellipse([-200, -200, 600, 600], fill=ACCENT)
        img.save(REGISTER_BG)
    if not os.path.exists(HOME_BG):
        img = Image.new("RGBA", (1600, 1000), WHITE)
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 1600, 120], fill=PRIMARY)
        img.save(HOME_BG)

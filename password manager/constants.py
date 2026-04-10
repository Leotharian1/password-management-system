from pathlib import Path
import os

BASE_DIR = Path(__file__).parent
ASSETS_DIR = str(BASE_DIR / "assets")
DB_FILE = str(BASE_DIR / "data.json")
KEY_FILE = str(BASE_DIR / "secret.key")
APP_NAME = "Password Engine"

# Colors / theme
PRIMARY = "#36454f"
SECONDARY = "#4682b4"
ACCENT = "#39ff14"
LIGHT = "#d3d3d3"
WHITE = "#ffffff"
GOLD = "#d4af37"
BLACK = "#000000"

# Asset paths
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
LOGIN_BG = os.path.join(ASSETS_DIR, "login_bg.png")
REGISTER_BG = os.path.join(ASSETS_DIR, "register_bg.png")
HOME_BG = os.path.join(ASSETS_DIR, "home_bg.png")

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>/?\\|"

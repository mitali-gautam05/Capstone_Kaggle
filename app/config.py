import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "outputs"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# config.py
import json
import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SCRAPING_TARGETS_FILE = os.path.join(BASE_DIR, 'scraping_targets.json')

    with open(SCRAPING_TARGETS_FILE) as f:
        SCRAPING_TARGETS = json.load(f)

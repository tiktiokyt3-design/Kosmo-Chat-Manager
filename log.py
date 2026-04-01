import time
from datetime import datetime

log_file = 'logger.log'

def log(action):
    with open(log_file, 'a', encoding="utf-8") as f:
        f.write(f"[{datetime.now()}]: {action}\n\n")
        f.close()    
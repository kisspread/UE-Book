#!/usr/bin/env python3
"""Monitor xlarge doc generation and notify via Telegram when done."""
import os
import time
import subprocess

TARGET = 85
DOCS_DIR = os.path.expanduser("~/mimo/ue-book/docs/xlarge")
CHECK_INTERVAL = 120  # check every 2 minutes

def count_done():
    if not os.path.isdir(DOCS_DIR):
        return 0
    return len([d for d in os.listdir(DOCS_DIR) 
                if os.path.exists(os.path.join(DOCS_DIR, d, "index.md"))])

def send_telegram(msg):
    subprocess.run(["tg-notify", msg], timeout=30)

def main():
    last_count = 0
    while True:
        done = count_done()
        
        if done > last_count:
            print(f"Progress: {done}/{TARGET}", flush=True)
            last_count = done
        
        if done >= TARGET:
            send_telegram(f"✅ UE5 xlarge 文档全部完成！{done}/{TARGET}")
            print(f"Done! {done}/{TARGET}", flush=True)
            break
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

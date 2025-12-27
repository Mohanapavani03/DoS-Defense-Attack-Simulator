from flask import Flask, request, jsonify
import time, math, psutil
from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import IsolationForest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

app = Flask(__name__)

# ================= LOGGING =================
logging.basicConfig(
    filename="defense.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ================= CONFIG =================
PORT = 5000
RATE_LIMIT = 30
WINDOW = 5
BLOCK_TIME = 3600
RATE_429_THRESHOLD = 3

# ================= DATA =================
ip_requests = defaultdict(deque)
ip_429_count = defaultdict(int)
blocked_ips = {}
blocked_history = []
layer_logs = deque(maxlen=50)
traffic_ips = deque(maxlen=500)
attack_vectors = defaultdict(int)

# ================= ML =================
ml_data = deque(maxlen=50)
ml_model = IsolationForest(contamination=0.3)
ml_trained = False
ml_status = "LEARNING"

# ================= EMAIL =================
ADMIN_EMAIL = "praveentati003@gmail.com"
EMAIL_PASSWORD = "kdet yosq tsoj neoe"   # Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
alert_sent = False

def send_attack_alert():
    msg = MIMEMultipart()
    msg["From"] = ADMIN_EMAIL
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = "🚨 ALERT: DoS Attack Detected"

    body = f"""
SECURITY ALERT 🚨

A Denial-of-Service (DoS) attack has been detected.

Attack Vectors:
{dict(attack_vectors)}

Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

-- Automated Defense System
"""
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(ADMIN_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ EMAIL ALERT SENT")
        logging.critical("ML DETECTED DoS ATTACK – Email Sent")
    except Exception as e:
        logging.error(f"Email error: {e}")

# ================= HELPERS =================
def entropy(values):
    counts = defaultdict(int)
    total = len(values)
    if total == 0:
        return 0
    e = 0
    for v in values:
        counts[v] += 1
    for c in counts.values():
        p = c / total
        e -= p * math.log2(p)
    return e

# ================= ROUTES =================
@app.route("/")
def home():
    ip = request.remote_addr
    now = time.time()

    # -------- VECTOR DETECTION --------
    vector = request.headers.get("X-Attack-Type")
    if vector:
        attack_vectors[vector] += 1
        msg = f"{ip} Vector Detected: {vector}"
        layer_logs.append(msg)
        logging.warning(msg)

    # -------- FIREWALL --------
    if ip in blocked_ips and now < blocked_ips[ip]:
        msg = f"{ip} Firewall Blocked"
        layer_logs.append(msg)
        logging.info(msg)
        return "Blocked", 403

    # -------- RATE LIMITER --------
    ip_requests[ip].append(now)
    while ip_requests[ip] and now - ip_requests[ip][0] > WINDOW:
        ip_requests[ip].popleft()

    if len(ip_requests[ip]) > RATE_LIMIT:
        ip_429_count[ip] += 1
        msg = f"{ip} 429 Too Many Requests"
        layer_logs.append(msg)
        logging.warning(msg)

        if ip_429_count[ip] >= RATE_429_THRESHOLD:
            blocked_ips[ip] = now + BLOCK_TIME
            blocked_history.append({
                "ip": ip,
                "blocked_at": time.strftime("%H:%M:%S"),
                "unblock_at": time.strftime(
                    "%H:%M:%S", time.localtime(now + BLOCK_TIME)
                ),
                "status": "Blocked"
            })
            msg = f"{ip} Auto-Blacklisted"
            layer_logs.append(msg)
            logging.error(msg)

        return "Too Many Requests", 429

    # -------- FEED ML --------
    traffic_ips.append(ip)
    traffic_ips.append(ip + "_atk")

    layer_logs.append(f"{ip} Allowed")
    return "OK", 200

@app.route("/status")
def status():
    global ml_trained, ml_status, alert_sent

    if len(traffic_ips) > 10:
        recent = list(traffic_ips)[-100:]
        rate = len(recent)
        ent = entropy(recent)
        ml_data.append([rate, ent])

        if len(ml_data) >= 5:
            X = np.array(ml_data)

            if not ml_trained:
                ml_model.fit(X)
                ml_trained = True
                ml_status = "NORMAL"
                alert_sent = False
            else:
                pred = ml_model.predict([[rate, ent]])[0]

                if pred == -1 or len(blocked_history) > 0:
                    ml_status = "ATTACK"
                    if not alert_sent:
                        send_attack_alert()
                        alert_sent = True
                else:
                    ml_status = "NORMAL"
                    alert_sent = False

    # 🔑 Force attack if vectors exist
    if len(attack_vectors) > 0:
        ml_status = "ATTACK"

    return jsonify({
        "ml_status": ml_status,
        "blocked_history": blocked_history,
        "defense_logs": list(layer_logs),
        "attack_vectors": dict(attack_vectors),
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent
    })

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

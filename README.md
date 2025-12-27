# 🔐 DoS Defense & Attack Simulator

A real-time **Denial-of-Service (DoS) / DDoS attack simulation and defense system** built using Python, Machine Learning, and a GUI dashboard.  
The project demonstrates how multi-vector attacks can be detected and mitigated using automated defense layers and ML-based anomaly detection.

> ⚠️ This project is strictly for **educational purposes** and runs safely on `localhost`.

---

## 📌 Features

### ⚔️ Attack Simulation
- Multi-vector DoS/DDoS attack simulation
- Botnet-style concurrent attack threads
- Supported attack types:
  - HTTP Flood
  - Burst Traffic
  - Slowloris
  - UDP Flood (simulated)
  - TCP SYN Flood (simulated)

### 🛡️ Defense Mechanisms
- Firewall-based IP blocking
- Rate limiting (HTTP 429 protection)
- Automated IP blacklisting
- Automatic IP unblocking after cooldown period

### 🤖 Machine Learning Detection
- ML-based anomaly detection using **Isolation Forest**
- Traffic feature analysis (rate, entropy, behavior)
- ML states:
  - LEARNING
  - NORMAL
  - ATTACK
- Hybrid detection (Rule-based + ML)

### 🚨 Alerting & Logging
- Automatic email alert when an attack is detected
- Persistent security logging (`defense.log`)
- Logs include:
  - Attack vector detection
  - Firewall blocks
  - Auto-blacklisting events
  - ML attack detection

### 📊 Monitoring & Visualization
- Real-time GUI dashboard
- Live CPU and memory usage graphs
- Attack vector counters
- Blocked IP history
- Defense logs displayed live

### 🖥️ GUI Control
- Two-page GUI:
  - Home page (Project title, logo, controls)
  - Dashboard (Monitoring & analytics)
- GUI-controlled attack execution
- Start/Stop attack without terminal usage

---

## 🏗️ Project Architecture

GUI (Tkinter)
|
v
REST API (/status)
|
v
Defense Server (Flask)
|
+--> Firewall & Rate Limiter
+--> ML Detection Engine
+--> Logging & Email Alerts
|
Attacker Module (Botnet Simulation)
---

## 🧠 Technologies Used

- Python
- Flask
- Tkinter
- Scikit-learn
- NumPy
- Matplotlib
- Psutil
- Requests
- Pillow

---



import tkinter as tk
from tkinter import ttk
import requests
import subprocess
import sys
from collections import deque
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= CONFIG =================
SERVER_URL = "###############" #use your sever url
attack_process = None

# ================= COLORS =================
BG = "#0f172a"
PANEL = "#020617"
TEXT = "#e5e7eb"
BLUE = "#2563eb"
RED = "#dc2626"
GREEN = "#16a34a"
ACCENT = "#38bdf8"

# ================= WINDOW =================
root = tk.Tk()

# ---- Treeview style (FIXES blank tables on Windows) ----
style = ttk.Style()
style.theme_use("default")
style.configure(
    "Treeview",
    background="#020617",
    foreground="#e5e7eb",
    fieldbackground="#020617",
    rowheight=25
)
style.map("Treeview", background=[("selected", "#2563eb")])

root.title("DoS Defense & Attack Simulator")
root.geometry("1100x750")
root.configure(bg=BG)

container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True)
pages = {}

def show_page(name):
    pages[name].tkraise()

# ================= ATTACK CONTROL =================
def start_attack():
    global attack_process
    if attack_process is None:
        try:
            attack_process = subprocess.Popen(
                [sys.executable, "attacker.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("🚨 Attack started")
        except Exception as e:
            print("Failed to start attacker.py:", e)
    show_page("dashboard")

def stop_attack():
    global attack_process
    if attack_process:
        attack_process.terminate()
        attack_process = None
        print("🛑 Attack stopped")
    show_page("dashboard")

# ================= PAGE 1 — HOME =================
home = tk.Frame(container, bg=BG)
home.place(relwidth=1, relheight=1)
pages["home"] = home

tk.Label(
    home,
    text="DoS Defense & Attack Simulator",
    font=("Segoe UI", 28, "bold"),
    fg=TEXT,
    bg=BG
).pack(pady=20)

# ---- LOGO ----
try:
    img = Image.open("logo1.jpg").resize((220, 140))
    logo_img = ImageTk.PhotoImage(img)
    logo = tk.Label(home, image=logo_img, bg=BG)
    logo.image = logo_img
    logo.pack(pady=10)
except:
    tk.Label(
        home,
        text="LOGO\n(Add logo1.jpg)",
        bg=PANEL,
        fg=TEXT,
        width=30,
        height=6
    ).pack(pady=10)

btn_frame = tk.Frame(home, bg=BG)
btn_frame.pack(pady=40)

def styled_btn(text, color, cmd):
    return tk.Button(
        btn_frame,
        text=text,
        font=("Segoe UI", 12, "bold"),
        bg=color,
        fg="white",
        width=18,
        height=2,
        relief="flat",
        command=cmd
    )

styled_btn("▶ Start Server", BLUE,
           lambda: show_page("dashboard")).grid(row=0, column=0, padx=12)

styled_btn("🔴 Start Attack", RED,
           start_attack).grid(row=0, column=1, padx=12)

styled_btn("⏹ Stop Attack", GREEN,
           stop_attack).grid(row=0, column=2, padx=12)

# ================= PAGE 2 — DASHBOARD =================
dashboard = tk.Frame(container, bg=PANEL)
dashboard.place(relwidth=1, relheight=1)
pages["dashboard"] = dashboard

header = tk.Frame(dashboard, bg=PANEL)
header.pack(fill="x", pady=10)

tk.Label(
    header,
    text="Defense Monitoring Dashboard",
    font=("Segoe UI", 20, "bold"),
    fg=TEXT,
    bg=PANEL
).pack(side="left", padx=20)

tk.Button(
    header,
    text="⬅ Back",
    bg="#334155",
    fg=TEXT,
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    command=lambda: show_page("home")
).pack(side="right", padx=20)

ml_label = tk.Label(
    dashboard,
    text="ML Status: ---",
    font=("Segoe UI", 14, "bold"),
    fg=ACCENT,
    bg=PANEL
)
ml_label.pack(pady=5)

# ---- DEFENSE LOGS ----
logs_frame = tk.LabelFrame(
    dashboard,
    text="Defense Logs",
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 12, "bold")
)
logs_frame.pack(fill="x", padx=20, pady=8)

logs = tk.Listbox(
    logs_frame,
    height=6,
    bg=BG,
    fg=TEXT,
    selectbackground=ACCENT,
    relief="flat"
)
logs.pack(fill="x", padx=5, pady=5)

# ---- BLOCKED IP TABLE ----
table_frame = tk.LabelFrame(
    dashboard,
    text="Blocked IPs",
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 12, "bold")
)
table_frame.pack(fill="x", padx=20, pady=8)

table = ttk.Treeview(
    table_frame,
    columns=("IP", "Blocked", "Unblock", "Status"),
    show="headings",
    height=4
)
for c in ("IP", "Blocked", "Unblock", "Status"):
    table.heading(c, text=c)
table.pack(fill="x", padx=5, pady=5)

# ---- ATTACK VECTOR TABLE ----
vector_frame = tk.LabelFrame(
    dashboard,
    text="Attack Vectors (Multi-Vector DDoS)",
    bg=PANEL,
    fg=TEXT,
    font=("Segoe UI", 12, "bold")
)
vector_frame.pack(fill="x", padx=20, pady=8)

vector_table = ttk.Treeview(
    vector_frame,
    columns=("Vector", "Count"),
    show="headings",
    height=4
)
vector_table.heading("Vector", text="Attack Vector")
vector_table.heading("Count", text="Requests")
vector_table.pack(fill="x", padx=5, pady=5)

# ---- CPU / MEMORY GRAPHS ----
cpu_data = deque(maxlen=30)
mem_data = deque(maxlen=30)

fig, ax = plt.subplots(2, 1, figsize=(5, 4))
fig.patch.set_facecolor(PANEL)
for a in ax:
    a.set_facecolor(BG)

canvas = FigureCanvasTkAgg(fig, master=dashboard)
canvas.get_tk_widget().pack(pady=10)

# ================= UPDATE LOOP =================
def update():
    try:
        data = requests.get(f"{SERVER_URL}/status", timeout=1).json()

        # ML STATUS
        ml = data.get("ml_status", "---")
        color = RED if ml == "ATTACK" else GREEN if ml == "NORMAL" else ACCENT
        ml_label.config(text=f"ML Status: {ml}", fg=color)

        # LOGS
        logs.delete(0, tk.END)
        for l in data.get("defense_logs", []):
            logs.insert(tk.END, l)

        # BLOCKED IPS
        table.delete(*table.get_children())
        for r in data.get("blocked_history", []):
            table.insert(
                "",
                tk.END,
                values=(r["ip"], r["blocked_at"], r["unblock_at"], r["status"])
            )

        # ATTACK VECTORS
        vector_table.delete(*vector_table.get_children())
        for v, c in data.get("attack_vectors", {}).items():
            vector_table.insert("", tk.END, values=(v, c))

        # METRICS
        cpu_data.append(data.get("cpu", 0))
        mem_data.append(data.get("memory", 0))

        ax[0].clear()
        ax[1].clear()
        ax[0].plot(cpu_data, color=ACCENT)
        ax[0].set_title("CPU Usage (%)", color=TEXT)
        ax[1].plot(mem_data, color="#facc15")
        ax[1].set_title("Memory Usage (%)", color=TEXT)
        canvas.draw()

        root.update_idletasks()

    except Exception as e:
        print("GUI update error:", e)

    root.after(1000, update)

# ================= START =================
show_page("home")
update()
root.mainloop()


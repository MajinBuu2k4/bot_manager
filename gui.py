import os
import subprocess
import json
import psutil
import threading
import customtkinter as ctk
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem
from tkinter import messagebox

# === Cấu hình ===
CONFIG_PATH = "main_bot.json"
WATCHDOG_PATH = r"C:\Users\Administrator\Desktop\bot_manager\watchdog.py"
ICON_FOLDER = r"C:\Users\Administrator\Desktop\bot_manager\icons"
ICON_DEFAULT = os.path.join(ICON_FOLDER, "icon.ico")
ICON_PAUSED = os.path.join(ICON_FOLDER, "shiba_do.ico")

watchdog_proc = None
watchdog_paused = False
tray_icon = None
bot_widgets = []
watchdog_button = None  # button toggle watchdog

# === Helper ===
def generate_icon(color):
    image = Image.new("RGB", (64, 64), color=color)
    draw = ImageDraw.Draw(image)
    draw.text((10, 20), "Bot", fill="white")
    return image

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["bots"]

def is_bot_running(run_with):
    exe_name = os.path.basename(run_with).lower()
    for proc in psutil.process_iter(["name", "exe"]):
        try:
            if proc.info["exe"] and exe_name in proc.info["exe"].lower():
                return True
        except:
            continue
    return False

# === Bot Control ===
def run_bot(bot):
    try:
        subprocess.Popen([bot["run_with"], bot["path"]], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể chạy bot {bot['name']}:\n{e}")

def kill_bot(bot):
    exe_name = os.path.basename(bot["run_with"]).lower()
    for proc in psutil.process_iter(["pid", "name", "exe"]):
        try:
            if proc.info["exe"] and exe_name in proc.info["exe"].lower():
                proc.kill()
        except:
            continue

def run_all_bots():
    for bot in load_config():
        run_bot(bot)

def kill_all_bots():
    global watchdog_paused
    for bot in load_config():
        kill_bot(bot)
    watchdog_paused = True
    update_tray_icon()

# === Watchdog ===
def start_watchdog():
    global watchdog_proc
    if watchdog_proc is None or watchdog_proc.poll() is not None:
        watchdog_proc = subprocess.Popen(["python", WATCHDOG_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)

def stop_watchdog():
    global watchdog_proc
    if watchdog_proc and watchdog_proc.poll() is None:
        watchdog_proc.kill()

def toggle_watchdog():
    global watchdog_paused
    watchdog_paused = not watchdog_paused
    if watchdog_paused:
        stop_watchdog()
    else:
        start_watchdog()
    update_tray_icon()
    update_watchdog_button()

# === Tray ===
def update_tray_icon():
    if tray_icon:
        try:
            icon_path = ICON_PAUSED if watchdog_paused else ICON_DEFAULT
            tray_icon.icon = Image.open(icon_path)
            tray_icon.update_menu()
        except Exception as e:
            print("❌ Không thể cập nhật tray icon:", e)

def create_tray_icon():
    global tray_icon
    try:
        icon_img = Image.open(ICON_DEFAULT) if os.path.exists(ICON_DEFAULT) else generate_icon("green")
        paused_img = Image.open(ICON_PAUSED) if os.path.exists(ICON_PAUSED) else generate_icon("red")

        def menu():
            return Menu(
                MenuItem("🖥️ Mở GUI", lambda icon, item: show_gui(), default=True),
                MenuItem("🔁 Tạm dừng/Chạy Watchdog", lambda icon, item: toggle_watchdog()),
                MenuItem("💀 Kill tất cả", lambda icon, item: kill_all_bots()),
                MenuItem("❌ Thoát", lambda icon, item: quit_app())
            )

        tray_icon = Icon("BotManager", icon_img, "BotAutoMinecraft", menu())
        tray_icon.icon = paused_img if watchdog_paused else icon_img
        tray_icon.on_activate = lambda icon: show_gui()
        threading.Thread(target=tray_icon.run, daemon=True).start()
    except Exception as e:
        print("❌ Lỗi khởi tạo system tray:", e)

def quit_app():
    global tray_icon
    stop_watchdog()
    kill_all_bots()

    # 🧹 Xóa icon khỏi system tray
    if tray_icon:
        tray_icon.visible = False
        tray_icon.stop()

    os._exit(0)


def show_gui():
    try:
        app.deiconify()
        app.lift()
        app.focus_force()
    except:
        pass

# === GUI ===
def refresh_status():
    bots = load_config()
    for bot, row in zip(bots, bot_widgets):
        running = is_bot_running(bot["run_with"])
        if running:
            row["status"].configure(text="🟢 ONLINE", text_color="#38f56b")
        else:
            row["status"].configure(text="🔴 OFFLINE", text_color="#f55353")
    app.after(5000, refresh_status)

def build_gui():
    global bot_widgets
    bots = load_config()
    for widget in bot_widgets:
        widget["frame"].destroy()
    bot_widgets.clear()

    for bot in bots:
        row = ctk.CTkFrame(master=scroll_frame)
        row.pack(pady=5, padx=15, fill="x")

        name_label = ctk.CTkLabel(row, text=bot["name"], width=140, anchor="w", font=ctk.CTkFont(weight="bold"))
        name_label.pack(side="left", padx=5)

        status_label = ctk.CTkLabel(row, text="⏳", width=120, text_color="gray")
        status_label.pack(side="left", padx=5)

        run_btn = ctk.CTkButton(row, text="▶️ Run", width=80, command=lambda b=bot: run_bot(b))
        run_btn.pack(side="left", padx=5)

        kill_btn = ctk.CTkButton(row, text="❌ Kill", width=80, fg_color="#b30000", hover_color="#ff1a1a", command=lambda b=bot: kill_bot(b))
        kill_btn.pack(side="left", padx=5)

        bot_widgets.append({"frame": row, "status": status_label})

def update_watchdog_button():
    if watchdog_button:
        if watchdog_paused:
            watchdog_button.configure(
                text="▶️ Tiếp tục",
                fg_color="#43A047",  # xanh lá
                hover_color="#2E7D32"
            )
        else:
            watchdog_button.configure(
                text="⏸ Tạm dừng",
                fg_color="#FFA726",  # cam
                hover_color="#FB8C00"
            )


# === Giao diện CustomTkinter ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("🐾 Bot Manager GUI")
app.geometry("650x520")
app.iconbitmap(ICON_DEFAULT)

ctk.CTkLabel(app, text="📋 Quản lý Bot Minecraft", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

scroll_frame = ctk.CTkScrollableFrame(app, width=620, height=350)
scroll_frame.pack(pady=10, padx=10)

btn_frame = ctk.CTkFrame(app)
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="▶️ Chạy tất cả", width=140, command=run_all_bots).pack(side="left", padx=10)
ctk.CTkButton(btn_frame, text="💀 Kill tất cả", width=140, fg_color="#b30000", hover_color="#ff1a1a", command=kill_all_bots).pack(side="left", padx=10)
watchdog_button = ctk.CTkButton(btn_frame, width=200, command=toggle_watchdog)
watchdog_button.pack(side="left", padx=10)
update_watchdog_button()


# === Khởi động ===
build_gui()
refresh_status()
start_watchdog()
create_tray_icon()

# Bấm [X] thì ẩn xuống tray
app.protocol("WM_DELETE_WINDOW", lambda: app.withdraw())

# Chạy GUI
app.mainloop()

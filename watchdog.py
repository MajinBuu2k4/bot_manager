import os
import subprocess
import time
import json
import psutil
import threading
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init
from pystray import Icon, Menu, MenuItem
from PIL import Image

init(autoreset=True)

CONFIG_PATH = "main_bot.json"
CHECK_INTERVAL = 30
LOG_TIMEOUT = 30
ACCEPTED_STATUS = "ALIVE-INGAME"
WATCHDOG_LOG_FILE = "watchdog-status.log"
CLEAR_LOG_INTERVAL = 3600

ICON_PATH = "icons/cool.ico"  # thay đường dẫn phù hợp với bạn

# === Tray Icon ===
tray_icon = None
watchdog_thread = None
is_running = True


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    try:
        with open(WATCHDOG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except Exception as e:
        print(f"❌ Ghi log thất bại: {e}")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["bots"]


def get_log_path(bot_name):
    return Path(f"logs/{bot_name}.log")


def is_bot_running(run_with):
    exe_name = os.path.basename(run_with).lower()
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['name'].lower() == exe_name or (proc.info['exe'] and run_with.lower() in proc.info['exe'].lower()):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def read_last_log(log_path):
    if not log_path.exists():
        return None, float('inf')
    try:
        mtime = log_path.stat().st_mtime
        seconds_ago = time.time() - mtime
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_line = lines[-1].strip() if lines else None
        return last_line, seconds_ago
    except Exception as e:
        log(f"❌ Lỗi đọc log: {e}")
        return None, float('inf')


def restart_bot(bot):
    name = bot["name"]
    run_with = bot["run_with"]
    path = bot["path"]

    proc = is_bot_running(run_with)
    if proc:
        try:
            log(f"🛑 [{name}] Dừng tiến trình cũ (PID: {proc.pid})")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                log(f"⚠️ [{name}] timeout → kill")
                proc.kill()
                proc.wait(timeout=5)
        except Exception as e:
            log(f"❌ [{name}] Lỗi khi kill: {e}")

    for _ in range(10):
        if not is_bot_running(run_with):
            break
        time.sleep(1)
    else:
        log(f"❌ [{name}] Không kill được process → BỎ restart")
        return

    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 6  # SW_MINIMIZE

        subprocess.Popen(
            [run_with, path],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        log(f"🚀 [{name}] Đã chạy lại bot.")
    except Exception as e:
        log(f"❌ [{name}] Lỗi khi chạy lại: {e}")


def check_bot(bot):
    name = bot["name"]
    run_with = bot["run_with"]
    log_path = get_log_path(name)

    proc = is_bot_running(run_with)
    last_log, seconds_ago = read_last_log(log_path)

    if not proc:
        log(f"❌ [{name}] Không chạy → restart")
        restart_bot(bot)
        return

    if seconds_ago > LOG_TIMEOUT:
        log(f"⏰ [{name}] Log cũ ({int(seconds_ago)}s) → restart")
        restart_bot(bot)
        return

    if last_log and ACCEPTED_STATUS not in last_log:
        log(f"⚠️ [{name}] Trạng thái lỗi ({last_log}) → restart")
        restart_bot(bot)
        return

    print(Fore.GREEN + f"✅ [{name}] OK ({int(seconds_ago)}s, trạng thái: {last_log})")


def watchdog_loop():
    Path("logs").mkdir(exist_ok=True)
    log("🚀 Watchdog bắt đầu...")
    last_log_clear_time = time.time()

    while is_running:
        try:
            bots = load_config()
            print(Style.BRIGHT + f"\n== 🕒 Kiểm tra {len(bots)} bot ==")
            for bot in bots:
                check_bot(bot)

            if time.time() - last_log_clear_time >= CLEAR_LOG_INTERVAL:
                if os.path.exists(WATCHDOG_LOG_FILE):
                    try:
                        os.remove(WATCHDOG_LOG_FILE)
                        print("🧹 Đã xóa watchdog-status.log (1h).")
                    except Exception as e:
                        print(f"❌ Không thể xóa log: {e}")
                last_log_clear_time = time.time()

        except Exception as e:
            log(f"❌ Lỗi hệ thống: {e}")

        time.sleep(CHECK_INTERVAL)


# ==== TRAY ICON ====

def open_log(_=None):
    os.system(f'start notepad "{WATCHDOG_LOG_FILE}"')


def exit_watchdog(_=None):
    global is_running
    is_running = False
    if tray_icon:
        tray_icon.visible = False
        tray_icon.stop()
    os._exit(0)


def create_tray_icon():
    global tray_icon
    try:
        icon_img = Image.open(ICON_PATH)
    except:
        icon_img = Image.new("RGB", (64, 64), "gray")

    tray_icon = Icon("Watchdog", icon_img, "Watchdog", menu=Menu(
        MenuItem("📄 Xem log", open_log),
        MenuItem("❌ Thoát", exit_watchdog)
    ))

    threading.Thread(target=tray_icon.run, daemon=True).start()


# ==== STARTUP ====
if __name__ == "__main__":
    create_tray_icon()
    watchdog_thread = threading.Thread(target=watchdog_loop, daemon=True)
    watchdog_thread.start()
    while True:
        time.sleep(1)

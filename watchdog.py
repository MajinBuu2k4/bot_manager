import os
import subprocess
import time
import json
import psutil
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

CONFIG_PATH = "main_bot.json"
CHECK_INTERVAL = 30  # seconds
LOG_TIMEOUT = 30     # seconds
ACCEPTED_STATUS = "ALIVE-INGAME"
WATCHDOG_LOG_FILE = "watchdog-status.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# 🧹 XÓA log ngay khi khởi động, không cần kiểm tra dung lượng
if os.path.exists(WATCHDOG_LOG_FILE):
    try:
        os.remove(WATCHDOG_LOG_FILE)
        print("🧹 Đã xóa watchdog-status.log khi khởi động.")
    except Exception as e:
        print(f"❌ Không thể xóa watchdog-status.log: {e}")

def log(msg):
    # Xóa log nếu vượt 10MB
    if os.path.exists(WATCHDOG_LOG_FILE) and os.path.getsize(WATCHDOG_LOG_FILE) > MAX_LOG_SIZE:
        try:
            os.remove(WATCHDOG_LOG_FILE)
            print("🧹 Đã xóa watchdog-status.log vì vượt quá 10MB.")
        except Exception as e:
            print(f"❌ Không thể xóa watchdog log: {e}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    with open(WATCHDOG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

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
            log(f"🛑 [{name}] Đang dừng process cũ (PID: {proc.pid})")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                log(f"⚠️ [{name}] terminate timeout → kill")
                proc.kill()
                proc.wait(timeout=5)
        except Exception as e:
            log(f"❌ [{name}] Lỗi khi kill tiến trình: {e}")

    # Đảm bảo tiến trình đã chết
    for _ in range(10):
        if not is_bot_running(run_with):
            break
        time.sleep(1)
    else:
        log(f"❌ [{name}] Process vẫn chưa chết sau timeout → BỎ restart!")
        return

    try:
        subprocess.Popen([run_with, path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        log(f"🚀 [{name}] Đã chạy lại bot.")
    except Exception as e:
        log(f"❌ [{name}] Lỗi khi chạy lại bot: {e}")

def check_bot(bot):
    name = bot["name"]
    run_with = bot["run_with"]
    log_path = get_log_path(name)

    proc = is_bot_running(run_with)
    last_log, seconds_ago = read_last_log(log_path)

    if not proc:
        log(f"❌ [{name}] Không chạy → khởi động lại")
        restart_bot(bot)
        return

    if seconds_ago > LOG_TIMEOUT:
        log(f"⏰ [{name}] Log quá cũ ({int(seconds_ago)}s) → restart")
        restart_bot(bot)
        return

    if last_log and ACCEPTED_STATUS not in last_log:
        log(f"⚠️ [{name}] Trạng thái không ổn ({last_log}) → restart")
        restart_bot(bot)
        return

    print(Fore.GREEN + f"✅ [{name}] OK ({int(seconds_ago)}s trước, trạng thái: {last_log})")

def main():
    Path("logs").mkdir(exist_ok=True)
    log("🚀 Watchdog bắt đầu...")

    while True:
        try:
            bots = load_config()
            print(Style.BRIGHT + f"\n== 🕒 Kiểm tra {len(bots)} bot ==")
            for bot in bots:
                check_bot(bot)
        except Exception as e:
            log(f"❌ Lỗi hệ thống: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

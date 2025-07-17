import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog

JSON_PATH = r"C:\Users\Administrator\Desktop\bot_manager\main_bot.json"

def load_bots():
    if not os.path.exists(JSON_PATH):
        return {"bots": []}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_bots(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def bot_exists(bots, name):
    return any(bot["name"].lower() == name.lower() for bot in bots)

def browse_file(entry_widget):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path.replace("\\", "/"))

def add_bot_gui():
    name = entry_name.get().strip()
    path = entry_path.get().strip()
    run_with = entry_runwith.get().strip()

    if not name or not path or not run_with:
        messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ các trường.")
        return

    data = load_bots()
    bots = data["bots"]

    if bot_exists(bots, name):
        messagebox.showwarning("Trùng tên", f"Bot với tên '{name}' đã tồn tại.")
        return

    bots.append({
        "name": name,
        "path": path,
        "run_with": run_with
    })

    save_bots(data)
    entry_name.delete(0, tk.END)
    entry_path.delete(0, tk.END)
    entry_runwith.delete(0, tk.END)

# === GUI ===
root = tk.Tk()
root.title("🧠 Thêm Bot Vào JSON")
root.geometry("500x300")
root.resizable(False, False)

# Tên Bot
tk.Label(root, text="Tên bot:").pack(pady=5)
entry_name = tk.Entry(root, width=60)
entry_name.pack()

# Đường dẫn JS
tk.Label(root, text="Đường dẫn đến file .js:").pack(pady=5)
frame_path = tk.Frame(root)
entry_path = tk.Entry(frame_path, width=48)
entry_path.pack(side=tk.LEFT)
tk.Button(frame_path, text="Chọn...", command=lambda: browse_file(entry_path)).pack(side=tk.LEFT, padx=5)
frame_path.pack()

# Đường dẫn EXE
tk.Label(root, text="Đường dẫn file .exe (run_with):").pack(pady=5)
frame_runwith = tk.Frame(root)
entry_runwith = tk.Entry(frame_runwith, width=48)
entry_runwith.pack(side=tk.LEFT)
tk.Button(frame_runwith, text="Chọn...", command=lambda: browse_file(entry_runwith)).pack(side=tk.LEFT, padx=5)
frame_runwith.pack()

# Nút thêm bot
tk.Button(root, text="➕ Thêm bot", command=add_bot_gui, bg="#4CAF50", fg="white", height=2).pack(pady=20)

root.mainloop()

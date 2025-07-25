import json
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

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

def get_bot_name_from_path(file_path):
    if file_path:
        base_name = os.path.basename(file_path)
        name_without_extension = os.path.splitext(base_name)[0]
        return name_without_extension
    return ""

def browse_file(entry_widget, is_js_path=False):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path.replace("\\", "/"))

        if is_js_path and not entry_name.get().strip():
            bot_name = get_bot_name_from_path(file_path)
            entry_name.delete(0, tk.END)
            entry_name.insert(0, bot_name)

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

def drop(event, entry_widget, is_js_path=False):
    file_path = event.data
    if file_path.startswith('{') and file_path.endswith('}'):
        file_path = file_path[1:-1]

    if ' ' in file_path and not file_path.startswith('{'):
        file_path = file_path.split(' ')[0]

    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path.replace("\\", "/"))

    if is_js_path and not entry_name.get().strip():
        bot_name = get_bot_name_from_path(file_path)
        entry_name.delete(0, tk.END)
        entry_name.insert(0, bot_name)
    elif not is_js_path and not entry_name.get().strip():
        bot_name = get_bot_name_from_path(file_path)
        entry_name.delete(0, tk.END)
        entry_name.insert(0, bot_name)

# === GUI ===
root = TkinterDnD.Tk()
root.title("🧠 Thêm Bot Vào JSON")
root.geometry("700x500") # Tăng kích thước ban đầu để có nhiều không gian hơn
root.resizable(True, True) # Cho phép thay đổi kích thước cửa sổ

# Cấu hình grid cho cửa sổ chính
root.grid_rowconfigure(0, weight=0) # Hàng label tên bot không co giãn
root.grid_rowconfigure(1, weight=0) # Hàng entry tên bot không co giãn
root.grid_rowconfigure(2, weight=1) # Hàng label JS co giãn để đẩy xuống
root.grid_rowconfigure(3, weight=3) # Hàng entry JS co giãn nhiều
root.grid_rowconfigure(4, weight=1) # Hàng label EXE co giãn để đẩy xuống
root.grid_rowconfigure(5, weight=3) # Hàng entry EXE co giãn nhiều
root.grid_rowconfigure(6, weight=0) # Hàng nút không co giãn

root.grid_columnconfigure(0, weight=1) # Cột duy nhất (hoặc cột đầu tiên) co giãn

# Định nghĩa font chữ cho các Entry
MEDIUM_FONT = ("Arial", 14) # Kích thước font phù hợp để chiếm nhiều không gian hơn
LARGE_FONT_ENTRY = ("Arial", 16) # Kích thước font lớn hơn cho các ô kéo thả

# Tên Bot
tk.Label(root, text="Tên bot:").grid(row=0, column=0, pady=5)
entry_name = tk.Entry(root, width=40, font=MEDIUM_FONT, justify='center') # Căn giữa chữ
entry_name.grid(row=1, column=0, pady=5, ipadx=10, ipady=10, sticky="ew", padx=50) # sticky="ew" để kéo giãn theo chiều ngang, padx để giới hạn độ rộng

# Đường dẫn JS (Khuôn 1)
tk.Label(root, text="Đường dẫn đến file .js: Kéo & Thả vào đây").grid(row=2, column=0, pady=5)
entry_path = tk.Entry(root, font=LARGE_FONT_ENTRY)
entry_path.grid(row=3, column=0, pady=5, ipadx=10, ipady=30, sticky="nsew", padx=20) # sticky="nsew" để kéo giãn mọi hướng
entry_path.drop_target_register(DND_FILES)
entry_path.dnd_bind('<<Drop>>', lambda event: drop(event, entry_path, is_js_path=True))

# Thêm nút "Chọn..." cho JS path vào một Frame riêng để đặt cạnh Entry nếu cần
frame_js_btn = tk.Frame(root)
tk.Button(frame_js_btn, text="Chọn...", command=lambda: browse_file(entry_path, is_js_path=True), height=2).pack(side=tk.LEFT, padx=5)
frame_js_btn.grid(row=3, column=0, sticky="ne", padx=25, pady=5) # Đặt nút ở góc trên bên phải của ô kéo thả

# Đường dẫn EXE (Khuôn 2)
tk.Label(root, text="Đường dẫn file .exe (run_with): Kéo & Thả vào đây").grid(row=4, column=0, pady=5)
entry_runwith = tk.Entry(root, font=LARGE_FONT_ENTRY)
entry_runwith.grid(row=5, column=0, pady=5, ipadx=10, ipady=30, sticky="nsew", padx=20) # sticky="nsew" để kéo giãn mọi hướng
entry_runwith.drop_target_register(DND_FILES)
entry_runwith.dnd_bind('<<Drop>>', lambda event: drop(event, entry_runwith, is_js_path=False))

# Thêm nút "Chọn..." cho EXE path vào một Frame riêng
frame_exe_btn = tk.Frame(root)
tk.Button(frame_exe_btn, text="Chọn...", command=lambda: browse_file(entry_runwith), height=2).pack(side=tk.LEFT, padx=5)
frame_exe_btn.grid(row=5, column=0, sticky="ne", padx=25, pady=5) # Đặt nút ở góc trên bên phải của ô kéo thả

# Nút thêm bot
tk.Button(root, text="➕ Thêm bot", command=add_bot_gui, bg="#4CAF50", fg="white", height=3).grid(row=6, column=0, pady=20)

root.mainloop()
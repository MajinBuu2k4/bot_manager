# ⚙️ Watchdog Bot Minecraft - Tự động giám sát & khởi động lại bot

Công cụ **watchdog.py** giúp bạn tự động theo dõi trạng thái các bot `.js` đang chạy qua `.exe` (đã gán proxy riêng qua Proxifier), và tự động **khởi động lại bot** nếu log quá cũ hoặc không ở trạng thái `ALIVE-INGAME`.

---

# 📁 Cấu trúc thư mục gợi ý

```bash
bot_manager/
├── bots/
│   ├── A1TrumMafia.js
│   └── Vanguard01.js
├── run_with/
│   ├── A1TrumMafia.exe
│   └── Vanguard01.exe
├── logs/
│   ├── A1TrumMafia.log
│   └── Vanguard01.log
├── main_bot.json
├── watchdog.py
└── watchdog-status.log

```

# 📦 1. Cài đặt yêu cầu Python
```bash
pip install psutil colorama
```


# 📄 2. Tạo file cấu hình main_bot.json
```bash
{
  "bots": [
    {
      "name": "A1TrumMafia",
      "path": "C:/Users/Administrator/Desktop/bot_manager/bots/A1TrumMafia.js",
      "run_with": "C:/Users/Administrator/Desktop/bot_manager/run_with/A1TrumMafia.exe"
    },
    {
      "name": "Vanguard01",
      "path": "C:/Users/Administrator/Desktop/bot_manager/bots/Vanguard01.js",
      "run_with": "C:/Users/Administrator/Desktop/bot_manager/run_with/Vanguard01.exe"
    }
  ]
}
```
**✦● ✅ name phải trùng với tên file log logs/{name}.log**


# 🚀 3. Cách sử dụng
```bash
python watchdog.py
```

**✦● Script sẽ kiểm tra trạng thái bot mỗi 30 giây**

### Nếu:

 **✦● File log không tồn tại****

 **✦● Log quá cũ (>30s)****

 **✦● Không chứa "ALIVE-INGAME"****

 **✦● Hoặc process .exe không chạy******

**✴ Thì bot sẽ được tắt (terminate) và chạy lại**


# 📜 4. Quản lý ```watchdog-status.log```

**✦● File watchdog-status.log sẽ ghi toàn bộ trạng thái giám sát**

**✦● Nếu file này vượt 10MB, nó sẽ được tự động xóa và tạo lại**

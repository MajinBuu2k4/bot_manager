const mineflayer = require('mineflayer');
const fs = require('fs');
const path = require('path');

const USERNAME = '111mrlonely';
const SERVER_HOST = 'mc.luckyvn.com';
const MINECRAFT_VERSION = '1.18.2';
const LOG_DIR = 'C:/Users/Administrator/Desktop/bot_manager/logs';
const LOG_FILE = path.join(LOG_DIR, `${USERNAME}.log`);
const MAX_RECONNECT_ATTEMPTS = 10;

let bot;
let checkClockInterval;
let logInterval;
let reconnectAttempts = 0;
let loggedIn = false;
let menuOpened = false;
let inGame = false;

if (!fs.existsSync(LOG_DIR)) fs.mkdirSync(LOG_DIR, { recursive: true });

logInterval = setInterval(() => {
  try {
    let state = 'ALIVE';
    if (inGame) state = 'ALIVE-INGAME';
    else if (menuOpened) state = 'ALIVE-MENU';
    else if (loggedIn) state = 'ALIVE-LOBBY';
    fs.writeFileSync(LOG_FILE, `${state} ${new Date().toISOString()}`);
  } catch (err) {
    console.error("❗ Không thể ghi log:", err.message);
  }
}, 5000);

function createBot() {
  loggedIn = false;
  menuOpened = false;
  inGame = false;

  bot = mineflayer.createBot({
    host: SERVER_HOST,
    username: USERNAME,
    version: MINECRAFT_VERSION,
    viewDistance: 'tiny',
  });

  bot.once('spawn', () => {
    reconnectAttempts = 0;
    console.log("🟢 Bot đã vào game, chờ login...");

    bot.on('physicTick', () => {
      for (const id in bot.entities) delete bot.entities[id];
    });

    checkClockInterval = setInterval(() => {
      if (loggedIn && !menuOpened) {
        const slot4 = bot.inventory.slots[36 + 4];
        if (slot4?.name === 'minecraft:clock') {
          bot.setQuickBarSlot(4);
          bot.activateItem();
        }
      }
    }, 10000);
  });

  bot.on('message', (message) => {
    const msg = message.toString();

    if (msg.includes(USERNAME + ':')) {
      console.log(msg);
    }

    if (msg.includes('/login') && !loggedIn) {
      bot.chat('/login Phuc2005');
      loggedIn = true;
      console.log("🔐 Đã gửi lệnh /login");
    }

    if (msg.includes('Đăng nhập thành công') && !menuOpened) {
      setTimeout(() => {
        console.log("🕹 Dùng đồng hồ mở menu chọn chế độ");
        bot.setQuickBarSlot(4);
        bot.activateItem();
      }, 1000);
    }

    if (msg.includes('Bạn đã mở bảng chọn máy chủ!') && !menuOpened) {
      menuOpened = true;
      console.log("📥 Menu mở, chuẩn bị click slot 22 và 34");
      setTimeout(() => bot.clickWindow(22, 0, 0), 1000);
      setTimeout(() => {
        bot.clickWindow(34, 0, 0);
        console.log("🎮 Đã chọn máy chủ, chờ vào In-Game...");
      }, 2500);
    }

    if (msg.includes(`${USERNAME} Đã tham gia máy chủ!`)) {
      inGame = true;
      console.log("✅ Bot đã vào In-Game!");
    }

    const autoChaoRegex = /Chào mừng \[ (.*?) ] lần đầu tiên đến/;
    const chaoMatch = msg.match(autoChaoRegex);
    if (chaoMatch && chaoMatch[1]) {
      const playerName = chaoMatch[1];
      bot.chat(`Xin chào bạn ${playerName}`);
      console.log(`👋 Đã chào người chơi mới: ${playerName}`);
    }
  });

  bot.on('respawn', () => {
    menuOpened = false;
    inGame = false;
    console.log('♻️ Reset trạng thái menu và inGame khi vào sảnh');

    setTimeout(() => {
      const clockSlot = bot.inventory.slots[36 + 4];
      if (clockSlot?.name.includes('clock')) {
        bot.setQuickBarSlot(4);
        console.log('🔁 Cầm lại đồng hồ sau khi vào sảnh');
      }
    }, 2000);
  });

  bot.on('end', () => {
    clearInterval(checkClockInterval);
    clearInterval(logInterval);
    reconnectAttempts++;
    console.log(`❌ Mất kết nối (lần thử ${reconnectAttempts}/10)`);

    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.log("🛑 Quá số lần reconnect, dừng bot");
      return process.exit(1);
    }

    const delay = Math.min(reconnectAttempts, 10) * 5000;
    console.log(`⌛ Thử kết nối lại sau ${delay / 1000}s...`);
    setTimeout(safeCreateBot, delay);
  });

  bot.on('kicked', (reason) => {
    clearInterval(checkClockInterval);
    clearInterval(logInterval);
    console.log("❌ Bị kick:", reason);

    if (reason.includes("đang kết nối") || reason.includes("already connected")) {
      console.log("⚠️ Lỗi session, đợi 20s rồi thử lại...");
      setTimeout(() => {
        reconnectAttempts = 0;
        safeCreateBot();
      }, 20000);
    } else {
      reconnect();
    }
  });

  bot.on('error', err => console.log("⚠️ Lỗi:", err.message));
}

function reconnect() {
  console.log("♻️ Reconnect sau 5s...");
  setTimeout(safeCreateBot, 5000);
}

function safeCreateBot() {
  try {
    createBot();
  } catch (err) {
    console.error("❗ Lỗi tạo bot:", err.message);
    setTimeout(safeCreateBot, 5000);
  }
}

safeCreateBot();
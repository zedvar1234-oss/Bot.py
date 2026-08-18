from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions, types
import asyncio
import sqlite3
import re
import time

api_id = 37168409
api_hash = "27854002f7d0883cb2ca54a2543f4386"
ADMIN_ID = 8865904939

TOKENS = [
    "8779025407:AAF_ALForH5vtiTMrayAbOUAVR8n2RoEszQ",
    "8907359672:AAFbLyO2FZ5liET9Jh0gt-Xnw-KVyMkhEz4",
    "8982991369:AAFwJ0ihsCekA5RjYT5iGeCzim2YM5HXqw4",
    "8817905346:AAHq18L3i_pLWZiWb9Y1zSqt1BCM2WKTPTU",
    "8699779753:AAFj9G7QfjY2ji-QqDcZ3nJ7ES7h1zbLDe4",
    "8743699134:AAHS7agowe4tiNHxqqF7-MtnB0t08NgAwz0",
    "8851315198:AAHRhRQRWrN-WjJfP9axi6K_YhN_hf6bUuE",
    "8932800122:AAHqT8AfhYY1rX1bnWoOt3ID5FlEqDRmNPg",
    "8903178323:AAE-KsbRa2j6f_Y1sgFyuvRCkRQbyeD38uc",
    "8796037543:AAEf-2C4D2N_YBk4S1NaZOweeY3h48cif5s"
]

attack_active = set()
target_users_list = {}
attack_delay = {}
admin_states = {}
reply_target_list = {}
mention_custom_texts = {}

def get_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS attack_texts (text TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    return conn, cur

def is_authorized(_, __, m):
    if m.from_user and m.from_user.id == ADMIN_ID: return True
    if not m.from_user: return False
    conn, cursor = get_db()
    res = cursor.execute("SELECT 1 FROM users WHERE user_id=?", (m.from_user.id,)).fetchone()
    conn.close()
    return res is not None

auth_filter = filters.create(is_authorized)

async def run_attack(c, chat_id):
    while chat_id in attack_active:
        conn, cursor = get_db()
        texts = [r[0] for r in cursor.execute("SELECT text FROM attack_texts").fetchall()]
        conn.close()
        for t in texts:
            if chat_id not in attack_active: break
            
            mentions_list = []
            for uid, name in target_users_list.get(chat_id, {}).items():
                display_name = mention_custom_texts.get(chat_id, name)
                mentions_list.append(f"[{display_name}](tg://user?id={uid})")
            mentions = " ".join(mentions_list)
            
            final_text = f"{t}\n{mentions}" if mentions else t
            reply_to = reply_target_list.get(chat_id)
            
            try:
                if reply_to:
                    await c.send_message(chat_id, final_text, reply_to_message_id=reply_to)
                else:
                    await c.send_message(chat_id, final_text)
            except:
                break
            
            await asyncio.sleep(attack_delay.get(chat_id, 2))
        await asyncio.sleep(1)

async def start_bot(token):
    try:
        app = Client(f"bot_{token[:10]}", api_id=api_id, api_hash=api_hash, bot_token=token, workers=1)

        @app.on_message(filters.text & auth_filter)
        async def main_handler(c, m):
            text_lower = m.text.lower() if m.text else ""
            text_raw = m.text if m.text else ""
            
            if text_lower == "panel":
                txt = ("≫ ATTACKER LEDERAF ≪\n\n"
                       "◤ پنل های مدیریت ربات ◥\n\n"
                       "📌 panel1 :\nدستورات حمله، استوپ، تنظیم ثانیه، منشن کاربر، تنظیم ظاهر منشن، حذف منشن، تنظیم ریپلای، حذف ریپلای، تنظیمات فحش و لیست فحش‌ها\n\n"
                       "📌 panel2 :\nوضعیت ربات، پینگ، کنترل دسترسی کاربران (افزودن و حذف) و لیست کاربران مجاز\n\n"
                       "📌 panel3 :\nتنظیم تصویر پروفایل، تغییر نام و تغییر بیوگرافی ربات\n\n"
                       "▬▭▬▭\nبرای ورود به هر پنل، نام آن را ارسال کنید (مثلا panel1)")
                await m.reply(txt)

            elif text_lower == "panel1":
                txt = ("≫ ATTACKER LEDERAF - PANEL 1 ≪\n\n"
                       "◤ سیستم حملات ◥\nattack : شروع حمله\nstop : متوقف کردن حمله\nmin (1-10) : تنظیم ثانیه\n▬▭▬▭\n"
                       "◤ سیستم منشن و ریپلای ◥\nmonshen : منشن کاربر ریپلای شده\ndilmon : پاکسازی همه منشن‌ها\nmon (متن/ایموجی) : تنظیم ظاهر منشن\nno mon : حذف ظاهر منشن\nsetrip : تنظیم ریپلای روی پیام\ndilrip : حذف ریپلای\n▬▭▬▭\n"
                       "◤ تنظیمات فحش ◥\nfosh (متن) : افزودن متن به لیست فحش‌ها\ndilfosh : پاکسازی فحش‌ها\nfoshlis : نمایش لیست فحش‌ها")
                await m.reply(txt)

            elif text_lower == "panel2":
                txt = ("≫ ATTACKER LEDERAF - PANEL 2 ≪\n\n"
                       "◤ کنترل و دسترسی ◥\nadd (ایدی) : افزودن دسترسی کاربر\nnoadd (ایدی) : حذف دسترسی کاربر\nlist : لیست کاربران مجاز\n▬▭▬▭\n"
                       "◤ سایر دستورات ◥\nbot : وضعیت ربات\nping : پینگ ربات")
                await m.reply(txt)

            elif text_lower == "panel3":
                txt = ("≫ ATTACKER LEDERAF - PANEL 3 ≪\n\n"
                       "◤ تنظیمات پروفایل و هویت ربات ◥\nsetprof : ریپلای روی عکس برای تنظیم پروفایل ربات\nname (متن) : تغییر نام ربات\nbio (متن) : تغییر بیوگرافی ربات")
                await m.reply(txt)

            elif text_lower == "list":
                conn, cursor = get_db()
                users = cursor.execute("SELECT user_id FROM users").fetchall()
                conn.close()
                if not users: 
                    bot_msg = await m.reply("لیست خالی است.")
                    admin_states[m.chat.id] = {"type": "list_empty", "msg_id": bot_msg.id}
                    return
                
                user_lines = []
                for i, u in enumerate(users):
                    uid = u[0]
                    try:
                        user_obj = await c.get_users(uid)
                        name = user_obj.first_name if user_obj else "User"
                    except:
                        name = "User"
                    user_lines.append(f"{i+1}. [{name}](tg://user?id={uid})")
                
                res = "لیست کاربران مجاز:\n" + "\n".join(user_lines)
                res += "\nبرای حذف، روی پیام کاربر ریپلای کنید یا شماره بفرستید، یا بنویسید برگشت."
                bot_msg = await m.reply(res)
                admin_states[m.chat.id] = {"type": "list", "users": [u[0] for u in users], "msg_id": bot_msg.id}

            elif text_lower == "برگشت":
                state = admin_states.get(m.chat.id)
                if state and isinstance(state, dict):
                    msg_id = state.get("msg_id")
                    if msg_id:
                        try:
                            await c.delete_messages(m.chat.id, msg_id)
                        except:
                            pass
                admin_states.pop(m.chat.id, None)
                await m.reply("عملیات لغو شد✅")

            elif m.chat.id in admin_states and isinstance(admin_states[m.chat.id], dict) and admin_states[m.chat.id].get("type") == "list":
                state = admin_states[m.chat.id]
                uid_to_delete = None
                
                if m.reply_to_message and m.reply_to_message.from_user:
                    uid_to_delete = m.reply_to_message.from_user.id
                elif text_lower.isdigit():
                    idx = int(text_lower) - 1
                    users_list = state.get("users", [])
                    if 0 <= idx < len(users_list):
                        uid_to_delete = users_list[idx]
                
                if uid_to_delete:
                    conn, cursor = get_db()
                    cursor.execute("DELETE FROM users WHERE user_id=?", (uid_to_delete,))
                    conn.commit()
                    conn.close()
                    
                    list_msg_id = state.get("msg_id")
                    admin_states.pop(m.chat.id, None)
                    await m.reply("کاربر حذف شد✅")
                    try:
                        if list_msg_id:
                            await c.delete_messages(m.chat.id, list_msg_id)
                    except:
                        pass
                else:
                    await m.reply("نامعتبر یا کاربر یافت نشد.")

            elif text_lower.startswith("min "):
                try:
                    val = int(text_raw.split()[1])
                    if 1 <= val <= 10: 
                        attack_delay[m.chat.id] = val
                        await m.reply(f"تنظیم روی {val} ثانیه✅")
                except:
                    pass

            elif text_lower == "monshen" and m.reply_to_message and m.reply_to_message.from_user:
                if m.chat.id not in target_users_list: target_users_list[m.chat.id] = {}
                target_users_list[m.chat.id][m.reply_to_message.from_user.id] = m.reply_to_message.from_user.first_name or "User"
                await m.reply("✅")

            elif text_lower == "dilmon": 
                target_users_list[m.chat.id] = {}
                mention_custom_texts.pop(m.chat.id, None)
                await m.reply("✅")

            elif text_lower.startswith("mon "):
                parts = text_raw.split(maxsplit=1)
                if len(parts) > 1:
                    custom_val = parts[1]
                    mention_custom_texts[m.chat.id] = custom_val
                    await m.reply(f"تنظیم ظاهر منشن به: {custom_val}✅")

            elif text_lower == "no mon":
                mention_custom_texts.pop(m.chat.id, None)
                await m.reply("ظاهر منشن به حالت پیش‌فرض برگشت✅")

            elif text_lower == "setrip":
                if m.reply_to_message:
                    reply_target_list[m.chat.id] = m.reply_to_message.id
                    await m.reply("✅")
                else:
                    await m.reply("لطفاً روی پیام مورد نظر ریپلای کنید.")

            elif text_lower == "dilrip":
                reply_target_list.pop(m.chat.id, None)
                await m.reply("✅")

            elif text_lower == "setprof":
                if m.reply_to_message and m.reply_to_message.photo:
                    try:
                        photo_path = await m.reply_to_message.download()
                        uploaded_file = await c.save_file(photo_path)
                        await c.invoke(
                            functions.photos.UploadProfilePhoto(
                                file=uploaded_file
                            )
                        )
                        await m.reply("تصویر پروفایل ربات با موفقیت تغییر کرد✅")
                    except Exception as e:
                        await m.reply(f"خطا در تغییر پروفایل: {e}")
                else:
                    await m.reply("لطفاً روی یک عکس ریپلای کنید و دستور setprof را بفرستید.")

            elif text_lower.startswith("bio "):
                parts = text_raw.split(maxsplit=1)
                if len(parts) > 1:
                    new_bio = parts[1]
                    try:
                        # استفاده از متد سازگار Bot API برای تغییر بیوگرافی ربات
                        await c.set_bot_description(new_bio)
                        await m.reply("بیوگرافی ربات با موفقیت تغییر کرد✅")
                    except Exception as e:
                        await m.reply(f"خطا در تغییر بیوگرافی: {e}")

            elif text_lower.startswith("name "):
                parts = text_raw.split(maxsplit=1)
                if len(parts) > 1:
                    new_name = parts[1]
                    try:
                        # استفاده از متد سازگار Bot API برای تغییر نام ربات
                        await c.set_bot_name(new_name)
                        await m.reply("نام ربات با موفقیت تغییر کرد✅")
                    except Exception as e:
                        await m.reply(f"خطا در تغییر نام: {e}")

            elif text_lower.startswith("fosh "):
                parts = text_raw.split(maxsplit=1)
                if len(parts) > 1:
                    conn, cursor = get_db()
                    cursor.execute("INSERT INTO attack_texts VALUES (?)", (parts[1],))
                    conn.commit(); conn.close()
                    await m.reply("✅")

            elif text_lower == "dilfosh":
                conn, cursor = get_db()
                cursor.execute("DELETE FROM attack_texts")
                conn.commit(); conn.close()
                await m.reply("✅")

            elif text_lower == "foshlis":
                conn, cursor = get_db()
                texts = cursor.execute("SELECT text FROM attack_texts").fetchall()
                conn.close()
                await m.reply("\n".join([t[0] for t in texts]) if texts else "Empty")

            elif text_lower.startswith("add "):
                parts = text_raw.split()
                if len(parts) > 1 and parts[1].isdigit():
                    conn, cursor = get_db()
                    cursor.execute("INSERT OR IGNORE INTO users VALUES (?)", (int(parts[1]),))
                    conn.commit(); conn.close()
                    await m.reply("✅")

            elif text_lower.startswith("noadd "):
                parts = text_raw.split()
                if len(parts) > 1 and parts[1].isdigit():
                    conn, cursor = get_db()
                    cursor.execute("DELETE FROM users WHERE user_id=?", (int(parts[1]),))
                    conn.commit(); conn.close()
                    await m.reply("✅")

            elif text_lower == "attack":
                attack_active.add(m.chat.id)
                asyncio.create_task(run_attack(c, m.chat.id))
                await m.reply("Started!")

            elif text_lower == "stop": 
                attack_active.discard(m.chat.id)
                await m.reply("Stopped!")

            elif text_lower == "bot": 
                await m.reply("Bot Tosipher online.⚡")

            elif text_lower == "ping":
                s = time.perf_counter()
                msg = await m.reply("Pinging...")
                e = time.perf_counter()
                await msg.edit_text(f"Pong! {round((e - s) * 1000, 2)} ms")

        await app.start()
        print(f"✅ Bot {token[:10]} is online.")
    except Exception as e: print(f"❌ Error in Bot {token[:10]}: {e}")

async def main():
    await asyncio.gather(*(start_bot(token) for token in TOKENS))
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

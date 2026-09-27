import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from pyrogram.errors import UserIsBlocked, PeerIdInvalid
from pymongo import MongoClient

# --- CONFIGURATION (Environment Variables) ---
API_ID = int(os.environ.get("API_ID", "38253829"))
API_HASH = os.environ.get("API_HASH", "c52cb1c9daa0e95cc3a9fcbc21307621")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8835749290:AAESf-l_JrRPN8jcAl6_-KsSxIL6hGgOM24")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8539758095"))
DB_URL = os.environ.get("DB_URL", "mongodb+srv://mohahmadabdulshaikh_db_user:0Kdq0KQNbg0ogT9k@cluster0.igqvd9d.mongodb.net")
STORAGE_CHANNEL = int(os.environ.get("STORAGE_CHANNEL", "-1003916120794"))

# Start Image Link
START_PHOTO = "https://telegraphoto.online/images/25bfc0a7-7551-40df-a87d-3fcd614b48e5.jpg"

# --- DATABASE SETUP ---
mongo = MongoClient(DB_URL)
db = mongo["disney_file_store"]
users_col = db["users"]
banned_col = db["banned_users"]

# State Management for Conversations
user_states = {}

bot = Client("DisneyPlusFileStore", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Custom Caption and Inline Keyboard for Stored Files
CUSTOM_CAPTION = (
    "[Hindi] [English] @cartoongram24.mkv\n"
    "▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
    "Iғ 🔇 Aᴜᴅɪᴏ ɪssᴜᴇ 👉 Use VLC Player"
)

FILE_INLINE_BTN = InlineKeyboardMarkup([
    [InlineKeyboardButton("Cartoongram24", url="https://t.me/cartoongram24")]
])

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def is_banned(user_id: int) -> bool:
    return banned_col.find_one({"user_id": user_id}) is not None

def add_user(user_id: int):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id})

# --- AUTO-DELETE TASK WITH RE-RETRIEVAL LINK ---
async def auto_delete_messages(client: Client, msgs: list, notice_msg: Message, user_id: int, start_param: str):
    # Wait 5 Minutes (300 seconds)
    await asyncio.sleep(300)
    
    # Delete file messages
    for msg in msgs:
        try:
            await msg.delete()
        except Exception:
            pass
            
    # Delete notice message
    try:
        await notice_msg.delete()
    except Exception:
        pass
        
    # Generate Re-retrieval Link
    bot_info = await client.get_me()
    retrieval_url = f"https://t.me/{bot_info.username}?start={start_param}"
    
    re_retrieve_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("♻️ Cʟɪᴄᴋ Hᴇʀᴇ", url=retrieval_url)]
    ])
    
    msg_text = (
        "Pʀᴇᴠɪᴏᴜs Mᴇssᴀɢᴇ ᴡᴀs Dᴇʟᴇᴛᴇᴅ 🗑\n"
        "Iғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: [♻️ Cʟɪᴄᴋ Hᴇʀᴇ]\n"
        "ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ."
    )
    
    try:
        await client.send_message(
            chat_id=user_id,
            text=f"> {msg_text}",
            reply_markup=re_retrieve_btn
        )
    except Exception:
        pass

# --- /START COMMAND ---
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    
    if is_banned(user_id):
        return await message.reply_text("🛑 You are banned from using this bot.")
        
    add_user(user_id)
    
    # Deep Linking Execution (Retrieving Files)
    if len(message.command) > 1:
        param = message.command[1]
        
        # Batch Retrieval
        if param.startswith("batch_"):
            try:
                start_id, end_id = map(int, param.replace("batch_", "").split("_"))
                msg_ids = list(range(start_id, end_id + 1))
                
                sent_msgs = []
                for m_id in msg_ids:
                    msg = await client.copy_message(
                        chat_id=user_id,
                        from_chat_id=STORAGE_CHANNEL,
                        message_id=m_id,
                        caption=CUSTOM_CAPTION,
                        reply_markup=FILE_INLINE_BTN
                    )
                    sent_msgs.append(msg)
                
                delete_text = (
                    "›› Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 5 Mɪɴᴜᴛᴇs. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ..\n"
                    "≡ ɴᴏᴛᴇ : ᴜsᴇ ᴠʟᴄ ᴘʟᴀʏᴇʀ ᴏʀ ᴍx ᴘʟᴀʏᴇʀ  ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ"
                )
                
                notice_msg = await message.reply_text(
                    f"⧗ **Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....**\n\n> {delete_text}"
                )
                
                asyncio.create_task(auto_delete_messages(client, sent_msgs, notice_msg, user_id, param))
                return
            except Exception as e:
                return await message.reply_text(f"❌ Failed to retrieve files: {str(e)}")
                
        # Single File Retrieval
        elif param.startswith("single_"):
            try:
                msg_id = int(param.replace("single_", ""))
                sent_msg = await client.copy_message(
                    chat_id=user_id,
                    from_chat_id=STORAGE_CHANNEL,
                    message_id=msg_id,
                    caption=CUSTOM_CAPTION,
                    reply_markup=FILE_INLINE_BTN
                )
                
                delete_text = (
                    "›› Yᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 5 Mɪɴᴜᴛᴇs. Sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ..\n"
                    "≡ ɴᴏᴛᴇ : ᴜsᴇ ᴠʟᴄ ᴘʟᴀʏᴇʀ ᴏʀ ᴍx ᴘʟᴀʏᴇʀ  ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ"
                )
                
                notice_msg = await message.reply_text(
                    f"⧗ **Dᴜᴇ ᴛᴏ Cᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....**\n\n> {delete_text}"
                )
                
                asyncio.create_task(auto_delete_messages(client, [sent_msg], notice_msg, user_id, param))
                return
            except Exception as e:
                return await message.reply_text(f"❌ Failed to retrieve file: {str(e)}")

    # Default Start Interface with Photo
    start_text = (
        f"𖣘 𝐇𝐞𝐲  {message.from_user.first_name}✦\n"
        f"𖡹  𝐈'𝐌 𝐀  𓆩 𝑫𝒊𝒔𝒏𝒆𝒑 𝑷𝒍𝒖𝒔 𝑭𝒊𝒍𝒆 𝑺𝒕𝒐𝒓𝒆 𓆪\n"
        f"✪ 𝓔𝔂 𝓜𝓪𝓼𝓽𝓮𝓻  ☛  @𝐜𝐚𝐫𝐭𝐨𝐨𝐧𝐠𝐫𝐚𝐦𝟐𝟒 ° ✧\n"
        f"⎙  𝐈 𝐂𝐚𝐧 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐂𝐚𝐫𝐭𝐨𝐨𝐧 𝐌𝐨𝐯𝐢𝐞𝐬 & 𝐒𝐞𝐫𝐢𝐞𝐬\n"
        f"⌬ Join ☛ @cartoongram24°"
    )
    
    reply_kb = ReplyKeyboardMarkup(
        [
            [KeyboardButton("@cartoongram24")],
            [KeyboardButton("/genlink Store one pst")]
        ],
        resize_keyboard=True
    )
    
    await message.reply_photo(
        photo=START_PHOTO,
        caption=start_text,
        reply_markup=reply_kb
    )

# --- COMMAND ROUTING & RESTRICTIONS ---
@bot.on_message(filters.command(["connect_group", "batch", "states", "button", "bordcast", "ban", "unban", "genlink"]) & filters.private)
async def command_router(client: Client, message: Message):
    user_id = message.from_user.id
    cmd = message.command[0]
    
    if not is_admin(user_id):
        await message.reply_text("🛑You Are Not Owner in The Bot")
        return

    # Admin Operations
    if cmd == "connect_group":
        await message.reply_text("🛑You Are Not Owner in The Bot")
        
    elif cmd == "states":
        total_users = users_col.count_documents({})
        user_list = [str(u["user_id"]) for u in users_col.find()]
        user_ids_str = ", ".join(user_list)
        response = (
            f"bot states Total Users in bot: **{total_users}**\n"
            f"Users IDs: `{user_ids_str}`\n\n"
            f"My Master Link https://t.me/cartoongram24"
        )
        await message.reply_text(response, disable_web_page_preview=True)
        
    elif cmd == "batch":
        user_states[user_id] = {"action": "awaiting_batch"}
        await message.reply_text("Give Me Your Link Make Sure The Bot Admin In your Channel")
        
    elif cmd == "genlink":
        user_states[user_id] = {"action": "awaiting_single"}
        await message.reply_text("Give me Any File See the Magic ✨")
        
    elif cmd == "button":
        user_states[user_id] = {"action": "awaiting_button_msg"}
        await message.reply_text("Give Any File & Message ect.")
        
    elif cmd == "bordcast":
        user_states[user_id] = {"action": "awaiting_broadcast"}
        await message.reply_text("What Do you want to bordcast")
        
    elif cmd == "ban":
        user_states[user_id] = {"action": "awaiting_ban"}
        await message.reply_text("User id")
        
    elif cmd == "unban":
        user_states[user_id] = {"action": "awaiting_unban"}
        await message.reply_text("User id")

# --- REPLY KEYBOARD & TEXT STATE HANDLERS ---
@bot.on_message(filters.text & filters.private & ~filters.command(["start", "batch", "states", "button", "bordcast", "ban", "unban", "connect_group", "genlink"]))
async def handle_text_inputs(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text

    if text == "@cartoongram24":
        await message.reply_text("join tg hindi cartoons  -  https://t.me/cartoongram24")
        return
        
    if text == "/genlink Store one pst":
        if not is_admin(user_id):
            await message.reply_text("Give me Any File See the Magic ✨ (if not Work than this camd not for users)")
            user_states[user_id] = {"action": "user_genlink_try"}
        else:
            user_states[user_id] = {"action": "awaiting_single"}
            await message.reply_text("Give me Any File See the Magic ✨")
        return

    # Process Active Inputs
    if user_id in user_states:
        state = user_states[user_id].get("action")
        
        if state == "user_genlink_try":
            await message.reply_text("🛑 Sorry You Are Not My Owner - This is Not Your Cmd")
            del user_states[user_id]
            return

        if is_admin(user_id):
            if state == "awaiting_broadcast":
                del user_states[user_id]
                users = users_col.find()
                count = 0
                for u in users:
                    try:
                        await message.copy(u["user_id"])
                        count += 1
                        await asyncio.sleep(0.05)
                    except Exception:
                        pass
                await message.reply_text(f"✅ Broadcast sent to {count} users.")
                return

            elif state == "awaiting_ban":
                try:
                    target_id = int(text)
                    banned_col.update_one({"user_id": target_id}, {"$set": {"user_id": target_id}}, upsert=True)
                    del user_states[user_id]
                    await message.reply_text(f"✅ User `{target_id}` banned successfully.")
                except ValueError:
                    await message.reply_text("❌ Invalid User ID. Please send numeric ID.")
                return

            elif state == "awaiting_unban":
                try:
                    target_id = int(text)
                    banned_col.delete_one({"user_id": target_id})
                    del user_states[user_id]
                    await message.reply_text(f"✅ User `{target_id}` unbanned successfully.")
                except ValueError:
                    await message.reply_text("❌ Invalid User ID. Please send numeric ID.")
                return

# --- MEDIA HANDLER FOR BATCH / SINGLE FILE LINKS ---
@bot.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.private)
async def handle_media_inputs(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        if user_states.get(user_id, {}).get("action") == "user_genlink_try":
            del user_states[user_id]
        await message.reply_text("🛑 Sorry You Are Not My Owner - This is Not Your Cmd")
        return

    if user_id in user_states:
        state = user_states[user_id].get("action")
        
        # Admin /genlink Single File Creation
        if state == "awaiting_single":
            status = await message.reply_text("Genrateing Your 🫥 Link")
            await asyncio.sleep(3)
            
            forwarded = await message.copy(
                STORAGE_CHANNEL,
                caption=CUSTOM_CAPTION,
                reply_markup=FILE_INLINE_BTN
            )
            bot_me = await client.get_me()
            link = f"https://t.me/{bot_me.username}?start=single_{forwarded.id}"
            
            await status.edit_text(f"Here is your link:\n\n{link}")
            del user_states[user_id]
            
        # Admin /button Workflow
        elif state == "awaiting_button_msg":
            status = await message.reply_text("Genrateing Your 🫥 Link")
            await asyncio.sleep(3)
            
            green_btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("Click Me - https://t.me/cartoongram24 - style : green", url="https://t.me/cartoongram24")]
            ])
            await message.copy(chat_id=message.chat.id, reply_markup=green_btn)
            await status.delete()
            del user_states[user_id]

        # Admin /batch Multi-file Storage Workflow
        elif state == "awaiting_batch":
            status = await message.reply_text("Genrateing Your 🫥 Link")
            await asyncio.sleep(20)
            
            forwarded = await message.copy(
                STORAGE_CHANNEL,
                caption=CUSTOM_CAPTION,
                reply_markup=FILE_INLINE_BTN
            )
            bot_me = await client.get_me()
            link = f"https://t.me/{bot_me.username}?start=batch_{forwarded.id}_{forwarded.id}"
            
            await status.edit_text(f"Here is your Batch link:\n\n{link}")
            del user_states[user_id]

# Start Bot
bot.run()

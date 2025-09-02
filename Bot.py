from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FORCE_SUB_CHANNEL = os.getenv("CHANNEL")   # channel username without @

app = Client(
    "filestore",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Check subscription
async def is_subscribed(client, user_id):
    try:
        await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return True
    except UserNotParticipant:
        return False

@app.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def save_file(client, message):
    file_id = (
        message.document.file_id if message.document else
        message.video.file_id if message.video else
        message.photo.file_id if message.photo else
        message.audio.file_id
    )
    link = f"https://t.me/{client.me.username}?start={file_id}"
    await message.reply(f"✅ File saved!\n🔗 Shareable Link:\n{link}")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if len(message.command) > 1:
        file_id = message.command[1]
        if await is_subscribed(client, message.from_user.id):
            await message.reply_document(file_id)
        else:
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
                    [InlineKeyboardButton("✅ Try Again", callback_data=f"getfile_{file_id}")]
                ]
            )
            await message.reply("⚠️ Pehle channel join karo fir file milegi!", reply_markup=buttons)
    else:
        await message.reply("👋 Mujhe koi file bhejo, main uska permanent link de dunga.")

@app.on_callback_query(filters.regex("getfile_"))
async def give_file(client, callback_query):
    file_id = callback_query.data.split("_")[1]
    if await is_subscribed(client, callback_query.from_user.id):
        await callback_query.message.reply_document(file_id)
        await callback_query.answer("✅ File unlocked!")
    else:
        await callback_query.answer("❌ Pehle channel join karo!", show_alert=True)

app.run()

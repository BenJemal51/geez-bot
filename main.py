import logging
from telegram import Update
from telegram.error import NetworkError, TimedOut
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ----------------------------------------------------
# 1. BOT CONFIGURATION
# ----------------------------------------------------
TOKEN = "8645857316:AAEGj5aAi67zcSsmR6MK8f8ztGx_ssQnRmc"

# Captured automatically when you send /start first
MY_PERSONAL_TELEGRAM_ID = None

logging.basicConfig(level=logging.WARNING)

# ----------------------------------------------------
# 2. PHONETIC TRANSLITERATION DICTIONARY
# ----------------------------------------------------
LATIN_TO_AMHARIC = {
    # Labialized/Diphthongs
    "hwo": "ኋ", "mwa": "ሟ", "rwa": "ሯ", "swa": "ሷ", "shwa": "ሿ",
    "qwa": "ቋ", "bwa": "ቧ", "twa": "ቷ", "chwa": "ቿ", "nwa": "ኗ",
    "kwa": "ኳ", "zwa": "ዟ", "dwa": "ዷ", "jwa": "ጇ", "gwa": "ጓ",
    "t'wa": "ጧ", "ch'wa": "ጯ", "fwa": "ፏ",
    # Core series
    "ha": "ሀ", "hu": "ሁ", "hi": "ሂ", "haa": "ሃ", "he": "ሄ", "h": "ህ", "ho": "ሆ",
    "la": "ለ", "lu": "ሉ", "li": "ሊ", "laa": "ላ", "le": "ሌ", "l": "ል", "lo": "ሎ",
    "ma": "መ", "mu": "ሙ", "mi": "ሚ", "maa": "ማ", "me": "ሜ", "m": "ም", "mo": "ሞ",
    "ra": "ረ", "ru": "ሩ", "ri": "ሪ", "raa": "ራ", "re": "ሬ", "r": "ር", "ro": "ሮ",
    "sa": "ሰ", "su": "ሱ", "si": "ሲ", "saa": "ሳ", "se": "ሴ", "s": "ስ", "so": "ሶ",
    "sha": "ሸ", "shu": "ሹ", "shi": "ሺ", "shaa": "ሻ", "she": "ሼ", "sh": "ሽ", "sho": "ሾ",
    "qa": "ቀ", "qu": "ቁ", "qi": "ቂ", "qaa": "ቃ", "qe": "ቄ", "q": "ቅ", "qo": "ቆ",
    "ba": "በ", "bu": "ቡ", "bi": "ቢ", "baa": "ባ", "be": "ቤ", "b": "ብ", "bo": "ቦ",
    "ta": "ተ", "tu": "ቱ", "ti": "ቲ", "taa": "ታ", "te": "ቴ", "t": "ት", "to": "ቶ",
    "cha": "ቸ", "chu": "ቹ", "chi": "ቺ", "chaa": "ቻ", "che": "ቼ", "ch": "ች", "cho": "ቾ",
    "na": "ነ", "nu": "ኑ", "ni": "ኒ", "naa": "ና", "ne": "ኔ", "n": "ን", "no": "ኖ",
    "nya": "ኘ", "nyu": "ኙ", "nyi": "ኚ", "nyaa": "ኛ", "nye": "ኜ", "ny": "ኝ", "nyo": "ኞ",
    "gna": "ኘ", "gnu": "ኙ", "gni": "ኚ", "gnaa": "ኛ", "gne": "ኜ", "gn": "ኝ", "gno": "ኞ",
    "a": "አ", "u": "ኡ", "i": "ኢ", "aa": "ኣ", "e": "ኤ", "ï": "እ", "o": "ኦ",
    "ka": "ከ", "ku": "ኩ", "ki": "ኪ", "kaa": "ካ", "ke": "ኬ", "k": "ክ", "ko": "ኮ",
    "wa": "ወ", "wu": "ዉ", "wi": "ዊ", "waa": "ዋ", "we": "ዌ", "w": "ው", "wo": "ዎ",
    "za": "ዘ", "zu": "ዙ", "zi": "ዚ", "zaa": "ዛ", "ze": "ዜ", "z": "ዝ", "zo": "ዞ",
    "zha": "ዠ", "zhu": "ዡ", "zhi": "ዢ", "zhaa": "ዣ", "zhe": "ዤ", "zh": "ዥ", "zho": "ዦ",
    "ya": "የ", "yu": "ዩ", "yi": "ዪ", "yaa": "ያ", "ye": "ዬ", "y": "ይ", "yo": "ዮ",
    "da": "ደ", "du": "ዱ", "di": "ዲ", "daa": "ዳ", "de": "ዴ", "d": "ድ", "do": "ዶ",
    "ja": "ጀ", "ju": "ጁ", "ji": "ጂ", "jaa": "ጃ", "je": "ጄ", "j": "ጅ", "jo": "ጆ",
    "ga": "ገ", "gu": "ጉ", "gi": "ጊ", "gaa": "ጋ", "ge": "ጌ", "g": "ግ", "go": "ጎ",
    "t'a": "ጠ", "t'u": "ጡ", "t'i": "ጢ", "t'aa": "ጣ", "t'e": "ጤ", "t'": "ጥ", "t'o": "ጦ",
    "ch'a": "ጨ", "ch'u": "ጩ", "ch'i": "ጪ", "ch'aa": "ጫ", "ch'e": "ጬ", "ch'": "ጭ", "ch'o": "ጮ",
    "fa": "ፈ", "fu": "ፉ", "fi": "ፊ", "faa": "ፋ", "fe": "ፌ", "f": "ፍ", "fo": "ፎ",
    "pa": "ፐ", "pu": "ፑ", "pi": "ፒ", "paa": "ፓ", "pe": "ፔ", "p": "ፕ", "po": "ፖ"
}

SORTED_KEYS = sorted(LATIN_TO_AMHARIC.keys(), key=len, reverse=True)


def convert_text(text: str) -> str:
    result = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for key in SORTED_KEYS:
            k_len = len(key)
            if i + k_len <= n and text[i : i + k_len].lower() == key:
                result.append(LATIN_TO_AMHARIC[key])
                i += k_len
                matched = True
                break
        if not matched:
            result.append(text[i])
            i += 1
    return "".join(result)


# ----------------------------------------------------
# 3. HANDLERS AND NOTIFICATIONS
# ----------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MY_PERSONAL_TELEGRAM_ID
    user = update.effective_user

    if MY_PERSONAL_TELEGRAM_ID is None:
        MY_PERSONAL_TELEGRAM_ID = user.id
        print(f"[SYSTEM] Registered Owner ID: {user.id}")

    print(f"[START COMMAND] User: {user.first_name} (@{user.username} | ID: {user.id})")

    try:
        await update.message.reply_text(
            "Selam! Send Latin Amharic text (e.g. 'selam endemin neh') to convert to Ge'ez."
        )
    except (TimedOut, NetworkError):
        pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_text = update.message.text

    print(f"\n[MSG FROM @{user.username} | ID: {user.id}]: {user_text}")

    # Forward message copy to owner
    if MY_PERSONAL_TELEGRAM_ID and user.id != MY_PERSONAL_TELEGRAM_ID:
        try:
            log_text = (
                f"📩 *New User Message*\n"
                f"From: {user.first_name} (@{user.username})\n"
                f"ID: `{user.id}`\n\n"
                f"*Text:* {user_text}"
            )
            await context.bot.send_message(
                chat_id=MY_PERSONAL_TELEGRAM_ID,
                text=log_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"[FORWARD ERROR] {e}")

    converted = convert_text(user_text)

    try:
        await update.message.reply_text(converted)
    except (TimedOut, NetworkError):
        try:
            await update.message.reply_text(converted)
        except Exception as e:
            print(f"[ERROR] Delivery failed: {e}")


if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is live on server!\n")
    app.run_polling(poll_interval=2.0)

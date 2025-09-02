import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import BadRequest, Forbidden
import instaloader
from instaloader import Profile, ProfileNotExistsException, ConnectionException
import json
import os
import random
import aiohttp
import requests
import threading
import asyncio
from urllib.parse import quote, urlparse, quote_plus
from io import BytesIO
import time
import zipfile
import shutil
import tempfile

# تمكين التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# بيانات البوت
TOKEN = "8106028644:AAFvPw68gwpPPGfCts80cyl_ZuxObboqWWs"
ADMIN_ID = 7170744706  # آيدي المشرف
DEVELOPER_USERNAME = "@FS_FV"  # يوزر المطور

# ملف التخزين
DATA_FILE = "bot_data.json"
CHANNELS_FILE = "channels_data.json"

# APIs
VIRUSTOTAL_API_KEY = "19462df75ad313db850e532a2e8869dc8713c07202b1c62ebf1aa7a18a2e0173"
VIDEO_API_BASE = "https://api.yabes-desu.workers.dev/ai/tool/txt2video"
SHORTENER_API = "https://api.dfkz.xo.je/apis/v1/short.php?url="
INSTA_INFO_API = "https://sherifbots.serv00.net/Api/insta.php?user="
AI_API_URL = 'https://ai-api.magicstudio.com/api/ai-art-generator'
# APIs
# ... الكود السابق ...
INSTA_INFO_API = "https://sherifbots.serv00.net/Api/insta.php?user="
# أضف هذا API في قسم الـ APIs
INSTA_INFO_API_2 = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
INSTA_INFO_HEADERS = {
    "x-rapidapi-key": "your-rapidapi-key-here",  # تحتاج تحصل على مفتاح من rapidapi.com
    "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
}

# أو جرب هذا API المجاني (بدون need for API key):
INSTA_INFO_API_FREE = "https://instagram-data1.p.rapidapi.com/user/info"
INSTA_INFO_HEADERS_FREE = {
    "x-rapidapi-key": "your-rapidapi-key-here",  # تحتاج تحصل على مفتاح من rapidapi.com
    "x-rapidapi-host": "instagram-data1.p.rapidapi.com"
}

# أو جرب هذا البديل الأبسط:
INSTA_INFO_SIMPLE = "https://www.instagram.com/{}/?__a=1&__d=dis"
# إعدادات أخرى
COLUMNS = 2
DOWNLOAD_FOLDER = "site_download"
ZIP_FILE_NAME = "site_download.zip"

# متغيرات صيد اليوزرات
insta = "1234567890qwertyuiopasdfghjklzxcvbnm"
all_chars = "_."
user_sessions = {}
good_users_cache = {}

# لغات الترجمة المدعومة
SUPPORTED_LANGUAGES = {
    "العربية": "ar",
    "الإنجليزية": "en",
    "الإسبانية": "es",
    "الفرنسية": "fr",
    "الألمانية": "de",
    "الإيطالية": "it",
    "البرتغالية": "pt",
    "الروسية": "ru",
    "الصينية": "zh",
    "اليابانية": "ja",
    "الكورية": "ko",
    "التركية": "tr",
    "الفارسية": "fa",
    "العبرية": "he"
}

# BINs شائعة للفيزا
COMMON_VISA_BINS = [
    '453201', '453202', '453203', '453204', '453205', '453206', '453207', '453208', '453209',
    '453210', '453211', '453212', '453213', '453214', '453215', '453216', '453217', '453218',
    '453219', '453220', '453221', '453222', '453223', '453224', '453225', '453226', '453227',
    '453228', '453229', '453230', '453231', '453232', '453233', '453234', '453235', '453236',
    '453237', '453238', '453239', '453240', '453241', '453242', '453243', '453244', '453245',
    '453246', '453247', '453248', '453249', '453250', '453251', '453252', '453253', '453254',
    '453255', '453256', '453257', '453258', '453259', '453260', '453261', '453262', '453263',
    '453264', '453265', '453266', '453267', '453268', '453269', '453270', '453271', '453272',
    '453273', '453274', '453275', '453276', '453277', '453278', '453279', '453280', '453281',
    '453282', '453283', '453284', '453285', '453286', '453287', '453288', '453289', '453290',
    '453291', '453292', '453293', '453294', '453295', '453296', '453297', '453298', '453299',
    '454000', '454001', '454002', '454003', '454004', '454005', '454006', '454007', '454008',
    '454009', '454010', '454011', '454012', '454013', '454014', '454015', '454016', '454017',
    '454018', '454019', '454020', '454021', '454022', '454023', '454024', '454025', '454026',
    '454027', '454028', '454029', '454030', '454031', '454032', '454033', '454034', '454035',
    '454036', '454037', '454038', '454039', '454040', '454041', '454042', '454043', '454044',
    '454045', '454046', '454047', '454048', '454049', '454050', '454051', '454052', '454053',
    '454054', '454055', '454056', '454057', '454058', '454059', '454060', '454061', '454062',
    '454063', '454064', '454065', '454066', '454067', '454068', '454069', '454070', '454071',
    '454072', '454073', '454074', '454075', '454076', '454077', '454078', '454079', '454080',
    '454081', '454082', '454083', '454084', '454085', '454086', '454087', '454088', '454089',
    '454090', '454091', '454092', '454093', '454094', '454095', '454096', '454097', '454098',
    '454099'
]

# تحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"buttons": [], "services_order": ["translation", "visa", "image", "video", "tiktok", "file_check", "site_download", "shortener", "insta_info"]}

def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r') as f:
            return json.load(f)
    return {"channels": []}

# حفظ البيانات
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def save_channels(data):
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(data, f)

# تحقق من صلاحية المشرف
def is_admin(user_id):
    return user_id == ADMIN_ID

# دالة لترتيب الأزرار في أعمدة
def arrange_buttons_in_columns(buttons_list, columns=COLUMNS):
    keyboard = []
    for i in range(0, len(buttons_list), columns):
        row = buttons_list[i:i+columns]
        keyboard.append(row)
    return keyboard

# التحقق من اشتراك المستخدم في القنوات
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    channels = load_channels()["channels"]
    
    if not channels:
        return True  # إذا لم توجد قنوات، نسمح بالاستخدام
    
    not_subscribed = []
    
    for channel in channels:
        try:
            member = await context.bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed.append(channel)
        except (BadRequest, Forbidden) as e:
            logging.error(f"Error checking subscription for channel {channel['id']}: {e}")
            continue
    
    if not_subscribed:
        # إنشاء رسالة مع أزرار الاشتراك
        keyboard = []
        for channel in not_subscribed:
            channel_id = channel["id"]
            channel_name = channel["name"]
            username = channel.get("username", "")
            
            if username:
                url = f"https://t.me/{username}"
            else:
                url = "https://t.me/c/{}".format(str(channel_id).replace('-100', ''))
            
            keyboard.append([InlineKeyboardButton(f"انضم إلى {channel_name}", url=url)])
        
        keyboard.append([InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ يجب عليك الانضمام إلى القنوات التالية لاستخدام البوت:",
            reply_markup=reply_markup
        )
        return False
    
    return True

# تطبيق خوارزمية لوهن (Luhn algorithm) للتحقق من صحة رقم البطاقة
def luhn_check(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    
    return checksum % 10 == 0

# توليد رقم بطاقة صحيح باستخدام خوارزمية لوهن
def generate_valid_card(bin):
    # توليد الأرقام العشوائية
    length = 16 - len(bin)
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(length - 1)])
    
    # حساب checksum باستخدام خوارزمية لوهن
    base_number = bin + random_part
    checksum = 0
    for i, digit in enumerate(base_number):
        n = int(digit)
        if (i + len(bin)) % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        checksum += n
    
    checksum_digit = (10 - (checksum % 10)) % 10
    card_number = base_number + str(checksum_digit)
    
    return card_number

# توليد فيزا حقيقي مع بيانات واقعية
def generate_realistic_visa():
    # اختيار BIN عشوائي من القائمة
    bin = random.choice(COMMON_VISA_BINS)
    
    # توليد رقم بطاقة صحيح
    card_number = generate_valid_card(bin)
    
    # تنسيق الرقم للعرض
    formatted_number = ' '.join([card_number[i:i+4] for i in range(0, 16, 4)])
    
    # توليد تاريخ انتهاء واقعي (ليس في الماضي)
    current_year = 2024
    month = random.randint(1, 12)
    year = random.randint(current_year, current_year + 5)
    
    # تنسيق التاريخ
    expiry_date = f"{month:02d}/{str(year)[2:]}"
    
    # توليد CVV واقعي
    cvv = f"{random.randint(0, 999):03d}"
    
    # توليد اسم حامل البطاقة (عشوائي)
    first_names = ["AHMED", "MOHAMMED", "ALI", "OMAR", "KHALED", "HASSAN", "HUSSEIN", "IBRAHIM", "YOUSEF", "ABDULLAH"]
    last_names = ["ALI", "HASSAN", "HUSSEIN", "ABDULRAHMAN", "ALSAUD", "ALGHAMDI", "ALOTAIBI", "ALAMRI", "ALSHEHRI", "ALZAHRANI"]
    
    card_holder = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    return formatted_number, expiry_date, cvv, card_holder

# ترجمة النص إلى الإنجليزية
def translate_to_english(text: str) -> str:
    """ترجمة النص إلى الإنجليزية باستخدام Google Translate"""
    try:
        translate_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={quote(text)}"
        response = requests.get(translate_url)
        response.raise_for_status()
        result = response.json()
        return result[0][0][0]
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text  # إذا فشلت الترجمة، نعود للنص الأصلي

# إنشاء صورة باستخدام الذكاء الاصطناعي
def create_ai_image(prompt: str) -> bytes:
    """إنشاء صورة باستخدام API الذكاء الاصطناعي"""
    try:
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,ar;q=0.8",
            "origin": "https://magicstudio.com",
            "priority": "u=1, i",
            "referer": "https://magicstudio.com/ai-art-generator/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        
        data = {
            'prompt': prompt,
            'output_format': 'bytes',
            'user_profile_id': 'null',
            'user_is_subscribed': 'true'
        }
        
        response = requests.post(AI_API_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f"AI Image generation error: {e}")
        raise

# وظائف إنشاء الفيديو
def fetch_video_to_temp(prompt: str) -> str:
    """إنشاء فيديو من النص باستخدام API"""
    url = f"{VIDEO_API_BASE}?prompt={quote_plus(prompt)}"
    # زيادة الوقت إلى 20 دقيقة
    resp = requests.get(url, stream=True, timeout=1200)

    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:200]}")

    ctype = resp.headers.get("Content-Type", "")
    if "application/json" in ctype:
        data = resp.json()
        video_url = (
            data.get("url")
            or data.get("video")
            or data.get("result")
            or data.get("data")
        )
        if not video_url:
            raise RuntimeError("❌ ما لكيت رابط فيديو بالـ API response.")

        # زيادة الوقت للفيديو أيضًا
        r2 = requests.get(video_url, stream=True, timeout=1200)
        if r2.status_code != 200:
            raise RuntimeError(f"Video URL error {r2.status_code}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tf:
            for chunk in r2.iter_content(chunk_size=1024 * 64):
                tf.write(chunk)
            return tf.name
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tf:
            for chunk in resp.iter_content(chunk_size=1024 * 64):
                tf.write(chunk)
            return tf.name

# وظائف صيد يوزرات انستجرام
def check_instagram_user(user):
    url = 'https://www.instagram.com/accounts/web_create_ajax/attempt/'
    
    headers = {
        'Host': 'www.instagram.com',
        'content-length': '85',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101"',
        'x-ig-app-id': '936619743392459',
        'x-ig-www-claim': '0',
        'sec-ch-ua-mobile': '?0',
        'x-instagram-ajax': '81f3a3c9dfe2',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'x-requested-with': 'XMLHttpRequest',
        'x-asbd-id': '198387',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Safari/537.36',
        'x-csrftoken': 'jzhjt4G11O37lW1aDFyFmy1K0yIEN9Qv',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://www.instagram.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.instagram.com/accounts/emailsignup/',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-IQ,en;q=0.9',
        'cookie': 'csrftoken=jzhjt4G11O37lW1aDFyFmy1K0yIEN9Qv; mid=YtsQ1gABAAEszHB5wT9VqccwQIUL; ig_did=227CCCC2-3675-4A04-8DA5-BA3195B46425; ig_nrcb=1'
    }
    
    data = f'email=aakmnnsjskksmsnsn%40gmail.com&username={user}&first_name=&opt_into_one_tap=false'
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response_text = response.text
        
        if '{"message":"feedback_required","spam":true,' in response_text:
            return False
        elif '"errors": {"username":' in response_text or '"code": "username_is_taken"' in response_text:
            return False
        else:
            return True
            
    except Exception as e:
        logging.error(f"Error checking user {user}: {e}")
        return False

def generate_4char_users(count):
    users = []
    for _ in range(count):
        if random.random() < 0.3:
            user = ''.join(random.choice(insta) for _ in range(4))
        else:
            num_symbols = random.randint(1, 2)
            positions = random.sample([0, 1, 2, 3], num_symbols)
            user_chars = []
            for i in range(4):
                if i in positions:
                    user_chars.append(random.choice(all_chars))
                else:
                    user_chars.append(random.choice(insta))
            user = ''.join(user_chars)
        users.append(user)
    return users

def generate_5char_users(count):
    users = []
    for _ in range(count):
        if random.random() < 0.4:
            user = ''.join(random.choice(insta) for _ in range(5))
        else:
            num_symbols = random.randint(1, 3)
            positions = random.sample([0, 1, 2, 3, 4], num_symbols)
            user_chars = []
            for i in range(5):
                if i in positions:
                    user_chars.append(random.choice(all_chars))
                else:
                    user_chars.append(random.choice(insta))
            user = ''.join(user_chars)
        users.append(user)
    return users

def generate_special_users(count, length=6):
    users = []
    for _ in range(count):
        if random.random() < 0.2:
            user = ''.join(random.choice(insta) for _ in range(length))
        else:
            num_symbols = random.randint(2, 4)
            positions = random.sample(range(length), num_symbols)
            user_chars = []
            for i in range(length):
                if i in positions:
                    user_chars.append(random.choice(all_chars))
                else:
                    user_chars.append(random.choice(insta))
            user = ''.join(user_chars)
        users.append(user)
    return users

def generate_easy_4char_users(count):
    users = []
    for _ in range(count):
        if random.random() < 0.1:
            user = ''.join(random.choice(insta) for _ in range(4))
        else:
            positions = random.sample([0, 1, 2, 3], 2)
            user_chars = []
            for i in range(4):
                if i in positions:
                    user_chars.append(random.choice(all_chars))
                else:
                    user_chars.append(random.choice(insta))
            user = ''.join(user_chars)
        users.append(user)
    return users

def check_users_batch(users):
    good_users = []
    for user in users:
        if check_instagram_user(user):
            good_users.append(user)
            if len(good_users) >= 5:
                break
    return good_users

def send_message_from_thread(application, chat_id, text, parse_mode=None):
    async def async_send_message():
        try:
            await application.bot.send_message(chat_id, text, parse_mode=parse_mode)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_send_message())
    loop.close()

def instagram_check_process(chat_id, application, user_type):
    user_sessions[chat_id] = True
    total_checked = 0
    found_users = 0
    
    type_name = "خماسية" if user_type == "5char" else "رباعية" if user_type == "4char" else "رباعية سهلة" if user_type == "easy4char" else "خاصة"
    send_message_from_thread(application, chat_id, f"🔍 بدء البحث عن 5 يوزرات {type_name} متاحة...")
    
    while user_sessions.get(chat_id, False) and found_users < 5:
        if user_type == "5char":
            users_batch = generate_5char_users(15)
        elif user_type == "4char":
            users_batch = generate_4char_users(15)
        elif user_type == "easy4char":
            users_batch = generate_easy_4char_users(15)
        else:
            users_batch = generate_special_users(15)
        
        good_users = check_users_batch(users_batch)
        total_checked += len(users_batch)
        
        if chat_id not in good_users_cache:
            good_users_cache[chat_id] = []
        
        for user in good_users:
            if user not in good_users_cache[chat_id]:
                good_users_cache[chat_id].append(user)
                found_users += 1
                
                symbol_count = sum(1 for char in user if char in all_chars)
                user_type_desc = ""
                if symbol_count == 0:
                    user_type_desc = "بدون رموز"
                elif symbol_count == 1:
                    user_type_desc = "برمز واحد"
                elif symbol_count == 2:
                    user_type_desc = "برمزين"
                else:
                    user_type_desc = f"ب{symbol_count} رموز"
                
                message = f"""✅ يوزر Instagram متاح!

📝 اليوزر: `{user}`
🔢 النوع: {type_name} ({user_type_desc})
🎯 الحاية: متاح للتسجيل

💾 اليوزر {found_users} من 5"""
                
                send_message_from_thread(application, chat_id, message, parse_mode='Markdown')
                
                if found_users >= 5:
                    break
        
        if found_users >= 5:
            break
    
    if found_users > 0:
        users_list = "\n".join([f"• `{user}`" for user in good_users_cache[chat_id][-found_users:]])
        final_message = f"""🎉 تم العثور على {found_users} يوزر متاح!

{users_list}

📊 إجمالي المفحوصة: {total_checked}"""
    else:
        final_message = f"""❌ لم يتم العثور على يوزرات متاحة

📊 إجمالي المفحوصة: {total_checked}"""
    
    send_message_from_thread(application, chat_id, final_message, parse_mode='Markdown')
    user_sessions[chat_id] = False

# دالة جلب معلومات تيك توك
async def get_tiktok_info(username: str) -> dict:
    """جلب معلومات حساب تيك توك"""
    api_url = f"https://tik-batbyte.vercel.app/tiktok?username={username}"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        logging.error(f"TikTok API error: {e}")
        return {}

# خدمة معلومات تيك توك
async def tiktok_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "📱 **معلومات حساب تيك توك**\n\n"
        "أرسل لي معرف حساب التيك توك بدون علامة @\n\n"
        "مثال:\n"
        "• iraq\n"
        "• username123\n"
        "• example_user\n\n"
        "أرسل المعرف الآن:"
    )
    
    context.user_data["awaiting_tiktok_username"] = True

# خدمة فحص الملفات
async def file_check_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "🔍 **فحص الملفات ضد الاختراق**\n\n"
        "أرسل لي ملف Python (.py) وسأفحصه في VirusTotal\n\n"
        "📂 فقط ملفات Python بصيغة .py مسموح بها\n"
        "⏳ قد تستغرق العملية بضع دقائق\n\n"
        "أرسل الملف الآن:"
    )
    
    context.user_data["awaiting_file_check"] = True

# خدمة إنشاء الفيديو
async def video_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "🎬 **إنشاء فيديو من النص**\n\n"
        "أرسل لي وصفاً للفيديو الذي تريد إنشاءه.\n\n"
        "مثال:\n"
        "• a boy running in the rain cinematic 4k\n"
        "• sunset over the ocean slow motion\n"
        "• futuristic city at night high quality\n\n"
        "⏰ ملاحظة: إنشاء الفيديو قد يستغرق من 2-10 دقائق\n\n"
        "أرسل الوصف الآن:"
    )
    
    context.user_data["awaiting_video_prompt"] = True

# فحص الملف باستخدام VirusTotal
async def check_file_with_virustotal(file_data, file_name):
    """فحص الملف باستخدام VirusTotal API"""
    try:
        files = {"file": (file_name, file_data)}
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        upload_url = "https://www.virustotal.com/api/v3/files"

        # رفع الملف
        upload_response = requests.post(upload_url, files=files, headers=headers)
        upload_response.raise_for_status()
        analysis_id = upload_response.json()["data"]["id"]

        # الانتظار حتى تجهز النتيجة
        analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        for _ in range(10):
            analysis_response = requests.get(analysis_url, headers=headers)
            result = analysis_response.json()
            status = result["data"]["attributes"]["status"]
            if status == "completed":
                break
            time.sleep(3)

        stats = result["data"]["attributes"]["stats"]
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        harmless = stats.get("harmless", 0)
        undetected = stats.get("undetected", 0)
        sha256 = result["meta"]["file_info"]["sha256"]

        return {
            "malicious": malicious,
            "suspicious": suspicious,
            "harmless": harmless,
            "undetected": undetected,
            "sha256": sha256,
            "success": True
        }
    except Exception as e:
        logging.error(f"VirusTotal error: {e}")
        return {"success": False, "error": str(e)}

# معالجة معلومات تيك توك
async def handle_tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_tiktok_username", False):
        username = update.message.text.strip()
        
        if not username:
            await update.message.reply_text("يرجى إرسال معرف صالح لحساب التيك توك.")
            return
        
        await update.message.reply_text(f"🔍 جاري البحث عن معلومات الحساب: {username}")
        
        try:
            data = await get_tiktok_info(username)
            
            if data.get('username'):
                caption = f"""*📊 معلومات حساب التيك توك:*

• 📛 الاسم: {data.get('nickname', 'غير متوفر')}
• 🆔 اليوزر: @{data.get('username', 'غير متوفر')}
• 📝 الوصف: {data.get('bio', 'غير متوفر')}
• 🔢 اليوزر ID: {data.get('user_id', 'غير متوفر')}
• 👥 المتابعون: {data.get('followers', '0')} 
• ❤️ الإعجابات: {data.get('hearts', '0')} 
• 🎬 الفيديوهات: {data.get('videos', '0')} 
• 📅 تاريخ الإنشاء: {data.get('create_date', 'غير معروف')}
• 🌐 اللغة: {data.get('language', 'غير معروف')} 
• 🔒 النوع: {"خاص" if data.get('is_private') else "عام"}"""

                # إرسال الصورة مع المعلومات
                await update.message.reply_photo(
                    photo=data.get('profile_picture', ''),
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    f"*❌ لم يتم العثور على معلومات للحساب:* `{username}`",
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            await update.message.reply_text(
                f"حدث خطأ أثناء جلب المعلومات: {str(e)}"
            )
        
        context.user_data["awaiting_tiktok_username"] = False
        return

# معالجة فحص الملفات
async def handle_file_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_file_check", False):
        document = update.message.document
        
        # فحص الامتداد
        if not document.file_name.endswith(".py"):
            await update.message.reply_text("⚠️ فقط ملفات Python بصيغة .py مسموح بها.")
            return
        
        await update.message.reply_text("📤 جاري رفع الملف وتحليله في VirusTotal...")
        
        try:
            # تحميل الملف
            file = await document.get_file()
            file_data = await file.download_as_bytearray()
            
            # فحص الملف
            result = await check_file_with_virustotal(bytes(file_data), document.file_name)
            
            if result["success"]:
                result_message = f"""✅ نتيجة تحليل الملف:

☠️ ضار: {result['malicious']}
⚠️ مشبوه: {result['suspicious']}
✅ آمن: {result['harmless']}
🕵️‍♂️ غير مكتشف: {result['undetected']}

رابط التحليل:
https://www.virustotal.com/gui/file/{result['sha256']}"""

                await update.message.reply_text(result_message)
                
                # إرسال نسخة للأدمن
                if is_admin(update.message.from_user.id):
                    await context.bot.send_document(
                        ADMIN_ID,
                        document=document.file_id,
                        caption=f"📂 ملف تم فحصه:\n{result_message}"
                    )
            else:
                await update.message.reply_text(f"❌ حدث خطأ أثناء تحليل الملف: {result['error']}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ أثناء معالجة الملف: {str(e)}")
        
        context.user_data["awaiting_file_check"] = False
        return

# معالجة إنشاء الفيديو
async def handle_video_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_video_prompt", False):
        prompt = update.message.text
        
        if not prompt.strip():
            await update.message.reply_text("يرجى إرسال وصف صالح للفيديو.")
            return
        
        loading_msg = await update.message.reply_text("⏳ جاري إنشاء الفيديو... قد يستغرق من 2-10 دقائق")
        
        try:
            # إنشاء الفيديو
            video_path = await asyncio.to_thread(fetch_video_to_temp, prompt)
            
            # حذف رسالة التحميل
            await loading_msg.delete()
            
            # إرسال الفيديو للمستخدم
            await update.message.reply_video(
                video=open(video_path, "rb"),
                caption=f"النص: {prompt}\n\n👨‍💻 Dev: {DEVELOPER_USERNAME}",
                supports_streaming=True,
            )
            
            # تنظيف الملف المؤقت
            os.unlink(video_path)
            
        except requests.exceptions.Timeout:
            await loading_msg.edit_text("⏰ طلبك استغرق وقتًا طويلاً جداً. جرب مرة أخرى بوصف أقصر.")
        except Exception as e:
            await loading_msg.edit_text(f"❌ حدث خطأ أثناء إنشاء الفيديو: {str(e)}")
        
        context.user_data["awaiting_video_prompt"] = False
        return

# وظائف سحب ملفات الموقع
async def cleanup_site_files(zip_path, folder_path):
    await asyncio.sleep(180)  # تنظيف الملفات بعد 3 دقائق
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    except Exception as e:
        logging.error(f"Error cleaning up site files: {e}")

def download_site_simple(url, folder):
    try:
        # تنظيف المجلد إذا كان موجوداً
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
        
        # تنزيل الصفحة الرئيسية فقط
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # استخراج اسم الملف من الرابط
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            filename = "index.html"
        
        # حفظ الصفحة الرئيسية
        main_file = os.path.join(folder, filename)
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return True
    except Exception as e:
        logging.error(f"Error downloading site: {e}")
        return False

def zip_folder_site(folder, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, folder)
                zipf.write(filepath, arcname)

# خدمة سحب ملفات الموقع
async def site_download_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "🌐 **سحب ملفات الموقع**\n\n"
        "أرسل لي رابط أي موقع وسأقوم بتحميل الصفحة الرئيسية وإرسالها لك كمضغوط.\n\n"
        "📝 مثال:\n"
        "• https://example.com\n"
        "• http://test-site.org\n\n"
        "ملاحظة: استخدم البوت بدون شي يغضب ربك\n\n"
        "أرسل الرابط الآن:"
    )
    
    context.user_data["awaiting_site_url"] = True

# معالجة سحب ملفات الموقع
async def handle_site_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_site_url", False):
        url = update.message.text.strip()
        
        if not (url.startswith('http://') or url.startswith('https://')):
            await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http:// أو https://")
            return
        
        await update.message.reply_text("جارٍ تحميل الصفحة الرئيسية... قد يستغرق هذا بعض الوقت.")
        
        try:
            # تحميل الصفحة الرئيسية فقط
            success = download_site_simple(url, DOWNLOAD_FOLDER)
            if not success:
                await update.message.reply_text("فشل في تحميل الصفحة الرئيسية. يرجى التحقق من الرابط والمحاولة مرة أخرى.")
                return
            
            # ضغط الملفات
            zip_folder_site(DOWNLOAD_FOLDER, ZIP_FILE_NAME)
            
            # إرسال الملف
            await update.message.reply_text("تم التحميل بنجاح! جاري إرسال الملف...")
            
            # التحقق من وجود الملف وحجمه قبل الإرسال
            if os.path.exists(ZIP_FILE_NAME) and os.path.getsize(ZIP_FILE_NAME) > 0:
                with open(ZIP_FILE_NAME, 'rb') as f:
                    await context.bot.send_document(
                        chat_id=update.message.chat_id,
                        document=f,
                        filename=ZIP_FILE_NAME,
                        caption="ها هو الموقع الذي طلبته مضغوطًا"
                    )
            else:
                await update.message.reply_text("عذرًا، لم يتم إنشاء الملف المضغوط بشكل صحيح.")
                return
            
            # تنظيف الملفات بعد الإرسال
            asyncio.create_task(cleanup_site_files(ZIP_FILE_NAME, DOWNLOAD_FOLDER))
            
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء معالجة الطلب: {str(e)}")
        
        context.user_data["awaiting_site_url"] = False
        return

# خدمة اختصار الروابط
async def shortener_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "🔗 **اختصار الروابط**\n\n"
        "أرسل لي الرابط الذي تريد اختصاره\n\n"
        "مثال:\n"
        "• https://www.google.com\n"
        "• https://www.youtube.com/watch?v=abc123\n\n"
        "أرسل الرابط الآن:"
    )
    
    context.user_data["awaiting_shortener_url"] = True

# خدمة معلومات انستجرام
async def insta_info_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "📷 **معلومات حساب انستجرام**\n\n"
        "أرسل لي معرف حساب الانستجرام بدون علامة @\n\n"
        "مثال:\n"
        "• username\n"
        "• example_user\n"
        "• instagram\n\n"
        "أرسل المعرف الآن:"
    )
    
    context.user_data["awaiting_insta_username"] = True

# معالجة اختصار الروابط
async def handle_shortener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_shortener_url", False):
        url = update.message.text.strip()
        
        if not (url.startswith('http://') or url.startswith('https://')):
            await update.message.reply_text("الرجاء إرسال رابط صحيح يبدأ بـ http:// أو https://")
            return
        
        await update.message.reply_text("🔗 جاري اختصار الرابط...")
        
        try:
            # استخدام API لاختصار الرابط
            api_url = f"{SHORTENER_API}{quote(url)}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                shortened_url = response.text.strip()
                await update.message.reply_text(
                    f"✅ تم اختصار الرابط بنجاح:\n\n"
                    f"📎 الرابط الأصلي: {url}\n"
                    f"🔗 الرابط المختصر: {shortened_url}"
                )
            else:
                await update.message.reply_text("❌ فشل في اختصار الرابط. يرجى المحاولة مرة أخرى.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ أثناء اختصار الرابط: {str(e)}")
        
        context.user_data["awaiting_shortener_url"] = False
        return


# معالجة معلومات انستجرام باستخدام instaloader
# معالجة معلومات انستجرام مع البيانات المطلوبة
async def handle_insta_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_insta_username", False):
        username = update.message.text.strip()
        
        if not username:
            await update.message.reply_text("يرجى إرسال معرف صالح لحساب الانستجرام.")
            return
        
        loading_msg = await update.message.reply_text(f"🔍 جاري جمع المعلومات عن الحساب: @{username}")
        
        try:
            # إنشاء كائن Instaloader
            L = instaloader.Instaloader()
            
            # تحميل بيانات البروفايل
            profile = Profile.from_username(L.context, username)
            
            # جمع المعلومات الأساسية
            full_name = profile.full_name if profile.full_name else username
            biography = profile.biography if profile.biography else "غير متوفر"
            followers = profile.followers
            following = profile.followees
            posts = profile.mediacount
            is_private = profile.is_private
            is_verified = profile.is_verified
            profile_pic = profile.profile_pic_url
            user_id = profile.userid  # ID الحساب
            
            # المعلومات الجديدة
            is_business = getattr(profile, 'is_business_account', False)
            business_category = getattr(profile, 'business_category_name', 'لا')
            external_url = getattr(profile, 'external_url', 'لا')
            
            # معالجة البيانات لتصبح أكثر وضوحاً
            business_status = "نعم ✅" if is_business else "لا ❌"
            private_status = "نعم 🔒" if is_private else "لا 🔓"
            verified_status = "نعم ✅" if is_verified else "لا ❌"
            
            # تنسيق الأرقام بفواصل
            followers_formatted = f"{followers:,}"
            following_formatted = f"{following:,}"
            posts_formatted = f"{posts:,}"
            
            caption = f"""*📊 معلومات حساب الانستجرام:*

• 📛 *الاسم:* {full_name}
• 🆔 *اليوزر:* @{username}
• 🔢 *الـ ID:* `{user_id}`
• 📝 *السيرة الذاتية:* {biography}

• 👥 *المتابعون:* {followers_formatted}
• 🔔 *يتابع:* {following_formatted}
• 📸 *المنشورات:* {posts_formatted}

• 🔒 *الحساب خاص:* {private_status}
• ✅ *الحساب موثوق:* {verified_status}
• 💼 *حساب أعمال:* {business_status}
• 📊 *فئة الأعمال:* {business_category}
• 🔗 *رابط خارجي:* {external_url if external_url != 'لا' else 'لا يوجد'}"""

            # إرسال الصورة مع المعلومات
            if profile_pic:
                await update.message.reply_photo(
                    photo=profile_pic,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(caption, parse_mode="Markdown")
                
            await loading_msg.delete()
            
        except ProfileNotExistsException:
            await loading_msg.edit_text(
                f"*❌ الحساب غير موجود:* `{username}`",
                parse_mode="Markdown"
            )
        except ConnectionException:
            await loading_msg.edit_text(
                "❌ حدث خطأ في الاتصال بإنستجرام. يرجى المحاولة مرة أخرى لاحقًا."
            )
        except Exception as e:
            await loading_msg.edit_text(
                f"*❌ حدث خطأ أثناء جلب المعلومات:*\n\n{str(e)}",
                parse_mode="Markdown"
            )
        
        context.user_data["awaiting_insta_username"] = False
        return

# خدمة معلومات انستجرام المتقدمة
async def insta_info_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "📊 **معلومات حساب انستجرام المتقدمة**\n\n"
        "أرسل لي معرف حساب الانستجرام بدون علامة @\n\n"
        "*المعلومات المتوفرة:*\n"
        "• 🆔 الرقم التعريفي (ID)\n"
        "• 💼 نوع الحساب (أعمال/عادي)\n" 
        "• 📊 فئة الأعمال\n"
        "• 🔗 الروابط الخارجية\n"
        "• 📈 الإحصائيات الكاملة\n\n"
        "أرسل المعرف الآن:"
    )
    
    context.user_data["awaiting_insta_username"] = True
# إنشاء لوحة المفاتيح الرئيسية مع الترتيب المطلوب
def create_main_keyboard(user_id):
    data = load_data()
    
    keyboard = []
    
    # إضافة أزرار المواقع أولاً
    buttons_list = []
    for btn in data["buttons"]:
        buttons_list.append(InlineKeyboardButton(
            btn["text"], 
            web_app=WebAppInfo(url=btn["url"])
        ))
    
    # ترتيب أزرار المواقع في أعمدة
    if buttons_list:
        keyboard.extend(arrange_buttons_in_columns(buttons_list))
    
    # إضافة أزرار الخدمات حسب الترتيب المحدد
    services_order = data.get("services_order", ["translation", "visa", "image", "video", "tiktok", "file_check", "site_download", "shortener", "insta_info"])
    service_buttons = []
    
    for service in services_order:
        if service == "translation":
            service_buttons.append(InlineKeyboardButton("خدمة الترجمة 🌐", callback_data="translation_service"))
        elif service == "visa":
            service_buttons.append(InlineKeyboardButton("توليد فيزا 💳", callback_data="generate_visa"))
        elif service == "image":
            service_buttons.append(InlineKeyboardButton("إنشاء صورة 🎨", callback_data="generate_image"))
        elif service == "video":
            service_buttons.append(InlineKeyboardButton("إنشاء فيديو 🎬", callback_data="generate_video"))
        elif service == "tiktok":
            service_buttons.append(InlineKeyboardButton("معلومات تيك توك 📱", callback_data="tiktok_service"))
        elif service == "file_check":
            service_buttons.append(InlineKeyboardButton("فحص الملفات 🔍", callback_data="file_check_service"))
        elif service == "site_download":
            service_buttons.append(InlineKeyboardButton("سحب ملفات الموقع 🌐", callback_data="site_download_service"))
        elif service == "shortener":
            service_buttons.append(InlineKeyboardButton("اختصار الروابط 🔗", callback_data="shortener_service"))
        elif service == "insta_info":
            service_buttons.append(InlineKeyboardButton("معلومات انستجرام 📷", callback_data="insta_info_service"))
    
    # ترتيب أزرار الخدمات في أعمدة
    if service_buttons:
        keyboard.extend(arrange_buttons_in_columns(service_buttons))
    
    # إضافة الأزرار الثابتة الجديدة
    keyboard.append([InlineKeyboardButton("صيد يوزرات انستا 🎯", callback_data="instagram_hunt")])
    keyboard.append([InlineKeyboardButton("المزيد من المميزات 🦾", url=f"https://t.me/Ss1_5_bot")])
    keyboard.append([InlineKeyboardButton("مطور البوت 👑", url=f"https://t.me/{DEVELOPER_USERNAME.replace('@', '')}")])
    
    # إضافة زر الإدارة للمشرف فقط
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton("الإدارة ⚙️", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)

# أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    reply_markup = create_main_keyboard(user_id)
    
    await update.message.reply_text(
        "مرحباً! يمكنك التمتع بالخدمات واختيار ما يناسبك من الخيارات المتاحة:",
        reply_markup=reply_markup
    )

# التحقق من الاشتراك
async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك
    if await check_subscription(update, context, user_id):
        await query.message.edit_text("✅ أنت مشترك في جميع القنوات! يمكنك الآن استخدام البوت.")
        # إعادة تحميل القائمة الرئيسية بعد التأكد من الاشتراك
        await start_from_callback(update, context)

# بدء من callback
async def start_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    reply_markup = create_main_keyboard(user_id)
    
    await query.message.edit_text(
        "مرحباً! هذه قائمة الخدمات المتاحة:",
        reply_markup=reply_markup
    )

# توليد فيزا
async def generate_visa_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    card_number, expiry, cvv, card_holder = generate_realistic_visa()
    
    await query.message.reply_text(
        f"💳 **بطاقة فيزا محاكاة:**\n\n"
        f"**الرقم:** `{card_number}`\n"
        f"**تاريخ الانتهاء:** `{expiry}`\n"
        f"**CVV:** `{cvv}`\n"
        f"**حامل البطاقة:** `{card_holder}`\n\n",
        parse_mode="Markdown"
    )

# إنشاء صورة بالذكاء الاصطناعي
async def generate_image_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "🎨 **إنشاء صورة بالذكاء الاصطناعي**\n\n"
        "أرسل لي وصفاً للصورة التي تريد إنشاءها.\n\n"
        "مثال:\n"
        "• منظر غروب الشمس على البحر\n"
        "• قطة لطيفة تجلس في الحديقة\n"
        "• منزل حديث في الغابة\n\n"
        "أرسل الوصف الآن:"
    )
    
    context.user_data["awaiting_image_prompt"] = True

# إنشاء فيديو بالذكاء الاصطناعي
async def generate_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    await query.message.edit_text(
        "🎬 **إنشاء فيديو من النص**\n\n"
        "أرسل لي وصفاً للفيديو الذي تريد إنشاءه.\n\n"
        "مثال:\n"
        "• a boy running in the rain cinematic 4k\n"
        "• sunset over the ocean slow motion\n"
        "• futuristic city at night high quality\n\n"
        "⏰ ملاحظة: إنشاء الفيديو قد يستغرق من 2-10 دقائق\n\n"
        "أرسل الوصف الآن:"
    )
    
    context.user_data["awaiting_video_prompt"] = True

# صيد يوزرات انستجرام
async def instagram_hunt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    keyboard = [
        [InlineKeyboardButton("🔍 يوزرات خماسية (5 أحرف)", callback_data='insta_5char')],
        [InlineKeyboardButton("🎯 يوزرات رباعية سهلة (4 أحرف + رمزين)", callback_data='insta_easy4char')],
        [InlineKeyboardButton("🔍 يوزرات خاصة (6 أحرف)", callback_data='insta_special')],
        [InlineKeyboardButton("العودة ↩️", callback_data='back_to_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "🎯 اختر نوع اليوزرات التي تريد صيدها:\n\n"
        "• يوزرات خماسية: 5 أحرف (عشوائي مع/بدون رموز)\n"
        "• يوزرات رباعية سهلة: 4 أحرف + رمزين (سهلة الصيد)\n"
        "• يوزرات خاصة: 6 أحرف (عشوائي مع/بدون رموز)\n\n"
        "🔍 البوت سيبحث حتى يعثر على 5 يوزرات متاحة",
        reply_markup=reply_markup
    )

# معالجة صيد اليوزرات
async def handle_instagram_hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    hunt_type = query.data.split('_')[1]
    
    if user_sessions.get(user_id, False):
        await query.message.edit_text("⚠️ هناك عملية صيد جارية بالفعل!")
        return
    
    def start_hunt():
        instagram_check_process(user_id, context.application, hunt_type)
    
    thread = threading.Thread(target=start_hunt)
    thread.start()
    
    await query.message.edit_text("🎯 بدأ الصيد! جاري البحث عن يوزرات متاحة...")

# خدمة الترجمة
async def translation_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    # إنشاء لوحة اختيار اللغة المصدر
    keyboard = []
    lang_list = list(SUPPORTED_LANGUAGES.keys())
    
    for i in range(0, len(lang_list), 2):
        row = []
        if i < len(lang_list):
            row.append(InlineKeyboardButton(lang_list[i], callback_data=f"src_lang_{SUPPORTED_LANGUAGES[lang_list[i]]}"))
        if i+1 < len(lang_list):
            row.append(InlineKeyboardButton(lang_list[i+1], callback_data=f"src_lang_{SUPPORTED_LANGUAGES[lang_list[i+1]]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("إلغاء ❌", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "اختر اللغة المصدر للنص الذي تريد ترجمته:",
        reply_markup=reply_markup
    )

# اختيار اللغة المصدر
async def choose_source_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    lang_code = query.data.split("_")[2]
    context.user_data["translation_source"] = lang_code
    
    # إنشاء لوحة اختيار اللغة الهدف
    keyboard = []
    lang_list = list(SUPPORTED_LANGUAGES.keys())
    
    for i in range(0, len(lang_list), 2):
        row = []
        if i < len(lang_list):
            row.append(InlineKeyboardButton(lang_list[i], callback_data=f"tgt_lang_{SUPPORTED_LANGUAGES[lang_list[i]]}"))
        if i+1 < len(lang_list):
            row.append(InlineKeyboardButton(lang_list[i+1], callback_data=f"tgt_lang_{SUPPORTED_LANGUAGES[lang_list[i+1]]}"))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("إلغاء ❌", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # الحصول على اسم اللغة المصدر
    src_lang_name = [name for name, code in SUPPORTED_LANGUAGES.items() if code == lang_code][0]
    
    await query.message.edit_text(
        f"لقد اخترت {src_lang_name} كلغة مصدر. الآن اختر اللغة الهدف:",
        reply_markup=reply_markup
    )

# اختيار اللغة الهدف وطلب النص للترجمة
async def choose_target_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    lang_code = query.data.split("_")[2]
    context.user_data["translation_target"] = lang_code
    
    # الحصول على أسماء اللغات
    src_lang_code = context.user_data["translation_source"]
    src_lang_name = [name for name, code in SUPPORTED_LANGUAGES.items() if code == src_lang_code][0]
    tgt_lang_name = [name for name, code in SUPPORTED_LANGUAGES.items() if code == lang_code][0]
    
    await query.message.edit_text(
        f"لقد اخترت الترجمة من {src_lang_name} إلى {tgt_lang_name}.\n\n"
        "أرسل الآن النص الذي تريد ترجمته:"
    )
    
    context.user_data["awaiting_translation"] = True

# ترجمة النص باستخدام MyMemory API
async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_translation", False):
        text_to_translate = update.message.text
        
        if not text_to_translate.strip():
            await update.message.reply_text("يرجى إرسال نص صالح للترجمة.")
            return
        
        src_lang = context.user_data.get("translation_source", "auto")
        tgt_lang = context.user_data.get("translation_target", "en")
        
        # استخدام API MyMemory للترجمة
        async with aiohttp.ClientSession() as session:
            encoded_text = quote(text_to_translate)
            url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair={src_lang}|{tgt_lang}"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        translated_text = data["responseData"]["translatedText"]
                        
                        # الحصول على أسماء اللغات
                        src_lang_name = [name for name, code in SUPPORTED_LANGUAGES.items() if code == src_lang][0]
                        tgt_lang_name = [name for name, code in SUPPORTED_LANGUAGES.items() if code == tgt_lang][0]
                        
                        await update.message.reply_text(
                            f"الترجمة من {src_lang_name} إلى {tgt_lang_name}:\n\n"
                            f"النص الأصلي: {text_to_translate}\n\n"
                            f"النص المترجم: {translated_text}"
                        )
                    else:
                        await update.message.reply_text("عذراً، حدث خطأ أثناء الترجمة. يرجى المحاولة مرة أخرى.")
            except Exception as e:
                logging.error(f"Translation error: {e}")
                await update.message.reply_text("عذراً، حدث خطأ أثناء الترجمة. يرجى المحاولة مرة أخرى.")
        
        context.user_data["awaiting_translation"] = False

# معالجة إنشاء الصور
async def handle_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_image_prompt", False):
        prompt = update.message.text
        
        if not prompt.strip():
            await update.message.reply_text("يرجى إرسال وصف صالح للصورة.")
            return
        
        await update.message.reply_text(f"🎨 جاري إنشاء صورة للوصف: {prompt}\nيرجى الانتظار...")
        
        try:
            # ترجمة النص إلى الإنجليزية
            translated_prompt = translate_to_english(prompt)
            
            # إنشاء الصورة
            image_data = create_ai_image(translated_prompt)
            
            # إرسال الصورة للمستخدم
            await update.message.reply_photo(
                photo=image_data, 
                caption=f"الصورة المنشأة للوصف: {prompt}"
            )
            
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء إنشاء الصورة: {str(e)}")
        
        context.user_data["awaiting_image_prompt"] = False
        return

# لوحة تحكم المشرف
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.message.reply_text("ليس لديك صلاحية للوصول إلى هذه اللوحة.")
        return
    
    keyboard = [
        [InlineKeyboardButton("إضافة زر ➕", callback_data="add_button")],
        [InlineKeyboardButton("حذف زر ➖", callback_data="delete_button")],
        [InlineKeyboardButton("تغيير عدد الأعمدة 🔢", callback_data="change_columns")],
        [InlineKeyboardButton("ترتيب الخدمات 🔄", callback_data="reorder_services")],
        [InlineKeyboardButton("إدارة القنوات 📢", callback_data="manage_channels")],
        [InlineKeyboardButton("العودة ↩️", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "لوحة تحكم المشرف:",
        reply_markup=reply_markup
    )

# إعادة ترتيب الخدمات
async def reorder_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    keyboard = [
        [InlineKeyboardButton("ترتيب افتراضي", callback_data="set_order_default")],
        [InlineKeyboardButton("ترتيب مخصص", callback_data="set_order_custom")],
        [InlineKeyboardButton("العودة ↩️", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    data = load_data()
    current_order = data.get("services_order", ["translation", "visa", "image", "video", "tiktok", "file_check", "site_download", "shortener", "insta_info"])
    
    order_text = "الترتيب الحالي للخدمات:\n\n"
    for i, service in enumerate(current_order, 1):
        if service == "translation":
            order_text += f"{i}. خدمة الترجمة 🌐\n"
        elif service == "visa":
            order_text += f"{i}. توليد فيزا 💳\n"
        elif service == "image":
            order_text += f"{i}. إنشاء صورة 🎨\n"
        elif service == "video":
            order_text += f"{i}. إنشاء فيديo 🎬\n"
        elif service == "tiktok":
            order_text += f"{i}. معلومات تيك توك 📱\n"
        elif service == "file_check":
            order_text += f"{i}. فحص الملفات 🔍\n"
        elif service == "site_download":
            order_text += f"{i}. سحب ملفات الموقع 🌐\n"
        elif service == "shortener":
            order_text += f"{i}. اختصار الروابط 🔗\n"
        elif service == "insta_info":
            order_text += f"{i}. معلومات انستجرام 📷\n"
    
    await query.message.edit_text(
        f"{order_text}\nاختر طريقة الترتيب:",
        reply_markup=reply_markup
    )

# تعيين الترتيب الافتراضي
async def set_order_default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    data = load_data()
    data["services_order"] = ["translation", "visa", "image", "video", "tiktok", "file_check", "site_download", "shortener", "insta_info"]
    save_data(data)
    
    await query.message.edit_text(
        "✅ تم تعيين الترتيب الافتراضي للخدمات:\n1. الترجمة\n2. الفيزا\n3. الصور\n4. الفيديو\n5. تيك توك\n6. فحص الملفات\n7. سحب ملفات الموقع\n8. اختصار الروابط\n9. معلومات انستجرام"
    )

# تعيين ترتيب مخصوص
async def set_order_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    keyboard = [
        [InlineKeyboardButton("الترجمة أولاً", callback_data="custom_order_translation_first")],
        [InlineKeyboardButton("الفيزا أولاً", callback_data="custom_order_visa_first")],
        [InlineKeyboardButton("الصور أولاً", callback_data="custom_order_image_first")],
        [InlineKeyboardButton("الفيديو أولاً", callback_data="custom_order_video_first")],
        [InlineKeyboardButton("تيك توك أولاً", callback_data="custom_order_tiktok_first")],
        [InlineKeyboardButton("فحص الملفات أولاً", callback_data="custom_order_file_check_first")],
        [InlineKeyboardButton("سحب الموقع أولاً", callback_data="custom_order_site_download_first")],
        [InlineKeyboardButton("اختصار الروابط أولاً", callback_data="custom_order_shortener_first")],
        [InlineKeyboardButton("معلومات انستجرام أولاً", callback_data="custom_order_insta_info_first")],
        [InlineKeyboardButton("العودة ↩️", callback_data="reorder_services")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "اختر الخدمة التي تريد أن تظهر أولاً:",
        reply_markup=reply_markup
    )

# معالجة الترتيب المخصص
async def handle_custom_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    order_type = query.data.split("_")[3]  # first, second, third
    
    data = load_data()
    
    if order_type == "translation_first":
        data["services_order"] = ["translation", "visa", "image", "video", "tiktok", "file_check", "site_download", "shortener", "insta_info"]
        message = "الترجمة ← الفيزا ← الصور ← الفيديو ← تيك توك ← فحص الملفات ← سحب الموقع ← اختصار الروابط ← معلومات انستجرام"
    elif order_type == "visa_first":
        data["services_order"] = ["visa", "translation", "image", "video", "tiktok", "file_check", "site_download", "shortener", "insta_info"]
        message = "الفيزا ← الترجمة ← الصور ← الفيديو ← تيك توك ← فحص الملفات ← سحب الموقع ← اختصار الروابط ← معلومات انستجرام"
    elif order_type == "image_first":
        data["services_order"] = ["image", "translation", "visa", "video", "tiktok", "file_check", "site_download", "shortener", "insta_info"]
        message = "الصور ← الترجمة ← الفيزا ← الفيديو ← تيك توك ← فحص الملفات ← سحب الموقع ← اختصار الروابط ← معلومات انستجرام"
    elif order_type == "video_first":
        data["services_order"] = ["video", "translation", "visa", "image", "tiktok", "file_check", "site_download", "shortener", "insta_info"]
        message = "الفيديو ← الترجمة ← الفيزا ← الصور ← تيك توك ← فحص الملفات ← سحب الموقع ← اختصار الروابط ← معلومات انستجرام"
    elif order_type == "tiktok_first":
        data["services_order"] = ["tiktok", "translation", "visa", "image", "video", "file_check", "site_download", "shortener", "insta_info"]
        message = "تيك توك ← الترجمة ← الفيزا ← الصور ← الفيديو ← فحص الملفات ← سحب الموقع ← اختصار الروابط ← معلومات انستجرام"
    elif order_type == "file_check_first":
        data["services_order"] = ["file_check", "translation", "visa", "image", "video", "tiktok", "site_download", "shortener", "insta_info"]
        message = "فحص الملفات ← الترجمة ← الفيزا ← الصور ← الفيديو ← تيك توك ← سحب الموقع ← اختصار الروابط ← معلومات انستجرام"
    elif order_type == "site_download_first":
        data["services_order"] = ["site_download", "translation", "visa", "image", "video", "tiktok", "file_check", "shortener", "insta_info"]
        message = "سحب الموقع ← الترجمة ← الفيزا ← الصور ← الفيديو ← تيك توك ← فحص الملفات ← اختصار الروابط ← معلومات انستجرام"
    elif order_type == "shortener_first":
        data["services_order"] = ["shortener", "translation", "visa", "image", "video", "tiktok", "file_check", "site_download", "insta_info"]
        message = "اختصار الروابط ← الترجمة ← الفيزا ← الصور ← الفيديو ← تيك توك ← فحص الملفات ← سحب الموقع ← معلومات انستجرام"
    elif order_type == "insta_info_first":
        data["services_order"] = ["insta_info", "translation", "visa", "image", "video", "tiktok", "file_check", "site_download", "shortener"]
        message = "معلومات انستجرام ← الترجمة ← الفيزا ← الصور ← الفيديو ← تيك توك ← فحص الملفات ← سحب الموقع ← اختصار الروابط"
    
    save_data(data)
    
    await query.message.edit_text(
        f"✅ تم تعيين الترتيب الجديد: {message}"
    )

# إدارة القنوات
async def manage_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    keyboard = [
        [InlineKeyboardButton("إضافة قناة ➕", callback_data="add_channel")],
        [InlineKeyboardButton("حذف قناة ➖", callback_data="delete_channel")],
        [InlineKeyboardButton("عرض القنوات 👁️", callback_data="view_channels")],
        [InlineKeyboardButton("العودة ↩️", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "إدارة قنوات الاشتراك الإجباري:",
        reply_markup=reply_markup
    )

# إضافة قناة
async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    await query.message.edit_text(
        "أرسل معرف القناة أو الرابط بالتنسيق التالي:\n\n"
        "معرف القناة - اسم القناة\n\n"
        "مثال:\n"
        "@channel_username - اسم القناة\n"
        "أو\n"
        "123456789 - اسم القناة (للقنوات الخاصة)"
    )
    
    context.user_data["awaiting_channel"] = True

# حذف قناة
async def delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    channels_data = load_channels()
    
    if not channels_data["channels"]:
        await query.message.edit_text("لا توجد قنوات لحذفها.")
        return
    
    keyboard = []
    for i, channel in enumerate(channels_data["channels"]):
        keyboard.append([InlineKeyboardButton(
            f"{channel['name']}", 
            callback_data=f"delete_ch_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("إلغاء ❌", callback_data="manage_channels")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "اختر القناة التي تريد حذفها:",
        reply_markup=reply_markup
    )

# عرض القنوات
async def view_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    channels_data = load_channels()
    
    if not channels_data["channels"]:
        await query.message.edit_text("لا توجد قنوات مضافة.")
        return
    
    channels_text = "📢 قنوات الاشتراك الإجباري:\n\n"
    for i, channel in enumerate(channels_data["channels"], 1):
        channel_id = channel["id"]
        channel_name = channel["name"]
        username = channel.get("username", f"ID: {channel_id}")
        channels_text += f"{i}. {channel_name} - {username}\n"
    
    await query.message.edit_text(
        channels_text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("العودة ↩️", callback_data="manage_channels")]])
    )

# تأكيد حذف القناة
async def confirm_delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    index = int(query.data.split("_")[2])
    channels_data = load_channels()
    
    if 0 <= index < len(channels_data["channels"]):
        deleted_channel = channels_data["channels"].pop(index)
        save_channels(channels_data)
        
        await query.message.edit_text(
            f"تم حذف القناة: {deleted_channel['name']}"
        )
    else:
        await query.message.edit_text("حدث خطأ أثناء الحذف.")

# معالجة إضافة زر جديد
async def add_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    await query.message.edit_text(
        "أرسل نص الزر والرابط بالتنسيق التالي:\n\n"
        "نص الزر - الرابط\n\n"
        "مثال:\n"
        "جوجل - https://google.com\n"
        "فيسبوك - https://facebook.com\n"
        "يوتيوب - https://youtube.com"
    )
    
    # حفظ حالة المستخدم للإدخال التالي
    context.user_data["awaiting_button"] = True

# معالجة حذف زر
async def delete_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    data = load_data()
    
    if not data["buttons"]:
        await query.message.edit_text("لا توجد أزرار لحذفها.")
        return
    
    # ترتيب أزرار الحذف في أعمدة
    buttons_list = []
    for i, btn in enumerate(data["buttons"]):
        buttons_list.append(InlineKeyboardButton(
            f"{btn['text']}", 
            callback_data=f"delete_{i}"
        ))
    
    keyboard = arrange_buttons_in_columns(buttons_list, columns=2)
    keyboard.append([InlineKeyboardButton("إلغاء ❌", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "اختر الزر الذي تريد حذفه:",
        reply_markup=reply_markup
    )

# معالجة تغيير عدد الأعمدة
async def change_columns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    keyboard = [
        [InlineKeyboardButton("عمود واحد 1", callback_data="set_columns_1")],
        [InlineKeyboardButton("عمودين 2", callback_data="set_columns_2")],
        [InlineKeyboardButton("ثلاثة أعمدة 3", callback_data="set_columns_3")],
        [InlineKeyboardButton("إلغاء ❌", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"عدد الأعمدة الحالي: {COLUMNS}\nاختر عدد الأعمدة الجديد:",
        reply_markup=reply_markup
    )

# تأكيد الحذف
async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    index = int(query.data.split("_")[1])
    data = load_data()
    
    if 0 <= index < len(data["buttons"]):
        deleted_btn = data["buttons"].pop(index)
        save_data(data)
        
        await query.message.edit_text(
            f"تم حذف الزر: {deleted_btn['text']} - {deleted_btn['url']}"
        )
    else:
        await query.message.edit_text("حدث خطأ أثناء الحذف.")

# تغيير عدد الأعمدة
async def set_columns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    global COLUMNS
    COLUMNS = int(query.data.split("_")[2])
    
    await query.message.edit_text(
        f"تم تغيير عدد الأعمدة إلى: {COLUMNS}"
    )

# معالجة الرسائل النصية (لإضافة أزرار جديدة أو الترجمة أو القنوات أو الصور أو الفيديو أو تيك توك أو فحص الملفات أو سحب الموقع)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # معالجة إضافة أزرار جديدة
    if context.user_data.get("awaiting_button", False) and is_admin(user_id):
        text = update.message.text
        
        # التحقق من وجود فاصلة بين النص والرابط
        if " - " not in text:
            await update.message.reply_text("التنسيق غير صحيح. يرجى استخدام: نص الزر - الرابط")
            return
        
        try:
            btn_text, url = text.split(" - ", 1)
            btn_text = btn_text.strip()
            url = url.strip()
            
            # التحقق من صحة الرابط
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            # إضافة الزر إلى البيانات
            data = load_data()
            data["buttons"].append({"text": btn_text, "url": url})
            save_data(data)
            
            context.user_data["awaiting_button"] = False
            await update.message.reply_text(f"تم إضافة الزر بنجاح: {btn_text} - {url}")
            
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ: {str(e)}")
        return
    
    # معالجة إضافة قنوات جديدة
    elif context.user_data.get("awaiting_channel", False) and is_admin(user_id):
        text = update.message.text
        
        # التحقق من وجود فاصلة بين المعرف والاسم
        if " - " not in text:
            await update.message.reply_text("التنسيق غير صحيح. يرجى استخدام: معرف القناة - اسم القناة")
            return
        
        try:
            channel_id, channel_name = text.split(" - ", 1)
            channel_id = channel_id.strip()
            channel_name = channel_name.strip()
            
            # معالجة معرف القناة
            channel_data = {"name": channel_name}
            
            if channel_id.startswith('@'):
                # إذا كان معرف مستخدم
                channel_data["username"] = channel_id[1:]
                # محاولة الحصول على ID من المعرف
                try:
                    chat = await context.bot.get_chat(channel_id)
                    channel_data["id"] = chat.id
                except Exception as e:
                    await update.message.reply_text(f"لا يمكن الوصول إلى القناة: {str(e)}")
                    return
            else:
                # إذا كان ID رقمي
                try:
                    channel_data["id"] = int(channel_id)
                    # التحقق من أن القناة موجودة
                    chat = await context.bot.get_chat(channel_data["id"])
                    if chat.username:
                        channel_data["username"] = chat.username
                except ValueError:
                    await update.message.reply_text("يجب أن يكون ID القناة رقماً أو يبدأ ب @")
                    return
                except Exception as e:
                    await update.message.reply_text(f"لا يمكن الوصول إلى القناة: {str(e)}")
                    return
            
            # إضافة القناة إلى البيانات
            channels_data = load_channels()
            channels_data["channels"].append(channel_data)
            save_channels(channels_data)
            
            context.user_data["awaiting_channel"] = False
            await update.message.reply_text(f"تم إضافة القناة بنجاح: {channel_name}")
            
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ: {str(e)}")
        return
    
    # معالجة الترجمة
    elif context.user_data.get("awaiting_translation", False):
        await translate_text(update, context)
        return
    
    # معالجة إنشاء الصور
    elif context.user_data.get("awaiting_image_prompt", False):
        await handle_image_generation(update, context)
        return
    
    # معالجة إنشاء الفيديو
    elif context.user_data.get("awaiting_video_prompt", False):
        await handle_video_generation(update, context)
        return
    
    # معالجة معلومات تيك توك
    elif context.user_data.get("awaiting_tiktok_username", False):
        await handle_tiktok_info(update, context)
        return
    
    # معالجة فحص الملفات
    elif context.user_data.get("awaiting_file_check", False):
        await handle_file_check(update, context)
        return
    
    # معالجة سحب ملفات الموقع
    elif context.user_data.get("awaiting_site_url", False):
        await handle_site_download(update, context)
        return
    
    # معالجة اختصار الروابط
    elif context.user_data.get("awaiting_shortener_url", False):
        await handle_shortener(update, context)
        return
    
    # معالجة معلومات انستجرام
    elif context.user_data.get("awaiting_insta_username", False):
        await handle_insta_info(update, context)
        return
    
    # إذا لم تكن الرسالة جزءاً من محادثة، نعيدها للقائمة الرئيسية
    else:
        await start(update, context)

# العودة للقائمة الرئيسية
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # التحقق من الاشتراك أولاً
    if not await check_subscription(update, context, user_id):
        return
    
    reply_markup = create_main_keyboard(user_id)
    
    await query.message.edit_text(
        "مرحباً! هذه قائمة الخدمات المتاحة:",
        reply_markup=reply_markup
    )

def main():
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إنشاء مجلد التحميل إذا لم يكن موجودًا
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(generate_visa_callback, pattern="^generate_visa$"))
    application.add_handler(CallbackQueryHandler(generate_image_callback, pattern="^generate_image$"))
    application.add_handler(CallbackQueryHandler(generate_video_callback, pattern="^generate_video$"))
    application.add_handler(CallbackQueryHandler(translation_service, pattern="^translation_service$"))
    application.add_handler(CallbackQueryHandler(tiktok_service_callback, pattern="^tiktok_service$"))
    application.add_handler(CallbackQueryHandler(file_check_service, pattern="^file_check_service$"))
    application.add_handler(CallbackQueryHandler(site_download_service, pattern="^site_download_service$"))
    application.add_handler(CallbackQueryHandler(shortener_service, pattern="^shortener_service$"))
    application.add_handler(CallbackQueryHandler(insta_info_service, pattern="^insta_info_service$"))
    application.add_handler(CallbackQueryHandler(instagram_hunt_callback, pattern="^instagram_hunt$"))
    application.add_handler(CallbackQueryHandler(handle_instagram_hunt, pattern="^insta_"))
    application.add_handler(CallbackQueryHandler(choose_source_language, pattern="^src_lang_"))
    application.add_handler(CallbackQueryHandler(choose_target_language, pattern="^tgt_lang_"))
    application.add_handler(CallbackQueryHandler(add_button, pattern="^add_button$"))
    application.add_handler(CallbackQueryHandler(delete_button, pattern="^delete_button$"))
    application.add_handler(CallbackQueryHandler(change_columns, pattern="^change_columns$"))
    application.add_handler(CallbackQueryHandler(confirm_delete, pattern="^delete_"))
    application.add_handler(CallbackQueryHandler(set_columns, pattern="^set_columns_"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))
    application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))
    application.add_handler(CallbackQueryHandler(manage_channels, pattern="^manage_channels$"))
    application.add_handler(CallbackQueryHandler(add_channel, pattern="^add_channel$"))
    application.add_handler(CallbackQueryHandler(delete_channel, pattern="^delete_channel$"))
    application.add_handler(CallbackQueryHandler(view_channels, pattern="^view_channels$"))
    application.add_handler(CallbackQueryHandler(confirm_delete_channel, pattern="^delete_ch_"))
    application.add_handler(CallbackQueryHandler(reorder_services, pattern="^reorder_services$"))
    application.add_handler(CallbackQueryHandler(set_order_default, pattern="^set_order_default$"))
    application.add_handler(CallbackQueryHandler(set_order_custom, pattern="^set_order_custom$"))
    application.add_handler(CallbackQueryHandler(handle_custom_order, pattern="^custom_order_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_message))
    
    # بدء البوت
    application.run_polling()

if __name__ == "__main__":
    main()
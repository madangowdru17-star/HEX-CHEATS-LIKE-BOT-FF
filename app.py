from flask import Flask, session
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson
import binascii
import aiohttp
import requests
import json
import like_pb2
import like_count_pb2
import uid_generator_pb2
import time
from collections import defaultdict
from datetime import datetime, timedelta
import random
import os
import urllib.parse
import jwt
import pickle
import threading
import hashlib
import secrets

# Create Flask app FIRST
app = Flask(__name__)
app.secret_key = 'hex-cheats-secret-key-2024'

# ============================================================
# SHARED DATA & FUNCTIONS
# ============================================================

TOKEN_CACHE = {}
KEY_LIMIT = 500
tracker = defaultdict(lambda: [0, time.time()])

LIKED_DATA_FILE = "liked_data.pkl"
liked_cache = defaultdict(set)
like_timestamps = {}

ACCOUNT_STATUS_FILE = "account_status.pkl"
account_status = {}

USERS_FILE = "users.pkl"
auto_like_users = []
user_stats = {}
like_history = []

USER_DB_FILE = "user_db.pkl"
user_db = {}
admin_codes = []

AUTO_LIKE_HOUR = 4
AUTO_LIKE_MINUTE = 0

RATE_LIMIT_DELAYS = [0.02, 0.05, 0.08, 0.1]

REGION_URLS = {
    'IND': 'https://client.ind.freefiremobile.com',
    'BR': 'https://client.us.freefiremobile.com',
    'US': 'https://client.us.freefiremobile.com',
    'SAC': 'https://client.us.freefiremobile.com',
    'NA': 'https://client.us.freefiremobile.com',
    'BD': 'https://clientbp.ggpolarbear.com',
    'RU': 'https://clientbp.ggpolarbear.com',
    'MENA': 'https://clientbp.ggpolarbear.com'
}

activity_logs = []

def add_activity_log(message, log_type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = {'time': timestamp, 'type': log_type, 'message': message}
    activity_logs.append(entry)
    if len(activity_logs) > 100:
        activity_logs.pop(0)
    print(f"[{timestamp}] [{log_type.upper()}] {message}")

def load_user_db():
    global user_db, admin_codes
    try:
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, 'rb') as f:
                data = pickle.load(f)
                user_db = data.get('users', {})
                admin_codes = data.get('codes', [])
                print(f"Loaded {len(user_db)} users, {len(admin_codes)} codes")
        else:
            user_db = {}
            admin_codes = []
            save_user_db()
    except Exception as e:
        print(f"Error loading user db: {e}")
        user_db = {}
        admin_codes = []

def save_user_db():
    try:
        data = {
            'users': user_db,
            'codes': admin_codes
        }
        with open(USER_DB_FILE, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error saving user db: {e}")

def generate_admin_code():
    code = secrets.token_hex(8).upper()
    admin_codes.append(code)
    save_user_db()
    add_activity_log(f"Generated admin code: {code}", "info")
    return code

def verify_admin_code(code):
    if code in admin_codes:
        admin_codes.remove(code)
        save_user_db()
        add_activity_log(f"Admin code used: {code}", "success")
        return True
    return False

def create_user(email, password):
    if email in user_db:
        return False
    hashed = hashlib.sha256(password.encode()).hexdigest()
    user_db[email] = {
        'password': hashed,
        'codes': [],
        'usage': 0,
        'last_active': datetime.now().isoformat(),
        'auto_like_targets': [],
        'created_at': datetime.now().isoformat(),
        'auto_like_unlocked': False
    }
    save_user_db()
    add_activity_log(f"New user registered: {email}", "info")
    return True

def verify_user(email, password):
    if email not in user_db:
        return False
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if user_db[email]['password'] == hashed:
        user_db[email]['last_active'] = datetime.now().isoformat()
        save_user_db()
        return True
    return False

def unlock_user_auto_like(email):
    if email in user_db:
        user_db[email]['auto_like_unlocked'] = True
        save_user_db()
        add_activity_log(f"Auto-like unlocked for {email}", "info")
        return True
    return False

def add_auto_like_target(email, target_uid):
    if email in user_db:
        if target_uid not in user_db[email]['auto_like_targets']:
            user_db[email]['auto_like_targets'].append(target_uid)
            save_user_db()
            add_activity_log(f"{email} added target {target_uid} to auto-like", "info")
            return True
    return False

def remove_auto_like_target(email, target_uid):
    if email in user_db and target_uid in user_db[email]['auto_like_targets']:
        user_db[email]['auto_like_targets'].remove(target_uid)
        save_user_db()
        add_activity_log(f"{email} removed target {target_uid} from auto-like", "info")
        return True
    return False

def load_users():
    global auto_like_users, user_stats, like_history
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    auto_like_users = data.get('users', [])
                    user_stats = data.get('stats', {})
                    like_history = data.get('history', [])
                else:
                    auto_like_users = data
                    user_stats = {}
                    like_history = []
                print(f"Loaded {len(auto_like_users)} users, {len(like_history)} history entries")
        else:
            auto_like_users = []
            user_stats = {}
            like_history = []
            save_users()
    except Exception as e:
        print(f"Error loading users: {e}")
        auto_like_users = []
        user_stats = {}
        like_history = []

def save_users():
    try:
        data = {
            'users': auto_like_users,
            'stats': user_stats,
            'history': like_history[-100:]
        }
        with open(USERS_FILE, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error saving users: {e}")

def load_account_status():
    global account_status
    try:
        if os.path.exists(ACCOUNT_STATUS_FILE):
            with open(ACCOUNT_STATUS_FILE, 'rb') as f:
                account_status = pickle.load(f)
                print(f"Loaded account status: {len(account_status)} accounts")
    except Exception as e:
        print(f"Error loading account status: {e}")
        account_status = {}

def save_account_status():
    try:
        with open(ACCOUNT_STATUS_FILE, 'wb') as f:
            pickle.dump(account_status, f)
    except Exception as e:
        print(f"Error saving account status: {e}")

def load_liked_data():
    global liked_cache, like_timestamps
    try:
        if os.path.exists(LIKED_DATA_FILE):
            with open(LIKED_DATA_FILE, 'rb') as f:
                data = pickle.load(f)
                liked_cache = data.get('liked_cache', defaultdict(set))
                like_timestamps = data.get('like_timestamps', {})
                print(f"Loaded liked data: {len(liked_cache)} entries")
    except Exception as e:
        print(f"Error loading liked data: {e}")
        liked_cache = defaultdict(set)
        like_timestamps = {}

def save_liked_data():
    try:
        data = {'liked_cache': liked_cache, 'like_timestamps': like_timestamps}
        with open(LIKED_DATA_FILE, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error saving liked data: {e}")

def is_uid_liked_in_24hrs(target_uid, account_uid):
    key = f"{account_uid}:{target_uid}"
    if key in like_timestamps:
        last_liked = datetime.fromtimestamp(like_timestamps[key])
        if datetime.now() - last_liked < timedelta(hours=24):
            return True
    return False

def mark_as_liked(target_uid, account_uid):
    key = f"{account_uid}:{target_uid}"
    like_timestamps[key] = datetime.now().timestamp()
    liked_cache[target_uid].add(account_uid)
    save_liked_data()

def update_user_stats(target_uid, likes_given, username="", current_likes=0):
    if target_uid not in user_stats:
        user_stats[target_uid] = {'total_likes': 0, 'today_likes': 0, 'last_like': None,
                                  'username': '', 'current_likes': 0}
    user_stats[target_uid]['total_likes'] += likes_given
    user_stats[target_uid]['today_likes'] += likes_given
    user_stats[target_uid]['last_like'] = datetime.now().isoformat()
    if username:
        user_stats[target_uid]['username'] = username
    if current_likes > 0:
        user_stats[target_uid]['current_likes'] = current_likes
    save_users()

def add_to_history(target_uid, likes_sent, before, after, username, server="IND"):
    entry = {
        'uid': target_uid,
        'username': username,
        'likes_sent': likes_sent,
        'before': before,
        'after': after,
        'verified_added': after - before,
        'server': server,
        'timestamp': datetime.now().isoformat()
    }
    like_history.append(entry)
    save_users()
    add_activity_log(f"{username} | +{likes_sent} likes | Verified: {after - before}", "success")

def get_next_reset_time():
    now = datetime.now()
    reset_time = datetime(now.year, now.month, now.day, AUTO_LIKE_HOUR, AUTO_LIKE_MINUTE, 0)
    if now >= reset_time:
        reset_time += timedelta(days=1)
    return reset_time

def daily_reset_task():
    while True:
        try:
            next_reset = get_next_reset_time()
            wait_seconds = (next_reset - datetime.now()).total_seconds()
            if wait_seconds > 0:
                print(f"Next reset at: {next_reset.strftime('%Y-%m-%d %H:%M:%S')} IST")
                time.sleep(wait_seconds)
            print(f"Performing daily reset at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST")
            reset_all_data()
        except Exception as e:
            print(f"Reset task error: {e}")
            time.sleep(60)

def reset_all_data():
    global liked_cache, like_timestamps, account_status, user_stats
    liked_cache.clear()
    like_timestamps.clear()
    for uid in account_status:
        account_status[uid]['status'] = 'reset'
        account_status[uid]['reset_time'] = datetime.now().isoformat()
    for uid in user_stats:
        user_stats[uid]['today_likes'] = 0
    save_liked_data()
    save_account_status()
    save_users()

def load_accounts(server_name):
    try:
        server_map = {
            'IND': 'account_ind.txt',
            'BR': 'account_br.txt',
            'US': 'account_br.txt',
            'SAC': 'account_br.txt',
            'NA': 'account_br.txt',
            'BD': 'account_bd.txt',
            'RU': 'account_bd.txt',
            'MENA': 'account_mena.txt'
        }
        filename = server_map.get(server_name, 'account_ind.txt')
        if not os.path.exists(filename):
            return []
        accounts = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    parts = line.split(':', 1)
                    uid = parts[0].strip()
                    password = parts[1].strip()
                    if uid and password and uid.isdigit():
                        accounts.append({"uid": uid, "password": password})
        return accounts
    except Exception as e:
        print(f"Error loading accounts: {e}")
        return []

async def get_user_info(target_uid, server_name="IND"):
    try:
        accounts = load_accounts(server_name)
        if not accounts:
            return None
        check_token = None
        for account in accounts[:3]:
            token = await get_valid_token(account['uid'], account['password'], server_name)
            if token:
                check_token = token
                break
        if not check_token:
            return None
        encrypted_uid = enc(target_uid)
        info = get_player_info(encrypted_uid, server_name, check_token)
        if info:
            try:
                data = json.loads(MessageToJson(info))
                account_info = data.get('AccountInfo', {})
                return {
                    'uid': account_info.get('UID', target_uid),
                    'name': account_info.get('PlayerNickname', 'Unknown'),
                    'likes': int(account_info.get('Likes', 0))
                }
            except:
                return None
        return None
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None

async def generate_jwt_token(uid, password):
    try:
        encoded_password = urllib.parse.quote(password)
        url = f"https://ff-jwt-gen-api.lovable.app/api/public/token?uid={uid}&password={encoded_password}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=8) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict):
                        if 'jwt_token' in data:
                            return data['jwt_token']
                        elif 'token' in data:
                            return data['token']
                return None
    except Exception as e:
        print(f"Error generating JWT: {e}")
        return None

async def get_valid_token(uid, password, server_name="IND"):
    cache_key = f"{uid}:{server_name}"
    if cache_key in TOKEN_CACHE:
        cached = TOKEN_CACHE[cache_key]
        remaining = (cached["expires_at"] - datetime.utcnow()).total_seconds()
        if remaining > 1800:
            return cached["token"]
    token = await generate_jwt_token(uid, password)
    if not token:
        return None
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        TOKEN_CACHE[cache_key] = {"token": token, "expires_at": datetime.utcfromtimestamp(exp)}
    except:
        TOKEN_CACHE[cache_key] = {"token": token, "expires_at": datetime.utcnow() + timedelta(hours=24)}
    return token

def encrypt_message(plaintext):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    return binascii.hexlify(cipher.encrypt(padded_message)).decode('utf-8')

def create_protobuf_message(user_id, region):
    message = like_pb2.like()
    message.uid = int(user_id)
    message.region = region
    return message.SerializeToString()

async def send_like_fast(encrypted_uid, token, url, account_uid, server_name):
    edata = bytes.fromhex(encrypted_uid)
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB54"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=edata, headers=headers, timeout=3) as response:
                if response.status == 200:
                    return True
                return False
    except:
        return False

async def send_likes_all_accounts(target_uid, server_name, url):
    accounts = load_accounts(server_name)
    if not accounts:
        return {'success': 0, 'failed': 0, 'total': 0}
    
    fresh_accounts = []
    skipped = 0
    for acc in accounts:
        if is_uid_liked_in_24hrs(target_uid, acc['uid']):
            skipped += 1
        else:
            fresh_accounts.append(acc)
    
    if not fresh_accounts:
        return {'success': 0, 'failed': 0, 'total': len(accounts), 'skipped': skipped}
    
    accounts_to_use = fresh_accounts
    protobuf_message = create_protobuf_message(target_uid, server_name)
    encrypted_uid = encrypt_message(protobuf_message)
    
    token_tasks = []
    for acc in accounts_to_use:
        token_tasks.append(get_valid_token(acc['uid'], acc['password'], server_name))
    tokens = await asyncio.gather(*token_tasks, return_exceptions=True)
    
    like_tasks = []
    for i, acc in enumerate(accounts_to_use):
        if isinstance(tokens[i], str) and tokens[i]:
            like_tasks.append(send_like_fast(encrypted_uid, tokens[i], url, acc['uid'], server_name))
        else:
            like_tasks.append(asyncio.sleep(0, result=False))
    
    results = await asyncio.gather(*like_tasks, return_exceptions=True)
    
    successful = 0
    failed = 0
    for r in results:
        if isinstance(r, bool) and r:
            successful += 1
        else:
            failed += 1
    
    user_info = None
    if successful > 0:
        user_info = await get_user_info(target_uid, server_name)
        if user_info:
            username = user_info.get('name', 'Unknown')
            current_likes = user_info.get('likes', 0)
            before_likes = user_stats.get(target_uid, {}).get('current_likes', 0)
            if before_likes == 0:
                before_likes = current_likes - successful
            update_user_stats(target_uid, successful, username, current_likes)
            add_to_history(target_uid, successful, before_likes, current_likes, username, server_name)
    
    return {
        'success': successful,
        'failed': failed,
        'total': len(accounts),
        'accounts_used': len(accounts_to_use),
        'skipped': skipped,
        'user_info': user_info
    }

def enc(uid):
    message = uid_generator_pb2.uid_generator()
    message.krishna_ = int(uid)
    message.teamXdarks = 1
    return encrypt_message(message.SerializeToString())

def decode_protobuf(binary):
    try:
        items = like_count_pb2.Info()
        items.ParseFromString(binary)
        return items
    except:
        return None

def get_player_info(encrypted_uid, server_name, token):
    base_url = REGION_URLS.get(server_name, 'https://clientbp.ggpolarbear.com')
    url = f"{base_url}/GetPlayerPersonalShow"
    edata = bytes.fromhex(encrypted_uid)
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Authorization': f"Bearer {token}",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB54"
    }
    try:
        response = requests.post(url, data=edata, headers=headers, verify=False, timeout=10)
        return decode_protobuf(response.content)
    except:
        return None

async def check_all_accounts_status(server="IND"):
    accounts = load_accounts(server)
    for acc in accounts:
        try:
            token = await get_valid_token(acc['uid'], acc['password'], server)
            if token:
                account_status[acc['uid']] = {'status': 'working', 'last_check': datetime.now().isoformat()}
            else:
                account_status[acc['uid']] = {'status': 'unknown', 'last_check': datetime.now().isoformat()}
            save_account_status()
            await asyncio.sleep(0.1)
        except:
            continue

def run_status_check(server="IND"):
    asyncio.run(check_all_accounts_status(server))

async def auto_like_daily():
    add_activity_log("Auto-like scheduler started", "info")
    while True:
        try:
            now = datetime.now()
            target_time = now.replace(hour=AUTO_LIKE_HOUR, minute=AUTO_LIKE_MINUTE, second=0, microsecond=0)
            if now >= target_time:
                target_time += timedelta(days=1)
            wait_seconds = (target_time - now).total_seconds()
            if wait_seconds > 0:
                add_activity_log(f"Next auto-like at: {target_time.strftime('%Y-%m-%d %H:%M:%S')} IST", "info")
                await asyncio.sleep(wait_seconds)
            
            add_activity_log(f"Starting auto-like at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST", "info")
            
            for email, user_data in user_db.items():
                if user_data.get('auto_like_unlocked', False):
                    targets = user_data.get('auto_like_targets', [])
                    for target_uid in targets:
                        add_activity_log(f"Processing {email} -> {target_uid}", "info")
                        result = await send_likes_all_accounts(
                            target_uid,
                            "IND",
                            "https://client.ind.freefiremobile.com/LikeProfile"
                        )
                        add_activity_log(f"Sent {result['success']} likes to {target_uid} for {email}", "success")
                        await asyncio.sleep(0.5)
            
            add_activity_log(f"Auto-like cycle complete.", "success")
            
        except Exception as e:
            add_activity_log(f"Auto-like error: {str(e)}", "error")
            await asyncio.sleep(60)

def start_auto_like():
    asyncio.run(auto_like_daily())

def set_auto_time(hour, minute):
    global AUTO_LIKE_HOUR, AUTO_LIKE_MINUTE
    AUTO_LIKE_HOUR = hour
    AUTO_LIKE_MINUTE = minute
    add_activity_log(f"Auto-like time changed to {hour:02d}:{minute:02d} IST", "info")
    return f"Auto-like time set to {hour:02d}:{minute:02d} IST"

# ============================================================
# STARTUP
# ============================================================
load_liked_data()
load_account_status()
load_users()
load_user_db()

reset_thread = threading.Thread(target=daily_reset_task, daemon=True)
reset_thread.start()

auto_thread = threading.Thread(target=start_auto_like, daemon=True)
auto_thread.start()

threading.Thread(target=run_status_check, args=("IND",)).start()

add_activity_log("HEX CHEATS System Started", "info")
add_activity_log(f"Accounts: {len(load_accounts('IND'))} (IND)", "info")
add_activity_log(f"Auto-queue: {len(auto_like_users)} users", "info")
add_activity_log(f"Users: {len(user_db)} registered", "info")
add_activity_log(f"Active codes: {len(admin_codes)}", "info")
add_activity_log(f"Auto-like at {AUTO_LIKE_HOUR:02d}:{AUTO_LIKE_MINUTE:02d} IST daily", "info")

print("HEX CHEATS – Complete System Started")
print(f"Accounts: {len(load_accounts('IND'))} (IND)")
print("Admin Login: HexMods / ADI444")
print(f"Users: {len(user_db)} registered")
print(f"Active codes: {len(admin_codes)}")
print(f"Auto-like: {AUTO_LIKE_HOUR:02d}:{AUTO_LIKE_MINUTE:02d} IST daily")
print("Public URL: / (no login)")

# ============================================================
# REGISTER BLUEPRINTS (After all functions are defined)
# ============================================================
try:
    from public import public_bp
    from admin import admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    
    print("Blueprints registered successfully!")
except Exception as e:
    print(f"Error registering blueprints: {e}")

# ============================================================
# ROOT ROUTE - Direct fallback
# ============================================================
@app.route('/')
def root_index():
    try:
        from public import PUBLIC_HTML
        return PUBLIC_HTML
    except:
        return "<h1>HEX CHEATS</h1><p>Public page loading... Please check logs.</p>"

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
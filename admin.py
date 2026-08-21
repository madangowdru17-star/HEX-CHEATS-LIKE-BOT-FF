from flask import Blueprint, request, jsonify, render_template_string, session, redirect, url_for
import asyncio
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import from app after blueprint creation
from app import (
    get_user_info, send_likes_all_accounts, update_user_stats,
    add_to_history, REGION_URLS, user_db, admin_codes,
    generate_admin_code, unlock_user_auto_like, load_accounts,
    auto_like_users, user_stats, like_history, account_status,
    liked_cache, activity_logs, AUTO_LIKE_HOUR, AUTO_LIKE_MINUTE,
    add_activity_log, save_user_db, save_users, get_next_reset_time,
    set_auto_time, reset_all_data, get_accounts_count, load_user_db,
    load_users, load_liked_data, load_account_status
)

# ============================================================
# LOGIN HTML
# ============================================================
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HEX CHEATS - Admin</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #080C14;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: radial-gradient(circle at 20% 30%, rgba(56,189,248,0.05) 0%, transparent 50%),
                              radial-gradient(circle at 80% 70%, rgba(52,211,153,0.05) 0%, transparent 50%);
        }
        .login-container {
            background: rgba(12, 22, 40, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(56,189,248,0.1);
            border-radius: 24px;
            padding: 50px 40px;
            max-width: 420px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .login-container .logo { text-align: center; margin-bottom: 30px; }
        .login-container .logo h1 {
            font-family: 'Orbitron', monospace;
            font-size: 2em;
            font-weight: 900;
            background: linear-gradient(135deg, #38BDF8, #34D399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
        }
        .login-container .logo p { color: #8899BB; font-size: 0.8em; letter-spacing: 4px; text-transform: uppercase; margin-top: 4px; }
        .login-container .input-group { margin-bottom: 16px; }
        .login-container .input-group label { color: #8899BB; font-size: 0.8em; font-weight: 600; letter-spacing: 0.5px; display: block; margin-bottom: 6px; }
        .login-container .input-group input {
            width: 100%;
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid rgba(56,189,248,0.1);
            background: rgba(0,0,0,0.3);
            color: #F0F4FF;
            font-size: 1em;
            font-family: 'Inter', sans-serif;
            transition: 0.3s;
        }
        .login-container .input-group input:focus { outline: none; border-color: rgba(56,189,248,0.3); box-shadow: 0 0 20px rgba(56,189,248,0.05); }
        .login-container .login-btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            background: linear-gradient(135deg, #38BDF8, #34D399);
            color: #080C14;
            font-size: 1em;
            font-weight: 700;
            cursor: pointer;
            transition: 0.3s;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.5px;
            margin-top: 8px;
        }
        .login-container .login-btn:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(56,189,248,0.2); }
        .login-container .error-msg { color: #F87171; font-size: 0.85em; text-align: center; margin-top: 12px; display: none; }
        .login-container .footer { text-align: center; margin-top: 20px; color: #4a5a7a; font-size: 0.7em; letter-spacing: 1px; }
        .login-container .footer i { color: #38BDF8; }
        @media (max-width: 480px) {
            .login-container { padding: 30px 20px; }
            .login-container .logo h1 { font-size: 1.5em; }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>HEX CHEATS</h1>
            <p>Admin Panel</p>
        </div>
        <form method="POST" action="/admin/login">
            <div class="input-group">
                <label><i class="fas fa-user"></i> Username</label>
                <input type="text" name="username" placeholder="Enter username" required />
            </div>
            <div class="input-group">
                <label><i class="fas fa-lock"></i> Password</label>
                <input type="password" name="password" placeholder="Enter password" required />
            </div>
            <button type="submit" class="login-btn"><i class="fas fa-sign-in-alt"></i> Login</button>
        </form>
        <div class="error-msg" id="login-error">Invalid credentials!</div>
        <div class="footer"><i class="fas fa-shield-alt"></i> Secure Access</div>
    </div>
    <script>
        if (window.location.search.includes('error=1')) {
            document.getElementById('login-error').style.display = 'block';
        }
    </script>
</body>
</html>
'''

# ============================================================
# ADMIN DASHBOARD HTML (Full Working Version)
# ============================================================
ADMIN_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HEX CHEATS - Admin</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #080C14;
            color: #F0F4FF;
            min-height: 100vh;
            background-image: radial-gradient(circle at 15% 20%, rgba(56,189,248,0.04) 0%, transparent 50%),
                              radial-gradient(circle at 85% 80%, rgba(52,211,153,0.04) 0%, transparent 50%);
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
        ::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.2); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(56,189,248,0.35); }
        
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes neonPulse { 0%,100% { box-shadow: 0 0 15px rgba(56,189,248,0.05), 0 0 30px rgba(56,189,248,0.02); } 50% { box-shadow: 0 0 25px rgba(56,189,248,0.12), 0 0 50px rgba(56,189,248,0.04); } }
        @keyframes glowPulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
        @keyframes titleGlow { 0%,100% { text-shadow: 0 0 20px rgba(56,189,248,0.2), 0 0 40px rgba(56,189,248,0.05); } 50% { text-shadow: 0 0 30px rgba(56,189,248,0.35), 0 0 60px rgba(56,189,248,0.1); } }
        
        .fade-in { animation: fadeInUp 0.4s ease forwards; }
        .main { max-width: 1400px; margin: 0 auto; padding: 24px 28px; width: 100%; }
        
        .title-section { text-align: center; padding: 12px 0 8px 0; margin-bottom: 8px; }
        .title-section h1 {
            font-family: 'Orbitron', monospace;
            font-size: 2.6em;
            font-weight: 900;
            background: linear-gradient(135deg, #38BDF8, #34D399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 4px;
            animation: titleGlow 3s ease-in-out infinite;
        }
        .title-section .sub-title { font-size: 0.85em; color: #8899BB; letter-spacing: 8px; text-transform: uppercase; margin-top: 2px; font-weight: 400; }
        
        .server-selector-row {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            margin: 10px 0 15px 0;
            flex-wrap: wrap;
        }
        .server-selector-row label { color: #8899BB; font-size: 0.85em; font-weight: 600; letter-spacing: 0.5px; }
        .server-selector-row select {
            padding: 10px 20px;
            border-radius: 12px;
            border: 1px solid rgba(56,189,248,0.1);
            background: rgba(0,0,0,0.25);
            color: #F0F4FF;
            font-size: 0.9em;
            font-family: 'Inter', sans-serif;
            min-width: 150px;
            transition: 0.3s;
            cursor: pointer;
        }
        .server-selector-row select:focus { outline: none; border-color: rgba(56,189,248,0.2); }
        .server-selector-row .server-status {
            background: rgba(12,22,40,0.6);
            padding: 8px 20px;
            border-radius: 20px;
            border: 1px solid rgba(56,189,248,0.1);
            font-size: 0.8em;
            color: #8899BB;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        .server-selector-row .server-status i { color: #38BDF8; }
        .server-selector-row .server-status .accounts-count { color: #34D399; font-weight: 700; font-size: 1.1em; }
        
        .header-top { display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin-bottom: 8px; }
        .logout-btn {
            padding: 8px 20px;
            border: 1px solid rgba(56,189,248,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.03);
            color: #8899BB;
            cursor: pointer;
            font-size: 0.8em;
            font-weight: 600;
            transition: 0.3s;
            font-family: 'Inter', sans-serif;
        }
        .logout-btn:hover { background: rgba(248,113,113,0.1); color: #F87171; border-color: rgba(248,113,113,0.2); }
        
        .glass {
            background: rgba(12,22,40,0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(56,189,248,0.08);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            border-radius: 16px;
            transition: 0.3s;
        }
        .glass:hover { border-color: rgba(56,189,248,0.12); }
        
        .status-row {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            margin-bottom: 18px;
            justify-content: center;
            padding: 4px 0;
        }
        .status-row .item {
            background: rgba(12,22,40,0.5);
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.82em;
            border: 1px solid rgba(56,189,248,0.08);
            color: #8899BB;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-row .item i { color: #38BDF8; font-size: 0.9em; }
        .status-row .item span { color: #F0F4FF; font-weight: 500; }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(105px, 1fr));
            gap: 10px;
            margin-bottom: 22px;
        }
        .nav-btn {
            padding: 12px 14px;
            border: 1px solid rgba(56,189,248,0.08);
            border-radius: 16px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.8em;
            transition: 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.3px;
            background: #0C1628;
            color: #8899BB;
            min-height: 44px;
            text-align: center;
        }
        .nav-btn:hover { background: rgba(56,189,248,0.06); color: #38BDF8; transform: translateY(-2px); border-color: rgba(56,189,248,0.15); box-shadow: 0 0 20px rgba(56,189,248,0.05); }
        .nav-btn.active-nav {
            background: linear-gradient(135deg, rgba(56,189,248,0.15), rgba(52,211,153,0.10));
            color: #38BDF8;
            border-color: rgba(56,189,248,0.2);
            box-shadow: 0 0 30px rgba(56,189,248,0.06);
            animation: neonPulse 2.5s infinite;
        }
        .nav-btn i { font-size: 0.9em; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }
        .stat-card {
            padding: 18px 14px;
            text-align: center;
            background: rgba(12,22,40,0.6);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(56,189,248,0.08);
            border-radius: 16px;
            transition: 0.3s;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .stat-card:hover { border-color: rgba(56,189,248,0.08); transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,0.15); }
        .stat-card .num { font-family: 'Orbitron', monospace; font-size: 2.2em; font-weight: 700; line-height: 1.2; }
        .stat-card .lbl { color: #8899BB; font-size: 0.7em; margin-top: 5px; letter-spacing: 1.2px; text-transform: uppercase; }
        .stat-card .icon { font-size: 1.1em; margin-bottom: 4px; opacity: 0.4; }
        .num-accounts { color: #60A5FA; }
        .num-likes { color: #A78BFA; }
        .num-targets { color: #FBBF24; }
        .num-queue { color: #38BDF8; }
        .num-users { color: #34D399; }
        
        .panel {
            padding: 20px 24px;
            margin-bottom: 20px;
            background: rgba(12,22,40,0.6);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(56,189,248,0.08);
            border-radius: 16px;
        }
        .panel h2 { color: #8899BB; font-size: 0.9em; margin-bottom: 14px; letter-spacing: 1.2px; text-transform: uppercase; font-weight: 600; }
        .panel h2 i { margin-right: 10px; color: #38BDF8; }
        
        .input-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }
        .input-group input, .input-group select {
            padding: 10px 16px;
            border-radius: 12px;
            border: 1px solid rgba(56,189,248,0.1);
            background: rgba(0,0,0,0.25);
            color: #F0F4FF;
            font-size: 0.9em;
            font-family: 'Inter', sans-serif;
            min-width: 140px;
            transition: 0.3s;
        }
        .input-group input:focus, .input-group select:focus { outline: none; border-color: rgba(56,189,248,0.2); box-shadow: 0 0 20px rgba(56,189,248,0.04); }
        .input-group select option { background: #0C1628; }
        
        .btn {
            padding: 10px 22px;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85em;
            transition: 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.3px;
            min-height: 42px;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-primary { background: linear-gradient(135deg, #38BDF8, #34D399); color: #080C14; border: none; }
        .btn-primary:hover { box-shadow: 0 0 30px rgba(56,189,248,0.2); }
        .btn-success { background: rgba(52,211,153,0.12); color: #34D399; border: 1px solid rgba(52,211,153,0.1); }
        .btn-success:hover { background: rgba(52,211,153,0.2); }
        .btn-danger { background: rgba(248,113,113,0.12); color: #F87171; border: 1px solid rgba(248,113,113,0.1); }
        .btn-danger:hover { background: rgba(248,113,113,0.2); }
        .btn-rocket { background: linear-gradient(135deg, #F472B6, #F87171); color: #080C14; border: none; }
        .btn-rocket:hover { box-shadow: 0 0 30px rgba(248,113,113,0.2); transform: scale(1.02); }
        .btn-warning { background: rgba(251,191,36,0.12); color: #FBBF24; border: 1px solid rgba(251,191,36,0.1); }
        .btn-warning:hover { background: rgba(251,191,36,0.2); }
        .btn-purple { background: rgba(167,139,250,0.12); color: #A78BFA; border: 1px solid rgba(167,139,250,0.1); }
        .btn-purple:hover { background: rgba(167,139,250,0.2); }
        
        .user-item {
            background: rgba(12,22,40,0.5);
            padding: 6px 16px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            border: 1px solid rgba(56,189,248,0.08);
            margin: 3px;
            font-size: 0.85em;
            transition: 0.3s;
        }
        .user-item:hover { border-color: rgba(56,189,248,0.1); }
        .user-item .uid { font-weight: 600; color: #38BDF8; }
        .user-item .stats { color: #8899BB; font-size: 0.75em; }
        .user-item .stats span { color: #34D399; font-weight: 600; }
        .user-item .del-btn { background: none; border: none; color: #F87171; cursor: pointer; padding: 0 4px; font-size: 1em; }
        
        .section-title { font-size: 1em; color: #F0F4FF; margin: 20px 0 10px; display: flex; align-items: center; gap: 10px; font-weight: 600; letter-spacing: 0.3px; }
        .live-dot { display: inline-block; width: 7px; height: 7px; background: #34D399; border-radius: 50%; animation: glowPulse 1.5s infinite; }
        .note { color: #8899BB; font-size: 0.8em; margin-top: 8px; }
        
        .history-item {
            padding: 8px 0;
            border-bottom: 1px solid rgba(56,189,248,0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 6px;
            font-size: 0.85em;
        }
        .history-item .uid { color: #38BDF8; font-weight: 600; }
        .history-item .name { color: #F0F4FF; }
        .history-item .likes { color: #34D399; font-weight: 600; }
        .history-item .time { color: #8899BB; font-size: 0.75em; }
        
        .logs-container {
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid rgba(56,189,248,0.08);
        }
        .log-entry { padding: 4px 0; border-bottom: 1px solid rgba(56,189,248,0.05); color: #8899BB; display: flex; gap: 12px; }
        .log-entry .log-time { color: #38BDF8; min-width: 60px; }
        .log-entry .log-success { color: #34D399; }
        .log-entry .log-error { color: #F87171; }
        .log-entry .log-info { color: #FBBF24; }
        
        .user-db-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 0.85em;
        }
        .user-db-table th {
            background: rgba(56,189,248,0.03);
            padding: 10px 16px;
            text-align: left;
            font-weight: 600;
            color: #8899BB;
            border-bottom: 1px solid rgba(56,189,248,0.08);
            text-transform: uppercase;
            font-size: 0.7em;
            letter-spacing: 0.8px;
        }
        .user-db-table td {
            padding: 10px 16px;
            border-bottom: 1px solid rgba(56,189,248,0.05);
        }
        .badge { padding: 2px 12px; border-radius: 20px; font-size: 0.65em; font-weight: 600; display: inline-block; text-transform: uppercase; letter-spacing: 0.5px; }
        .badge-active { background: rgba(52,211,153,0.12); color: #34D399; border: 1px solid rgba(52,211,153,0.06); }
        .badge-inactive { background: rgba(248,113,113,0.12); color: #F87171; border: 1px solid rgba(248,113,113,0.06); }
        .badge-unlocked { background: rgba(56,189,248,0.12); color: #38BDF8; border: 1px solid rgba(56,189,248,0.06); }
        .badge-locked { background: rgba(251,191,36,0.12); color: #FBBF24; border: 1px solid rgba(251,191,36,0.06); }
        
        .result-modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 999;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(8px);
        }
        .result-modal.active { display: flex; }
        .result-box {
            background: #0C1628;
            padding: 32px 36px;
            border-radius: 18px;
            max-width: 500px;
            width: 90%;
            border: 1px solid rgba(56,189,248,0.1);
            box-shadow: 0 0 60px rgba(56,189,248,0.03);
            animation: fadeInUp 0.4s ease;
        }
        .result-box h2 { font-family: 'Orbitron', monospace; font-size: 1.1em; color: #38BDF8; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
        .result-box .row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(56,189,248,0.08); }
        .result-box .row .label { color: #8899BB; font-size: 0.9em; }
        .result-box .row .value { color: #34D399; font-weight: 600; font-size: 0.9em; }
        .result-box .row .value-failed { color: #F87171; }
        .result-box .close-btn { margin-top: 16px; padding: 10px; background: rgba(255,255,255,0.04); color: #8899BB; border: 1px solid rgba(56,189,248,0.1); border-radius: 12px; cursor: pointer; font-weight: 600; width: 100%; transition: 0.3s; font-family: 'Inter', sans-serif; font-size: 0.9em; }
        .result-box .close-btn:hover { background: rgba(255,255,255,0.08); color: #F0F4FF; }
        
        .section { display: none; }
        .section.active { display: block; animation: fadeInUp 0.35s ease; }
        
        .server-accounts-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .server-account-item {
            background: rgba(12,22,40,0.5);
            padding: 4px 12px;
            border-radius: 12px;
            border: 1px solid rgba(56,189,248,0.05);
            font-size: 0.75em;
            color: #8899BB;
            font-family: monospace;
        }
        
        @media (max-width: 992px) { .main { padding: 18px 20px; } .stats-grid { grid-template-columns: repeat(3, 1fr); } .nav-grid { grid-template-columns: repeat(4, 1fr); } .title-section h1 { font-size: 2em; } .server-selector-row { flex-direction: column; gap: 10px; } }
        @media (max-width: 768px) { .main { padding: 14px 16px; } .stats-grid { grid-template-columns: repeat(3, 1fr); gap: 12px; } .stat-card { padding: 14px 10px; min-height: 80px; } .stat-card .num { font-size: 1.6em; } .nav-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; } .nav-btn { font-size: 0.7em; padding: 10px 12px; min-height: 38px; } .title-section h1 { font-size: 1.6em; } .title-section .sub-title { font-size: 0.7em; letter-spacing: 4px; } .panel { padding: 16px 18px; } .input-group input, .input-group select { min-width: 100px; font-size: 0.8em; padding: 8px 12px; } .btn { font-size: 0.8em; padding: 8px 16px; min-height: 36px; } .result-box { padding: 20px; } .status-row .item { font-size: 0.7em; padding: 4px 12px; } .server-selector-row .server-status { font-size: 0.7em; padding: 4px 12px; } }
        @media (max-width: 480px) { .main { padding: 10px 12px; } .stats-grid { grid-template-columns: 1fr 1fr; } .nav-grid { grid-template-columns: repeat(2, 1fr); } .nav-btn { font-size: 0.65em; padding: 8px 10px; min-height: 34px; } .title-section h1 { font-size: 1.3em; } .title-section .sub-title { font-size: 0.6em; letter-spacing: 3px; } .stat-card .num { font-size: 1.3em; } .stat-card { padding: 12px 8px; min-height: 70px; } .status-row .item { font-size: 0.65em; padding: 3px 10px; } }
    </style>
</head>
<body>
    <div class="main">
        <div class="title-section">
            <h1>HEX CHEATS</h1>
            <div class="sub-title">Admin Panel</div>
        </div>
        
        <div class="server-selector-row">
            <label for="server-select-main"><i class="fas fa-globe"></i> Select Server:</label>
            <select id="server-select-main" onchange="changeServer(this.value)">
                <option value="IND">India</option>
                <option value="BD">Bangladesh</option>
                <option value="MENA">MENA</option>
                <option value="BR">Brazil</option>
                <option value="US">US</option>
                <option value="SAC">SAC</option>
                <option value="NA">NA</option>
                <option value="RU">Russia</option>
            </select>
            <div class="server-status">
                <i class="fas fa-users"></i>
                Accounts: <span class="accounts-count" id="server-accounts">0</span>
            </div>
            <a href="/admin/logout"><button class="logout-btn"><i class="fas fa-sign-out-alt"></i> Logout</button></a>
        </div>
        
        <div class="status-row">
            <div class="item"><i class="fas fa-history"></i> Last Auto-Run: <span id="lastAutoRun">Never</span></div>
            <div class="item"><i class="fas fa-info-circle"></i> Status: <span id="autoRunStatus">Idle</span></div>
            <div class="item"><i class="fas fa-comment"></i> Message: <span id="autoRunMessage">-</span></div>
        </div>
        
        <div class="nav-grid">
            <button class="nav-btn active-nav" onclick="showSection('dashboard')"><i class="fas fa-home"></i> Dashboard</button>
            <button class="nav-btn" onclick="showSection('send')"><i class="fas fa-paper-plane"></i> Send</button>
            <button class="nav-btn" onclick="showSection('auto')"><i class="fas fa-clock"></i> Auto Like</button>
            <button class="nav-btn" onclick="showSection('users')"><i class="fas fa-users"></i> Users</button>
            <button class="nav-btn" onclick="showSection('codes')"><i class="fas fa-key"></i> Codes</button>
            <button class="nav-btn" onclick="showSection('history')"><i class="fas fa-history"></i> History</button>
            <button class="nav-btn" onclick="showSection('stats')"><i class="fas fa-chart-bar"></i> Stats</button>
            <button class="nav-btn" onclick="showSection('logs')"><i class="fas fa-terminal"></i> Logs</button>
            <button class="nav-btn" onclick="showSection('settings')"><i class="fas fa-cog"></i> Settings</button>
            <button class="nav-btn" onclick="showSection('accounts')"><i class="fas fa-database"></i> Accounts</button>
        </div>
        
        <div id="section-dashboard" class="section active">
            <div class="stats-grid">
                <div class="stat-card"><div class="icon" style="color:#60A5FA;"><i class="fas fa-users"></i></div><div class="num num-accounts" id="total-accounts">0</div><div class="lbl">Accounts</div></div>
                <div class="stat-card"><div class="icon" style="color:#A78BFA;"><i class="fas fa-heart"></i></div><div class="num num-likes" id="total-likes">0</div><div class="lbl">Likes</div></div>
                <div class="stat-card"><div class="icon" style="color:#FBBF24;"><i class="fas fa-bullseye"></i></div><div class="num num-targets" id="targets-liked">0</div><div class="lbl">Targets</div></div>
                <div class="stat-card"><div class="icon" style="color:#38BDF8;"><i class="fas fa-list-ul"></i></div><div class="num num-queue" id="auto-users">0</div><div class="lbl">Queue</div></div>
                <div class="stat-card"><div class="icon" style="color:#34D399;"><i class="fas fa-user-plus"></i></div><div class="num num-users" id="total-users">0</div><div class="lbl">Users</div></div>
            </div>
        </div>
        
        <div id="section-send" class="section">
            <div class="panel">
                <h2><i class="fas fa-paper-plane"></i> Send Likes</h2>
                <div class="input-group">
                    <input type="number" id="target-uid-send" placeholder="Enter Target UID" />
                    <select id="server-send">
                        <option value="IND">India</option>
                        <option value="BD">Bangladesh</option>
                        <option value="MENA">MENA</option>
                        <option value="BR">Brazil</option>
                        <option value="US">US</option>
                        <option value="SAC">SAC</option>
                        <option value="NA">NA</option>
                        <option value="RU">Russia</option>
                    </select>
                    <button class="btn btn-rocket" onclick="sendAdminLikes()"><i class="fas fa-rocket"></i> Send All</button>
                </div>
                <div class="note"><i class="fas fa-info-circle"></i> Sends ALL likes from all available accounts.</div>
            </div>
            <div class="panel">
                <h2><i class="fas fa-check-double"></i> Verify Profile</h2>
                <div class="input-group">
                    <input type="number" id="admin-verify-uid" placeholder="Enter UID" />
                    <select id="admin-verify-server">
                        <option value="IND">India</option>
                        <option value="BD">Bangladesh</option>
                        <option value="MENA">MENA</option>
                        <option value="BR">Brazil</option>
                        <option value="US">US</option>
                        <option value="SAC">SAC</option>
                        <option value="NA">NA</option>
                        <option value="RU">Russia</option>
                    </select>
                    <button class="btn btn-primary" onclick="adminVerify()"><i class="fas fa-check-double"></i> Verify</button>
                </div>
                <div id="admin-verify-result" style="margin-top:12px;"></div>
            </div>
        </div>
        
        <div id="section-auto" class="section">
            <div class="panel">
                <h2><i class="fas fa-clock"></i> Auto Like Management</h2>
                <p style="color:#8899BB; margin-bottom:12px; font-size:0.85em;">Manage user auto-like targets and unlock status.</p>
                <div style="margin-bottom:15px; display:flex; flex-wrap:wrap; gap:10px;">
                    <div class="input-group" style="flex:1;">
                        <input type="email" id="user-email-unlock" placeholder="User Email" style="min-width:200px;" />
                        <button class="btn btn-warning" onclick="unlockUserAuto()"><i class="fas fa-unlock"></i> Unlock Auto-Like</button>
                    </div>
                </div>
                <div class="note"><i class="fas fa-info-circle"></i> Unlock auto-like for users so they can add targets on public page.</div>
            </div>
            <div class="panel">
                <h2><i class="fas fa-list"></i> Auto-Queue Users</h2>
                <div id="auto-user-list"></div>
                <div style="margin-top:12px;">
                    <button class="btn btn-danger" onclick="deleteAllAuto()"><i class="fas fa-trash"></i> Clear All</button>
                </div>
            </div>
        </div>
        
        <div id="section-users" class="section">
            <div class="panel">
                <h2><i class="fas fa-users"></i> User Database</h2>
                <div id="user-db-content"></div>
            </div>
        </div>
        
        <div id="section-codes" class="section">
            <div class="panel">
                <h2><i class="fas fa-key"></i> Unlock Codes</h2>
                <div class="input-group">
                    <button class="btn btn-primary" onclick="generateCode()"><i class="fas fa-plus"></i> Generate Code</button>
                </div>
                <div id="codes-list" style="margin-top:15px;"></div>
                <div class="note"><i class="fas fa-info-circle"></i> Users enter these codes on the public page to unlock auto-like.</div>
            </div>
        </div>
        
        <div id="section-history" class="section">
            <div class="panel">
                <h2><i class="fas fa-history"></i> Like History</h2>
                <div id="history-list"></div>
            </div>
        </div>
        
        <div id="section-stats" class="section">
            <div class="panel">
                <h2><i class="fas fa-chart-bar"></i> Statistics</h2>
                <div id="stats-content"></div>
            </div>
        </div>
        
        <div id="section-logs" class="section">
            <div class="panel">
                <h2><i class="fas fa-terminal"></i> Activity Logs</h2>
                <div class="logs-container" id="logs-container">
                    <div class="log-entry"><span class="log-time">[--:--:--]</span> <span class="log-info">System ready...</span></div>
                </div>
            </div>
        </div>
        
        <div id="section-settings" class="section">
            <div class="panel">
                <h2><i class="fas fa-cog"></i> Settings</h2>
                <div style="margin-bottom:12px;">
                    <label style="color:#8899BB; font-size:0.85em;">Auto-Like Time (IST)</label>
                    <div class="input-group" style="margin-top:6px;">
                        <input type="number" id="set-hour" placeholder="Hour" value="4" style="width:80px;" />
                        <input type="number" id="set-minute" placeholder="Minute" value="0" style="width:80px;" />
                        <button class="btn btn-primary" onclick="setAutoTime()"><i class="fas fa-save"></i> Save Time</button>
                    </div>
                    <div style="margin-top:8px; font-size:0.8em; color:#4a5a7a;">
                        Current: <span id="current-auto-time">04:00 IST</span>
                    </div>
                </div>
                <div id="time-status" style="color:#34D399; font-size:0.85em;"></div>
            </div>
        </div>
        
        <div id="section-accounts" class="section">
            <div class="panel">
                <h2><i class="fas fa-database"></i> Account Management</h2>
                <div style="margin-bottom:12px;">
                    <div class="input-group">
                        <select id="account-server-select" onchange="loadAccountsList(this.value)">
                            <option value="IND">India</option>
                            <option value="BD">Bangladesh</option>
                            <option value="MENA">MENA</option>
                            <option value="BR">Brazil</option>
                            <option value="US">US</option>
                            <option value="SAC">SAC</option>
                            <option value="NA">NA</option>
                            <option value="RU">Russia</option>
                        </select>
                        <button class="btn btn-primary" onclick="refreshAccounts()"><i class="fas fa-sync"></i> Refresh</button>
                    </div>
                </div>
                <div id="accounts-list-content">
                    <div class="note">Select a server to view accounts.</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="result-modal" id="resultModal">
        <div class="result-box">
            <h2><i class="fas fa-check-circle"></i> Like Result</h2>
            <div id="result-content">
                <div class="row"><span class="label">Player Name</span><span class="value" id="res-name">-</span></div>
                <div class="row"><span class="label">Likes Sent</span><span class="value" id="res-sent">0</span></div>
                <div class="row"><span class="label">Likes Before</span><span class="value" id="res-before">0</span></div>
                <div class="row"><span class="label">Likes After</span><span class="value" id="res-after">0</span></div>
                <div class="row"><span class="label">Verified Added</span><span class="value" id="res-added">0</span></div>
                <div class="row"><span class="label">Failed</span><span class="value value-failed" id="res-failed">0</span></div>
            </div>
            <button class="close-btn" onclick="closeResult()"><i class="fas fa-times"></i> Close</button>
        </div>
    </div>

    <script>
        let currentServer = 'IND';
        
        function changeServer(server) {
            currentServer = server;
            document.querySelectorAll('select[id^="server-"]').forEach(sel => { sel.value = server; });
            document.getElementById('server-select-main').value = server;
            loadAdminData();
        }
        
        function showSection(id) {
            document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
            document.getElementById('section-' + id).classList.add('active');
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active-nav'));
            document.querySelector(`.nav-btn[onclick*="${id}"]`).classList.add('active-nav');
            if (id === 'history') loadHistory();
            if (id === 'stats') loadStats();
            if (id === 'logs') loadLogs();
            if (id === 'settings') loadAutoTime();
            if (id === 'users') loadUsersDB();
            if (id === 'codes') loadCodes();
            if (id === 'accounts') loadAccountsList(document.getElementById('account-server-select').value);
        }
        
        function formatTime(iso) {
            if (!iso) return 'Never';
            try { const d = new Date(iso); return d.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }); } catch { return iso; }
        }
        
        function loadAutoTime() {
            fetch('/api/auto-time')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('current-auto-time').textContent = data.time;
                    document.getElementById('set-hour').value = data.hour;
                    document.getElementById('set-minute').value = data.minute;
                });
        }
        
        function loadAdminData() {
            fetch('/api/dashboard-data?server=' + currentServer)
                .then(res => res.json())
                .then(data => {
                    if (data.error) return;
                    document.getElementById('total-accounts').textContent = data.total_accounts || 0;
                    document.getElementById('total-likes').textContent = data.total_likes || 0;
                    document.getElementById('targets-liked').textContent = data.targets_liked || 0;
                    document.getElementById('auto-users').textContent = data.auto_users || 0;
                    document.getElementById('total-users').textContent = data.total_users || 0;
                    document.getElementById('server-accounts').textContent = data.total_accounts || 0;
                    document.getElementById('lastAutoRun').textContent = data.last_auto_run ? formatTime(data.last_auto_run) : 'Never';
                    document.getElementById('autoRunStatus').textContent = data.auto_run_status || 'Idle';
                    document.getElementById('autoRunMessage').textContent = data.auto_run_message || '-';
                    
                    let userHtml = '';
                    if (data.users && data.users.length > 0) {
                        data.users.forEach(user => {
                            const s = data.user_stats[user] || { total_likes: 0, today_likes: 0 };
                            userHtml += `<div class="user-item"><span class="uid">${user}</span><span class="stats">T:<span>${s.total_likes||0}</span> D:<span>${s.today_likes||0}</span></span><button class="del-btn" onclick="deleteUser('${user}')"><i class="fas fa-times"></i></button></div>`;
                        });
                    } else {
                        userHtml = '<div class="note">No users in auto-queue</div>';
                    }
                    document.getElementById('auto-user-list').innerHTML = userHtml;
                });
        }
        
        function loadAccountsList(server) {
            fetch('/api/admin/accounts?server=' + server)
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.accounts && data.accounts.length > 0) {
                        html += `<div style="margin-bottom:10px;color:#8899BB;font-size:0.85em;">Total: <strong style="color:#38BDF8;">${data.accounts.length}</strong> accounts</div>`;
                        html += `<div class="server-accounts-list">`;
                        data.accounts.forEach(acc => {
                            html += `<span class="server-account-item">${acc.uid}</span>`;
                        });
                        html += `</div>`;
                    } else {
                        html = '<div class="note">No accounts found for this server.</div>';
                    }
                    document.getElementById('accounts-list-content').innerHTML = html;
                });
        }
        
        function refreshAccounts() {
            const server = document.getElementById('account-server-select').value;
            loadAccountsList(server);
        }
        
        function loadHistory() {
            fetch('/api/history')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.history && data.history.length > 0) {
                        data.history.forEach(h => {
                            html += `<div class="history-item">
                                <span><span class="uid">${h.uid}</span> <span class="name">${h.username || 'Unknown'}</span></span>
                                <span class="likes">+${h.likes_sent} (${h.verified_added} verified)</span>
                                <span class="time">${formatTime(h.timestamp)}</span>
                            </div>`;
                        });
                    } else {
                        html = '<div class="note">No history yet</div>';
                    }
                    document.getElementById('history-list').innerHTML = html;
                });
        }
        
        function loadStats() {
            fetch('/api/stats')
                .then(res => res.json())
                .then(data => {
                    let html = `
                        <div class="row" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(56,189,248,0.08);">
                            <span style="color:#8899BB;">Total Likes Sent</span>
                            <span style="color:#34D399;font-weight:600;">${data.total_likes_sent}</span>
                        </div>
                        <div class="row" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(56,189,248,0.08);">
                            <span style="color:#8899BB;">Total Targets</span>
                            <span style="color:#34D399;font-weight:600;">${data.total_targets}</span>
                        </div>
                        <div class="row" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(56,189,248,0.08);">
                            <span style="color:#8899BB;">Queue Users</span>
                            <span style="color:#34D399;font-weight:600;">${data.auto_users}</span>
                        </div>
                        <div class="row" style="display:flex;justify-content:space-between;padding:8px 0;">
                            <span style="color:#8899BB;">Registered Users</span>
                            <span style="color:#34D399;font-weight:600;">${data.total_users}</span>
                        </div>
                        <div class="row" style="display:flex;justify-content:space-between;padding:8px 0;">
                            <span style="color:#8899BB;">Next Reset</span>
                            <span style="color:#FBBF24;font-weight:600;">${data.next_reset}</span>
                        </div>
                    `;
                    document.getElementById('stats-content').innerHTML = html;
                });
        }
        
        function loadLogs() {
            fetch('/api/logs')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.logs && data.logs.length > 0) {
                        data.logs.forEach(log => {
                            const colorClass = log.type === 'success' ? 'log-success' : log.type === 'error' ? 'log-error' : 'log-info';
                            html += `<div class="log-entry"><span class="log-time">[${log.time}]</span> <span class="${colorClass}">${log.message}</span></div>`;
                        });
                    } else {
                        html = '<div class="log-entry"><span class="log-time">[--:--:--]</span> <span class="log-info">No logs yet</span></div>';
                    }
                    document.getElementById('logs-container').innerHTML = html;
                });
        }
        
        function loadUsersDB() {
            fetch('/api/admin/users')
                .then(res => res.json())
                .then(data => {
                    let html = `
                        <div style="overflow-x:auto;">
                            <table class="user-db-table">
                                <thead><tr>
                                    <th>Email</th>
                                    <th>Usage</th>
                                    <th>Targets</th>
                                    <th>Auto-Like</th>
                                    <th>Last Active</th>
                                    <th>Created</th>
                                </tr></thead>
                                <tbody>
                    `;
                    if (data.users && Object.keys(data.users).length > 0) {
                        Object.entries(data.users).forEach(([email, info]) => {
                            const autoStatus = info.auto_like_unlocked ? 'Unlocked' : 'Locked';
                            const autoClass = info.auto_like_unlocked ? 'badge-unlocked' : 'badge-locked';
                            const targetCount = (info.auto_like_targets || []).length;
                            html += `
                                <tr>
                                    <td><strong>${email}</strong></td>
                                    <td>${info.usage || 0}</td>
                                    <td>${targetCount}</td>
                                    <td><span class="badge ${autoClass}">${autoStatus}</span></td>
                                    <td>${formatTime(info.last_active)}</td>
                                    <td>${formatTime(info.created_at)}</td>
                                </tr>
                            `;
                        });
                    } else {
                        html += `<tr><td colspan="6" style="text-align:center;color:#8899BB;">No users registered</td></tr>`;
                    }
                    html += `</tbody></table></div>`;
                    document.getElementById('user-db-content').innerHTML = html;
                });
        }
        
        function loadCodes() {
            fetch('/api/admin/codes')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.codes && data.codes.length > 0) {
                        data.codes.forEach(code => {
                            html += `<div class="user-item" style="background:rgba(56,189,248,0.05);border-color:rgba(56,189,248,0.1);">
                                <span style="font-family:monospace;font-weight:700;color:#38BDF8;">${code}</span>
                            </div>`;
                        });
                    } else {
                        html = '<div class="note">No active codes</div>';
                    }
                    document.getElementById('codes-list').innerHTML = html;
                });
        }
        
        function showResult(data) {
            document.getElementById('res-name').textContent = data.username || 'Unknown';
            document.getElementById('res-sent').textContent = data.likes_sent || 0;
            document.getElementById('res-before').textContent = data.likes_before || 0;
            document.getElementById('res-after').textContent = data.total_likes || 0;
            document.getElementById('res-added').textContent = data.verified_added || 0;
            document.getElementById('res-failed').textContent = data.failed || 0;
            document.getElementById('resultModal').classList.add('active');
        }
        
        function closeResult() { document.getElementById('resultModal').classList.remove('active'); }
        document.getElementById('resultModal').addEventListener('click', function(e) { if (e.target === this) closeResult(); });
        
        function getServer() { return currentServer; }
        
        function sendAdminLikes() {
            const uid = document.getElementById('target-uid-send').value.trim();
            const server = document.getElementById('server-send').value;
            if (!uid) { alert('Enter a target UID'); return; }
            if (!confirm('Send ALL likes to ' + uid + ' on ' + server + '?')) return;
            
            const btn = document.querySelector('.btn-rocket');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            btn.disabled = true;
            
            fetch('/send-likes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid, server_name: server, key: 'JMLB' })
            })
            .then(res => res.json())
            .then(data => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                if (data.success) {
                    showResult(data);
                    loadAdminData();
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            });
        }
        
        function adminVerify() {
            const uid = document.getElementById('admin-verify-uid').value.trim();
            const server = document.getElementById('admin-verify-server').value;
            if (!uid) { alert('Enter a UID'); return; }
            
            fetch('/verify-likes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid, server_name: server, key: 'JMLB' })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('admin-verify-result').innerHTML = '<div style="color:#F87171;">' + data.error + '</div>';
                    return;
                }
                document.getElementById('admin-verify-result').innerHTML = `
                    <div style="background:rgba(12,22,40,0.5);padding:14px;border-radius:12px;border:1px solid rgba(56,189,248,0.08);">
                        <div style="color:#38BDF8;font-weight:600;font-size:1em;">UID: ${data.uid}</div>
                        <div style="color:#F0F4FF;font-size:0.9em;">Name: ${data.username}</div>
                        <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:0.85em;color:#8899BB;">
                            <span>Total Likes</span>
                            <span style="color:#34D399;font-weight:600;">${data.likes}</span>
                        </div>
                    </div>
                `;
            });
        }
        
        function generateCode() {
            fetch('/api/admin/generate-code', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('Code generated: ' + data.code);
                        loadCodes();
                    } else {
                        alert('Error generating code');
                    }
                });
        }
        
        function unlockUserAuto() {
            const email = document.getElementById('user-email-unlock').value.trim();
            if (!email) { alert('Enter user email'); return; }
            
            fetch('/api/admin/unlock-user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    loadUsersDB();
                    document.getElementById('user-email-unlock').value = '';
                } else {
                    alert(data.message);
                }
            });
        }
        
        function deleteUser(uid) {
            if (!confirm('Remove ' + uid + ' from auto-queue?')) return;
            fetch('/delete-user', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ uid }) })
                .then(res => res.json())
                .then(data => { if (data.success) loadAdminData(); else alert(data.message); });
        }
        
        function deleteAllAuto() {
            if (!confirm('Clear entire auto-queue?')) return;
            fetch('/delete-all-users', { method: 'POST' })
                .then(res => res.json())
                .then(data => { if (data.success) loadAdminData(); else alert(data.message); });
        }
        
        function setAutoTime() {
            const hour = parseInt(document.getElementById('set-hour').value);
            const minute = parseInt(document.getElementById('set-minute').value);
            if (isNaN(hour) || isNaN(minute) || hour < 0 || hour > 23 || minute < 0 || minute > 59) {
                alert('Enter valid time (Hour: 0-23, Minute: 0-59)');
                return;
            }
            fetch('/set-auto-time', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hour, minute })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('time-status').textContent = data.message;
                document.getElementById('current-auto-time').textContent = String(hour).padStart(2,'0') + ':' + String(minute).padStart(2,'0') + ' IST';
                loadAdminData();
            });
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            const sel = document.getElementById('server-select-main');
            currentServer = sel.value;
            loadAdminData();
            loadAutoTime();
            setInterval(loadAdminData, 5000);
            setInterval(loadLogs, 5000);
            setInterval(loadHistory, 10000);
        });
    </script>
</body>
</html>
'''

# ============================================================
# ADMIN ROUTES
# ============================================================
@admin_bp.route('/')
def admin_index():
    if session.get('logged_in'):
        return render_template_string(ADMIN_HTML)
    return render_template_string(LOGIN_HTML)

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'HexMods' and password == 'ADI444':
        session['logged_in'] = True
        add_activity_log("Admin logged in", "success")
        return redirect('/admin')
    return redirect('/admin?error=1')

@admin_bp.route('/logout')
def admin_logout():
    session.pop('logged_in', None)
    add_activity_log("Admin logged out", "info")
    return redirect('/')

@admin_bp.route('/api/dashboard-data')
def dashboard_data():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    server = request.args.get('server', 'IND')
    accounts = load_accounts(server)
    total = len(accounts)
    total_likes = sum(len(v) for v in liked_cache.values())
    targets_liked = len(liked_cache)
    next_reset = get_next_reset_time().strftime('%Y-%m-%d %H:%M:%S IST')
    return jsonify({
        'total_accounts': total,
        'total_likes': total_likes,
        'targets_liked': targets_liked,
        'auto_users': len(auto_like_users),
        'total_users': len(user_db),
        'next_reset': next_reset,
        'users': auto_like_users,
        'user_stats': user_stats,
        'last_auto_run': None,
        'auto_run_status': 'Idle',
        'auto_run_message': '',
        'auto_time': f"{AUTO_LIKE_HOUR:02d}:{AUTO_LIKE_MINUTE:02d}"
    })

@admin_bp.route('/api/admin/accounts')
def get_admin_accounts():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    server = request.args.get('server', 'IND')
    accounts = load_accounts(server)
    return jsonify({'accounts': accounts, 'total': len(accounts)})

@admin_bp.route('/api/auto-time')
def get_auto_time():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'hour': AUTO_LIKE_HOUR,
        'minute': AUTO_LIKE_MINUTE,
        'time': f"{AUTO_LIKE_HOUR:02d}:{AUTO_LIKE_MINUTE:02d} IST"
    })

@admin_bp.route('/api/history')
def get_history():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'history': like_history[-50:]})

@admin_bp.route('/api/stats')
def get_stats():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    total_likes = sum(len(v) for v in liked_cache.values())
    total_targets = len(liked_cache)
    return jsonify({
        'total_likes_sent': total_likes,
        'total_targets': total_targets,
        'auto_users': len(auto_like_users),
        'total_users': len(user_db),
        'next_reset': get_next_reset_time().strftime('%Y-%m-%d %H:%M:%S IST')
    })

@admin_bp.route('/api/logs')
def get_logs():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'logs': activity_logs[-50:]})

@admin_bp.route('/api/admin/generate-code', methods=['POST'])
def generate_code():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    code = generate_admin_code()
    return jsonify({'success': True, 'code': code})

@admin_bp.route('/api/admin/codes')
def get_codes():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'codes': admin_codes})

@admin_bp.route('/api/admin/users')
def get_users():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'users': user_db})

@admin_bp.route('/api/admin/unlock-user', methods=['POST'])
def unlock_user():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    email = data.get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'message': 'Email required'})
    if unlock_user_auto_like(email):
        return jsonify({'success': True, 'message': f'Auto-like unlocked for {email}'})
    return jsonify({'success': False, 'message': 'User not found'})

@admin_bp.route('/verify-likes', methods=['POST'])
def verify_likes():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    uid = data.get('uid', '').strip()
    server_name = data.get('server_name', 'IND').upper()
    key = data.get('key', 'JMLB')
    if key != "JMLB":
        return jsonify({'error': 'Invalid key'})
    if not uid:
        return jsonify({'error': 'UID required'})
    user_info = asyncio.run(get_user_info(uid, server_name))
    if user_info:
        return jsonify({
            'uid': user_info['uid'],
            'username': user_info['name'],
            'likes': user_info['likes']
        })
    return jsonify({'error': 'User not found'})

@admin_bp.route('/send-likes', methods=['POST'])
def send_likes():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    data = request.get_json()
    uid = data.get('uid', '').strip()
    server_name = data.get('server_name', 'IND').upper()
    key = data.get('key', 'JMLB')
    if key != "JMLB":
        return jsonify({'success': False, 'error': 'Invalid key'})
    if not uid:
        return jsonify({'success': False, 'error': 'UID required'})
    
    user_info_before = asyncio.run(get_user_info(uid, server_name))
    before_likes = user_info_before.get('likes', 0) if user_info_before else 0
    before_name = user_info_before.get('name', 'Unknown') if user_info_before else 'Unknown'
    
    base_url = REGION_URLS.get(server_name, 'https://clientbp.ggpolarbear.com')
    like_url = f"{base_url}/LikeProfile"
    
    result = asyncio.run(send_likes_all_accounts(uid, server_name, like_url))
    likes_sent = result['success']
    
    user_info_after = asyncio.run(get_user_info(uid, server_name))
    if user_info_after:
        username = user_info_after.get('name', 'Unknown')
        current_likes = user_info_after.get('likes', 0)
        update_user_stats(uid, likes_sent, username, current_likes)
        add_to_history(uid, likes_sent, before_likes, current_likes, username, server_name)
        after_likes = current_likes
    else:
        after_likes = before_likes
        username = before_name
    
    return jsonify({
        'success': likes_sent > 0,
        'likes_sent': likes_sent,
        'username': username,
        'total_likes': after_likes,
        'likes_before': before_likes,
        'verified_added': after_likes - before_likes,
        'failed': result.get('failed', 0),
        'server': server_name
    })

@admin_bp.route('/delete-user', methods=['POST'])
def delete_user():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    data = request.get_json()
    uid = data.get('uid', '').strip()
    if uid in auto_like_users:
        auto_like_users.remove(uid)
        if uid in user_stats:
            del user_stats[uid]
        save_users()
        add_activity_log(f"Removed {uid} from auto-queue", "info")
        return jsonify({'success': True, 'message': f'Removed {uid}'})
    return jsonify({'success': False, 'message': 'UID not found'})

@admin_bp.route('/delete-all-users', methods=['POST'])
def delete_all_users():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    auto_like_users.clear()
    user_stats.clear()
    save_users()
    add_activity_log("Cleared entire auto-queue", "info")
    return jsonify({'success': True, 'message': 'All users deleted'})

@admin_bp.route('/set-auto-time', methods=['POST'])
def set_auto_time():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    data = request.get_json()
    hour = data.get('hour', 4)
    minute = data.get('minute', 0)
    result = set_auto_time(hour, minute)
    return jsonify({'success': True, 'message': result})

@admin_bp.route('/reset-cache', methods=['GET'])
def reset_cache():
    key = request.args.get("key")
    if key != "JMLB":
        return jsonify({"error": "Invalid key"}), 403
    reset_all_data()
    return jsonify({"message": "All data reset"})

@admin_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "accounts": len(load_accounts("IND"))})
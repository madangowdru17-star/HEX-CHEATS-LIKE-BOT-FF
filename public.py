from flask import Blueprint, request, jsonify, render_template_string, session
import asyncio
from app import (
    get_user_info, send_likes_all_accounts, update_user_stats,
    add_to_history, REGION_URLS, user_db, admin_codes,
    verify_admin_code, unlock_user_auto_like, add_auto_like_target,
    remove_auto_like_target, load_accounts, AUTO_LIKE_HOUR, AUTO_LIKE_MINUTE,
    add_activity_log, save_user_db
)

public_bp = Blueprint('public', __name__)

# ============================================================
# PUBLIC HTML
# ============================================================
PUBLIC_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HEX CHEATS</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #0D1117;
            color: #F8FAFC;
            min-height: 100vh;
            background-image: radial-gradient(circle at 15% 20%, rgba(0,229,255,0.04) 0%, transparent 50%),
                              radial-gradient(circle at 85% 80%, rgba(77,124,254,0.04) 0%, transparent 50%);
        }
        .main { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        .title-section { text-align: center; padding: 20px 0; }
        .title-section h1 {
            font-family: 'Orbitron', monospace;
            font-size: 2.8em;
            font-weight: 900;
            background: linear-gradient(135deg, #00E5FF, #00E676);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 4px;
            animation: titleGlow 3s ease-in-out infinite;
        }
        @keyframes titleGlow { 0%,100% { text-shadow: 0 0 20px rgba(0,229,255,0.2), 0 0 40px rgba(0,229,255,0.05); } 50% { text-shadow: 0 0 30px rgba(0,229,255,0.35), 0 0 60px rgba(0,229,255,0.1); } }
        .title-section .sub-title { font-size: 0.9em; color: #A8B3CF; letter-spacing: 8px; text-transform: uppercase; margin-top: 2px; font-weight: 400; }
        
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .tab-btn {
            padding: 12px 24px;
            background: rgba(22,27,34,0.6);
            border: 1px solid rgba(43,52,66,0.3);
            border-radius: 12px;
            color: #A8B3CF;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.85em;
            transition: 0.3s;
            font-family: 'Inter', sans-serif;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .tab-btn:hover { background: rgba(0,229,255,0.05); color: #00E5FF; }
        .tab-btn.active-tab {
            background: linear-gradient(135deg, rgba(0,229,255,0.15), rgba(0,230,118,0.10));
            color: #00E5FF;
            border-color: rgba(0,229,255,0.2);
        }
        .tab-btn i { font-size: 0.9em; }
        
        .glass {
            background: rgba(22,27,34,0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(43,52,66,0.4);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            border-radius: 16px;
            transition: 0.3s;
            padding: 30px;
            margin-bottom: 20px;
        }
        .glass:hover { border-color: rgba(0,229,255,0.12); }
        
        .tab-content { display: none; }
        .tab-content.active-tab { display: block; animation: fadeInUp 0.35s ease; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        .server-status-bar {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
            padding: 10px 0;
            margin-bottom: 10px;
        }
        .server-status-bar .status-item {
            background: rgba(0,0,0,0.2);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.8em;
            color: #A8B3CF;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .server-status-bar .status-item i { color: #00E5FF; }
        .server-status-bar .status-item .count { color: #00E676; font-weight: 700; }
        
        .input-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }
        .input-group input, .input-group select {
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid rgba(43,52,66,0.3);
            background: rgba(0,0,0,0.25);
            color: #F8FAFC;
            font-size: 1em;
            font-family: 'Inter', sans-serif;
            min-width: 140px;
            transition: 0.3s;
            flex: 1;
        }
        .input-group input:focus, .input-group select:focus { outline: none; border-color: rgba(0,229,255,0.2); box-shadow: 0 0 20px rgba(0,229,255,0.04); }
        .input-group select option { background: #0D1117; }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-weight: 700;
            font-size: 1em;
            transition: 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.3px;
            min-height: 48px;
            white-space: nowrap;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-rocket {
            background: linear-gradient(135deg, #00E5FF, #00E676);
            color: #0D1117;
            border: none;
        }
        .btn-rocket:hover { box-shadow: 0 0 30px rgba(0,229,255,0.2); }
        .btn-telegram { background: rgba(0,136,204,0.15); color: #00BFFF; border: 1px solid rgba(0,136,204,0.2); }
        .btn-telegram:hover { background: rgba(0,136,204,0.25); }
        .btn-youtube { background: rgba(255,0,0,0.15); color: #FF4444; border: 1px solid rgba(255,0,0,0.2); }
        .btn-youtube:hover { background: rgba(255,0,0,0.25); }
        .btn-unlock { background: rgba(255,200,0,0.15); color: #FFC107; border: 1px solid rgba(255,200,0,0.2); }
        .btn-unlock:hover { background: rgba(255,200,0,0.25); }
        .btn-success { background: rgba(0,230,118,0.15); color: #00E676; border: 1px solid rgba(0,230,118,0.2); }
        .btn-success:hover { background: rgba(0,230,118,0.25); }
        .btn-danger { background: rgba(255,77,109,0.15); color: #FF4D6D; border: 1px solid rgba(255,77,109,0.2); }
        .btn-danger:hover { background: rgba(255,77,109,0.25); }
        
        .note { color: #A8B3CF; font-size: 0.85em; margin-top: 12px; text-align: center; }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .social-links a { text-decoration: none; }
        
        .user-item {
            background: rgba(22,27,34,0.5);
            padding: 6px 16px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            border: 1px solid rgba(43,52,66,0.3);
            margin: 3px;
            font-size: 0.85em;
            transition: 0.3s;
        }
        .user-item .uid { font-weight: 600; color: #00E5FF; }
        .user-item .del-btn { background: none; border: none; color: #FF4D6D; cursor: pointer; padding: 0 4px; font-size: 1em; }
        
        .result-modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 999;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(8px);
        }
        .result-modal.active { display: flex; }
        .result-box {
            background: #161B22;
            padding: 35px 40px;
            border-radius: 18px;
            max-width: 500px;
            width: 90%;
            border: 1px solid rgba(43,52,66,0.4);
            box-shadow: 0 0 60px rgba(0,229,255,0.03);
            animation: fadeInUp 0.4s ease;
        }
        .result-box h2 {
            font-family: 'Orbitron', monospace;
            font-size: 1.1em;
            color: #00E5FF;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .result-box .row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(43,52,66,0.2);
        }
        .result-box .row .label { color: #A8B3CF; font-size: 0.9em; }
        .result-box .row .value { color: #00E676; font-weight: 600; font-size: 0.9em; }
        .result-box .row .value-failed { color: #FF4D6D; }
        .result-box .close-btn {
            margin-top: 16px;
            padding: 10px;
            background: rgba(255,255,255,0.04);
            color: #A8B3CF;
            border: 1px solid rgba(43,52,66,0.3);
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
            transition: 0.3s;
            font-family: 'Inter', sans-serif;
            font-size: 0.9em;
        }
        .result-box .close-btn:hover { background: rgba(255,255,255,0.08); color: #F8FAFC; }
        
        .footer-contact {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: rgba(255,200,0,0.05);
            border-radius: 12px;
            border: 1px solid rgba(255,200,0,0.1);
        }
        .footer-contact h3 { color: #FFC107; font-size: 1.1em; margin-bottom: 8px; }
        .footer-contact p { color: #A8B3CF; font-size: 0.9em; }
        .footer-contact a { color: #00E5FF; text-decoration: none; }
        .footer-contact a:hover { text-decoration: underline; }
        
        .verify-result-box {
            background: rgba(22,27,34,0.5);
            padding: 14px;
            border-radius: 12px;
            border: 1px solid rgba(43,52,66,0.3);
            margin-top: 12px;
        }
        .verify-result-box .uid-display { color: #00E5FF; font-weight: 600; font-size: 1em; }
        .verify-result-box .name-display { color: #F8FAFC; font-size: 0.9em; }
        .verify-result-box .likes-display { color: #00E676; font-weight: 600; font-size: 0.9em; }
        .verify-result-box .row-display { display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.85em; color: #A8B3CF; }
        
        .history-item {
            padding: 8px 0;
            border-bottom: 1px solid rgba(43,52,66,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 6px;
            font-size: 0.85em;
        }
        .history-item .uid { color: #00E5FF; font-weight: 600; }
        .history-item .name { color: #F8FAFC; }
        .history-item .likes { color: #00E676; font-weight: 600; }
        .history-item .time { color: #A8B3CF; font-size: 0.75em; }
        
        .badge { padding: 2px 12px; border-radius: 20px; font-size: 0.65em; font-weight: 600; display: inline-block; text-transform: uppercase; letter-spacing: 0.5px; }
        .badge-unlocked { background: rgba(0,229,255,0.12); color: #00E5FF; border: 1px solid rgba(0,229,255,0.06); }
        .badge-locked { background: rgba(255,200,0,0.12); color: #FFC107; border: 1px solid rgba(255,200,0,0.06); }
        
        @media (max-width: 768px) {
            .main { padding: 20px 15px; }
            .title-section h1 { font-size: 2em; }
            .glass { padding: 20px; }
            .input-group input { min-width: 100px; font-size: 0.9em; }
            .btn { font-size: 0.85em; padding: 10px 16px; min-height: 40px; }
            .result-box { padding: 20px; }
            .server-status-bar { gap: 8px; }
            .server-status-bar .status-item { font-size: 0.7em; padding: 4px 12px; }
            .social-links .btn { font-size: 0.8em; padding: 8px 14px; }
            .tabs { gap: 6px; }
            .tab-btn { padding: 8px 14px; font-size: 0.75em; }
        }
        @media (max-width: 480px) {
            .title-section h1 { font-size: 1.5em; }
            .title-section .sub-title { font-size: 0.6em; letter-spacing: 4px; }
            .input-group { flex-direction: column; }
            .input-group input, .input-group select { width: 100%; }
            .btn { width: 100%; justify-content: center; }
            .tab-btn { flex: 1; justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="main">
        <div class="title-section">
            <h1>HEX CHEATS</h1>
            <div class="sub-title">Like Bot System</div>
        </div>
        
        <div class="server-status-bar">
            <div class="status-item"><i class="fas fa-server"></i> Server: <span style="color:#00E5FF;font-weight:600;" id="pub-server">IND</span></div>
            <div class="status-item"><i class="fas fa-users"></i> Accounts: <span class="count" id="pub-accounts">0</span></div>
            <div class="status-item"><i class="fas fa-heart"></i> Auto-Like: <span id="auto-status-badge" class="badge badge-locked">Locked</span></div>
        </div>
        
        <div class="tabs">
            <button class="tab-btn active-tab" onclick="switchTab('send-tab')"><i class="fas fa-paper-plane"></i> Send</button>
            <button class="tab-btn" onclick="switchTab('verify-tab')"><i class="fas fa-check-double"></i> Verify</button>
            <button class="tab-btn" onclick="switchTab('auto-tab')"><i class="fas fa-clock"></i> Auto-Like</button>
            <button class="tab-btn" onclick="switchTab('history-tab')"><i class="fas fa-history"></i> History</button>
            <button class="tab-btn" onclick="switchTab('status-tab')"><i class="fas fa-chart-bar"></i> Status</button>
        </div>
        
        <!-- Send Tab -->
        <div id="send-tab" class="tab-content active-tab">
            <div class="glass">
                <h2 style="color:#A8B3CF; font-size:1em; letter-spacing:1px; text-transform:uppercase; font-weight:600; margin-bottom:15px;">
                    <i class="fas fa-rocket" style="color:#00E5FF;"></i> Send Likes
                </h2>
                <div class="input-group">
                    <input type="number" id="target-uid" placeholder="Enter Target UID" />
                    <select id="server-select" onchange="updateServerStatus(this.value)">
                        <option value="IND">India</option>
                        <option value="BD">Bangladesh</option>
                        <option value="MENA">MENA</option>
                        <option value="BR">Brazil</option>
                        <option value="US">US</option>
                        <option value="SAC">SAC</option>
                        <option value="NA">NA</option>
                        <option value="RU">Russia</option>
                    </select>
                    <button class="btn btn-rocket" onclick="sendLikes()"><i class="fas fa-paper-plane"></i> Send</button>
                </div>
                <div class="note"><i class="fas fa-info-circle"></i> Sends ALL likes from all available accounts to the target UID.</div>
            </div>
        </div>
        
        <!-- Verify Tab -->
        <div id="verify-tab" class="tab-content">
            <div class="glass">
                <h2 style="color:#A8B3CF; font-size:1em; letter-spacing:1px; text-transform:uppercase; font-weight:600; margin-bottom:15px;">
                    <i class="fas fa-check-double" style="color:#00E5FF;"></i> Verify Profile
                </h2>
                <div class="input-group">
                    <input type="number" id="verify-uid" placeholder="Enter UID" />
                    <select id="verify-server" onchange="updateServerStatus(this.value)">
                        <option value="IND">India</option>
                        <option value="BD">Bangladesh</option>
                        <option value="MENA">MENA</option>
                        <option value="BR">Brazil</option>
                        <option value="US">US</option>
                        <option value="SAC">SAC</option>
                        <option value="NA">NA</option>
                        <option value="RU">Russia</option>
                    </select>
                    <button class="btn btn-rocket" onclick="verifyProfile()"><i class="fas fa-check-double"></i> Verify</button>
                </div>
                <div id="verify-result"></div>
            </div>
        </div>
        
        <!-- Auto-Like Tab -->
        <div id="auto-tab" class="tab-content">
            <div class="glass" id="auto-glass">
                <h2 style="color:#A8B3CF; font-size:1em; letter-spacing:1px; text-transform:uppercase; font-weight:600; margin-bottom:15px;">
                    <i class="fas fa-clock" style="color:#FFC107;"></i> Auto Like
                    <span id="auto-status-label" style="color:#FFC107; font-size:0.7em;">Locked</span>
                </h2>
                
                <div id="auto-unlocked-content" style="display:none;">
                    <div class="input-group">
                        <input type="number" id="auto-target-uid" placeholder="Enter Target UID for Auto-Like" />
                        <button class="btn btn-success" onclick="addAutoTarget()"><i class="fas fa-plus"></i> Add Target</button>
                    </div>
                    <div id="auto-targets-list" style="margin-top:12px;"></div>
                    <div class="note"><i class="fas fa-info-circle"></i> Targets added here will receive auto-likes daily at <span id="auto-time-display">04:00</span> IST.</div>
                </div>
                
                <div id="auto-locked-content">
                    <div style="text-align:center; padding:20px 0;">
                        <i class="fas fa-lock" style="font-size:3em; color:#FFC107; opacity:0.5;"></i>
                        <p style="color:#A8B3CF; margin-top:10px;">Auto-Like feature is locked.</p>
                        <div class="input-group" style="justify-content:center; margin-top:15px;">
                            <input type="text" id="unlock-code" placeholder="Enter Unlock Code" style="max-width:250px;" />
                            <button class="btn btn-unlock" onclick="unlockAutoLike()"><i class="fas fa-key"></i> Unlock</button>
                        </div>
                        <div id="unlock-message" style="margin-top:10px;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- History Tab -->
        <div id="history-tab" class="tab-content">
            <div class="glass">
                <h2 style="color:#A8B3CF; font-size:1em; letter-spacing:1px; text-transform:uppercase; font-weight:600; margin-bottom:15px;">
                    <i class="fas fa-history" style="color:#00E5FF;"></i> Like History
                </h2>
                <div id="history-list">
                    <div class="note">Loading history...</div>
                </div>
            </div>
        </div>
        
        <!-- Status Tab -->
        <div id="status-tab" class="tab-content">
            <div class="glass">
                <h2 style="color:#A8B3CF; font-size:1em; letter-spacing:1px; text-transform:uppercase; font-weight:600; margin-bottom:15px;">
                    <i class="fas fa-chart-bar" style="color:#00E5FF;"></i> System Status
                </h2>
                <div id="status-content">
                    <div class="row-display" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(43,52,66,0.2);">
                        <span style="color:#A8B3CF;">Server</span>
                        <span style="color:#00E5FF;font-weight:600;" id="status-server">IND</span>
                    </div>
                    <div class="row-display" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(43,52,66,0.2);">
                        <span style="color:#A8B3CF;">Accounts Available</span>
                        <span style="color:#00E676;font-weight:600;" id="status-accounts">0</span>
                    </div>
                    <div class="row-display" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(43,52,66,0.2);">
                        <span style="color:#A8B3CF;">Auto-Like Status</span>
                        <span style="font-weight:600;" id="status-auto">Locked</span>
                    </div>
                    <div class="row-display" style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(43,52,66,0.2);">
                        <span style="color:#A8B3CF;">Auto-Like Time</span>
                        <span style="color:#FFC107;font-weight:600;" id="status-auto-time">04:00 IST</span>
                    </div>
                    <div class="row-display" style="display:flex;justify-content:space-between;padding:8px 0;">
                        <span style="color:#A8B3CF;">Total Likes Sent</span>
                        <span style="color:#00E676;font-weight:600;" id="status-total-likes">0</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="social-links">
            <a href="https://t.me/+dP7xLb3AoE1jNmRl" target="_blank">
                <button class="btn btn-telegram"><i class="fab fa-telegram"></i> Join Telegram</button>
            </a>
            <a href="https://t.me/HeX_CiPhEr" target="_blank">
                <button class="btn btn-telegram"><i class="fab fa-telegram"></i> Contact</button>
            </a>
            <a href="https://youtube.com/@define_hex?si=EJ86nAHxM29GfMqh" target="_blank">
                <button class="btn btn-youtube"><i class="fab fa-youtube"></i> YouTube</button>
            </a>
        </div>
        
        <div class="footer-contact">
            <h3><i class="fas fa-headset"></i> Need Help?</h3>
            <p>Contact us on <a href="https://t.me/HeX_CiPhEr" target="_blank">Telegram</a> for support or to get an unlock code.</p>
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
        let isAutoUnlocked = false;
        let autoTime = '04:00';
        
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active-tab'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active-tab'));
            document.getElementById(tabId).classList.add('active-tab');
            document.querySelector(`.tab-btn[onclick*="${tabId}"]`).classList.add('active-tab');
            if (tabId === 'history-tab') loadHistory();
            if (tabId === 'status-tab') loadStatus();
        }
        
        function updateServerStatus(server) {
            currentServer = server;
            document.getElementById('pub-server').textContent = server;
            document.querySelectorAll('#server-select, #verify-server').forEach(el => el.value = server);
            if (document.getElementById('status-server')) {
                document.getElementById('status-server').textContent = server;
            }
            loadPublicData();
        }
        
        function formatTime(iso) {
            if (!iso) return 'Never';
            try { const d = new Date(iso); return d.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }); } catch { return iso; }
        }
        
        function loadPublicData() {
            fetch('/api/public-data?server=' + currentServer)
                .then(res => res.json())
                .then(data => {
                    if (data.error) return;
                    document.getElementById('pub-accounts').textContent = data.total_accounts || 0;
                    if (document.getElementById('status-accounts')) {
                        document.getElementById('status-accounts').textContent = data.total_accounts || 0;
                    }
                });
        }
        
        function loadAutoTargets() {
            if (!isAutoUnlocked) return;
            fetch('/api/auto-targets')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.targets && data.targets.length > 0) {
                        data.targets.forEach(target => {
                            html += `<div class="user-item"><span class="uid">${target}</span><button class="del-btn" onclick="removeAutoTarget('${target}')"><i class="fas fa-times"></i></button></div>`;
                        });
                    } else {
                        html = '<div class="note">No targets added yet</div>';
                    }
                    document.getElementById('auto-targets-list').innerHTML = html;
                });
        }
        
        function loadHistory() {
            fetch('/api/public-history')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.history && data.history.length > 0) {
                        data.history.slice().reverse().forEach(h => {
                            html += `<div class="history-item">
                                <span><span class="uid">${h.uid}</span> <span class="name">${h.username || 'Unknown'}</span></span>
                                <span class="likes">+${h.likes_sent}</span>
                                <span class="time">${formatTime(h.timestamp)}</span>
                            </div>`;
                        });
                    } else {
                        html = '<div class="note">No history yet</div>';
                    }
                    document.getElementById('history-list').innerHTML = html;
                });
        }
        
        function loadStatus() {
            fetch('/api/public-status')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('status-accounts').textContent = data.total_accounts || 0;
                    document.getElementById('status-auto').textContent = data.auto_unlocked ? 'Unlocked' : 'Locked';
                    document.getElementById('status-auto').style.color = data.auto_unlocked ? '#00E676' : '#FFC107';
                    document.getElementById('status-auto-time').textContent = data.auto_time || '04:00 IST';
                    document.getElementById('status-total-likes').textContent = data.total_likes_sent || 0;
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
        
        function sendLikes() {
            const uid = document.getElementById('target-uid').value.trim();
            const server = document.getElementById('server-select').value;
            if (!uid) { alert('Enter a target UID'); return; }
            if (!confirm('Send likes to ' + uid + ' on ' + server + '?')) return;
            
            const btn = document.querySelector('#send-tab .btn-rocket');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            btn.disabled = true;
            
            fetch('/api/public-send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid, server_name: server })
            })
            .then(res => res.json())
            .then(data => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                if (data.success) {
                    showResult(data);
                    loadHistory();
                    loadStatus();
                } else {
                    alert('Error: ' + (data.error || 'Unknown error'));
                }
            });
        }
        
        function verifyProfile() {
            const uid = document.getElementById('verify-uid').value.trim();
            const server = document.getElementById('verify-server').value;
            if (!uid) { alert('Enter a UID'); return; }
            
            const btn = document.querySelector('#verify-tab .btn-rocket');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
            btn.disabled = true;
            
            fetch('/api/public-verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid, server_name: server })
            })
            .then(res => res.json())
            .then(data => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                if (data.error) {
                    document.getElementById('verify-result').innerHTML = '<div style="color:#FF4D6D;">' + data.error + '</div>';
                    return;
                }
                document.getElementById('verify-result').innerHTML = `
                    <div class="verify-result-box">
                        <div class="uid-display">UID: ${data.uid}</div>
                        <div class="name-display">Name: ${data.username}</div>
                        <div class="row-display">
                            <span>Total Likes</span>
                            <span class="likes-display">${data.likes}</span>
                        </div>
                    </div>
                `;
            });
        }
        
        function unlockAutoLike() {
            const code = document.getElementById('unlock-code').value.trim();
            if (!code) { alert('Enter an unlock code'); return; }
            
            fetch('/api/unlock-auto', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('unlock-message').innerHTML = '<div style="color:#00E676;">' + data.message + '</div>';
                    setTimeout(() => location.reload(), 1500);
                } else {
                    document.getElementById('unlock-message').innerHTML = '<div style="color:#FF4D6D;">' + data.message + '</div>';
                }
            });
        }
        
        function addAutoTarget() {
            const uid = document.getElementById('auto-target-uid').value.trim();
            if (!uid) { alert('Enter a target UID'); return; }
            
            fetch('/api/add-auto-target', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('auto-target-uid').value = '';
                    loadAutoTargets();
                } else {
                    alert(data.message);
                }
            });
        }
        
        function removeAutoTarget(uid) {
            if (!confirm('Remove ' + uid + ' from auto-like targets?')) return;
            fetch('/api/remove-auto-target', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uid })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) loadAutoTargets();
                else alert(data.message);
            });
        }
        
        function checkAutoStatus() {
            fetch('/api/check-auto-status')
                .then(res => res.json())
                .then(data => {
                    isAutoUnlocked = data.unlocked;
                    const badge = document.getElementById('auto-status-badge');
                    const label = document.getElementById('auto-status-label');
                    const lockedContent = document.getElementById('auto-locked-content');
                    const unlockedContent = document.getElementById('auto-unlocked-content');
                    
                    if (isAutoUnlocked) {
                        badge.className = 'badge badge-unlocked';
                        badge.textContent = 'Unlocked';
                        label.textContent = 'Unlocked';
                        label.style.color = '#00E676';
                        lockedContent.style.display = 'none';
                        unlockedContent.style.display = 'block';
                        document.getElementById('auto-time-display').textContent = data.auto_time || '04:00';
                        loadAutoTargets();
                    } else {
                        badge.className = 'badge badge-locked';
                        badge.textContent = 'Locked';
                        label.textContent = 'Locked';
                        label.style.color = '#FFC107';
                        lockedContent.style.display = 'block';
                        unlockedContent.style.display = 'none';
                    }
                    
                    if (data.auto_time) {
                        autoTime = data.auto_time;
                    }
                });
        }
        
        loadPublicData();
        checkAutoStatus();
        setInterval(loadPublicData, 10000);
        setInterval(checkAutoStatus, 30000);
    </script>
</body>
</html>
'''

@public_bp.route('/')
def index():
    return render_template_string(PUBLIC_HTML)

@public_bp.route('/api/public-data')
def public_data():
    server = request.args.get('server', 'IND')
    accounts = load_accounts(server)
    return jsonify({'total_accounts': len(accounts)})

@public_bp.route('/api/public-history')
def public_history():
    return jsonify({'history': like_history[-50:]})

@public_bp.route('/api/public-status')
def public_status():
    total_likes = sum(len(v) for v in liked_cache.values())
    return jsonify({
        'total_accounts': len(load_accounts('IND')),
        'total_likes_sent': total_likes,
        'auto_unlocked': session.get('auto_like_unlocked', False),
        'auto_time': f"{AUTO_LIKE_HOUR:02d}:{AUTO_LIKE_MINUTE:02d} IST"
    })

@public_bp.route('/api/check-auto-status')
def check_auto_status():
    return jsonify({
        'unlocked': session.get('auto_like_unlocked', False),
        'auto_time': f"{AUTO_LIKE_HOUR:02d}:{AUTO_LIKE_MINUTE:02d} IST"
    })

@public_bp.route('/api/public-send', methods=['POST'])
def public_send():
    data = request.get_json()
    uid = data.get('uid', '').strip()
    server_name = data.get('server_name', 'IND').upper()
    
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

@public_bp.route('/api/public-verify', methods=['POST'])
def public_verify():
    data = request.get_json()
    uid = data.get('uid', '').strip()
    server_name = data.get('server_name', 'IND').upper()
    
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

@public_bp.route('/api/unlock-auto', methods=['POST'])
def unlock_auto():
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    
    if not code:
        return jsonify({'success': False, 'message': 'Code required'})
    
    if verify_admin_code(code):
        session['auto_like_unlocked'] = True
        add_activity_log(f"User unlocked auto-like with code: {code}", "info")
        return jsonify({'success': True, 'message': 'Auto-like unlocked successfully!'})
    
    return jsonify({'success': False, 'message': 'Invalid code. Contact admin.'})

@public_bp.route('/api/auto-targets', methods=['GET'])
def get_auto_targets():
    email = session.get('user_email')
    if not email:
        return jsonify({'targets': []})
    
    targets = user_db.get(email, {}).get('auto_like_targets', [])
    return jsonify({'targets': targets})

@public_bp.route('/api/add-auto-target', methods=['POST'])
def add_auto_target():
    data = request.get_json()
    uid = data.get('uid', '').strip()
    email = session.get('user_email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    if not uid:
        return jsonify({'success': False, 'message': 'UID required'})
    
    if add_auto_like_target(email, uid):
        return jsonify({'success': True, 'message': f'Added {uid} to auto-like targets'})
    
    return jsonify({'success': False, 'message': 'Failed to add target'})

@public_bp.route('/api/remove-auto-target', methods=['POST'])
def remove_auto_target():
    data = request.get_json()
    uid = data.get('uid', '').strip()
    email = session.get('user_email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    if remove_auto_like_target(email, uid):
        return jsonify({'success': True, 'message': f'Removed {uid} from auto-like targets'})
    
    return jsonify({'success': False, 'message': 'Failed to remove target'})
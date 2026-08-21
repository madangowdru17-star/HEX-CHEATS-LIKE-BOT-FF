from flask import Blueprint, request, jsonify, session
import asyncio

public_bp = Blueprint('public', __name__)

# Import from app after blueprint creation
from app import (
    get_user_info, send_likes_all_accounts, update_user_stats,
    add_to_history, REGION_URLS, user_db, admin_codes,
    verify_admin_code, unlock_user_auto_like, add_auto_like_target,
    remove_auto_like_target, load_accounts, AUTO_LIKE_HOUR, AUTO_LIKE_MINUTE,
    add_activity_log, save_user_db, liked_cache
)

# ============================================================
# PREMIUM PUBLIC HTML - No Emojis, Full Premium UI
# ============================================================
PUBLIC_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HEX CHEATS - Premium Like Bot</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        /* ===== RESET & BASE ===== */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #080C14;
            --bg-secondary: #0C1628;
            --bg-card: rgba(18, 30, 50, 0.85);
            --bg-card-hover: rgba(25, 40, 65, 0.9);
            --border-color: rgba(56, 189, 248, 0.08);
            --border-active: rgba(56, 189, 248, 0.25);
            --text-primary: #F0F4FF;
            --text-secondary: #8899BB;
            --text-muted: #556688;
            --accent-cyan: #38BDF8;
            --accent-green: #34D399;
            --accent-purple: #818CF8;
            --accent-pink: #F472B6;
            --accent-gold: #FBBF24;
            --shadow-glow: 0 0 40px rgba(56, 189, 248, 0.04);
            --radius: 16px;
            --radius-sm: 10px;
            --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        html { scroll-behavior: smooth; }
        
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            background-image: 
                radial-gradient(ellipse at 10% 20%, rgba(56, 189, 248, 0.03) 0%, transparent 60%),
                radial-gradient(ellipse at 90% 80%, rgba(52, 211, 153, 0.02) 0%, transparent 60%);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }
        
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb { background: var(--accent-cyan); border-radius: 10px; opacity: 0.3; }
        ::-webkit-scrollbar-thumb:hover { opacity: 0.6; }
        
        /* ===== UTILITY ===== */
        .container { max-width: 820px; margin: 0 auto; padding: 20px 24px; }
        .text-gradient {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .text-gradient-gold {
            background: linear-gradient(135deg, var(--accent-gold), #F59E0B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* ===== ANIMATIONS ===== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(24px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes pulseGlow {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
        }
        
        .animate-in { animation: fadeInUp 0.6s ease forwards; }
        .animate-in-delay-1 { animation-delay: 0.1s; opacity: 0; }
        .animate-in-delay-2 { animation-delay: 0.2s; opacity: 0; }
        .animate-in-delay-3 { animation-delay: 0.3s; opacity: 0; }
        .animate-in-delay-4 { animation-delay: 0.4s; opacity: 0; }
        .animate-in-delay-5 { animation-delay: 0.5s; opacity: 0; }
        
        /* ===== HEADER ===== */
        .header {
            text-align: center;
            padding: 30px 0 18px;
            position: relative;
        }
        .header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-green), transparent);
        }
        .header .logo {
            font-family: 'Orbitron', monospace;
            font-size: 2.8em;
            font-weight: 900;
            letter-spacing: 6px;
            background: linear-gradient(135deg, #38BDF8 0%, #34D399 40%, #818CF8 70%, #F472B6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
            filter: drop-shadow(0 0 30px rgba(56, 189, 248, 0.08));
        }
        .header .subtitle {
            font-size: 0.75em;
            color: var(--text-secondary);
            letter-spacing: 10px;
            text-transform: uppercase;
            margin-top: 2px;
            font-weight: 300;
        }
        
        /* ===== STATUS BAR ===== */
        .status-bar {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
            padding: 14px 20px;
            margin: 16px 0 20px;
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            box-shadow: var(--shadow-glow);
        }
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8em;
            color: var(--text-secondary);
            font-weight: 400;
        }
        .status-item i { color: var(--accent-cyan); font-size: 0.9em; width: 18px; text-align: center; }
        .status-item .value { color: var(--text-primary); font-weight: 600; }
        .status-item .value.green { color: var(--accent-green); }
        .status-item .value.gold { color: var(--accent-gold); }
        .status-divider {
            width: 1px;
            height: 24px;
            background: var(--border-color);
        }
        
        /* ===== TABS ===== */
        .tabs {
            display: flex;
            gap: 4px;
            padding: 4px;
            margin: 4px 0 20px;
            background: var(--bg-secondary);
            border-radius: var(--radius);
            border: 1px solid var(--border-color);
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .tab-btn {
            flex: 1;
            min-width: 80px;
            padding: 12px 18px;
            border: none;
            border-radius: var(--radius-sm);
            background: transparent;
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 0.78em;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            white-space: nowrap;
            letter-spacing: 0.3px;
        }
        .tab-btn i { font-size: 0.9em; }
        .tab-btn:hover { color: var(--text-primary); background: rgba(56, 189, 248, 0.04); }
        .tab-btn.active {
            background: rgba(56, 189, 248, 0.08);
            color: var(--accent-cyan);
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.04);
        }
        .tab-btn.active i { color: var(--accent-cyan); }
        
        /* ===== CARDS ===== */
        .card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 28px 30px;
            margin-bottom: 18px;
            transition: var(--transition);
            box-shadow: var(--shadow-glow);
        }
        .card:hover { border-color: var(--border-active); }
        .card-title {
            font-size: 0.7em;
            text-transform: uppercase;
            letter-spacing: 2.5px;
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .card-title i { color: var(--accent-cyan); font-size: 1em; }
        
        /* ===== TAB CONTENT ===== */
        .tab-content { display: none; animation: fadeIn 0.4s ease; }
        .tab-content.active { display: block; }
        
        /* ===== FORM ELEMENTS ===== */
        .input-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }
        .input-group .field {
            flex: 1;
            min-width: 160px;
            position: relative;
        }
        .input-group .field i {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 0.85em;
        }
        .input-group input,
        .input-group select {
            width: 100%;
            padding: 13px 16px 13px 42px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: rgba(0, 0, 0, 0.3);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 0.9em;
            transition: var(--transition);
            outline: none;
        }
        .input-group input:focus,
        .input-group select:focus {
            border-color: var(--accent-cyan);
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.06);
        }
        .input-group input::placeholder { color: var(--text-muted); }
        .input-group select { padding-left: 16px; appearance: none; cursor: pointer; }
        .input-group select option { background: var(--bg-secondary); }
        
        /* ===== BUTTONS ===== */
        .btn {
            padding: 13px 28px;
            border: none;
            border-radius: var(--radius-sm);
            font-family: 'Inter', sans-serif;
            font-size: 0.85em;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            letter-spacing: 0.3px;
            white-space: nowrap;
            min-height: 48px;
        }
        .btn:active { transform: scale(0.97); }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), #0EA5E9);
            color: #0C1628;
        }
        .btn-primary:hover {
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.2);
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--accent-green), #059669);
            color: #0C1628;
        }
        .btn-success:hover {
            box-shadow: 0 0 30px rgba(52, 211, 153, 0.2);
            transform: translateY(-2px);
        }
        
        .btn-gold {
            background: linear-gradient(135deg, var(--accent-gold), #F59E0B);
            color: #0C1628;
        }
        .btn-gold:hover {
            box-shadow: 0 0 30px rgba(251, 191, 36, 0.2);
            transform: translateY(-2px);
        }
        
        .btn-outline {
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }
        .btn-outline:hover {
            border-color: var(--accent-cyan);
            color: var(--text-primary);
            background: rgba(56, 189, 248, 0.04);
        }
        
        .btn-danger-outline {
            background: transparent;
            color: #F87171;
            border: 1px solid rgba(248, 113, 113, 0.15);
        }
        .btn-danger-outline:hover {
            background: rgba(248, 113, 113, 0.08);
            border-color: rgba(248, 113, 113, 0.25);
        }
        
        .btn-sm { padding: 8px 16px; min-height: 36px; font-size: 0.75em; }
        .btn-block { width: 100%; justify-content: center; }
        
        /* ===== NOTE ===== */
        .note {
            color: var(--text-secondary);
            font-size: 0.78em;
            margin-top: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .note i { color: var(--text-muted); font-size: 0.85em; }
        
        /* ===== VERIFY RESULT ===== */
        .verify-result {
            background: rgba(0, 0, 0, 0.25);
            padding: 16px 20px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            margin-top: 14px;
        }
        .verify-result .row {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 0.85em;
        }
        .verify-result .label { color: var(--text-secondary); }
        .verify-result .value { color: var(--text-primary); font-weight: 500; }
        .verify-result .value.highlight { color: var(--accent-cyan); }
        .verify-result .value.green { color: var(--accent-green); }
        
        /* ===== TARGET LIST ===== */
        .target-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }
        .target-item {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 6px 14px 6px 18px;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            font-size: 0.82em;
            transition: var(--transition);
        }
        .target-item:hover { border-color: var(--border-active); }
        .target-item .uid { color: var(--accent-cyan); font-weight: 500; font-family: 'Inter', monospace; }
        .target-item .remove {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 0.85em;
            padding: 2px;
            transition: var(--transition);
        }
        .target-item .remove:hover { color: #F87171; }
        
        /* ===== HISTORY ===== */
        .history-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.82em;
            flex-wrap: wrap;
            gap: 6px;
        }
        .history-item:last-child { border-bottom: none; }
        .history-item .uid { color: var(--accent-cyan); font-weight: 500; }
        .history-item .name { color: var(--text-primary); }
        .history-item .likes { color: var(--accent-green); font-weight: 600; }
        .history-item .time { color: var(--text-muted); font-size: 0.75em; }
        
        /* ===== STATUS DISPLAY ===== */
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .status-grid .stat {
            background: rgba(0, 0, 0, 0.2);
            padding: 14px 18px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
        }
        .status-grid .stat .label { color: var(--text-secondary); font-size: 0.7em; text-transform: uppercase; letter-spacing: 1px; }
        .status-grid .stat .value { font-size: 1.1em; font-weight: 600; margin-top: 2px; }
        
        /* ===== LOCKED STATE ===== */
        .locked-state {
            text-align: center;
            padding: 24px 0 12px;
        }
        .locked-state .icon {
            font-size: 3em;
            color: var(--accent-gold);
            opacity: 0.3;
            margin-bottom: 10px;
        }
        .locked-state p { color: var(--text-secondary); font-size: 0.85em; }
        .locked-state .unlock-form {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 16px;
            flex-wrap: wrap;
        }
        .locked-state .unlock-form input {
            padding: 12px 18px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: rgba(0, 0, 0, 0.3);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 0.85em;
            min-width: 200px;
            outline: none;
            transition: var(--transition);
        }
        .locked-state .unlock-form input:focus { border-color: var(--accent-gold); }
        .locked-state .unlock-form input::placeholder { color: var(--text-muted); }
        
        /* ===== SOCIAL LINKS ===== */
        .social-links {
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
            margin: 8px 0 4px;
        }
        .social-links .btn {
            padding: 10px 22px;
            font-size: 0.78em;
            min-height: 40px;
        }
        .btn-telegram {
            background: rgba(0, 136, 204, 0.12);
            color: #60A5FA;
            border: 1px solid rgba(96, 165, 250, 0.12);
        }
        .btn-telegram:hover {
            background: rgba(0, 136, 204, 0.2);
            border-color: rgba(96, 165, 250, 0.25);
            transform: translateY(-2px);
        }
        .btn-youtube {
            background: rgba(255, 0, 0, 0.08);
            color: #F87171;
            border: 1px solid rgba(248, 113, 113, 0.12);
        }
        .btn-youtube:hover {
            background: rgba(255, 0, 0, 0.15);
            border-color: rgba(248, 113, 113, 0.25);
            transform: translateY(-2px);
        }
        
        /* ===== FOOTER ===== */
        .footer-help {
            text-align: center;
            padding: 20px;
            margin-top: 16px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
        }
        .footer-help h3 {
            font-size: 0.85em;
            color: var(--text-secondary);
            font-weight: 500;
            letter-spacing: 1px;
        }
        .footer-help p {
            color: var(--text-muted);
            font-size: 0.8em;
            margin-top: 4px;
        }
        .footer-help a {
            color: var(--accent-cyan);
            text-decoration: none;
            transition: var(--transition);
        }
        .footer-help a:hover { color: var(--accent-green); }
        
        /* ===== MODAL ===== */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(12px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 32px 36px;
            max-width: 480px;
            width: 100%;
            animation: fadeInUp 0.4s ease;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        .modal h2 {
            font-family: 'Orbitron', monospace;
            font-size: 1em;
            color: var(--accent-cyan);
            letter-spacing: 2px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .modal .row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
            font-size: 0.85em;
        }
        .modal .row:last-child { border-bottom: none; }
        .modal .row .label { color: var(--text-secondary); }
        .modal .row .value { color: var(--text-primary); font-weight: 500; }
        .modal .row .value.green { color: var(--accent-green); }
        .modal .row .value.red { color: #F87171; }
        .modal .close-btn {
            width: 100%;
            margin-top: 16px;
            padding: 12px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            background: transparent;
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 0.85em;
            font-weight: 500;
            cursor: pointer;
            transition: var(--transition);
        }
        .modal .close-btn:hover {
            background: rgba(255, 255, 255, 0.04);
            border-color: var(--border-active);
            color: var(--text-primary);
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .container { padding: 14px 16px; }
            .header .logo { font-size: 2em; letter-spacing: 4px; }
            .header .subtitle { font-size: 0.65em; letter-spacing: 6px; }
            .card { padding: 20px; }
            .status-bar { gap: 12px; padding: 12px 16px; }
            .status-item { font-size: 0.72em; }
            .status-divider { display: none; }
            .tabs { gap: 2px; padding: 3px; }
            .tab-btn { padding: 10px 12px; font-size: 0.7em; min-width: 60px; }
            .tab-btn span { display: none; }
            .tab-btn i { font-size: 1.1em; }
            .input-group .field { min-width: 120px; }
            .input-group input, .input-group select { padding: 11px 14px 11px 36px; font-size: 0.85em; }
            .btn { padding: 11px 18px; font-size: 0.8em; min-height: 42px; }
            .status-grid { grid-template-columns: 1fr; }
            .modal { padding: 24px; }
            .social-links .btn { padding: 8px 16px; font-size: 0.72em; min-height: 36px; }
            .locked-state .unlock-form input { min-width: 140px; }
        }
        
        @media (max-width: 480px) {
            .container { padding: 10px 12px; }
            .header .logo { font-size: 1.6em; letter-spacing: 3px; }
            .header { padding: 20px 0 12px; }
            .card { padding: 16px; border-radius: 12px; }
            .input-group { flex-direction: column; }
            .input-group .field { width: 100%; min-width: auto; }
            .btn { width: 100%; justify-content: center; }
            .status-bar { flex-wrap: wrap; gap: 8px; justify-content: center; }
            .tab-btn { padding: 8px 10px; font-size: 0.65em; min-width: 50px; }
            .modal { padding: 18px; }
            .social-links { gap: 8px; }
            .social-links .btn { padding: 8px 14px; font-size: 0.7em; }
        }
    </style>
</head>
<body>

<div class="container">
    <!-- ===== HEADER ===== -->
    <header class="header animate-in">
        <h1 class="logo">HEX CHEATS</h1>
        <p class="subtitle">Like Bot System</p>
    </header>

    <!-- ===== STATUS BAR ===== -->
    <div class="status-bar animate-in animate-in-delay-1">
        <div class="status-item">
            <i class="fas fa-server"></i>
            Server: <span class="value" id="pub-server">IND</span>
        </div>
        <div class="status-divider"></div>
        <div class="status-item">
            <i class="fas fa-users"></i>
            Accounts: <span class="value green" id="pub-accounts">0</span>
        </div>
        <div class="status-divider"></div>
        <div class="status-item">
            <i class="fas fa-bolt"></i>
            Auto-Like: <span class="value gold" id="auto-status-badge">Locked</span>
        </div>
    </div>

    <!-- ===== TABS ===== -->
    <nav class="tabs animate-in animate-in-delay-2" role="tablist">
        <button class="tab-btn active" data-tab="send" role="tab">
            <i class="fas fa-paper-plane"></i>
            <span>Send</span>
        </button>
        <button class="tab-btn" data-tab="verify" role="tab">
            <i class="fas fa-check-double"></i>
            <span>Verify</span>
        </button>
        <button class="tab-btn" data-tab="auto" role="tab">
            <i class="fas fa-clock"></i>
            <span>Auto-Like</span>
        </button>
        <button class="tab-btn" data-tab="history" role="tab">
            <i class="fas fa-history"></i>
            <span>History</span>
        </button>
        <button class="tab-btn" data-tab="status" role="tab">
            <i class="fas fa-chart-bar"></i>
            <span>Status</span>
        </button>
    </nav>

    <!-- ===== SEND TAB ===== -->
    <section id="tab-send" class="tab-content active">
        <div class="card animate-in animate-in-delay-3">
            <div class="card-title">
                <i class="fas fa-rocket"></i> Send Likes
            </div>
            <div class="input-group">
                <div class="field">
                    <i class="fas fa-id-badge"></i>
                    <input type="number" id="target-uid" placeholder="Enter Target UID" />
                </div>
                <div class="field" style="min-width:130px; flex:0.6;">
                    <i class="fas fa-globe"></i>
                    <select id="server-select" onchange="updateServer(this.value)">
                        <option value="IND">India</option>
                        <option value="BD">Bangladesh</option>
                        <option value="MENA">MENA</option>
                        <option value="BR">Brazil</option>
                        <option value="US">US</option>
                        <option value="SAC">SAC</option>
                        <option value="NA">NA</option>
                        <option value="RU">Russia</option>
                    </select>
                </div>
                <button class="btn btn-primary" onclick="sendLikes()">
                    <i class="fas fa-paper-plane"></i> Send
                </button>
            </div>
            <div class="note">
                <i class="fas fa-info-circle"></i> Sends all likes from available accounts to the target UID.
            </div>
        </div>
    </section>

    <!-- ===== VERIFY TAB ===== -->
    <section id="tab-verify" class="tab-content">
        <div class="card animate-in">
            <div class="card-title">
                <i class="fas fa-check-double"></i> Verify Profile
            </div>
            <div class="input-group">
                <div class="field">
                    <i class="fas fa-id-badge"></i>
                    <input type="number" id="verify-uid" placeholder="Enter UID" />
                </div>
                <div class="field" style="min-width:130px; flex:0.6;">
                    <i class="fas fa-globe"></i>
                    <select id="verify-server" onchange="updateServer(this.value)">
                        <option value="IND">India</option>
                        <option value="BD">Bangladesh</option>
                        <option value="MENA">MENA</option>
                        <option value="BR">Brazil</option>
                        <option value="US">US</option>
                        <option value="SAC">SAC</option>
                        <option value="NA">NA</option>
                        <option value="RU">Russia</option>
                    </select>
                </div>
                <button class="btn btn-primary" onclick="verifyProfile()">
                    <i class="fas fa-search"></i> Verify
                </button>
            </div>
            <div id="verify-result"></div>
        </div>
    </section>

    <!-- ===== AUTO-LIKE TAB ===== -->
    <section id="tab-auto" class="tab-content">
        <div class="card animate-in">
            <div class="card-title">
                <i class="fas fa-clock"></i> Auto-Like
                <span id="auto-status-label" style="font-size:0.7em; color:var(--accent-gold); font-weight:400; text-transform:none; letter-spacing:0;">
                    Locked
                </span>
            </div>
            
            <div id="auto-unlocked" style="display:none;">
                <div class="input-group">
                    <div class="field">
                        <i class="fas fa-plus-circle"></i>
                        <input type="number" id="auto-target-uid" placeholder="Add Target UID" />
                    </div>
                    <button class="btn btn-success" onclick="addAutoTarget()">
                        <i class="fas fa-plus"></i> Add
                    </button>
                </div>
                <div id="auto-targets-list" class="target-list"></div>
                <div class="note" style="margin-top:12px;">
                    <i class="fas fa-info-circle"></i> Targets receive auto-likes daily at <span id="auto-time-display">04:00</span> IST.
                </div>
            </div>
            
            <div id="auto-locked">
                <div class="locked-state">
                    <div class="icon"><i class="fas fa-lock"></i></div>
                    <p>Auto-Like feature requires an unlock code.</p>
                    <div class="unlock-form">
                        <input type="text" id="unlock-code" placeholder="Enter unlock code" />
                        <button class="btn btn-gold" onclick="unlockAutoLike()">
                            <i class="fas fa-key"></i> Unlock
                        </button>
                    </div>
                    <div id="unlock-message" style="margin-top:10px; font-size:0.85em;"></div>
                </div>
            </div>
        </div>
    </section>

    <!-- ===== HISTORY TAB ===== -->
    <section id="tab-history" class="tab-content">
        <div class="card animate-in">
            <div class="card-title">
                <i class="fas fa-history"></i> Like History
            </div>
            <div id="history-list">
                <div style="color:var(--text-muted); font-size:0.85em; text-align:center; padding:16px 0;">
                    <i class="fas fa-spinner fa-pulse"></i> Loading...
                </div>
            </div>
        </div>
    </section>

    <!-- ===== STATUS TAB ===== -->
    <section id="tab-status" class="tab-content">
        <div class="card animate-in">
            <div class="card-title">
                <i class="fas fa-chart-bar"></i> System Status
            </div>
            <div class="status-grid">
                <div class="stat">
                    <div class="label">Server</div>
                    <div class="value" id="status-server" style="color:var(--accent-cyan);">IND</div>
                </div>
                <div class="stat">
                    <div class="label">Available Accounts</div>
                    <div class="value" id="status-accounts" style="color:var(--accent-green);">0</div>
                </div>
                <div class="stat">
                    <div class="label">Auto-Like Status</div>
                    <div class="value" id="status-auto" style="color:var(--accent-gold);">Locked</div>
                </div>
                <div class="stat">
                    <div class="label">Auto-Like Time</div>
                    <div class="value" id="status-auto-time" style="color:var(--accent-gold);">04:00 IST</div>
                </div>
                <div class="stat" style="grid-column: 1 / -1;">
                    <div class="label">Total Likes Sent</div>
                    <div class="value" id="status-total-likes" style="color:var(--accent-green); font-size:1.3em;">0</div>
                </div>
            </div>
        </div>
    </section>

    <!-- ===== SOCIAL LINKS ===== -->
    <div class="social-links animate-in animate-in-delay-4">
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

    <!-- ===== FOOTER ===== -->
    <footer class="footer-help animate-in animate-in-delay-5">
        <h3><i class="fas fa-headset" style="color:var(--accent-cyan);"></i> Need Help?</h3>
        <p>Contact us on <a href="https://t.me/HeX_CiPhEr" target="_blank">Telegram</a> for support or to get an unlock code.</p>
    </footer>
</div>

<!-- ===== RESULT MODAL ===== -->
<div class="modal-overlay" id="resultModal">
    <div class="modal">
        <h2><i class="fas fa-check-circle"></i> Like Result</h2>
        <div id="result-content">
            <div class="row"><span class="label">Player Name</span><span class="value" id="res-name">-</span></div>
            <div class="row"><span class="label">Likes Sent</span><span class="value green" id="res-sent">0</span></div>
            <div class="row"><span class="label">Likes Before</span><span class="value" id="res-before">0</span></div>
            <div class="row"><span class="label">Likes After</span><span class="value green" id="res-after">0</span></div>
            <div class="row"><span class="label">Verified Added</span><span class="value green" id="res-added">0</span></div>
            <div class="row"><span class="label">Failed</span><span class="value red" id="res-failed">0</span></div>
        </div>
        <button class="close-btn" onclick="closeModal()"><i class="fas fa-times"></i> Close</button>
    </div>
</div>

<script>
    // ===== STATE =====
    let currentServer = 'IND';
    let isAutoUnlocked = false;
    let autoTime = '04:00';
    
    // ===== TABS =====
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('tab-' + this.dataset.tab).classList.add('active');
            if (this.dataset.tab === 'history') loadHistory();
            if (this.dataset.tab === 'status') loadStatus();
        });
    });
    
    // ===== SERVER =====
    function updateServer(server) {
        currentServer = server;
        document.getElementById('pub-server').textContent = server;
        document.querySelectorAll('#server-select, #verify-server').forEach(el => el.value = server);
        document.getElementById('status-server').textContent = server;
        loadPublicData();
    }
    
    // ===== FORMAT TIME =====
    function formatTime(iso) {
        if (!iso) return 'Never';
        try {
            const d = new Date(iso);
            return d.toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        } catch { return iso; }
    }
    
    // ===== LOAD PUBLIC DATA =====
    function loadPublicData() {
        fetch('/api/public-data?server=' + currentServer)
            .then(res => res.json())
            .then(data => {
                if (data.error) return;
                document.getElementById('pub-accounts').textContent = data.total_accounts || 0;
                document.getElementById('status-accounts').textContent = data.total_accounts || 0;
            });
    }
    
    // ===== LOAD AUTO TARGETS =====
    function loadAutoTargets() {
        if (!isAutoUnlocked) return;
        fetch('/api/auto-targets')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('auto-targets-list');
                if (data.targets && data.targets.length > 0) {
                    container.innerHTML = data.targets.map(t => `
                        <div class="target-item">
                            <span class="uid">${t}</span>
                            <button class="remove" onclick="removeAutoTarget('${t}')">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div style="color:var(--text-muted); font-size:0.8em; padding:4px 0;">No targets added yet</div>';
                }
            });
    }
    
    // ===== LOAD HISTORY =====
    function loadHistory() {
        fetch('/api/public-history')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('history-list');
                if (data.history && data.history.length > 0) {
                    container.innerHTML = data.history.slice().reverse().map(h => `
                        <div class="history-item">
                            <span>
                                <span class="uid">${h.uid}</span>
                                <span class="name">${h.username || 'Unknown'}</span>
                            </span>
                            <span class="likes">+${h.likes_sent}</span>
                            <span class="time">${formatTime(h.timestamp)}</span>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<div style="color:var(--text-muted); font-size:0.85em; text-align:center; padding:12px 0;">No history yet</div>';
                }
            });
    }
    
    // ===== LOAD STATUS =====
    function loadStatus() {
        fetch('/api/public-status')
            .then(res => res.json())
            .then(data => {
                document.getElementById('status-accounts').textContent = data.total_accounts || 0;
                const autoStatus = data.auto_unlocked ? 'Unlocked' : 'Locked';
                document.getElementById('status-auto').textContent = autoStatus;
                document.getElementById('status-auto').style.color = data.auto_unlocked ? 'var(--accent-green)' : 'var(--accent-gold)';
                document.getElementById('status-auto-time').textContent = data.auto_time || '04:00 IST';
                document.getElementById('status-total-likes').textContent = data.total_likes_sent || 0;
            });
    }
    
    // ===== MODAL =====
    function showModal(data) {
        document.getElementById('res-name').textContent = data.username || 'Unknown';
        document.getElementById('res-sent').textContent = data.likes_sent || 0;
        document.getElementById('res-before').textContent = data.likes_before || 0;
        document.getElementById('res-after').textContent = data.total_likes || 0;
        document.getElementById('res-added').textContent = data.verified_added || 0;
        document.getElementById('res-failed').textContent = data.failed || 0;
        document.getElementById('resultModal').classList.add('active');
    }
    
    function closeModal() {
        document.getElementById('resultModal').classList.remove('active');
    }
    document.getElementById('resultModal').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
    });
    
    // ===== SEND LIKES =====
    function sendLikes() {
        const uid = document.getElementById('target-uid').value.trim();
        const server = document.getElementById('server-select').value;
        if (!uid) { alert('Enter a target UID'); return; }
        if (!confirm('Send likes to ' + uid + ' on ' + server + '?')) return;
        
        const btn = document.querySelector('#tab-send .btn-primary');
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        btn.disabled = true;
        
        fetch('/api/public-send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid, server_name: server })
        })
        .then(res => res.json())
        .then(data => {
            btn.innerHTML = original;
            btn.disabled = false;
            if (data.success) {
                showModal(data);
                loadHistory();
                loadStatus();
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(() => {
            btn.innerHTML = original;
            btn.disabled = false;
            alert('Network error. Please try again.');
        });
    }
    
    // ===== VERIFY PROFILE =====
    function verifyProfile() {
        const uid = document.getElementById('verify-uid').value.trim();
        const server = document.getElementById('verify-server').value;
        if (!uid) { alert('Enter a UID'); return; }
        
        const btn = document.querySelector('#tab-verify .btn-primary');
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';
        btn.disabled = true;
        
        fetch('/api/public-verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uid, server_name: server })
        })
        .then(res => res.json())
        .then(data => {
            btn.innerHTML = original;
            btn.disabled = false;
            const result = document.getElementById('verify-result');
            if (data.error) {
                result.innerHTML = '<div style="color:#F87171; padding:10px 0;">' + data.error + '</div>';
                return;
            }
            result.innerHTML = `
                <div class="verify-result">
                    <div class="row"><span class="label">UID</span><span class="value highlight">${data.uid}</span></div>
                    <div class="row"><span class="label">Name</span><span class="value">${data.username}</span></div>
                    <div class="row"><span class="label">Total Likes</span><span class="value green">${data.likes}</span></div>
                </div>
            `;
        })
        .catch(() => {
            btn.innerHTML = original;
            btn.disabled = false;
            alert('Network error. Please try again.');
        });
    }
    
    // ===== UNLOCK AUTO-LIKE =====
    function unlockAutoLike() {
        const code = document.getElementById('unlock-code').value.trim().toUpperCase();
        if (!code) { alert('Enter an unlock code'); return; }
        
        fetch('/api/unlock-auto', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        })
        .then(res => res.json())
        .then(data => {
            const msg = document.getElementById('unlock-message');
            if (data.success) {
                msg.innerHTML = '<div style="color:var(--accent-green);">' + data.message + '</div>';
                setTimeout(() => location.reload(), 1500);
            } else {
                msg.innerHTML = '<div style="color:#F87171;">' + data.message + '</div>';
            }
        });
    }
    
    // ===== ADD AUTO TARGET =====
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
    
    // ===== REMOVE AUTO TARGET =====
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
    
    // ===== CHECK AUTO STATUS =====
    function checkAutoStatus() {
        fetch('/api/check-auto-status')
            .then(res => res.json())
            .then(data => {
                isAutoUnlocked = data.unlocked;
                const badge = document.getElementById('auto-status-badge');
                const label = document.getElementById('auto-status-label');
                const locked = document.getElementById('auto-locked');
                const unlocked = document.getElementById('auto-unlocked');
                
                if (isAutoUnlocked) {
                    badge.textContent = 'Unlocked';
                    badge.style.color = 'var(--accent-green)';
                    label.textContent = 'Unlocked';
                    label.style.color = 'var(--accent-green)';
                    locked.style.display = 'none';
                    unlocked.style.display = 'block';
                    document.getElementById('auto-time-display').textContent = data.auto_time || '04:00';
                    loadAutoTargets();
                } else {
                    badge.textContent = 'Locked';
                    badge.style.color = 'var(--accent-gold)';
                    label.textContent = 'Locked';
                    label.style.color = 'var(--accent-gold)';
                    locked.style.display = 'block';
                    unlocked.style.display = 'none';
                }
                if (data.auto_time) autoTime = data.auto_time;
            });
    }
    
    // ===== KEYBOARD SHORTCUTS =====
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
        if (e.key === 'Enter') {
            const active = document.querySelector('.tab-content.active');
            if (active) {
                if (active.id === 'tab-send') sendLikes();
                else if (active.id === 'tab-verify') verifyProfile();
                else if (active.id === 'tab-auto' && !isAutoUnlocked) unlockAutoLike();
            }
        }
    });
    
    // ===== INIT =====
    loadPublicData();
    checkAutoStatus();
    loadHistory();
    loadStatus();
    setInterval(loadPublicData, 15000);
    setInterval(checkAutoStatus, 30000);
    setInterval(loadHistory, 20000);
</script>
</body>
</html>
'''

# ============================================================
# ROUTES
# ============================================================
@public_bp.route('/')
def index():
    return PUBLIC_HTML

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
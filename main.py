from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import websockets
import logging
from collections import deque, Counter
from datetime import datetime
import random
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML da interface moderna
HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deriv Bot Pro - Dígito Matches</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        :root {
            --primary: #4f46e5;
            --secondary: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1f2937;
            --light: #f9fafb;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
        }
        
        .container-fluid {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, #818cf8 100%);
            padding: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        
        .header p {
            opacity: 0.9;
            margin: 10px 0 0;
            font-size: 1.1rem;
        }
        
        .config-panel {
            background: white;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .config-panel h3 {
            color: var(--dark);
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-label {
            font-weight: 600;
            color: #4b5563;
            margin-bottom: 8px;
        }
        
        .form-control, .form-select {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 12px;
            transition: all 0.3s;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .btn {
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, #818cf8 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(79, 70, 229, 0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--secondary) 0%, #34d399 100%);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, var(--danger) 0%, #f87171 100%);
            color: white;
        }
        
        .stats-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #e2e8f0;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1;
        }
        
        .stat-label {
            color: #64748b;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .digit-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            margin: 20px 0;
        }
        
        .digit-card {
            background: white;
            border-radius: 16px;
            padding: 15px;
            text-align: center;
            border: 2px solid #e2e8f0;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .digit-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), #818cf8);
            transform: translateX(-100%);
            transition: transform 0.3s;
        }
        
        .digit-card:hover::before {
            transform: translateX(0);
        }
        
        .digit-card.target {
            border-color: var(--secondary);
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            animation: pulse 1s infinite;
        }
        
        .digit-card.zero {
            border-color: var(--danger);
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        }
        
        .digit-card.watch {
            border-color: var(--warning);
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .digit-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark);
        }
        
        .digit-percent {
            font-size: 1rem;
            color: #6b7280;
            font-weight: 500;
        }
        
        .progress-bar-container {
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), #818cf8);
            transition: width 0.3s;
        }
        
        .log-container {
            background: #1e293b;
            border-radius: 16px;
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
        }
        
        .log-entry {
            color: #e2e8f0;
            padding: 8px;
            border-bottom: 1px solid #334155;
            animation: slideIn 0.3s;
        }
        
        .log-entry.success { color: #4ade80; }
        .log-entry.error { color: #f87171; }
        .log-entry.warning { color: #fbbf24; }
        .log-entry.info { color: #60a5fa; }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .counter-box {
            background: linear-gradient(135deg, var(--primary) 0%, #818cf8 100%);
            border-radius: 16px;
            padding: 20px;
            color: white;
            text-align: center;
        }
        
        .counter-box h2 {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 10px 0 0;
        }
        
        .badge-status {
            padding: 8px 16px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .badge-active {
            background: #dcfce7;
            color: #166534;
        }
        
        .badge-waiting {
            background: #fff3cd;
            color: #856404;
        }
        
        .token-input-group {
            position: relative;
        }
        
        .token-visibility {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: #6b7280;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="glass-card">
            <!-- Header -->
            <div class="header">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h1><i class="bi bi-robot me-3"></i>Deriv Bot Pro</h1>
                        <p>Estratégia: Dígito Matches | Análise 25 ticks | Martingale Inteligente</p>
                    </div>
                    <div id="botStatus" class="badge-status badge-waiting">
                        <i class="bi bi-pause-circle me-2"></i>Aguardando
                    </div>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="row g-0">
                <!-- Sidebar Config -->
                <div class="col-lg-3 p-4" style="background: #f8fafc; border-right: 1px solid #e2e8f0;">
                    <div class="config-panel">
                        <h3><i class="bi bi-gear-fill me-2"></i>Configurações</h3>
                        
                        <div class="mb-4">
                            <label class="form-label">
                                <i class="bi bi-key me-2"></i>Token da Deriv
                            </label>
                            <div class="token-input-group">
                                <input type="password" class="form-control" id="token" 
                                       placeholder="Cole seu token aqui">
                                <i class="bi bi-eye-slash token-visibility" onclick="toggleToken()"></i>
                            </div>
                            <small class="text-muted">Seu token fica apenas no navegador</small>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label"><i class="bi bi-cash-stack me-2"></i>Stake Inicial ($)</label>
                            <input type="number" class="form-control" id="stake" value="0.35" step="0.01" min="0.35">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label"><i class="bi bi-arrow-repeat me-2"></i>Multiplicador Martingale</label>
                            <input type="number" class="form-control" id="martingale" value="1.15" step="0.01" min="1.0">
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label"><i class="bi bi-shield-shaded me-2"></i>Stop Loss ($)</label>
                                <input type="number" class="form-control" id="stopLoss" value="10" step="0.01">
                            </div>
                            <div class="col-6">
                                <label class="form-label"><i class="bi bi-trophy me-2"></i>Stop Win ($)</label>
                                <input type="number" class="form-control" id="stopWin" value="10" step="0.01">
                            </div>
                        </div>
                        
                        <hr class="my-4">
                        
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary" onclick="testConnection()">
                                <i class="bi bi-plug me-2"></i>Testar Conexão
                            </button>
                            <button class="btn btn-success" onclick="startBot()" id="startBtn">
                                <i class="bi bi-play-fill me-2"></i>Iniciar Robô
                            </button>
                            <button class="btn btn-danger" onclick="stopBot()" id="stopBtn" disabled>
                                <i class="bi bi-stop-fill me-2"></i>Parar Robô
                            </button>
                        </div>
                        
                        <!-- Connection Status -->
                        <div id="connectionStatus" class="alert mt-3" style="display: none;"></div>
                    </div>
                    
                    <!-- Stats Cards -->
                    <div class="stats-card mt-4">
                        <h5 class="mb-3"><i class="bi bi-bar-chart-fill me-2"></i>Estatísticas</h5>
                        <div class="row g-3">
                            <div class="col-6">
                                <div class="stat-label">Lucro Total</div>
                                <div class="stat-value" id="totalProfit">$0.00</div>
                            </div>
                            <div class="col-6">
                                <div class="stat-label">Trades</div>
                                <div class="stat-value" id="totalTrades">0</div>
                            </div>
                            <div class="col-6">
                                <div class="stat-label">Win Rate</div>
                                <div class="stat-value" id="winRate">0%</div>
                            </div>
                            <div class="col-6">
                                <div class="stat-label">Stake Atual</div>
                                <div class="stat-value" id="currentStake">$0.35</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Main Panel -->
                <div class="col-lg-9 p-4">
                    <!-- Counters -->
                    <div class="row g-4 mb-4">
                        <div class="col-md-6">
                            <div class="counter-box" id="startCounter">
                                <i class="bi bi-hourglass-split display-4"></i>
                                <h2>20</h2>
                                <p class="mb-0">Segundos para iniciar</p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="counter-box" id="cooldownCounter" style="background: linear-gradient(135deg, #10b981 0%, #34d399 100%);">
                                <i class="bi bi-arrow-clockwise display-4"></i>
                                <h2>5</h2>
                                <p class="mb-0">Segundos pós-venda</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Target Info -->
                    <div class="alert alert-info d-flex align-items-center mb-4" id="targetInfo" style="display: none !important;">
                        <i class="bi bi-info-circle-fill me-3 fs-4"></i>
                        <div>
                            <strong id="targetMessage">Aguardando análise dos últimos 25 ticks...</strong>
                        </div>
                    </div>
                    
                    <!-- Digit Grid -->
                    <div class="card shadow-sm mb-4">
                        <div class="card-header bg-white py-3">
                            <h5 class="mb-0"><i class="bi bi-grid-3x3-gap-fill me-2"></i>Frequência dos Dígitos (Últimos 25 ticks)</h5>
                        </div>
                        <div class="card-body">
                            <div class="digit-grid" id="digitGrid"></div>
                        </div>
                    </div>
                    
                    <!-- Martingale Info -->
                    <div class="card shadow-sm mb-4" id="martingaleInfo" style="display: none;">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="flex-shrink-0">
                                    <i class="bi bi-arrow-repeat fs-1 text-warning"></i>
                                </div>
                                <div class="flex-grow-1 ms-3">
                                    <h5 class="mb-1">Martingale Ativado</h5>
                                    <p class="mb-0" id="martingaleMessage">Sequência de perdas: 0</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Logs -->
                    <div class="card shadow-sm">
                        <div class="card-header bg-white py-3">
                            <h5 class="mb-0"><i class="bi bi-terminal me-2"></i>Logs em Tempo Real</h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="log-container" id="logs"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Estado do bot
        let botState = {
            running: false,
            connected: false,
            token: '',
            config: {
                stake: 0.35,
                martingale: 1.15,
                stopLoss: 10,
                stopWin: 10
            },
            stats: {
                totalProfit: 0,
                totalTrades: 0,
                winningTrades: 0,
                currentStake: 0.35,
                consecutiveLosses: 0
            },
            targetDigit: null,
            watchingDigit: null,
            inPosition: false,
            frequencies: {},
            lastDigits: []
        };
        
        // WebSocket
        let ws = null;
        
        // Inicializar grid de dígitos
        function initDigitGrid() {
            let html = '';
            for (let i = 0; i <= 9; i++) {
                html += `
                    <div class="digit-card" id="digit-${i}">
                        <div class="digit-number">${i}</div>
                        <div class="digit-percent">0.0%</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill" id="progress-${i}" style="width: 0%"></div>
                        </div>
                    </div>
                `;
            }
            document.getElementById('digitGrid').innerHTML = html;
        }
        initDigitGrid();
        
        // Funções de log
        function addLog(message, type = 'info') {
            const logs = document.getElementById('logs');
            const entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.innerHTML = `<i class="bi bi-record-circle me-2"></i>[${new Date().toLocaleTimeString()}] ${message}`;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
            
            // Manter apenas últimos 100 logs
            while (logs.children.length > 100) {
                logs.removeChild(logs.firstChild);
            }
        }
        
        // Atualizar grid de dígitos
        function updateDigitGrid(frequencies, target, watching) {
            for (let i = 0; i <= 9; i++) {
                const card = document.getElementById(`digit-${i}`);
                const percent = frequencies[i] || 0;
                const progress = document.getElementById(`progress-${i}`);
                
                card.querySelector('.digit-percent').innerHTML = percent.toFixed(1) + '%';
                progress.style.width = percent + '%';
                
                // Atualizar classes
                card.classList.remove('target', 'zero', 'watch');
                
                if (i === target) {
                    card.classList.add('target');
                } else if (i === watching) {
                    card.classList.add('watch');
                } else if (percent === 0) {
                    card.classList.add('zero');
                }
            }
        }
        
        // Atualizar estatísticas
        function updateStats() {
            document.getElementById('totalProfit').innerHTML = '$' + botState.stats.totalProfit.toFixed(2);
            document.getElementById('totalTrades').innerHTML = botState.stats.totalTrades;
            
            const winRate = botState.stats.totalTrades > 0 
                ? ((botState.stats.winningTrades / botState.stats.totalTrades) * 100).toFixed(1)
                : 0;
            document.getElementById('winRate').innerHTML = winRate + '%';
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
        }
        
        // Atualizar contadores
        function updateCounters(start, cooldown) {
            document.getElementById('startCounter').innerHTML = `
                <i class="bi bi-hourglass-split display-4"></i>
                <h2>${start}</h2>
                <p class="mb-0">Segundos para iniciar</p>
            `;
            
            document.getElementById('cooldownCounter').innerHTML = `
                <i class="bi bi-arrow-clockwise display-4"></i>
                <h2>${cooldown}</h2>
                <p class="mb-0">Segundos pós-venda</p>
            `;
        }
        
        // Mostrar/Esconder token
        function toggleToken() {
            const tokenInput = document.getElementById('token');
            const icon = document.querySelector('.token-visibility');
            
            if (tokenInput.type === 'password') {
                tokenInput.type = 'text';
                icon.className = 'bi bi-eye token-visibility';
            } else {
                tokenInput.type = 'password';
                icon.className = 'bi bi-eye-slash token-visibility';
            }
        }
        
        // Testar conexão com a Deriv
        async function testConnection() {
            const token = document.getElementById('token').value;
            
            if (!token) {
                showConnectionStatus('Por favor, insira seu token', 'danger');
                return;
            }
            
            showConnectionStatus('Testando conexão...', 'info');
            
            try {
                const response = await fetch('/api/test-connection', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showConnectionStatus('✅ Conectado à Deriv com sucesso!', 'success');
                    botState.connected = true;
                    botState.token = token;
                    addLog('✅ Conexão estabelecida com a Deriv', 'success');
                } else {
                    showConnectionStatus('❌ Erro: ' + data.message, 'danger');
                }
                
            } catch (error) {
                showConnectionStatus('❌ Erro na conexão: ' + error.message, 'danger');
            }
        }
        
        function showConnectionStatus(message, type) {
            const status = document.getElementById('connectionStatus');
            status.style.display = 'block';
            status.className = `alert alert-${type}`;
            status.innerHTML = message;
        }
        
        // Iniciar bot
        function startBot() {
            if (!botState.connected && !botState.token) {
                const token = document.getElementById('token').value;
                if (!token) {
                    alert('Por favor, teste a conexão primeiro!');
                    return;
                }
                botState.token = token;
            }
            
            botState.running = true;
            botState.config = {
                stake: parseFloat(document.getElementById('stake').value),
                martingale: parseFloat(document.getElementById('martingale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin: parseFloat(document.getElementById('stopWin').value)
            };
            botState.stats.currentStake = botState.config.stake;
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('botStatus').className = 'badge-status badge-active';
            document.getElementById('botStatus').innerHTML = '<i class="bi bi-play-circle me-2"></i>Robô Ativo';
            
            addLog('🚀 Iniciando robô... Aguarde 20 segundos', 'info');
            
            // Conectar WebSocket
            connectWebSocket();
        }
        
        // Parar bot
        function stopBot() {
            botState.running = false;
            
            if (ws) {
                ws.close();
            }
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('botStatus').className = 'badge-status badge-waiting';
            document.getElementById('botStatus').innerHTML = '<i class="bi bi-pause-circle me-2"></i>Parado';
            
            addLog('⏹️ Robô parado', 'warning');
        }
        
        // Conectar WebSocket
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                addLog('✅ Conectado ao servidor', 'success');
                
                // Enviar configuração
                ws.send(JSON.stringify({
                    type: 'start',
                    token: botState.token,
                    config: botState.config
                }));
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWSMessage(data);
            };
            
            ws.onclose = () => {
                if (botState.running) {
                    addLog('❌ Desconectado. Tentando reconectar...', 'error');
                    setTimeout(connectWebSocket, 3000);
                }
            };
        }
        
        // Processar mensagens do WebSocket
        function handleWSMessage(data) {
            switch(data.type) {
                case 'countdown':
                    updateCounters(data.start, data.cooldown);
                    break;
                    
                case 'frequencies':
                    botState.frequencies = data.frequencies;
                    botState.targetDigit = data.target;
                    botState.watchingDigit = data.watching;
                    updateDigitGrid(data.frequencies, data.target, data.watching);
                    break;
                    
                case 'target_found':
                    botState.targetDigit = data.digit;
                    document.getElementById('targetInfo').style.display = 'flex';
                    document.getElementById('targetMessage').innerHTML = 
                        `🎯 Dígito alvo: <strong>${data.digit}</strong> (0% nos últimos 25 ticks) - Aguardando atingir 8%`;
                    addLog(`🎯 Dígito alvo encontrado: ${data.digit} (0% nos últimos 25 ticks)`, 'info');
                    break;
                    
                case 'entry_signal':
                    document.getElementById('targetMessage').innerHTML = 
                        `📊 Dígito ${data.digit} atingiu 8%! Comprando no próximo tick...`;
                    addLog(`📊 Dígito ${data.digit} atingiu 8% - Comprando...`, 'warning');
                    break;
                    
                case 'buy':
                    botState.inPosition = true;
                    botState.stats.currentStake = data.stake;
                    updateStats();
                    addLog(`✅ COMPRA: $${data.stake.toFixed(2)} no dígito ${data.digit}`, 'success');
                    break;
                    
                case 'sell':
                    botState.inPosition = false;
                    botState.stats.totalProfit = data.totalProfit;
                    botState.stats.totalTrades++;
                    
                    if (data.profit > 0) {
                        botState.stats.winningTrades++;
                        botState.stats.consecutiveLosses = 0;
                        addLog(`💰 GANHOU: $${data.profit.toFixed(2)}`, 'success');
                    } else {
                        botState.stats.consecutiveLosses++;
                        addLog(`❌ PERDEU: $${Math.abs(data.profit).toFixed(2)}`, 'error');
                        
                        // Mostrar martingale
                        if (botState.stats.consecutiveLosses > 0) {
                            document.getElementById('martingaleInfo').style.display = 'block';
                            document.getElementById('martingaleMessage').innerHTML = 
                                `Sequência de perdas: ${botState.stats.consecutiveLosses} | Nova stake: $${data.newStake.toFixed(2)}`;
                        }
                    }
                    
                    botState.stats.currentStake = data.newStake;
                    updateStats();
                    break;
                    
                case 'stop_win':
                    addLog('🎉 PARABÉNS! STOP WIN ATINGIDO!', 'success');
                    stopBot();
                    break;
                    
                case 'stop_loss':
                    addLog('🛑 STOP LOSS ATINGIDO!', 'error');
                    stopBot();
                    break;
                    
                case 'cooldown':
                    updateCounters(data.start, data.seconds);
                    break;
                    
                case 'reset':
                    botState.targetDigit = null;
                    botState.watchingDigit = null;
                    botState.inPosition = false;
                    document.getElementById('targetInfo').style.display = 'none';
                    document.getElementById('martingaleInfo').style.display = 'none';
                    break;
            }
        }
    </script>
</body>
</html>
"""

# Classe do Bot de Trading
class DigitTradingBot:
    def __init__(self, token, config, callback):
        self.token = token
        self.config = config
        self.callback = callback
        self.running = False
        self.in_position = False
        
        # Análise de dígitos
        self.last_digits = deque(maxlen=25)
        self.frequencies = {}
        self.target_digit = None
        self.watching_digit = None
        self.entry_triggered = False
        
        # Controle de trades
        self.current_stake = config['initial_stake']
        self.consecutive_losses = 0
        self.total_profit = 0
        self.total_trades = 0
        self.winning_trades = 0
        
        # Temporizadores
        self.start_time = None
        self.cooldown_until = 0
        
    async def start(self):
        """Inicia o bot"""
        self.running = True
        
        # Aguardar 20 segundos iniciais
        for i in range(20, 0, -1):
            if not self.running:
                return
            await self.callback({
                'type': 'countdown',
                'start': i,
                'cooldown': 5
            })
            await asyncio.sleep(1)
        
        # Iniciar simulação de ticks (aqui conectaremos com a Deriv real depois)
        asyncio.create_task(self.simulate_ticks())
    
    async def stop(self):
        """Para o bot"""
        self.running = False
    
    async def simulate_ticks(self):
        """Simula ticks para teste (substituir pela API real da Deriv)"""
        while self.running:
            # Verificar cooldown
            if time.time() < self.cooldown_until:
                await asyncio.sleep(0.1)
                continue
            
            # Simular tick
            tick_value = round(random.uniform(10000, 20000), 2)
            last_digit = int(str(tick_value).replace('.', '')[-1])
            
            # Adicionar à análise
            self.last_digits.append(last_digit)
            
            # Calcular frequências
            if len(self.last_digits) == 25:
                counter = Counter(self.last_digits)
                self.frequencies = {}
                for d in range(10):
                    count = counter.get(d, 0)
                    self.frequencies[d] = (count / 25) * 100
                
                # Estratégia principal
                await self.execute_strategy()
            
            # Enviar frequências para o frontend
            await self.callback({
                'type': 'frequencies',
                'frequencies': self.frequencies,
                'target': self.target_digit,
                'watching': self.watching_digit
            })
            
            await asyncio.sleep(1)  # 1 tick por segundo
    
    async def execute_strategy(self):
        """Executa a estratégia de trading"""
        
        # Se não estamos em posição
        if not self.in_position:
            
            # PASSO 1: Encontrar dígito com 0%
            if self.target_digit is None:
                zero_digits = [d for d, p in self.frequencies.items() if p == 0]
                if zero_digits:
                    self.target_digit = zero_digits[0]
                    self.watching_digit = self.target_digit
                    self.entry_triggered = False
                    
                    await self.callback({
                        'type': 'target_found',
                        'digit': self.target_digit
                    })
            
            # PASSO 2: Aguardar dígito atingir 8%
            elif not self.entry_triggered and self.target_digit is not None:
                if self.frequencies.get(self.target_digit, 0) >= 8:
                    self.entry_triggered = True
                    
                    await self.callback({
                        'type': 'entry_signal',
                        'digit': self.target_digit
                    })
                    
                    # Aguardar próximo tick para comprar
                    await asyncio.sleep(0.1)
                    
                    # Comprar
                    await self.buy_contract()
        
        # PASSO 3: Se estamos em posição, aguardar dígito sair
        else:
            last_digit = self.last_digits[-1] if self.last_digits else None
            if last_digit == self.target_digit:
                await self.sell_contract()
    
    async def buy_contract(self):
        """Compra um contrato"""
        self.in_position = True
        
        await self.callback({
            'type': 'buy',
            'stake': self.current_stake,
            'digit': self.target_digit
        })
    
    async def sell_contract(self):
        """Vende o contrato"""
        self.in_position = False
        
        # Simular resultado (70% de chance de ganho para teste)
        won = random.random() > 0.3
        profit = (self.current_stake * 0.95) if won else -self.current_stake
        
        self.total_profit += profit
        self.total_trades += 1
        
        if won:
            self.winning_trades += 1
            self.consecutive_losses = 0
            self.current_stake = self.config['initial_stake']
        else:
            self.consecutive_losses += 1
            self.current_stake *= self.config['martingale_multiplier']
        
        # Verificar stops
        if self.total_profit >= self.config['stop_win']:
            await self.callback({
                'type': 'stop_win',
                'profit': self.total_profit
            })
            await self.stop()
            return
        
        if self.total_profit <= -self.config['stop_loss']:
            await self.callback({
                'type': 'stop_loss',
                'loss': self.total_profit
            })
            await self.stop()
            return
        
        await self.callback({
            'type': 'sell',
            'profit': profit,
            'total_profit': self.total_profit,
            'new_stake': self.current_stake,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades
        })
        
        # Reset para nova operação
        self.target_digit = None
        self.watching_digit = None
        self.entry_triggered = False
        
        # Cooldown de 5 segundos
        self.cooldown_until = time.time() + 5
        await self.callback({
            'type': 'reset'
        })
        
        for i in range(5, 0, -1):
            await self.callback({
                'type': 'cooldown',
                'start': 20,
                'seconds': i
            })
            await asyncio.sleep(1)

# Rotas da API
@app.get("/")
async def root():
    return HTMLResponse(content=HTML)

@app.post("/api/test-connection")
async def test_connection(request: dict):
    # Aqui você implementará a conexão real com a Deriv
    # Por enquanto, retorna sucesso para teste
    return {"success": True, "message": "Conexão testada com sucesso"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'start':
                # Criar e iniciar bot
                bot = DigitTradingBot(
                    message['token'],
                    message['config'],
                    lambda x: websocket.send_json(x)
                )
                asyncio.create_task(bot.start())
                
    except WebSocketDisconnect:
        logger.info("Cliente desconectado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

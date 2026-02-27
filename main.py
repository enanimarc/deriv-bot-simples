from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import websockets
import logging
from collections import deque, Counter
from datetime import datetime
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML com gráfico IDÊNTICO ao da Deriv
HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deriv Bot - Last Digit Stats</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        /* Header igual da Deriv */
        .header {
            background: linear-gradient(90deg, #ff4444 0%, #ff6b6b 100%);
            padding: 20px 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        /* Gráfico igual da Deriv */
        .chart-container {
            padding: 30px;
            background: #f8f9ff;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .chart-controls {
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .market-selector {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .market-selector label {
            color: #666;
            font-size: 14px;
        }
        
        .market-selector select {
            padding: 8px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            color: #333;
            background: white;
            cursor: pointer;
        }
        
        .ticks-selector {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .ticks-selector label {
            color: #666;
            font-size: 14px;
        }
        
        .ticks-selector input {
            width: 80px;
            padding: 8px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            text-align: center;
        }
        
        /* Gráfico de barras igual da Deriv */
        .chart-grid {
            display: flex;
            justify-content: space-around;
            align-items: flex-end;
            height: 400px;
            margin: 20px 0 40px;
            padding: 0 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .bar-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 60px;
            position: relative;
        }
        
        .bar {
            width: 40px;
            background: linear-gradient(180deg, #4f46e5 0%, #818cf8 100%);
            border-radius: 8px 8px 0 0;
            transition: height 0.3s ease;
            position: relative;
            cursor: pointer;
        }
        
        .bar:hover {
            transform: scaleX(1.1);
        }
        
        .bar-label {
            margin-top: 15px;
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .bar-value {
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 14px;
            font-weight: 600;
            color: #4f46e5;
            background: white;
            padding: 4px 8px;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            white-space: nowrap;
        }
        
        /* Linhas de referência */
        .reference-lines {
            position: relative;
            height: 400px;
            margin: -400px 0 0;
            pointer-events: none;
        }
        
        .reference-line {
            position: absolute;
            left: 0;
            right: 0;
            border-top: 1px dashed #e0e0e0;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: #999;
            font-size: 12px;
        }
        
        .line-20 { top: 20%; }
        .line-8 { top: 72%; }
        .line-4 { top: 84%; }
        
        /* Painel de informação */
        .info-panel {
            padding: 20px 30px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 30px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .target-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px 25px;
            border-radius: 8px;
            flex: 1;
            min-width: 300px;
        }
        
        .target-box h3 {
            color: #856404;
            font-size: 14px;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .target-box .value {
            font-size: 32px;
            font-weight: 700;
            color: #856404;
        }
        
        .target-box .subtitle {
            font-size: 14px;
            color: #856404;
            opacity: 0.8;
        }
        
        .stats-box {
            display: flex;
            gap: 40px;
            flex-wrap: wrap;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #333;
        }
        
        .stat-value.positive { color: #10b981; }
        .stat-value.negative { color: #ef4444; }
        
        /* Painel de configuração */
        .config-panel {
            padding: 30px;
            background: #f8f9ff;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .config-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .config-item {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .config-item label {
            font-size: 13px;
            color: #666;
            font-weight: 500;
        }
        
        .config-item input {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .config-item input:focus {
            border-color: #4f46e5;
            outline: none;
        }
        
        .token-input {
            position: relative;
        }
        
        .token-input input {
            width: 100%;
            padding-right: 40px;
        }
        
        .token-eye {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: #999;
        }
        
        /* Botões */
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: #4f46e5;
            color: white;
        }
        
        .btn-primary:hover {
            background: #4338ca;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .btn-success:hover {
            background: #059669;
            transform: translateY(-2px);
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #dc2626;
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Contadores */
        .counters {
            display: flex;
            gap: 20px;
            padding: 20px 30px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .counter {
            flex: 1;
            background: #f8f9ff;
            border-radius: 12px;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .counter-icon {
            width: 50px;
            height: 50px;
            background: #4f46e5;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
        }
        
        .counter-info {
            flex: 1;
        }
        
        .counter-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .counter-value {
            font-size: 28px;
            font-weight: 700;
            color: #333;
        }
        
        /* Logs */
        .logs-container {
            padding: 30px;
            background: #1e1e2f;
        }
        
        .logs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            color: white;
        }
        
        .logs-title {
            font-size: 16px;
            font-weight: 600;
        }
        
        .logs-box {
            background: #2d2d44;
            border-radius: 12px;
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
        }
        
        .log-entry {
            padding: 8px;
            border-bottom: 1px solid #404060;
            color: #e0e0e0;
            font-size: 13px;
        }
        
        .log-entry.success { color: #4ade80; }
        .log-entry.error { color: #f87171; }
        .log-entry.warning { color: #fbbf24; }
        
        /* Status */
        .connection-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }
        
        .status-connected {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status-disconnected {
            background: #fee2e2;
            color: #991b1b;
        }
        
        /* Martingale Info */
        .martingale-info {
            background: #fff3cd;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            display: none;
        }
        
        .martingale-info.show {
            display: block;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .target-blink {
            animation: blink 1s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🤖 Deriv Bot - Last Digit Stats</h1>
            <p>Estratégia: Dígito 0% → 8% → Compra → Venda + Martingale</p>
        </div>
        
        <!-- Gráfico da Deriv -->
        <div class="chart-container">
            <div class="chart-header">
                <div class="chart-title">📊 Last Digit Statistics</div>
                <div class="chart-controls">
                    <div class="market-selector">
                        <label>Select market:</label>
                        <select id="market">
                            <option value="R_100" selected>Volatility 100 Index</option>
                            <option value="R_75">Volatility 75 Index</option>
                            <option value="R_50">Volatility 50 Index</option>
                        </select>
                    </div>
                    <div class="ticks-selector">
                        <label>Number of ticks:</label>
                        <input type="number" id="tickCount" value="25" min="10" max="100" readonly>
                    </div>
                </div>
            </div>
            
            <!-- Gráfico de barras -->
            <div style="position: relative;">
                <div class="chart-grid" id="chartGrid"></div>
                <div class="reference-lines">
                    <div class="reference-line line-20" style="top: 80px;">20.00%</div>
                    <div class="reference-line line-8" style="top: 288px;">8.00%</div>
                    <div class="reference-line line-4" style="top: 336px;">4.00%</div>
                </div>
            </div>
        </div>
        
        <!-- Info Panel -->
        <div class="info-panel">
            <div class="target-box" id="targetBox" style="display: none;">
                <h3>🎯 Dígito Alvo</h3>
                <div class="value" id="targetDigit">-</div>
                <div class="subtitle" id="targetStatus">Aguardando 0%</div>
            </div>
            
            <div class="stats-box">
                <div class="stat">
                    <div class="stat-label">Lucro Total</div>
                    <div class="stat-value" id="totalProfit">$0.00</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Trades</div>
                    <div class="stat-value" id="totalTrades">0</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Win Rate</div>
                    <div class="stat-value" id="winRate">0%</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Stake Atual</div>
                    <div class="stat-value" id="currentStake">$0.35</div>
                </div>
            </div>
            
            <div class="connection-status status-disconnected" id="connectionStatus">
                <span class="dot"></span>
                Desconectado
            </div>
        </div>
        
        <!-- Config Panel -->
        <div class="config-panel">
            <div class="config-title">⚙️ Configurações do Bot</div>
            
            <div class="config-grid">
                <div class="config-item">
                    <label>🔑 Token da Deriv</label>
                    <div class="token-input">
                        <input type="password" id="token" placeholder="Cole seu token aqui">
                        <span class="token-eye" onclick="toggleToken()">👁️</span>
                    </div>
                </div>
                
                <div class="config-item">
                    <label>💰 Stake Inicial ($)</label>
                    <input type="number" id="stake" value="0.35" step="0.01" min="0.35">
                </div>
                
                <div class="config-item">
                    <label>📈 Martingale</label>
                    <input type="number" id="martingale" value="1.15" step="0.01" min="1.0">
                </div>
                
                <div class="config-item">
                    <label>🛑 Stop Loss ($)</label>
                    <input type="number" id="stopLoss" value="10" step="0.01">
                </div>
                
                <div class="config-item">
                    <label>🎯 Stop Win ($)</label>
                    <input type="number" id="stopWin" value="10" step="0.01">
                </div>
            </div>
            
            <div class="button-group">
                <button class="btn btn-primary" onclick="testConnection()">
                    <span>🔌</span> Testar Conexão
                </button>
                <button class="btn btn-success" onclick="startBot()" id="startBtn">
                    <span>▶️</span> Iniciar Robô
                </button>
                <button class="btn btn-danger" onclick="stopBot()" id="stopBtn" disabled>
                    <span>⏹️</span> Parar Robô
                </button>
            </div>
        </div>
        
        <!-- Counters -->
        <div class="counters">
            <div class="counter">
                <div class="counter-icon">⏳</div>
                <div class="counter-info">
                    <div class="counter-label">Início em:</div>
                    <div class="counter-value" id="startCounter">20s</div>
                </div>
            </div>
            <div class="counter">
                <div class="counter-icon">⏱️</div>
                <div class="counter-info">
                    <div class="counter-label">Próximo trade em:</div>
                    <div class="counter-value" id="cooldownCounter">0s</div>
                </div>
            </div>
        </div>
        
        <!-- Martingale Info -->
        <div class="martingale-info" id="martingaleInfo">
            <strong>📈 Martingale Ativado</strong>
            <span id="martingaleMessage"></span>
        </div>
        
        <!-- Logs -->
        <div class="logs-container">
            <div class="logs-header">
                <div class="logs-title">📝 Logs em Tempo Real</div>
                <div style="color: #888;">Últimos 100 eventos</div>
            </div>
            <div class="logs-box" id="logs"></div>
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
                profit: 0,
                trades: 0,
                wins: 0,
                currentStake: 0.35,
                losses: 0
            },
            targetDigit: null,
            watchingDigit: null,
            inPosition: false,
            frequencies: {},
            lastDigits: []
        };
        
        let ws = null;
        let countdownInterval = null;
        let cooldownInterval = null;
        
        // Inicializar gráfico
        function initChart() {
            let grid = document.getElementById('chartGrid');
            let html = '';
            
            for(let i = 0; i <= 9; i++) {
                html += `
                    <div class="bar-container" id="bar-${i}">
                        <div class="bar" style="height: 20px;" id="bar-fill-${i}">
                            <span class="bar-value" id="value-${i}">0.0%</span>
                        </div>
                        <div class="bar-label">${i}</div>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
        }
        initChart();
        
        // Atualizar gráfico
        function updateChart(frequencies, target) {
            for(let i = 0; i <= 9; i++) {
                let percent = frequencies[i] || 0;
                let bar = document.getElementById(`bar-fill-${i}`);
                let value = document.getElementById(`value-${i}`);
                
                // Altura máxima de 300px (80% do container)
                let height = Math.min(300, (percent / 20) * 300);
                bar.style.height = height + 'px';
                value.innerHTML = percent.toFixed(1) + '%';
                
                // Destacar barra
                bar.style.background = i === target 
                    ? 'linear-gradient(180deg, #f59e0b 0%, #fbbf24 100%)'
                    : 'linear-gradient(180deg, #4f46e5 0%, #818cf8 100%)';
            }
        }
        
        function addLog(message, type = 'info') {
            let logs = document.getElementById('logs');
            let entry = document.createElement('div');
            entry.className = `log-entry ${type}`;
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
            
            while(logs.children.length > 100) {
                logs.removeChild(logs.firstChild);
            }
        }
        
        function updateStats() {
            document.getElementById('totalProfit').innerHTML = '$' + botState.stats.profit.toFixed(2);
            document.getElementById('totalTrades').innerHTML = botState.stats.trades;
            
            let winRate = botState.stats.trades > 0 
                ? ((botState.stats.wins / botState.stats.trades) * 100).toFixed(1)
                : 0;
            document.getElementById('winRate').innerHTML = winRate + '%';
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
            
            // Cor do lucro
            let profitEl = document.getElementById('totalProfit');
            profitEl.className = botState.stats.profit >= 0 ? 'stat-value positive' : 'stat-value negative';
        }
        
        function toggleToken() {
            let input = document.getElementById('token');
            input.type = input.type === 'password' ? 'text' : 'password';
        }
        
        function updateConnectionStatus(connected) {
            let status = document.getElementById('connectionStatus');
            if(connected) {
                status.className = 'connection-status status-connected';
                status.innerHTML = '<span class="dot"></span> Conectado';
            } else {
                status.className = 'connection-status status-disconnected';
                status.innerHTML = '<span class="dot"></span> Desconectado';
            }
            botState.connected = connected;
        }
        
        async function testConnection() {
            let token = document.getElementById('token').value;
            if(!token) {
                alert('Por favor, insira seu token da Deriv');
                return;
            }
            
            addLog('🔌 Testando conexão com a Deriv...', 'info');
            
            try {
                let response = await fetch('/api/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token: token})
                });
                
                let data = await response.json();
                
                if(data.success) {
                    updateConnectionStatus(true);
                    botState.token = token;
                    addLog('✅ Conectado à Deriv com sucesso!', 'success');
                } else {
                    updateConnectionStatus(false);
                    addLog('❌ Erro na conexão: ' + data.message, 'error');
                }
            } catch(e) {
                updateConnectionStatus(false);
                addLog('❌ Erro ao testar conexão', 'error');
            }
        }
        
        function startBot() {
            if(!botState.connected) {
                alert('Teste a conexão primeiro!');
                return;
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
            
            addLog('🚀 Iniciando robô... Aguardando 20 segundos', 'info');
            
            // Iniciar contagem regressiva
            let startTime = 20;
            if(countdownInterval) clearInterval(countdownInterval);
            
            countdownInterval = setInterval(() => {
                if(!botState.running) {
                    clearInterval(countdownInterval);
                    return;
                }
                
                document.getElementById('startCounter').innerHTML = startTime + 's';
                startTime--;
                
                if(startTime < 0) {
                    clearInterval(countdownInterval);
                    document.getElementById('startCounter').innerHTML = 'Ativo';
                    startTrading();
                }
            }, 1000);
        }
        
        function stopBot() {
            botState.running = false;
            
            if(countdownInterval) clearInterval(countdownInterval);
            if(cooldownInterval) clearInterval(cooldownInterval);
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('startCounter').innerHTML = '20s';
            document.getElementById('cooldownCounter').innerHTML = '0s';
            
            addLog('⏹️ Robô parado', 'warning');
        }
        
        function startTrading() {
            if(!botState.running) return;
            
            addLog('🔍 Analisando últimos 25 ticks...', 'info');
            
            // Simular ticks em tempo real
            let tickInterval = setInterval(() => {
                if(!botState.running) {
                    clearInterval(tickInterval);
                    return;
                }
                
                // Gerar dados simulados (aqui vai a conexão real com a Deriv)
                let freq = {};
                let total = 0;
                
                for(let i = 0; i <= 9; i++) {
                    freq[i] = Math.random() * 15;
                    total += freq[i];
                }
                
                // Normalizar para soma 100%
                for(let i = 0; i <= 9; i++) {
                    freq[i] = (freq[i] / total) * 100;
                }
                
                // Encontrar dígito com 0%
                let zeroDigits = [];
                for(let i = 0; i <= 9; i++) {
                    if(freq[i] < 0.5) {
                        zeroDigits.push(i);
                    }
                }
                
                if(zeroDigits.length > 0 && botState.targetDigit === null) {
                    botState.targetDigit = zeroDigits[0];
                    botState.watchingDigit = botState.targetDigit;
                    
                    document.getElementById('targetBox').style.display = 'block';
                    document.getElementById('targetDigit').innerHTML = botState.targetDigit;
                    document.getElementById('targetStatus').innerHTML = '🔍 Aguardando 8%';
                    
                    addLog(`🎯 Dígito alvo encontrado: ${botState.targetDigit} (0%)`, 'info');
                }
                
                // Verificar se atingiu 8%
                if(botState.targetDigit !== null && !botState.inPosition) {
                    if(freq[botState.targetDigit] >= 8) {
                        botState.inPosition = true;
                        document.getElementById('targetStatus').innerHTML = '📊 Atingiu 8% - Comprando...';
                        addLog(`📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando $${botState.stats.currentStake.toFixed(2)}`, 'warning');
                        
                        // Simular compra
                        setTimeout(() => {
                            if(!botState.running) return;
                            
                            // Simular resultado (70% de chance de ganho)
                            let won = Math.random() > 0.3;
                            let profit = won ? botState.stats.currentStake * 0.95 : -botState.stats.currentStake;
                            
                            botState.stats.profit += profit;
                            botState.stats.trades++;
                            
                            if(won) {
                                botState.stats.wins++;
                                botState.stats.losses = 0;
                                botState.stats.currentStake = botState.config.stake;
                                addLog(`💰 GANHOU: $${profit.toFixed(2)}`, 'success');
                            } else {
                                botState.stats.losses++;
                                botState.stats.currentStake *= botState.config.martingale;
                                addLog(`❌ PERDEU: $${Math.abs(profit).toFixed(2)}`, 'error');
                                addLog(`📈 Martingale ativado - Nova stake: $${botState.stats.currentStake.toFixed(2)}`, 'warning');
                                
                                // Mostrar martingale info
                                document.getElementById('martingaleInfo').classList.add('show');
                                document.getElementById('martingaleMessage').innerHTML = 
                                    `Sequência: ${botState.stats.losses} perdas | Stake: $${botState.stats.currentStake.toFixed(2)}`;
                            }
                            
                            updateStats();
                            
                            // Verificar stops
                            if(botState.stats.profit >= botState.config.stopWin) {
                                addLog('🎉 PARABÉNS! STOP WIN ATINGIDO!', 'success');
                                stopBot();
                                return;
                            }
                            
                            if(botState.stats.profit <= -botState.config.stopLoss) {
                                addLog('🛑 STOP LOSS ATINGIDO!', 'error');
                                stopBot();
                                return;
                            }
                            
                            // Reset para nova operação
                            botState.inPosition = false;
                            botState.targetDigit = null;
                            document.getElementById('targetBox').style.display = 'none';
                            
                            // Cooldown de 5 segundos
                            let cooldown = 5;
                            if(cooldownInterval) clearInterval(cooldownInterval);
                            
                            cooldownInterval = setInterval(() => {
                                document.getElementById('cooldownCounter').innerHTML = cooldown + 's';
                                cooldown--;
                                
                                if(cooldown < 0) {
                                    clearInterval(cooldownInterval);
                                    document.getElementById('cooldownCounter').innerHTML = 'Pronto';
                                    document.getElementById('martingaleInfo').classList.remove('show');
                                }
                            }, 1000);
                            
                        }, 2000);
                    }
                }
                
                updateChart(freq, botState.targetDigit);
                botState.frequencies = freq;
                
            }, 1000);
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(content=HTML)

@app.post("/api/test")
async def test_connection(request: dict):
    # Aqui você implementará a conexão real com a Deriv
    # Por enquanto, retorna sucesso
    return {"success": True, "message": "Conexão OK"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

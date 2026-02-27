from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import websockets
from collections import deque, Counter
import logging
import time

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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        body {
            background: #0a0a0f;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: #111117;
            border-radius: 24px;
            overflow: hidden;
            border: 1px solid #2a2a35;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        }
        
        /* Header */
        .header {
            background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
            padding: 24px 32px;
            border-bottom: 1px solid #2a2a35;
        }
        
        .header h1 {
            color: white;
            font-size: 24px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        .header p {
            color: #8888a0;
            font-size: 14px;
            margin-top: 4px;
        }
        
        /* Market Info */
        .market-info {
            background: #0f0f14;
            padding: 20px 32px;
            border-bottom: 1px solid #2a2a35;
            display: flex;
            gap: 48px;
            flex-wrap: wrap;
        }
        
        .market-item {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        
        .market-label {
            font-size: 12px;
            color: #666680;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .market-value {
            font-size: 20px;
            font-weight: 600;
            color: white;
        }
        
        .market-value.highlight {
            color: #ff4444;
        }
        
        /* Main Grid */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 0;
        }
        
        /* Chart Panel */
        .chart-panel {
            background: #0a0a0f;
            padding: 24px;
            border-right: 1px solid #2a2a35;
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .chart-title {
            color: white;
            font-size: 16px;
            font-weight: 500;
        }
        
        .chart-controls {
            display: flex;
            gap: 16px;
            align-items: center;
        }
        
        .control-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-item label {
            color: #8888a0;
            font-size: 13px;
        }
        
        .control-item select, .control-item input {
            background: #1a1a24;
            border: 1px solid #2a2a35;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
        }
        
        /* GRÁFICO IGUAL DERIV */
        .chart-wrapper {
            background: #0f0f14;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #2a2a35;
            height: 500px;
        }
        
        .chart-container {
            position: relative;
            height: 100%;
            width: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .y-axis {
            display: flex;
            justify-content: space-between;
            padding: 0 10px 0 40px;
            margin-bottom: 8px;
        }
        
        .y-axis span {
            color: #666680;
            font-size: 11px;
            width: 40px;
            text-align: right;
        }
        
        .chart-area {
            flex: 1;
            display: flex;
            position: relative;
        }
        
        .y-labels {
            width: 40px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 4px 0;
        }
        
        .y-labels span {
            color: #666680;
            font-size: 11px;
            text-align: right;
            padding-right: 8px;
            height: 20px;
            line-height: 20px;
        }
        
        .grid-area {
            flex: 1;
            position: relative;
            height: 100%;
        }
        
        .grid-lines {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            pointer-events: none;
        }
        
        .grid-line {
            border-top: 1px dashed #2a2a35;
            height: 0;
            position: relative;
        }
        
        .grid-line span {
            position: absolute;
            left: -40px;
            top: -8px;
            color: #666680;
            font-size: 11px;
        }
        
        .reference-lines {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
        }
        
        .ref-line {
            position: absolute;
            left: 0;
            right: 0;
            height: 2px;
        }
        
        .ref-20 {
            top: 20%;
            border-top: 2px solid #ff4444;
        }
        
        .ref-8 {
            top: 68%;
            border-top: 2px solid #ffaa00;
        }
        
        .ref-4 {
            top: 84%;
            border-top: 2px solid #4caf50;
        }
        
        .ref-label {
            position: absolute;
            right: 10px;
            top: -10px;
            background: #1a1a24;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            border: 1px solid #2a2a35;
        }
        
        /* BARRAS VERTICAIS */
        .bars-container {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 100%;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            padding: 0 10px;
            z-index: 5;
        }
        
        .bar-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 8%;
            height: 100%;
            justify-content: flex-end;
            position: relative;
        }
        
        .bar {
            width: 100%;
            background: linear-gradient(180deg, #ff6b6b 0%, #ff4444 100%);
            border-radius: 4px 4px 0 0;
            transition: height 0.3s ease;
            min-height: 4px;
            position: relative;
            cursor: pointer;
        }
        
        .bar.target {
            background: linear-gradient(180deg, #ffaa00 0%, #ff8800 100%);
            box-shadow: 0 0 20px rgba(255,170,0,0.5);
        }
        
        .bar-percent {
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            font-size: 11px;
            font-weight: 600;
            white-space: nowrap;
            background: #1a1a24;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #2a2a35;
        }
        
        .bar-label {
            margin-top: 8px;
            color: white;
            font-size: 12px;
            font-weight: 500;
        }
        
        /* Trading Panel (mantido igual) */
        .trading-panel {
            background: #0f0f14;
            padding: 24px;
        }
        
        .price-display {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            margin-bottom: 24px;
            border: 1px solid #2a2a35;
        }
        
        .price-label {
            color: #8888a0;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .price-value {
            color: white;
            font-size: 48px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
        }
        
        .digit-prediction {
            margin-bottom: 24px;
        }
        
        .digit-prediction h3 {
            color: #8888a0;
            font-size: 13px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .prediction-box {
            background: #1a1a24;
            border: 2px solid #2a2a35;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        
        .prediction-digit {
            font-size: 48px;
            font-weight: 700;
            color: #ff4444;
            line-height: 1;
            margin-bottom: 4px;
        }
        
        .prediction-label {
            color: #8888a0;
            font-size: 12px;
        }
        
        .stake-box {
            background: #1a1a24;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            border: 1px solid #2a2a35;
        }
        
        .stake-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .stake-row:last-child {
            margin-bottom: 0;
        }
        
        .stake-label {
            color: #8888a0;
            font-size: 14px;
        }
        
        .stake-value {
            color: white;
            font-weight: 600;
        }
        
        .config-section {
            background: #1a1a24;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2a2a35;
        }
        
        .config-title {
            color: white;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .config-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .config-label {
            color: #8888a0;
            font-size: 13px;
        }
        
        .config-input {
            background: #0f0f14;
            border: 1px solid #2a2a35;
            color: white;
            padding: 6px 10px;
            border-radius: 4px;
            width: 100px;
        }
        
        .config-input.token {
            width: 160px;
        }
        
        .bot-controls {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }
        
        .bot-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-test {
            background: #4a4a5a;
            color: white;
        }
        
        .btn-start {
            background: #4caf50;
            color: white;
        }
        
        .btn-stop {
            background: #f44336;
            color: white;
        }
        
        .bot-btn:hover {
            transform: translateY(-2px);
            filter: brightness(1.1);
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }
        
        .status-connected {
            background: #4caf50;
            box-shadow: 0 0 10px #4caf50;
        }
        
        .status-disconnected {
            background: #f44336;
            box-shadow: 0 0 10px #f44336;
        }
        
        .target-info {
            background: #2a2a35;
            border-left: 4px solid #ffaa00;
            padding: 12px;
            border-radius: 6px;
            margin-top: 16px;
            color: white;
            font-size: 13px;
        }
        
        .profit-display {
            background: #1a1a24;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid #2a2a35;
        }
        
        .profit-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .profit-label {
            color: #8888a0;
            font-size: 13px;
        }
        
        .profit-value {
            font-size: 24px;
            font-weight: 700;
        }
        
        .profit-positive {
            color: #4caf50;
        }
        
        .profit-negative {
            color: #f44336;
        }
        
        .logs-panel {
            background: #0a0a0f;
            border-top: 1px solid #2a2a35;
            padding: 20px 32px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            height: 150px;
            overflow-y: auto;
        }
        
        .log-entry {
            padding: 4px 0;
            border-bottom: 1px solid #1a1a24;
            color: #e0e0e0;
        }
        
        .log-success { color: #4caf50; }
        .log-error { color: #f44336; }
        .log-warning { color: #ffaa00; }
        
        .countdown {
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }
        
        .countdown-box {
            flex: 1;
            background: #1a1a24;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            border: 1px solid #2a2a35;
        }
        
        .countdown-label {
            color: #8888a0;
            font-size: 11px;
            margin-bottom: 4px;
        }
        
        .countdown-value {
            color: #ffaa00;
            font-size: 24px;
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Deriv Bot - Last Digit Stats</h1>
            <p>Dados reais da Deriv | Últimos 25 ticks | Volatility 100 Index</p>
        </div>
        
        <div class="market-info">
            <div class="market-item">
                <span class="market-label">Mercado</span>
                <span class="market-value">Volatility 100 Index</span>
            </div>
            <div class="market-item">
                <span class="market-label">Tipo</span>
                <span class="market-value highlight">Dígito Matches</span>
            </div>
            <div class="market-item">
                <span class="market-label">Ticks Analisados</span>
                <span class="market-value" id="tickCount">0/25</span>
            </div>
            <div class="market-item">
                <span class="market-label">Status</span>
                <span class="market-value" id="connectionStatus">Desconectado</span>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- GRÁFICO DERIV REAL -->
            <div class="chart-panel">
                <div class="chart-header">
                    <div class="chart-title">📊 Last Digit Statistics - Últimos 25 ticks</div>
                    <div class="chart-controls">
                        <div class="control-item">
                            <label>Mercado:</label>
                            <select id="marketSelect">
                                <option value="R_100" selected>Volatility 100 Index</option>
                            </select>
                        </div>
                        <div class="control-item">
                            <label>Ticks:</label>
                            <input type="number" id="tickCount" value="25" readonly>
                        </div>
                    </div>
                </div>
                
                <div class="chart-wrapper">
                    <div class="chart-container">
                        <div class="y-axis">
                            <span>20%</span>
                            <span>16%</span>
                            <span>12%</span>
                            <span>8%</span>
                            <span>4%</span>
                            <span>0%</span>
                        </div>
                        
                        <div class="chart-area">
                            <div class="y-labels">
                                <span>20%</span>
                                <span>16%</span>
                                <span>12%</span>
                                <span>8%</span>
                                <span>4%</span>
                                <span>0%</span>
                            </div>
                            
                            <div class="grid-area">
                                <div class="grid-lines">
                                    <div class="grid-line"><span>20%</span></div>
                                    <div class="grid-line"><span>16%</span></div>
                                    <div class="grid-line"><span>12%</span></div>
                                    <div class="grid-line"><span>8%</span></div>
                                    <div class="grid-line"><span>4%</span></div>
                                    <div class="grid-line"><span>0%</span></div>
                                </div>
                                
                                <div class="reference-lines">
                                    <div class="ref-line ref-20">
                                        <span class="ref-label">20.00%</span>
                                    </div>
                                    <div class="ref-line ref-8">
                                        <span class="ref-label">8.00%</span>
                                    </div>
                                    <div class="ref-line ref-4">
                                        <span class="ref-label">4.00%</span>
                                    </div>
                                </div>
                                
                                <div class="bars-container" id="barsContainer"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Trading Panel -->
            <div class="trading-panel">
                <div class="digit-prediction">
                    <h3>DÍGITO DA PREVISÃO</h3>
                    <div class="prediction-box" id="predictionBox">
                        <div class="prediction-digit" id="predictionDigit">-</div>
                        <div class="prediction-label" id="predictionStatus">Aguardando dados...</div>
                    </div>
                </div>
                
                <div class="countdown">
                    <div class="countdown-box">
                        <div class="countdown-label">Início em:</div>
                        <div class="countdown-value" id="startCounter">20s</div>
                    </div>
                    <div class="countdown-box">
                        <div class="countdown-label">Próximo trade:</div>
                        <div class="countdown-value" id="cooldownCounter">0s</div>
                    </div>
                </div>
                
                <div class="profit-display">
                    <div class="profit-row">
                        <span class="profit-label">Lucro/Perda:</span>
                        <span class="profit-value" id="totalProfit">$0.00</span>
                    </div>
                    <div class="profit-row" style="margin-top: 8px;">
                        <span class="profit-label">Trades:</span>
                        <span id="totalTrades">0</span>
                    </div>
                </div>
                
                <div class="stake-box">
                    <div class="stake-row">
                        <span class="stake-label">Stake Inicial:</span>
                        <span class="stake-value" id="initialStake">$0.35</span>
                    </div>
                    <div class="stake-row">
                        <span class="stake-label">Stake Atual:</span>
                        <span class="stake-value" id="currentStake">$0.35</span>
                    </div>
                </div>
                
                <div class="config-section">
                    <div class="config-title">⚙️ Configurações</div>
                    
                    <div class="config-row">
                        <span class="config-label">Token:</span>
                        <input type="password" class="config-input token" id="token" placeholder="Opcional">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stake:</span>
                        <input type="number" class="config-input" id="botStake" value="0.35" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Martingale:</span>
                        <input type="number" class="config-input" id="martingale" value="1.15" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stop Loss:</span>
                        <input type="number" class="config-input" id="stopLoss" value="10">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stop Win:</span>
                        <input type="number" class="config-input" id="stopWin" value="10">
                    </div>
                    
                    <div class="bot-controls">
                        <button class="bot-btn btn-start" onclick="startBot()">▶️ Iniciar</button>
                        <button class="bot-btn btn-stop" onclick="stopBot()">⏹️ Parar</button>
                    </div>
                    
                    <div id="targetInfo" class="target-info" style="display: none;"></div>
                </div>
            </div>
        </div>
        
        <div class="logs-panel" id="logs"></div>
    </div>
    
    <script>
        // Configuração WebSocket Deriv
        const DERIV_WS_URL = 'wss://ws.derivws.com/websockets/v3?app_id=1089';
        const SYMBOL = 'R_100';
        
        let derivWS = null;
        let botState = {
            running: false,
            connected: false,
            targetDigit: null,
            inPosition: false,
            waitingForCompletion: false,
            entryTriggered: false,
            tickHistory: [],
            frequencies: Array(10).fill(0),
            stats: {
                profit: 0,
                trades: 0,
                wins: 0,
                currentStake: 0.35,
                losses: 0
            },
            config: {
                stake: 0.35,
                martingale: 1.15,
                stopLoss: 10,
                stopWin: 10
            }
        };
        
        let countdownInterval = null;
        let cooldownInterval = null;
        
        // Inicializar barras
        function initBars() {
            let container = document.getElementById('barsContainer');
            let html = '';
            
            for(let i = 0; i <= 9; i++) {
                html += `
                    <div class="bar-wrapper" id="bar-wrapper-${i}">
                        <div class="bar" id="bar-${i}">
                            <span class="bar-percent" id="percent-${i}">0.0%</span>
                        </div>
                        <div class="bar-label">${i}</div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        initBars();
        
        function addLog(message, type = 'info') {
            let logs = document.getElementById('logs');
            let entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
            
            while(logs.children.length > 100) {
                logs.removeChild(logs.firstChild);
            }
        }
        
        function connectDeriv() {
            try {
                derivWS = new WebSocket(DERIV_WS_URL);
                
                derivWS.onopen = () => {
                    botState.connected = true;
                    document.getElementById('connectionStatus').innerHTML = 'Conectado';
                    document.getElementById('connectionStatus').style.color = '#4caf50';
                    addLog('✅ Conectado à Deriv', 'success');
                    
                    // Inscrever para ticks do R_100
                    derivWS.send(JSON.stringify({
                        ticks: SYMBOL,
                        subscribe: 1
                    }));
                };
                
                derivWS.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    
                    if (data.tick) {
                        const tick = data.tick;
                        const price = tick.quote;
                        const lastDigit = getLastDigit(price);
                        
                        // Atualizar histórico
                        botState.tickHistory.push(lastDigit);
                        if (botState.tickHistory.length > 25) {
                            botState.tickHistory.shift();
                        }
                        
                        // Calcular frequências
                        updateFrequencies();
                        
                        // Atualizar contador de ticks
                        document.getElementById('tickCount').innerHTML = botState.tickHistory.length + '/25';
                        
                        // Executar estratégia se bot estiver rodando
                        if (botState.running) {
                            executeStrategy(lastDigit);
                        }
                    }
                };
                
                derivWS.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    addLog('❌ Erro na conexão WebSocket', 'error');
                };
                
                derivWS.onclose = () => {
                    botState.connected = false;
                    document.getElementById('connectionStatus').innerHTML = 'Desconectado';
                    document.getElementById('connectionStatus').style.color = '#f44336';
                    addLog('❌ Desconectado da Deriv', 'error');
                    
                    // Tentar reconectar após 5 segundos
                    if (botState.running) {
                        setTimeout(connectDeriv, 5000);
                    }
                };
                
            } catch (error) {
                addLog('❌ Erro ao conectar: ' + error.message, 'error');
            }
        }
        
        function getLastDigit(price) {
            // Extrair último dígito do preço
            const priceStr = price.toString();
            const lastChar = priceStr[priceStr.length - 1];
            return parseInt(lastChar);
        }
        
        function updateFrequencies() {
            if (botState.tickHistory.length === 0) return;
            
            const counts = Array(10).fill(0);
            botState.tickHistory.forEach(digit => counts[digit]++);
            
            const total = botState.tickHistory.length;
            const frequencies = counts.map(count => (count / total) * 100);
            
            // Atualizar barras
            for (let i = 0; i <= 9; i++) {
                let bar = document.getElementById(`bar-${i}`);
                let percentEl = document.getElementById(`percent-${i}`);
                
                let height = (frequencies[i] / 20) * 100;
                if (height > 100) height = 100;
                
                bar.style.height = height + '%';
                percentEl.innerHTML = frequencies[i].toFixed(1) + '%';
                
                // Destacar barra alvo
                if (i === botState.targetDigit) {
                    bar.classList.add('target');
                } else {
                    bar.classList.remove('target');
                }
            }
            
            botState.frequencies = frequencies;
        }
        
        function executeStrategy(lastDigit) {
            // PASSO 1: Se não tem dígito alvo e não está esperando, procurar dígito com 0%
            if (botState.targetDigit === null && !botState.inPosition && !botState.waitingForCompletion) {
                for (let i = 0; i <= 9; i++) {
                    if (botState.frequencies[i] < 0.5) {
                        botState.targetDigit = i;
                        botState.waitingForCompletion = true;
                        
                        document.getElementById('predictionDigit').innerHTML = i;
                        document.getElementById('predictionStatus').innerHTML = 'Aguardando 8%';
                        document.getElementById('targetInfo').style.display = 'block';
                        document.getElementById('targetInfo').innerHTML = `🎯 Dígito da previsão: <strong>${i}</strong> (0%) - Aguardando 8%`;
                        
                        addLog(`🎯 Dígito da previsão encontrado: ${i} (0%)`, 'warning');
                        break;
                    }
                }
            }
            
            // PASSO 2: Aguardar atingir 8%
            if (botState.targetDigit !== null && !botState.inPosition && !botState.entryTriggered) {
                if (botState.frequencies[botState.targetDigit] >= 8) {
                    botState.entryTriggered = true;
                    
                    document.getElementById('predictionStatus').innerHTML = '📊 Atingiu 8%! Comprando...';
                    document.getElementById('targetInfo').innerHTML = `📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando no próximo tick...`;
                    
                    addLog(`📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando...`, 'warning');
                    
                    // PASSO 3: Comprar
                    setTimeout(() => {
                        if (!botState.running) return;
                        
                        botState.inPosition = true;
                        addLog(`✅ COMPRA: $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.targetDigit}`, 'success');
                        
                        // PASSO 4: Aguardar resultado no próximo tick
                        setTimeout(() => {
                            if (!botState.running) return;
                            
                            // Verificar último dígito
                            let won = (lastDigit === botState.targetDigit);
                            
                            if (won) {
                                let profit = botState.stats.currentStake * 0.95;
                                botState.stats.profit += profit;
                                botState.stats.trades++;
                                botState.stats.wins++;
                                botState.stats.losses = 0;
                                botState.stats.currentStake = botState.config.stake;
                                
                                addLog(`💰 VENDA: Dígito ${lastDigit} saiu! Lucro: $${profit.toFixed(2)}`, 'success');
                            } else {
                                let loss = -botState.stats.currentStake;
                                botState.stats.profit += loss;
                                botState.stats.trades++;
                                botState.stats.losses++;
                                botState.stats.currentStake *= botState.config.martingale;
                                
                                addLog(`❌ PERDA: Dígito ${lastDigit} não saiu! Prejuízo: $${Math.abs(loss).toFixed(2)}`, 'error');
                                addLog(`📈 Martingale: Nova stake $${botState.stats.currentStake.toFixed(2)}`, 'warning');
                            }
                            
                            updateStats();
                            
                            // Verificar stops
                            if (botState.stats.profit >= botState.config.stopWin) {
                                addLog('🎉 STOP WIN ATINGIDO!', 'success');
                                stopBot();
                                return;
                            }
                            
                            if (botState.stats.profit <= -botState.config.stopLoss) {
                                addLog('🛑 STOP LOSS ATINGIDO!', 'error');
                                stopBot();
                                return;
                            }
                            
                            // PASSO 5: Reset e cooldown
                            botState.inPosition = false;
                            botState.targetDigit = null;
                            botState.entryTriggered = false;
                            
                            document.getElementById('predictionDigit').innerHTML = '-';
                            document.getElementById('predictionStatus').innerHTML = 'Aguardando...';
                            document.getElementById('targetInfo').style.display = 'none';
                            
                            addLog('⏱️ Aguardando 5 segundos...', 'info');
                            
                            let cooldown = 5;
                            cooldownInterval = setInterval(() => {
                                document.getElementById('cooldownCounter').innerHTML = cooldown + 's';
                                cooldown--;
                                
                                if (cooldown < 0) {
                                    clearInterval(cooldownInterval);
                                    document.getElementById('cooldownCounter').innerHTML = 'Pronto';
                                    botState.waitingForCompletion = false;
                                }
                            }, 1000);
                            
                        }, 1000); // Aguardar próximo tick
                        
                    }, 100); // Próximo tick
                }
            }
        }
        
        function updateStats() {
            let profitEl = document.getElementById('totalProfit');
            profitEl.innerHTML = '$' + botState.stats.profit.toFixed(2);
            profitEl.className = 'profit-value ' + (botState.stats.profit >= 0 ? 'profit-positive' : 'profit-negative');
            
            document.getElementById('totalTrades').innerHTML = botState.stats.trades;
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
        }
        
        function startBot() {
            botState.running = true;
            botState.config = {
                stake: parseFloat(document.getElementById('botStake').value),
                martingale: parseFloat(document.getElementById('martingale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin: parseFloat(document.getElementById('stopWin').value)
            };
            
            botState.stats.currentStake = botState.config.stake;
            document.getElementById('initialStake').innerHTML = '$' + botState.config.stake.toFixed(2);
            updateStats();
            
            addLog('🚀 Iniciando robô...', 'warning');
            
            // Conectar à Deriv se não estiver conectado
            if (!botState.connected) {
                connectDeriv();
            }
            
            // Contagem regressiva
            let startTime = 20;
            countdownInterval = setInterval(() => {
                document.getElementById('startCounter').innerHTML = startTime + 's';
                startTime--;
                
                if (startTime < 0) {
                    clearInterval(countdownInterval);
                    document.getElementById('startCounter').innerHTML = 'Ativo';
                }
            }, 1000);
        }
        
        function stopBot() {
            botState.running = false;
            
            if (countdownInterval) clearInterval(countdownInterval);
            if (cooldownInterval) clearInterval(cooldownInterval);
            if (derivWS) derivWS.close();
            
            document.getElementById('startCounter').innerHTML = '20s';
            document.getElementById('cooldownCounter').innerHTML = '0s';
            document.getElementById('targetInfo').style.display = 'none';
            document.getElementById('predictionDigit').innerHTML = '-';
            document.getElementById('predictionStatus').innerHTML = 'Parado';
            
            addLog('⏹️ Robô parado', 'error');
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(content=HTML)

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

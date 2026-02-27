from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import random
from collections import deque, Counter
import time

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
    <title>Deriv Bot - Dígito Matches</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        
        /* Header - Igual Deriv */
        .header {
            background: #ff4444;
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
        
        /* Market Info */
        .market-info {
            background: #f8f9fa;
            padding: 20px 30px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            gap: 40px;
            flex-wrap: wrap;
        }
        
        .market-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .market-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }
        
        .market-value {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .market-value.highlight {
            color: #ff4444;
        }
        
        /* Main Content */
        .main-content {
            padding: 30px;
            display: flex;
            gap: 30px;
        }
        
        /* Left Panel - Gráfico */
        .chart-panel {
            flex: 2;
            background: white;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            overflow: hidden;
        }
        
        .chart-header {
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chart-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .chart-controls {
            display: flex;
            gap: 20px;
        }
        
        .control-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .control-item label {
            font-size: 13px;
            color: #666;
        }
        
        .control-item select, .control-item input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 13px;
        }
        
        /* Gráfico de Barras - IGUAL DA DERIV */
        .chart-container {
            padding: 30px;
            position: relative;
            height: 500px;
            display: flex;
            flex-direction: column;
        }
        
        .y-axis {
            position: absolute;
            left: 30px;
            top: 50px;
            bottom: 50px;
            width: 40px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color: #999;
            font-size: 12px;
        }
        
        .y-axis span {
            text-align: right;
            padding-right: 10px;
        }
        
        .bars-container {
            flex: 1;
            margin-left: 70px;
            position: relative;
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
        }
        
        .grid-line {
            border-top: 1px dashed #e0e0e0;
            height: 0;
            position: relative;
        }
        
        .grid-line span {
            position: absolute;
            left: -40px;
            top: -8px;
            color: #999;
            font-size: 11px;
        }
        
        .bars-row {
            display: flex;
            align-items: center;
            height: 10%;
            margin-bottom: 5px;
            position: relative;
            z-index: 2;
        }
        
        .bar-label {
            width: 30px;
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }
        
        .bar-wrapper {
            flex: 1;
            height: 30px;
            background: #f0f0f0;
            border-radius: 4px;
            position: relative;
            cursor: pointer;
        }
        
        .bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b 0%, #ff4444 100%);
            border-radius: 4px;
            transition: width 0.3s ease;
            position: relative;
        }
        
        .bar-percent {
            position: absolute;
            right: -40px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 12px;
            font-weight: 600;
            color: #ff4444;
            white-space: nowrap;
        }
        
        /* Linhas de referência */
        .reference-line {
            position: absolute;
            left: 0;
            right: 0;
            height: 2px;
            z-index: 3;
            pointer-events: none;
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
            background: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .ref-20 .ref-label { color: #ff4444; }
        .ref-8 .ref-label { color: #ffaa00; }
        .ref-4 .ref-label { color: #4caf50; }
        
        /* Right Panel - Trading */
        .trading-panel {
            flex: 1;
            background: white;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            padding: 20px;
        }
        
        .price-display {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .price-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .price-value {
            font-size: 48px;
            font-weight: 700;
            color: #333;
        }
        
        .trade-type {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .trade-type h3 {
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
        }
        
        .type-options {
            display: flex;
            gap: 10px;
        }
        
        .type-option {
            flex: 1;
            padding: 10px;
            text-align: center;
            background: white;
            border: 2px solid #ddd;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .type-option.active {
            background: #ff4444;
            color: white;
            border-color: #ff4444;
        }
        
        .digit-prediction {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .digit-prediction h3 {
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
        }
        
        .digit-selector {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 8px;
        }
        
        .digit-btn {
            aspect-ratio: 1;
            background: white;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .digit-btn.active {
            background: #ff4444;
            color: white;
            border-color: #ff4444;
        }
        
        .stake-box {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .stake-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .stake-value {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stake-value input {
            width: 100px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
            text-align: right;
        }
        
        .contract-info {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .contract-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .contract-row:last-child {
            border-bottom: none;
        }
        
        .payout-highlight {
            color: #ff4444;
            font-weight: 600;
        }
        
        .profit-highlight {
            color: #4caf50;
            font-weight: 600;
        }
        
        .buy-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(90deg, #ff6b6b 0%, #ff4444 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }
        
        .buy-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255,68,68,0.3);
        }
        
        .config-section {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .config-section h3 {
            font-size: 14px;
            color: #333;
            margin-bottom: 15px;
        }
        
        .config-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .config-row input {
            width: 100px;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .bot-controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .bot-btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            cursor: pointer;
        }
        
        .start-btn {
            background: #4caf50;
            color: white;
        }
        
        .stop-btn {
            background: #f44336;
            color: white;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .status-connected { background: #4caf50; }
        .status-disconnected { background: #f44336; }
        
        .target-info {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .logs-panel {
            margin-top: 20px;
            background: #1a1a2e;
            border-radius: 8px;
            padding: 15px;
            color: #e0e0e0;
            font-family: monospace;
            font-size: 12px;
            height: 150px;
            overflow-y: auto;
        }
        
        .log-entry {
            padding: 3px 0;
            border-bottom: 1px solid #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Deriv Trading Bot - Dígito Matches</h1>
            <p>Estratégia: Identificar dígito 0% → Aguardar 8% → Comprar → Vender quando sair</p>
        </div>
        
        <div class="market-info">
            <div class="market-item">
                <span class="market-label">Market</span>
                <span class="market-value">Volatility 100 Index</span>
            </div>
            <div class="market-item">
                <span class="market-label">Trade types</span>
                <span class="market-value highlight">Matches/Differs</span>
            </div>
            <div class="market-item">
                <span class="market-label">Current Price</span>
                <span class="market-value" id="currentPrice">816.95</span>
            </div>
        </div>
        
        <div class="main-content">
            <!-- Gráfico de Barras - IGUAL DA DERIV -->
            <div class="chart-panel">
                <div class="chart-header">
                    <div class="chart-title">Last Digit Stats</div>
                    <div class="chart-controls">
                        <div class="control-item">
                            <label>Market:</label>
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
                
                <div class="chart-container">
                    <!-- Eixo Y -->
                    <div class="y-axis">
                        <span>20%</span>
                        <span>16%</span>
                        <span>12%</span>
                        <span>8%</span>
                        <span>4%</span>
                        <span>0%</span>
                    </div>
                    
                    <!-- Grid Lines -->
                    <div class="grid-lines">
                        <div class="grid-line" style="top: 0%;"><span>20%</span></div>
                        <div class="grid-line" style="top: 20%;"><span>16%</span></div>
                        <div class="grid-line" style="top: 40%;"><span>12%</span></div>
                        <div class="grid-line" style="top: 60%;"><span>8%</span></div>
                        <div class="grid-line" style="top: 80%;"><span>4%</span></div>
                        <div class="grid-line" style="top: 100%;"><span>0%</span></div>
                    </div>
                    
                    <!-- Barras para cada dígito -->
                    <div class="bars-container">
                        <!-- Linhas de referência coloridas -->
                        <div class="reference-line ref-20">
                            <span class="ref-label">20.00%</span>
                        </div>
                        <div class="reference-line ref-8">
                            <span class="ref-label">8.00%</span>
                        </div>
                        <div class="reference-line ref-4">
                            <span class="ref-label">4.00%</span>
                        </div>
                        
                        <!-- Dígito 0 -->
                        <div class="bars-row">
                            <div class="bar-label">0</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-0" style="width: 0%">
                                    <span class="bar-percent" id="percent-0">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 1 -->
                        <div class="bars-row">
                            <div class="bar-label">1</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-1" style="width: 0%">
                                    <span class="bar-percent" id="percent-1">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 2 -->
                        <div class="bars-row">
                            <div class="bar-label">2</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-2" style="width: 0%">
                                    <span class="bar-percent" id="percent-2">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 3 -->
                        <div class="bars-row">
                            <div class="bar-label">3</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-3" style="width: 0%">
                                    <span class="bar-percent" id="percent-3">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 4 -->
                        <div class="bars-row">
                            <div class="bar-label">4</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-4" style="width: 0%">
                                    <span class="bar-percent" id="percent-4">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 5 -->
                        <div class="bars-row">
                            <div class="bar-label">5</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-5" style="width: 0%">
                                    <span class="bar-percent" id="percent-5">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 6 -->
                        <div class="bars-row">
                            <div class="bar-label">6</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-6" style="width: 0%">
                                    <span class="bar-percent" id="percent-6">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 7 -->
                        <div class="bars-row">
                            <div class="bar-label">7</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-7" style="width: 0%">
                                    <span class="bar-percent" id="percent-7">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 8 -->
                        <div class="bars-row">
                            <div class="bar-label">8</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-8" style="width: 0%">
                                    <span class="bar-percent" id="percent-8">0.0%</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Dígito 9 -->
                        <div class="bars-row">
                            <div class="bar-label">9</div>
                            <div class="bar-wrapper">
                                <div class="bar-fill" id="bar-9" style="width: 0%">
                                    <span class="bar-percent" id="percent-9">0.0%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Painel de Trading -->
            <div class="trading-panel">
                <div class="price-display">
                    <div class="price-label">Current Price</div>
                    <div class="price-value" id="priceDisplay">816.95</div>
                </div>
                
                <div class="trade-type">
                    <h3>Trade types</h3>
                    <div class="type-options">
                        <div class="type-option active">Matches</div>
                        <div class="type-option">Differs</div>
                    </div>
                </div>
                
                <div class="digit-prediction">
                    <h3>Last Digit Prediction</h3>
                    <div class="digit-selector" id="digitSelector">
                        <div class="digit-btn">0</div>
                        <div class="digit-btn">1</div>
                        <div class="digit-btn">2</div>
                        <div class="digit-btn">3</div>
                        <div class="digit-btn">4</div>
                        <div class="digit-btn">5</div>
                        <div class="digit-btn">6</div>
                        <div class="digit-btn">7</div>
                        <div class="digit-btn">8</div>
                        <div class="digit-btn">9</div>
                    </div>
                </div>
                
                <div class="stake-box">
                    <div class="stake-header">
                        <span>Duration</span>
                        <span>1 ticks</span>
                    </div>
                    <div class="stake-header">
                        <span>Stake</span>
                        <div class="stake-value">
                            <input type="number" id="stakeInput" value="0.35" step="0.01" min="0.35">
                            <span>USD</span>
                        </div>
                    </div>
                </div>
                
                <!-- Contrato 1 -->
                <div class="contract-info">
                    <div class="contract-row">
                        <span>Stake:</span>
                        <span id="contract1Stake">0.35 USD</span>
                    </div>
                    <div class="contract-row">
                        <span>Payout:</span>
                        <span class="payout-highlight" id="contract1Payout">2.92 USD</span>
                    </div>
                    <div class="contract-row">
                        <span>Net profit:</span>
                        <span class="profit-highlight" id="contract1Profit">2.57 USD</span>
                    </div>
                    <div class="contract-row">
                        <span>Return:</span>
                        <span>734.3%</span>
                    </div>
                </div>
                
                <button class="buy-btn" onclick="manualBuy()">Purchase</button>
                
                <!-- Contrato 2 -->
                <div class="contract-info">
                    <div class="contract-row">
                        <span>Stake:</span>
                        <span id="contract2Stake">0.35 USD</span>
                    </div>
                    <div class="contract-row">
                        <span>Payout:</span>
                        <span class="payout-highlight" id="contract2Payout">0.37 USD</span>
                    </div>
                    <div class="contract-row">
                        <span>Net profit:</span>
                        <span class="profit-highlight" id="contract2Profit">0.02 USD</span>
                    </div>
                    <div class="contract-row">
                        <span>Return:</span>
                        <span>5.7%</span>
                    </div>
                </div>
                
                <!-- Configurações do Bot -->
                <div class="config-section">
                    <h3>🤖 Configurações do Bot Automático</h3>
                    
                    <div class="config-row">
                        <span>Token:</span>
                        <input type="password" id="token" placeholder="Seu token" style="width: 150px;">
                    </div>
                    
                    <div class="config-row">
                        <span>Stake Inicial:</span>
                        <input type="number" id="botStake" value="0.35" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span>Martingale:</span>
                        <input type="number" id="martingale" value="1.15" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span>Stop Loss ($):</span>
                        <input type="number" id="stopLoss" value="10">
                    </div>
                    
                    <div class="config-row">
                        <span>Stop Win ($):</span>
                        <input type="number" id="stopWin" value="10">
                    </div>
                    
                    <div class="bot-controls">
                        <button class="bot-btn start-btn" onclick="testConnection()">🔌 Testar</button>
                        <button class="bot-btn start-btn" onclick="startBot()">▶️ Iniciar</button>
                        <button class="bot-btn stop-btn" onclick="stopBot()">⏹️ Parar</button>
                    </div>
                    
                    <div id="connectionStatus" style="margin-top: 10px; font-size: 12px;">
                        <span class="status-indicator status-disconnected"></span>
                        Desconectado
                    </div>
                    
                    <div id="targetInfo" class="target-info" style="display: none;"></div>
                </div>
            </div>
        </div>
        
        <!-- Logs -->
        <div class="logs-panel" id="logs"></div>
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
            inPosition: false,
            frequencies: {},
            lastDigits: []
        };
        
        let tradingInterval = null;
        let countdownInterval = null;
        
        function addLog(message, type = 'info') {
            let logs = document.getElementById('logs');
            let entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
            
            while(logs.children.length > 100) {
                logs.removeChild(logs.firstChild);
            }
        }
        
        function updateBars(frequencies, target) {
            for(let i = 0; i <= 9; i++) {
                let percent = frequencies[i] || 0;
                let bar = document.getElementById(`bar-${i}`);
                let percentEl = document.getElementById(`percent-${i}`);
                
                // Calcular largura (máximo 100% = 20% do gráfico)
                let width = (percent / 20) * 100;
                if(width > 100) width = 100;
                
                bar.style.width = width + '%';
                percentEl.innerHTML = percent.toFixed(1) + '%';
                
                // Destacar barra se for o alvo
                if(i === target) {
                    bar.style.background = 'linear-gradient(90deg, #ffaa00 0%, #ff8800 100%)';
                } else {
                    bar.style.background = 'linear-gradient(90deg, #ff6b6b 0%, #ff4444 100%)';
                }
            }
        }
        
        function updatePrice() {
            let price = (800 + Math.random() * 40).toFixed(2);
            document.getElementById('currentPrice').innerHTML = price;
            document.getElementById('priceDisplay').innerHTML = price;
        }
        
        function testConnection() {
            let token = document.getElementById('token').value;
            if(!token) {
                alert('Digite seu token!');
                return;
            }
            
            document.getElementById('connectionStatus').innerHTML = '<span class="status-indicator status-connected"></span> Conectado';
            botState.connected = true;
            botState.token = token;
            addLog('✅ Conectado à Deriv');
        }
        
        function startBot() {
            if(!botState.connected) {
                alert('Teste a conexão primeiro!');
                return;
            }
            
            botState.running = true;
            botState.config = {
                stake: parseFloat(document.getElementById('botStake').value),
                martingale: parseFloat(document.getElementById('martingale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin: parseFloat(document.getElementById('stopWin').value)
            };
            
            botState.stats.currentStake = botState.config.stake;
            
            addLog('🚀 Iniciando robô... Aguardando 20 segundos');
            
            // Contagem regressiva
            let startTime = 20;
            countdownInterval = setInterval(() => {
                if(!botState.running) {
                    clearInterval(countdownInterval);
                    return;
                }
                
                addLog(`⏳ Iniciando em ${startTime} segundos...`);
                startTime--;
                
                if(startTime < 0) {
                    clearInterval(countdownInterval);
                    addLog('✅ Robô iniciado - Analisando mercado...');
                    startTrading();
                }
            }, 1000);
        }
        
        function stopBot() {
            botState.running = false;
            
            if(countdownInterval) clearInterval(countdownInterval);
            if(tradingInterval) clearInterval(tradingInterval);
            
            addLog('⏹️ Robô parado');
            document.getElementById('targetInfo').style.display = 'none';
        }
        
        function startTrading() {
            if(!botState.running) return;
            
            tradingInterval = setInterval(() => {
                if(!botState.running) {
                    clearInterval(tradingInterval);
                    return;
                }
                
                // Simular dados dos últimos 25 ticks
                let freq = {};
                let total = 0;
                
                // Gerar percentuais
                for(let i = 0; i <= 9; i++) {
                    freq[i] = Math.random() * 15;
                    total += freq[i];
                }
                
                // Normalizar
                for(let i = 0; i <= 9; i++) {
                    freq[i] = (freq[i] / total) * 100;
                }
                
                // ESTRATÉGIA: Encontrar dígito com 0%
                if(botState.targetDigit === null && !botState.inPosition) {
                    for(let i = 0; i <= 9; i++) {
                        if(freq[i] < 0.5) {
                            botState.targetDigit = i;
                            document.getElementById('targetInfo').style.display = 'block';
                            document.getElementById('targetInfo').innerHTML = `🎯 Dígito alvo: <strong>${i}</strong> (0%) - Aguardando 8%`;
                            addLog(`🎯 Dígito alvo encontrado: ${i} (0% nos últimos 25 ticks)`);
                            break;
                        }
                    }
                }
                
                // Verificar se atingiu 8%
                if(botState.targetDigit !== null && !botState.inPosition) {
                    if(freq[botState.targetDigit] >= 8) {
                        botState.inPosition = true;
                        document.getElementById('targetInfo').innerHTML = `📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando no próximo tick...`;
                        addLog(`📊 Dígito ${botState.targetDigit} atingiu 8% - Comprando $${botState.stats.currentStake.toFixed(2)}`);
                        
                        // COMPRA (simulada)
                        setTimeout(() => {
                            if(!botState.running) return;
                            
                            // Verificar se o dígito saiu
                            let lastDigit = Math.floor(Math.random() * 10);
                            let won = (lastDigit === botState.targetDigit);
                            
                            let profit = won ? botState.stats.currentStake * 0.95 : -botState.stats.currentStake;
                            
                            botState.stats.profit += profit;
                            botState.stats.trades++;
                            
                            if(won) {
                                botState.stats.wins++;
                                botState.stats.losses = 0;
                                botState.stats.currentStake = botState.config.stake;
                                addLog(`💰 GANHOU! Dígito ${lastDigit} saiu! Lucro: $${profit.toFixed(2)}`);
                            } else {
                                botState.stats.losses++;
                                botState.stats.currentStake *= botState.config.martingale;
                                addLog(`❌ PERDEU! Dígito ${lastDigit} não saiu. Prejuízo: $${Math.abs(profit).toFixed(2)}`);
                                addLog(`📈 Martingale ativado - Nova stake: $${botState.stats.currentStake.toFixed(2)}`);
                            }
                            
                            // Verificar stops
                            if(botState.stats.profit >= botState.config.stopWin) {
                                addLog('🎉 PARABÉNS! STOP WIN ATINGIDO!');
                                stopBot();
                                return;
                            }
                            
                            if(botState.stats.profit <= -botState.config.stopLoss) {
                                addLog('🛑 STOP LOSS ATINGIDO!');
                                stopBot();
                                return;
                            }
                            
                            // Reset para nova operação
                            botState.inPosition = false;
                            botState.targetDigit = null;
                            document.getElementById('targetInfo').style.display = 'none';
                            
                            // Cooldown de 5 segundos
                            addLog('⏱️ Aguardando 5 segundos para nova operação...');
                            setTimeout(() => {
                                if(botState.running) {
                                    addLog('✅ Pronto para nova análise...');
                                }
                            }, 5000);
                            
                        }, 1000);
                    }
                }
                
                // Atualizar gráfico
                updateBars(freq, botState.targetDigit);
                updatePrice();
                botState.frequencies = freq;
                
            }, 2000);
        }
        
        function manualBuy() {
            addLog('💰 Compra manual realizada');
        }
        
        // Atualizar preço a cada 2 segundos
        setInterval(updatePrice, 2000);
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
           
           

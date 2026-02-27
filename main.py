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
        
        /* GRÁFICO VERTICAL - IGUAL DERIV */
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
        
        /* Trading Panel */
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
        
        .trade-type {
            margin-bottom: 24px;
        }
        
        .trade-type h3 {
            color: #8888a0;
            font-size: 13px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .type-active {
            background: #ff4444;
            color: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
            font-size: 16px;
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
        
        .stake-input {
            background: #0f0f14;
            border: 1px solid #2a2a35;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            width: 100px;
            text-align: right;
        }
        
        .contract-card {
            background: #1a1a24;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid #2a2a35;
        }
        
        .contract-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2a35;
        }
        
        .contract-row:last-child {
            border-bottom: none;
        }
        
        .contract-label {
            color: #8888a0;
            font-size: 13px;
        }
        
        .contract-value {
            color: white;
            font-weight: 500;
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
            background: linear-gradient(90deg, #ff4444 0%, #ff6b6b 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 24px;
            transition: all 0.3s;
        }
        
        .buy-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,68,68,0.3);
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
            color: #8888a0;
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
            <h1>🤖 Deriv Bot - Estratégia Dígito Matches</h1>
            <p>Análise 25 ticks | Identifica 0% → Aguarda 8% → Compra → Venda no dígito | Martingale 1.15x</p>
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
                <span class="market-label">Duração</span>
                <span class="market-value">1 tick</span>
            </div>
            <div class="market-item">
                <span class="market-label">Preço Atual</span>
                <span class="market-value" id="currentPrice">---</span>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- GRÁFICO VERTICAL -->
            <div class="chart-panel">
                <div class="chart-header">
                    <div class="chart-title">📊 Estatísticas dos Últimos 25 Dígitos</div>
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
                        <!-- Eixo Y superior -->
                        <div class="y-axis">
                            <span>20%</span>
                            <span>16%</span>
                            <span>12%</span>
                            <span>8%</span>
                            <span>4%</span>
                            <span>0%</span>
                        </div>
                        
                        <div class="chart-area">
                            <!-- Labels Y -->
                            <div class="y-labels">
                                <span>20%</span>
                                <span>16%</span>
                                <span>12%</span>
                                <span>8%</span>
                                <span>4%</span>
                                <span>0%</span>
                            </div>
                            
                            <!-- Grid Area -->
                            <div class="grid-area">
                                <!-- Grid Lines -->
                                <div class="grid-lines">
                                    <div class="grid-line"><span>20%</span></div>
                                    <div class="grid-line"><span>16%</span></div>
                                    <div class="grid-line"><span>12%</span></div>
                                    <div class="grid-line"><span>8%</span></div>
                                    <div class="grid-line"><span>4%</span></div>
                                    <div class="grid-line"><span>0%</span></div>
                                </div>
                                
                                <!-- Reference Lines -->
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
                                
                                <!-- BARRAS VERTICAIS -->
                                <div class="bars-container" id="barsContainer"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Trading Panel -->
            <div class="trading-panel">
                <!-- Current Prediction -->
                <div class="digit-prediction">
                    <h3>DÍGITO DA PREVISÃO</h3>
                    <div class="prediction-box" id="predictionBox">
                        <div class="prediction-digit" id="predictionDigit">-</div>
                        <div class="prediction-label" id="predictionStatus">Aguardando análise...</div>
                    </div>
                </div>
                
                <!-- Countdowns -->
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
                
                <!-- Profit/Loss Display -->
                <div class="profit-display">
                    <div class="profit-row">
                        <span class="profit-label">Lucro/Perda:</span>
                        <span class="profit-value" id="totalProfit">$0.00</span>
                    </div>
                    <div class="profit-row" style="margin-top: 8px;">
                        <span class="profit-label">Trades:</span>
                        <span id="totalTrades">0</span>
                    </div>
                    <div class="profit-row">
                        <span class="profit-label">Win Rate:</span>
                        <span id="winRate">0%</span>
                    </div>
                </div>
                
                <!-- Stake Info -->
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
                
                <!-- Contract Info -->
                <div class="contract-card">
                    <div class="contract-row">
                        <span class="contract-label">Stake:</span>
                        <span class="contract-value" id="contractStake">0.35 USD</span>
                    </div>
                    <div class="contract-row">
                        <span class="contract-label">Payout:</span>
                        <span class="contract-value payout-highlight" id="contractPayout">2.92 USD</span>
                    </div>
                    <div class="contract-row">
                        <span class="contract-label">Retorno:</span>
                        <span class="contract-value">734.3%</span>
                    </div>
                </div>
                
                <!-- Config Section -->
                <div class="config-section">
                    <div class="config-title">
                        <span>⚙️ Configurações do Robô</span>
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Token:</span>
                        <input type="password" class="config-input token" id="token" placeholder="Seu token">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stake Inicial:</span>
                        <input type="number" class="config-input" id="botStake" value="0.35" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Martingale:</span>
                        <input type="number" class="config-input" id="martingale" value="1.15" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stop Loss ($):</span>
                        <input type="number" class="config-input" id="stopLoss" value="10">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stop Win ($):</span>
                        <input type="number" class="config-input" id="stopWin" value="10">
                    </div>
                    
                    <div class="bot-controls">
                        <button class="bot-btn btn-test" onclick="testConnection()">🔌 Testar</button>
                        <button class="bot-btn btn-start" onclick="startBot()">▶️ Iniciar</button>
                        <button class="bot-btn btn-stop" onclick="stopBot()">⏹️ Parar</button>
                    </div>
                    
                    <div style="margin-top: 16px; display: flex; align-items: center; gap: 8px;">
                        <span class="status-indicator status-disconnected" id="statusIndicator"></span>
                        <span style="color: #8888a0; font-size: 13px;" id="statusText">Desconectado</span>
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
            lastDigits: [],
            predictionDigit: null,
            predictionStatus: 'Aguardando...',
            entryTriggered: false,
            waitingForCompletion: false  // NOVO: aguarda ciclo completo
        };
        
        let tradingInterval = null;
        let countdownInterval = null;
        let cooldownInterval = null;
        let priceInterval = null;
        
        // Inicializar barras verticais
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
        
        function updateBars(frequencies, target) {
            for(let i = 0; i <= 9; i++) {
                let percent = frequencies[i] || 0;
                let bar = document.getElementById(`bar-${i}`);
                let percentEl = document.getElementById(`percent-${i}`);
                
                // Altura baseada no percentual (máx 100% = 20%)
                let height = (percent / 20) * 100;
                if(height > 100) height = 100;
                
                bar.style.height = height + '%';
                percentEl.innerHTML = percent.toFixed(1) + '%';
                
                // Destacar barra alvo
                if(i === target) {
                    bar.classList.add('target');
                } else {
                    bar.classList.remove('target');
                }
            }
        }
        
        function updatePrice() {
            // Simular preço R_100
            let price = (800 + Math.random() * 100).toFixed(2);
            document.getElementById('currentPrice').innerHTML = price;
        }
        
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
        
        function updateStats() {
            let profitEl = document.getElementById('totalProfit');
            profitEl.innerHTML = '$' + botState.stats.profit.toFixed(2);
            profitEl.className = 'profit-value ' + (botState.stats.profit >= 0 ? 'profit-positive' : 'profit-negative');
            
            document.getElementById('totalTrades').innerHTML = botState.stats.trades;
            
            let winRate = botState.stats.trades > 0 
                ? ((botState.stats.wins / botState.stats.trades) * 100).toFixed(1)
                : 0;
            document.getElementById('winRate').innerHTML = winRate + '%';
            
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
            document.getElementById('contractStake').innerHTML = botState.stats.currentStake.toFixed(2) + ' USD';
            
            // Calcular payout
            let payout = botState.stats.currentStake * 8.34; // Aproximadamente 734% de retorno
            document.getElementById('contractPayout').innerHTML = payout.toFixed(2) + ' USD';
        }
        
        function testConnection() {
            let token = document.getElementById('token').value;
            if(!token) {
                alert('Digite seu token!');
                return;
            }
            
            document.getElementById('statusIndicator').className = 'status-indicator status-connected';
            document.getElementById('statusText').innerHTML = 'Conectado';
            botState.connected = true;
            botState.token = token;
            addLog('✅ Conectado à Deriv', 'success');
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
            document.getElementById('initialStake').innerHTML = '$' + botState.config.stake.toFixed(2);
            updateStats();
            
            addLog('🚀 Iniciando robô... Aguardando 20 segundos', 'warning');
            
            // Iniciar preço em tempo real
            if(priceInterval) clearInterval(priceInterval);
            priceInterval = setInterval(updatePrice, 1000);
            
            // Contagem regressiva inicial
            let startTime = 20;
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
                    addLog('✅ Robô iniciado - Analisando mercado...', 'success');
                    startAnalysis();
                }
            }, 1000);
        }
        
        function stopBot() {
            botState.running = false;
            
            if(countdownInterval) clearInterval(countdownInterval);
            if(cooldownInterval) clearInterval(cooldownInterval);
            if(tradingInterval) clearInterval(tradingInterval);
            if(priceInterval) clearInterval(priceInterval);
            
            document.getElementById('startCounter').innerHTML = '20s';
            document.getElementById('cooldownCounter').innerHTML = '0s';
            document.getElementById('targetInfo').style.display = 'none';
            
            // Reset prediction
            botState.targetDigit = null;
            botState.predictionDigit = null;
            botState.waitingForCompletion = false;
            document.getElementById('predictionDigit').innerHTML = '-';
            document.getElementById('predictionStatus').innerHTML = 'Parado';
            
            addLog('⏹️ Robô parado', 'error');
        }
        
        function startAnalysis() {
            if(!botState.running) return;
            
            addLog('🔍 Analisando últimos 25 ticks...', 'info');
            
            tradingInterval = setInterval(() => {
                if(!botState.running) {
                    clearInterval(tradingInterval);
                    return;
                }
                
                // Se está aguardando completar ciclo, não faz nova análise
                if(botState.waitingForCompletion) {
                    return;
                }
                
                // Gerar dados dos últimos 25 ticks
                let freq = {};
                let total = 0;
                
                for(let i = 0; i <= 9; i++) {
                    freq[i] = Math.random() * 15;
                    total += freq[i];
                }
                
                // Normalizar
                for(let i = 0; i <= 9; i++) {
                    freq[i] = (freq[i] / total) * 100;
                }
                
                // PASSO 1: Identificar número da previsão (0%) - SÓ EXECUTA SE NÃO TEM DÍGITO ALVO
                if(botState.targetDigit === null && !botState.inPosition && !botState.waitingForCompletion) {
                    for(let i = 0; i <= 9; i++) {
                        if(freq[i] < 0.5) {
                            botState.targetDigit = i;
                            botState.predictionDigit = i;
                            botState.entryTriggered = false;
                            botState.waitingForCompletion = true; // AGUARDA CICLO COMPLETAR
                            
                            document.getElementById('predictionDigit').innerHTML = i;
                            document.getElementById('predictionStatus').innerHTML = 'Aguardando 8%';
                            document.getElementById('targetInfo').style.display = 'block';
                            document.getElementById('targetInfo').innerHTML = `🎯 Dígito da previsão: <strong>${i}</strong> (0% nos últimos 25 ticks) - Aguardando 8% para comprar`;
                            
                            addLog(`🎯 Dígito da previsão encontrado: ${i} (0%) - Aguardando 8%`, 'warning');
                            break;
                        }
                    }
                }
                
                // PASSO 2: Aguardar chegar a 8% (só executa se tem dígito alvo)
                if(botState.targetDigit !== null && !botState.inPosition && !botState.entryTriggered) {
                    if(freq[botState.targetDigit] >= 8) {
                        botState.entryTriggered = true;
                        
                        document.getElementById('predictionStatus').innerHTML = '📊 Atingiu 8%! Comprando...';
                        document.getElementById('targetInfo').innerHTML = `📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando no próximo tick...`;
                        
                        addLog(`📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando no próximo tick...`, 'warning');
                        
                        // PASSO 3: Comprar no próximo tick
                        setTimeout(() => {
                            if(!botState.running) return;
                            
                            botState.inPosition = true;
                            addLog(`✅ COMPRA REALIZADA: $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.targetDigit}`, 'success');
                            
                            // Simular próximo tick para resultado
                            setTimeout(() => {
                                if(!botState.running) return;
                                
                                // Verificar se o dígito da previsão saiu
                                let lastDigit = Math.floor(Math.random() * 10);
                                let won = (lastDigit === botState.targetDigit);
                                
                                // PASSO 4: Aplicar martingale se perdeu / Vender se ganhou
                                if(won) {
                                    let profit = botState.stats.currentStake * 0.95;
                                    botState.stats.profit += profit;
                                    botState.stats.trades++;
                                    botState.stats.wins++;
                                    botState.stats.losses = 0;
                                    botState.stats.currentStake = botState.config.stake;
                                    
                                    addLog(`💰 DÍGITO ${lastDigit} SAIU! VENDA REALIZADA - Lucro: $${profit.toFixed(2)}`, 'success');
                                } else {
                                    let loss = -botState.stats.currentStake;
                                    botState.stats.profit += loss;
                                    botState.stats.trades++;
                                    botState.stats.losses++;
                                    botState.stats.currentStake *= botState.config.martingale;
                                    
                                    addLog(`❌ DÍGITO ${lastDigit} NÃO SAIU! Prejuízo: $${Math.abs(loss).toFixed(2)}`, 'error');
                                    addLog(`📈 Martingale ativado - Nova stake: $${botState.stats.currentStake.toFixed(2)}`, 'warning');
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
                                
                                // PASSO 5: Reset e cooldown de 5 segundos APÓS VENDA
                                botState.inPosition = false;
                                botState.targetDigit = null;
                                botState.entryTriggered = false;
                                
                                document.getElementById('predictionDigit').innerHTML = '-';
                                document.getElementById('predictionStatus').innerHTML = 'Aguardando nova análise...';
                                document.getElementById('targetInfo').style.display = 'none';
                                
                                addLog('⏱️ Aguardando 5 segundos para nova análise...', 'info');
                                
                                let cooldown = 5;
                                cooldownInterval = setInterval(() => {
                                    document.getElementById('cooldownCounter').innerHTML = cooldown + 's';
                                    cooldown--;
                                    
                                    if(cooldown < 0) {
                                        clearInterval(cooldownInterval);
                                        document.getElementById('cooldownCounter').innerHTML = 'Pronto';
                                        botState.waitingForCompletion = false; // LIBERA PARA NOVA ANÁLISE
                                        addLog('✅ Pronto para nova análise...', 'success');
                                    }
                                }, 1000);
                                
                            }, 2000); // Próximo tick
                            
                        }, 100); // Delay mínimo para próximo tick
                    }
                }
                
                // Atualizar gráfico
                updateBars(freq, botState.targetDigit);
                botState.frequencies = freq;
                
            }, 2000);
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

@app.get("/api/price")
async def get_price():
    price = 800 + random.random() * 100
    return {"price": round(price, 2)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

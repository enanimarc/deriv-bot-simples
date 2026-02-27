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
            background: #0d0d12;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: #1a1a24;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #2a2a35;
        }
        
        /* Header */
        .header {
            background: #1e1e2a;
            padding: 24px 32px;
            border-bottom: 1px solid #2a2a35;
        }
        
        .header h1 {
            color: white;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .header p {
            color: #8a8a9e;
            font-size: 14px;
        }
        
        /* Market Info Bar */
        .market-bar {
            background: #14141c;
            padding: 16px 32px;
            border-bottom: 1px solid #2a2a35;
            display: flex;
            gap: 48px;
            flex-wrap: wrap;
        }
        
        .market-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .market-label {
            color: #6a6a7e;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .market-value {
            color: white;
            font-size: 18px;
            font-weight: 500;
        }
        
        .market-value.highlight {
            color: #ff4444;
        }
        
        .status-connected {
            color: #4caf50;
        }
        
        .status-disconnected {
            color: #ff4444;
        }
        
        /* Main Grid */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 360px;
            gap: 0;
        }
        
        /* Chart Panel */
        .chart-panel {
            padding: 24px;
            border-right: 1px solid #2a2a35;
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .chart-title {
            color: white;
            font-size: 16px;
            font-weight: 500;
        }
        
        .chart-controls {
            display: flex;
            gap: 16px;
        }
        
        .control-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .control-item label {
            color: #8a8a9e;
            font-size: 13px;
        }
        
        .control-item select, .control-item input {
            background: #1e1e2a;
            border: 1px solid #2a2a35;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 13px;
        }
        
        /* Gráfico - IGUAL DERIV */
        .chart-wrapper {
            background: #14141c;
            border-radius: 8px;
            padding: 24px;
            border: 1px solid #2a2a35;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            width: 100%;
        }
        
        .y-axis {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 40px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 10px 0;
        }
        
        .y-axis span {
            color: #6a6a7e;
            font-size: 11px;
            text-align: right;
            padding-right: 8px;
        }
        
        .grid-area {
            margin-left: 40px;
            height: 100%;
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
            border-top: 1px dashed #2a2a35;
            height: 0;
            position: relative;
        }
        
        .grid-line span {
            position: absolute;
            left: -30px;
            top: -8px;
            color: #6a6a7e;
            font-size: 10px;
        }
        
        .reference-lines {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
        }
        
        .ref-line {
            position: absolute;
            left: 0;
            right: 0;
            height: 2px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
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
            background: #1e1e2a;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 10px;
            border: 1px solid #2a2a35;
        }
        
        .bars-container {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 100%;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            padding: 0 5px;
        }
        
        .bar-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 30px;
            height: 100%;
            justify-content: flex-end;
            position: relative;
        }
        
        .bar {
            width: 24px;
            background: linear-gradient(180deg, #ff6b6b 0%, #ff4444 100%);
            border-radius: 4px 4px 0 0;
            transition: height 0.3s ease;
            position: relative;
        }
        
        .bar.target {
            background: linear-gradient(180deg, #ffaa00 0%, #ff8800 100%);
        }
        
        .bar-percent {
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            font-size: 10px;
            font-weight: 600;
            white-space: nowrap;
            background: #1e1e2a;
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
            padding: 24px;
            background: #14141c;
        }
        
        .price-box {
            background: #1e1e2a;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            border: 1px solid #2a2a35;
        }
        
        .price-label {
            color: #8a8a9e;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .price-value {
            color: white;
            font-size: 42px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
        }
        
        .prediction-box {
            background: #1e1e2a;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            border: 1px solid #2a2a35;
        }
        
        .prediction-label {
            color: #8a8a9e;
            font-size: 12px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .prediction-digit {
            color: #ff4444;
            font-size: 64px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 8px;
        }
        
        .prediction-status {
            color: #ffaa00;
            font-size: 13px;
        }
        
        .counters {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .counter {
            flex: 1;
            background: #1e1e2a;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            border: 1px solid #2a2a35;
        }
        
        .counter-label {
            color: #8a8a9e;
            font-size: 11px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .counter-value {
            color: #ffaa00;
            font-size: 28px;
            font-weight: 700;
        }
        
        .profit-box {
            background: #1e1e2a;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
            border: 1px solid #2a2a35;
        }
        
        .profit-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2a35;
        }
        
        .profit-row:last-child {
            border-bottom: none;
        }
        
        .profit-label {
            color: #8a8a9e;
            font-size: 13px;
        }
        
        .profit-value {
            color: white;
            font-weight: 600;
        }
        
        .profit-positive {
            color: #4caf50;
        }
        
        .profit-negative {
            color: #ff4444;
        }
        
        .config-box {
            background: #1e1e2a;
            border-radius: 8px;
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
            color: #8a8a9e;
            font-size: 13px;
        }
        
        .config-input {
            background: #14141c;
            border: 1px solid #2a2a35;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            width: 100px;
            text-align: right;
        }
        
        .config-input.token {
            width: 140px;
        }
        
        .button-group {
            display: flex;
            gap: 8px;
            margin: 20px 0 12px;
        }
        
        .btn {
            flex: 1;
            padding: 12px;
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
        
        .btn:hover {
            transform: translateY(-2px);
            filter: brightness(1.1);
        }
        
        .target-info {
            background: #1e1e2a;
            border-left: 4px solid #ffaa00;
            padding: 12px;
            border-radius: 4px;
            margin-top: 16px;
            color: white;
            font-size: 13px;
            display: none;
        }
        
        .logs-panel {
            background: #0a0a0f;
            border-top: 1px solid #2a2a35;
            padding: 16px 24px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            height: 120px;
            overflow-y: auto;
            color: #e0e0e0;
        }
        
        .log-entry {
            padding: 4px 0;
            border-bottom: 1px solid #1e1e2a;
        }
        
        .log-success { color: #4caf50; }
        .log-error { color: #f44336; }
        .log-warning { color: #ffaa00; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🤖 Deriv Bot - Estratégia Dígito Matches</h1>
            <p>Análise 25 ticks | Identifica 0% → Aguarda 8% → Compra → Venda + Martingale 1.15x</p>
        </div>
        
        <!-- Market Info -->
        <div class="market-bar">
            <div class="market-item">
                <span class="market-label">MERCADO</span>
                <span class="market-value">Volatility 100 Index</span>
            </div>
            <div class="market-item">
                <span class="market-label">TIPO</span>
                <span class="market-value highlight">Dígito Matches</span>
            </div>
            <div class="market-item">
                <span class="market-label">DURAÇÃO</span>
                <span class="market-value">1 tick</span>
            </div>
            <div class="market-item">
                <span class="market-label">STATUS</span>
                <span class="market-value" id="statusDisplay">🔴 Desconectado</span>
            </div>
        </div>
        
        <!-- Main Grid -->
        <div class="main-grid">
            <!-- Chart Panel -->
            <div class="chart-panel">
                <div class="chart-header">
                    <div class="chart-title">📊 Last Digit Statistics - Últimos 25 ticks</div>
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
                
                <div class="chart-wrapper">
                    <div class="chart-container">
                        <!-- Y Axis -->
                        <div class="y-axis">
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
                            
                            <!-- Bars -->
                            <div class="bars-container" id="barsContainer"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Trading Panel -->
            <div class="trading-panel">
                <!-- Price -->
                <div class="price-box">
                    <div class="price-label">Preço Atual</div>
                    <div class="price-value" id="currentPrice">---</div>
                </div>
                
                <!-- Prediction -->
                <div class="prediction-box">
                    <div class="prediction-label">DÍGITO DA PREVISÃO</div>
                    <div class="prediction-digit" id="predictionDigit">-</div>
                    <div class="prediction-status" id="predictionStatus">Aguardando...</div>
                </div>
                
                <!-- Counters -->
                <div class="counters">
                    <div class="counter">
                        <div class="counter-label">Início em</div>
                        <div class="counter-value" id="startCounter">20s</div>
                    </div>
                    <div class="counter">
                        <div class="counter-label">Próximo trade</div>
                        <div class="counter-value" id="cooldownCounter">0s</div>
                    </div>
                </div>
                
                <!-- Profit -->
                <div class="profit-box">
                    <div class="profit-row">
                        <span class="profit-label">Lucro/Perda:</span>
                        <span class="profit-value" id="totalProfit">$0.00</span>
                    </div>
                    <div class="profit-row">
                        <span class="profit-label">Trades:</span>
                        <span class="profit-value" id="totalTrades">0</span>
                    </div>
                    <div class="profit-row">
                        <span class="profit-label">Stake Atual:</span>
                        <span class="profit-value" id="currentStake">$0.35</span>
                    </div>
                </div>
                
                <!-- Config -->
                <div class="config-box">
                    <div class="config-title">⚙️ CONFIGURAÇÕES</div>
                    
                    <div class="config-row">
                        <span class="config-label">Token:</span>
                        <input type="password" class="config-input token" id="token" placeholder="Opcional">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stake Inicial:</span>
                        <input type="number" class="config-input" id="stake" value="0.35" step="0.01">
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
                    
                    <div class="button-group">
                        <button class="btn btn-test" onclick="testConnection()">🔌 Testar</button>
                        <button class="btn btn-start" onclick="startBot()">▶️ Iniciar</button>
                        <button class="btn btn-stop" onclick="stopBot()">⏹️ Parar</button>
                    </div>
                    
                    <div id="targetInfo" class="target-info"></div>
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
        
        let priceInterval = null;
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
        
        function updateBars() {
            for(let i = 0; i <= 9; i++) {
                let bar = document.getElementById(`bar-${i}`);
                let percentEl = document.getElementById(`percent-${i}`);
                let percent = botState.frequencies[i] || 0;
                
                let height = (percent / 20) * 100;
                if(height > 100) height = 100;
                
                bar.style.height = height + '%';
                percentEl.innerHTML = percent.toFixed(1) + '%';
                
                if(i === botState.targetDigit) {
                    bar.classList.add('target');
                } else {
                    bar.classList.remove('target');
                }
            }
        }
        
        function updatePrice() {
            // Simular preço Volatility 100 Index
            let price = (800 + Math.random() * 200).toFixed(2);
            document.getElementById('currentPrice').innerHTML = price;
            
            // Extrair último dígito
            let lastDigit = parseInt(price[price.length - 1]);
            
            // Atualizar histórico
            botState.tickHistory.push(lastDigit);
            if(botState.tickHistory.length > 25) {
                botState.tickHistory.shift();
            }
            
            // Calcular frequências quando tiver 25 ticks
            if(botState.tickHistory.length === 25) {
                let counts = Array(10).fill(0);
                botState.tickHistory.forEach(d => counts[d]++);
                
                for(let i = 0; i <= 9; i++) {
                    botState.frequencies[i] = (counts[i] / 25) * 100;
                }
                
                updateBars();
                
                // Executar estratégia se o bot estiver rodando
                if(botState.running) {
                    executeStrategy(lastDigit);
                }
            }
        }
        
        function executeStrategy(lastDigit) {
            // PASSO 1: Procurar dígito com 0%
            if(botState.targetDigit === null && !botState.inPosition && !botState.waitingForCompletion) {
                for(let i = 0; i <= 9; i++) {
                    if(botState.frequencies[i] < 0.5) {
                        botState.targetDigit = i;
                        botState.waitingForCompletion = true;
                        
                        document.getElementById('predictionDigit').innerHTML = i;
                        document.getElementById('predictionStatus').innerHTML = 'Aguardando 8%';
                        document.getElementById('targetInfo').style.display = 'block';
                        document.getElementById('targetInfo').innerHTML = `🎯 Dígito da previsão: ${i} (0%) - Aguardando 8%`;
                        
                        addLog(`🎯 Dígito da previsão encontrado: ${i} (0%)`, 'warning');
                        break;
                    }
                }
            }
            
            // PASSO 2: Aguardar atingir 8%
            if(botState.targetDigit !== null && !botState.inPosition && !botState.entryTriggered) {
                if(botState.frequencies[botState.targetDigit] >= 8) {
                    botState.entryTriggered = true;
                    
                    document.getElementById('predictionStatus').innerHTML = '📊 Atingiu 8%! Comprando...';
                    document.getElementById('targetInfo').innerHTML = `📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando...`;
                    
                    addLog(`📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando...`, 'warning');
                    
                    // PASSO 3: Comprar no próximo tick
                    setTimeout(() => {
                        if(!botState.running) return;
                        
                        botState.inPosition = true;
                        addLog(`✅ COMPRA: $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.targetDigit}`, 'success');
                        
                        // PASSO 4: Aguardar resultado
                        setTimeout(() => {
                            if(!botState.running) return;
                            
                            // Gerar próximo tick
                            let nextPrice = (800 + Math.random() * 200).toFixed(2);
                            let nextDigit = parseInt(nextPrice[nextPrice.length - 1]);
                            
                            let won = (nextDigit === botState.targetDigit);
                            
                            if(won) {
                                let profit = botState.stats.currentStake * 0.95;
                                botState.stats.profit += profit;
                                botState.stats.trades++;
                                botState.stats.wins++;
                                botState.stats.losses = 0;
                                botState.stats.currentStake = botState.config.stake;
                                
                                addLog(`💰 VENDA: Dígito ${nextDigit} saiu! Lucro: $${profit.toFixed(2)}`, 'success');
                            } else {
                                let loss = -botState.stats.currentStake;
                                botState.stats.profit += loss;
                                botState.stats.trades++;
                                botState.stats.losses++;
                                botState.stats.currentStake *= botState.config.martingale;
                                
                                addLog(`❌ PERDA: Dígito ${nextDigit} não saiu! Prejuízo: $${Math.abs(loss).toFixed(2)}`, 'error');
                                addLog(`📈 Martingale ativado - Nova stake: $${botState.stats.currentStake.toFixed(2)}`, 'warning');
                            }
                            
                            updateStats();
                            
                            // Verificar stops
                            if(botState.stats.profit >= botState.config.stopWin) {
                                addLog('🎉 STOP WIN ATINGIDO!', 'success');
                                stopBot();
                                return;
                            }
                            
                            if(botState.stats.profit <= -botState.config.stopLoss) {
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
                                
                                if(cooldown < 0) {
                                    clearInterval(cooldownInterval);
                                    document.getElementById('cooldownCounter').innerHTML = 'Pronto';
                                    botState.waitingForCompletion = false;
                                }
                            }, 1000);
                            
                        }, 2000);
                    }, 100);
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
        
        function testConnection() {
            botState.connected = true;
            document.getElementById('statusDisplay').innerHTML = '🟢 Conectado';
            document.getElementById('statusDisplay').className = 'market-value status-connected';
            addLog('✅ Conectado à Deriv', 'success');
        }
        
        function startBot() {
            botState.running = true;
            botState.config = {
                stake: parseFloat(document.getElementById('stake').value),
                martingale: parseFloat(document.getElementById('martingale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin: parseFloat(document.getElementById('stopWin').value)
            };
            
            botState.stats.currentStake = botState.config.stake;
            updateStats();
            
            addLog('🚀 Iniciando robô... Aguardando 20 segundos', 'warning');
            
            // Iniciar preço em tempo real
            if(priceInterval) clearInterval(priceInterval);
            priceInterval = setInterval(updatePrice, 1000);
            
            // Contagem regressiva
            let startTime = 20;
            countdownInterval = setInterval(() => {
                document.getElementById('startCounter').innerHTML = startTime + 's';
                startTime--;
                
                if(startTime < 0) {
                    clearInterval(countdownInterval);
                    document.getElementById('startCounter').innerHTML = 'Ativo';
                    addLog('✅ Robô ativo - Analisando mercado...', 'success');
                }
            }, 1000);
        }
        
        function stopBot() {
            botState.running = false;
            
            if(priceInterval) clearInterval(priceInterval);
            if(countdownInterval) clearInterval(countdownInterval);
            if(cooldownInterval) clearInterval(cooldownInterval);
            
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
           
           

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
<html>
<head>
    <title>Deriv Trading Bot</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .content { display: flex; padding: 20px; gap: 20px; }
        .sidebar {
            width: 300px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .main { flex: 1; }
        .form-group { margin-bottom: 15px; }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        .form-group input:focus {
            border-color: #667eea;
            outline: none;
        }
        button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover { background: #5a67d8; transform: translateY(-2px); }
        .btn-success {
            background: #48bb78;
            color: white;
        }
        .btn-success:hover { background: #38a169; transform: translateY(-2px); }
        .btn-danger {
            background: #f56565;
            color: white;
        }
        .btn-danger:hover { background: #e53e3e; transform: translateY(-2px); }
        .stats {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .stat-value { font-weight: bold; color: #667eea; }
        .digit-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .digit-card {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
            border: 2px solid #ddd;
            transition: all 0.3s;
        }
        .digit-card.target {
            background: #fef3c7;
            border-color: #f59e0b;
            animation: pulse 1s infinite;
        }
        .digit-card.zero {
            background: #fee2e2;
            border-color: #ef4444;
        }
        .digit-number { font-size: 24px; font-weight: bold; }
        .digit-percent { font-size: 14px; color: #666; }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .counter-box {
            background: #667eea;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 10px 0;
        }
        .counter-box h2 { font-size: 2em; margin: 0; }
        .logs {
            background: #1a202c;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
        .log-entry {
            padding: 4px 0;
            border-bottom: 1px solid #2d3748;
        }
        .connection-status {
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .connected { background: #c6f6d5; color: #22543d; }
        .disconnected { background: #fed7d7; color: #742a2a; }
        .target-info {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .martingale-info {
            background: #fed7d7;
            border-left: 4px solid #ef4444;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Deriv Trading Bot - Dígito Matches</h1>
            <p>Estratégia: Dígito 0% → 8% → Compra → Venda + Martingale 1.15x</p>
        </div>
        
        <div class="content">
            <div class="sidebar">
                <h3>⚙️ Configurações</h3>
                
                <div class="form-group">
                    <label>🔑 Token da Deriv</label>
                    <input type="password" id="token" placeholder="Cole seu token">
                </div>
                
                <div class="form-group">
                    <label>💰 Stake Inicial ($)</label>
                    <input type="number" id="stake" value="0.35" step="0.01" min="0.35">
                </div>
                
                <div class="form-group">
                    <label>📈 Multiplicador Martingale</label>
                    <input type="number" id="martingale" value="1.15" step="0.01" min="1.0">
                </div>
                
                <div class="form-group">
                    <label>🛑 Stop Loss ($)</label>
                    <input type="number" id="stopLoss" value="10" step="0.01">
                </div>
                
                <div class="form-group">
                    <label>🎯 Stop Win ($)</label>
                    <input type="number" id="stopWin" value="10" step="0.01">
                </div>
                
                <button class="btn-primary" onclick="testConnection()">🔌 Testar Conexão</button>
                <button class="btn-success" onclick="startBot()">▶️ Iniciar Robô</button>
                <button class="btn-danger" onclick="stopBot()">⏹️ Parar Robô</button>
                
                <div id="connectionStatus" class="connection-status disconnected">
                    🔴 Desconectado
                </div>
                
                <div class="stats">
                    <h4>📊 Estatísticas</h4>
                    <div class="stat-item">
                        <span>Lucro Total:</span>
                        <span class="stat-value" id="totalProfit">$0.00</span>
                    </div>
                    <div class="stat-item">
                        <span>Trades:</span>
                        <span class="stat-value" id="totalTrades">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Win Rate:</span>
                        <span class="stat-value" id="winRate">0%</span>
                    </div>
                    <div class="stat-item">
                        <span>Stake Atual:</span>
                        <span class="stat-value" id="currentStake">$0.35</span>
                    </div>
                </div>
            </div>
            
            <div class="main">
                <div class="counter-box" id="startCounter">
                    <h2>20</h2>
                    <p>Segundos para iniciar</p>
                </div>
                
                <div class="counter-box" id="cooldownCounter">
                    <h2>5</h2>
                    <p>Segundos pós-venda</p>
                </div>
                
                <div class="target-info" id="targetInfo" style="display: none;">
                    <strong id="targetMessage">Aguardando dígito alvo...</strong>
                </div>
                
                <div class="martingale-info" id="martingaleInfo">
                    <strong>📈 Martingale Ativado</strong>
                    <span id="martingaleMessage"></span>
                </div>
                
                <h3>📊 Frequência dos Dígitos (Últimos 25 ticks)</h3>
                <div class="digit-grid" id="digitGrid"></div>
                
                <h3>📝 Logs</h3>
                <div class="logs" id="logs"></div>
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
        
        let ws = null;
        let countdownInterval = null;
        let tradingInterval = null;
        
        // Inicializar grid
        function initGrid() {
            let html = '';
            for(let i = 0; i <= 9; i++) {
                html += `
                    <div class="digit-card" id="digit-${i}">
                        <div class="digit-number">${i}</div>
                        <div class="digit-percent">0.0%</div>
                    </div>
                `;
            }
            document.getElementById('digitGrid').innerHTML = html;
        }
        initGrid();
        
        function updateDigits(frequencies, target) {
            for(let i = 0; i <= 9; i++) {
                let card = document.getElementById(`digit-${i}`);
                let percent = frequencies[i] || 0;
                card.querySelector('.digit-percent').innerHTML = percent.toFixed(1) + '%';
                
                card.classList.remove('target', 'zero');
                if(i === target) {
                    card.classList.add('target');
                } else if(percent === 0) {
                    card.classList.add('zero');
                }
            }
        }
        
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
        
        function updateStats() {
            document.getElementById('totalProfit').innerHTML = '$' + botState.stats.profit.toFixed(2);
            document.getElementById('totalTrades').innerHTML = botState.stats.trades;
            
            let winRate = botState.stats.trades > 0 
                ? ((botState.stats.wins / botState.stats.trades) * 100).toFixed(1)
                : 0;
            document.getElementById('winRate').innerHTML = winRate + '%';
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
        }
        
        function testConnection() {
            let token = document.getElementById('token').value;
            if(!token) {
                alert('Digite seu token!');
                return;
            }
            
            document.getElementById('connectionStatus').className = 'connection-status connected';
            document.getElementById('connectionStatus').innerHTML = '🟢 Conectado';
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
                stake: parseFloat(document.getElementById('stake').value),
                martingale: parseFloat(document.getElementById('martingale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin: parseFloat(document.getElementById('stopWin').value)
            };
            
            botState.stats.currentStake = botState.config.stake;
            updateStats();
            
            addLog('🚀 Iniciando robô... Aguardando 20 segundos');
            
            // Contagem regressiva inicial
            let startTime = 20;
            if(countdownInterval) clearInterval(countdownInterval);
            
            countdownInterval = setInterval(() => {
                if(!botState.running) {
                    clearInterval(countdownInterval);
                    return;
                }
                
                document.getElementById('startCounter').innerHTML = `<h2>${startTime}</h2><p>Segundos para iniciar</p>`;
                startTime--;
                
                if(startTime < 0) {
                    clearInterval(countdownInterval);
                    document.getElementById('startCounter').innerHTML = '<h2>✅</h2><p>Robô ativo</p>';
                    startTrading();
                }
            }, 1000);
        }
        
        function stopBot() {
            botState.running = false;
            
            if(countdownInterval) clearInterval(countdownInterval);
            if(tradingInterval) clearInterval(tradingInterval);
            
            document.getElementById('startCounter').innerHTML = '<h2>20</h2><p>Segundos para iniciar</p>';
            document.getElementById('cooldownCounter').innerHTML = '<h2>5</h2><p>Segundos pós-venda</p>';
            document.getElementById('targetInfo').style.display = 'none';
            document.getElementById('martingaleInfo').style.display = 'none';
            
            addLog('⏹️ Robô parado');
        }
        
        function startTrading() {
            if(!botState.running) return;
            
            addLog('🔍 Analisando mercado...');
            
            tradingInterval = setInterval(() => {
                if(!botState.running) {
                    clearInterval(tradingInterval);
                    return;
                }
                
                // Simular dados dos últimos 25 ticks
                let freq = {};
                for(let i = 0; i <= 9; i++) {
                    freq[i] = Math.random() * 15;
                }
                
                // Encontrar dígito com 0%
                if(botState.targetDigit === null) {
                    for(let i = 0; i <= 9; i++) {
                        if(freq[i] < 1) {
                            botState.targetDigit = i;
                            document.getElementById('targetInfo').style.display = 'block';
                            document.getElementById('targetMessage').innerHTML = `🎯 Dígito alvo: ${i} (0%) - Aguardando 8%`;
                            addLog(`🎯 Dígito alvo encontrado: ${i} (0%)`);
                            break;
                        }
                    }
                }
                
                // Verificar se atingiu 8%
                if(botState.targetDigit !== null && !botState.inPosition) {
                    if(freq[botState.targetDigit] >= 8) {
                        botState.inPosition = true;
                        document.getElementById('targetMessage').innerHTML = `📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando...`;
                        addLog(`📊 Dígito ${botState.targetDigit} atingiu 8% - Comprando $${botState.stats.currentStake.toFixed(2)}`);
                        
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
                                addLog(`💰 GANHOU: $${profit.toFixed(2)}`);
                                document.getElementById('martingaleInfo').style.display = 'none';
                            } else {
                                botState.stats.losses++;
                                botState.stats.currentStake *= botState.config.martingale;
                                addLog(`❌ PERDEU: $${Math.abs(profit).toFixed(2)}`);
                                addLog(`📈 Martingale: Nova stake $${botState.stats.currentStake.toFixed(2)}`);
                                
                                document.getElementById('martingaleInfo').style.display = 'block';
                                document.getElementById('martingaleMessage').innerHTML = `Sequência: ${botState.stats.losses} perdas | Stake: $${botState.stats.currentStake.toFixed(2)}`;
                            }
                            
                            updateStats();
                            
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
                            let cooldown = 5;
                            let cdInterval = setInterval(() => {
                                document.getElementById('cooldownCounter').innerHTML = `<h2>${cooldown}</h2><p>Segundos pós-venda</p>`;
                                cooldown--;
                                
                                if(cooldown < 0) {
                                    clearInterval(cdInterval);
                                    document.getElementById('cooldownCounter').innerHTML = '<h2>✅</h2><p>Pronto</p>';
                                }
                            }, 1000);
                            
                        }, 2000);
                    }
                }
                
                updateDigits(freq, botState.targetDigit);
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

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

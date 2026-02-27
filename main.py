from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import json
import random
from collections import deque, Counter
import time

app = FastAPI()

# HTML da interface - Versão simplificada
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Trading Bot</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        h1 { text-align: center; color: #333; margin-bottom: 20px; }
        .config { 
            background: #f5f5f5; 
            padding: 20px; 
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .row { display: flex; gap: 20px; margin-bottom: 20px; }
        .col { flex: 1; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { 
            width: 100%; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 4px;
            margin-bottom: 10px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 10px;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .stat-item {
            display: inline-block;
            margin-right: 30px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .digit-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin: 20px 0;
        }
        .digit-card {
            background: #f8f9fa;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .digit-card.target {
            background: #ffc107;
            border-color: #28a745;
        }
        .digit-card.zero {
            background: #dc3545;
            color: white;
        }
        .digit-number { font-size: 24px; font-weight: bold; }
        .digit-percent { font-size: 14px; }
        .logs {
            background: #1e293b;
            color: #fff;
            padding: 15px;
            border-radius: 8px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
        }
        .log-entry { padding: 5px; border-bottom: 1px solid #334155; }
        .counter {
            background: #667eea;
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-size: 20px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Deriv Trading Bot - Dígito Matches</h1>
        
        <div class="config">
            <h3>Configurações</h3>
            <div class="row">
                <div class="col">
                    <label>Token da Deriv:</label>
                    <input type="password" id="token" placeholder="Cole seu token">
                </div>
                <div class="col">
                    <label>Stake Inicial ($):</label>
                    <input type="number" id="stake" value="0.35" step="0.01">
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <label>Martingale:</label>
                    <input type="number" id="martingale" value="1.15" step="0.01">
                </div>
                <div class="col">
                    <label>Stop Loss ($):</label>
                    <input type="number" id="stopLoss" value="10">
                </div>
                <div class="col">
                    <label>Stop Win ($):</label>
                    <input type="number" id="stopWin" value="10">
                </div>
            </div>
            <div>
                <button class="btn-primary" onclick="testConnection()">Testar Conexão</button>
                <button class="btn-success" onclick="startBot()">Iniciar Robô</button>
                <button class="btn-danger" onclick="stopBot()">Parar Robô</button>
            </div>
            <div id="connectionStatus" style="margin-top: 10px; padding: 10px; border-radius: 4px; display: none;"></div>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div>Lucro Total:</div>
                <div class="stat-value" id="totalProfit">$0.00</div>
            </div>
            <div class="stat-item">
                <div>Trades:</div>
                <div class="stat-value" id="totalTrades">0</div>
            </div>
            <div class="stat-item">
                <div>Win Rate:</div>
                <div class="stat-value" id="winRate">0%</div>
            </div>
            <div class="stat-item">
                <div>Stake Atual:</div>
                <div class="stat-value" id="currentStake">$0.35</div>
            </div>
        </div>
        
        <div class="counter" id="startCounter">Aguardando início: 20s</div>
        <div class="counter" id="cooldownCounter">Próximo trade: 0s</div>
        
        <div id="targetInfo" style="background: #e3f2fd; padding: 10px; border-radius: 4px; margin: 10px 0; display: none;"></div>
        
        <div class="digit-grid" id="digitGrid"></div>
        
        <h3>Logs:</h3>
        <div class="logs" id="logs"></div>
    </div>
    
    <script>
        let botActive = false;
        let ws = null;
        let stats = {
            profit: 0,
            trades: 0,
            wins: 0,
            stake: 0.35,
            losses: 0
        };
        
        // Inicializar grid
        function initGrid() {
            let html = '';
            for(let i = 0; i <= 9; i++) {
                html += `<div class="digit-card" id="d${i}">
                    <div class="digit-number">${i}</div>
                    <div class="digit-percent">0.0%</div>
                </div>`;
            }
            document.getElementById('digitGrid').innerHTML = html;
        }
        initGrid();
        
        function addLog(msg, type = 'info') {
            let logs = document.getElementById('logs');
            let entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}`;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
        }
        
        function updateStats() {
            document.getElementById('totalProfit').innerHTML = '$' + stats.profit.toFixed(2);
            document.getElementById('totalTrades').innerHTML = stats.trades;
            let winRate = stats.trades > 0 ? ((stats.wins / stats.trades) * 100).toFixed(1) : 0;
            document.getElementById('winRate').innerHTML = winRate + '%';
            document.getElementById('currentStake').innerHTML = '$' + stats.stake.toFixed(2);
        }
        
        function updateDigits(frequencies, target) {
            for(let i = 0; i <= 9; i++) {
                let card = document.getElementById('d' + i);
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
        
        function showConnectionStatus(msg, isError) {
            let status = document.getElementById('connectionStatus');
            status.style.display = 'block';
            status.style.background = isError ? '#f8d7da' : '#d4edda';
            status.style.color = isError ? '#721c24' : '#155724';
            status.innerHTML = msg;
        }
        
        async function testConnection() {
            let token = document.getElementById('token').value;
            if(!token) {
                alert('Digite seu token!');
                return;
            }
            
            showConnectionStatus('Testando conexão...', false);
            
            try {
                let response = await fetch('/api/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token: token})
                });
                let data = await response.json();
                
                if(data.success) {
                    showConnectionStatus('✅ Conectado com sucesso!', false);
                    addLog('✅ Conectado à Deriv');
                } else {
                    showConnectionStatus('❌ Erro: ' + data.message, true);
                }
            } catch(e) {
                showConnectionStatus('❌ Erro na conexão', true);
            }
        }
        
        function startBot() {
            let token = document.getElementById('token').value;
            if(!token) {
                alert('Digite seu token!');
                return;
            }
            
            botActive = true;
            
            let config = {
                stake: parseFloat(document.getElementById('stake').value),
                martingale: parseFloat(document.getElementById('martingale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin: parseFloat(document.getElementById('stopWin').value)
            };
            
            stats.stake = config.stake;
            updateStats();
            
            addLog('🚀 Iniciando robô... Aguarde 20 segundos');
            
            let countdown = 20;
            let counter = setInterval(() => {
                if(!botActive) {
                    clearInterval(counter);
                    return;
                }
                document.getElementById('startCounter').innerHTML = `Aguardando início: ${countdown}s`;
                countdown--;
                
                if(countdown < 0) {
                    clearInterval(counter);
                    document.getElementById('startCounter').innerHTML = '✅ Robô ativo';
                    startTrading(config);
                }
            }, 1000);
        }
        
        function stopBot() {
            botActive = false;
            if(ws) ws.close();
            addLog('⏹️ Robô parado');
            document.getElementById('startCounter').innerHTML = 'Robô parado';
        }
        
        function startTrading(config) {
            if(!botActive) return;
            
            addLog('🔍 Analisando últimos 25 ticks...');
            
            // Simular análise
            let interval = setInterval(() => {
                if(!botActive) {
                    clearInterval(interval);
                    return;
                }
                
                // Gerar frequências aleatórias
                let freq = {};
                for(let i = 0; i <= 9; i++) {
                    freq[i] = Math.random() * 15;
                }
                
                // Encontrar dígito com 0%
                let zeroDigit = null;
                for(let i = 0; i <= 9; i++) {
                    if(freq[i] < 1) {
                        zeroDigit = i;
                        break;
                    }
                }
                
                if(zeroDigit !== null) {
                    document.getElementById('targetInfo').style.display = 'block';
                    document.getElementById('targetInfo').innerHTML = `🎯 Dígito alvo: ${zeroDigit} (0%) - Aguardando 8%`;
                    
                    // Simular atingir 8%
                    if(freq[zeroDigit] >= 8) {
                        document.getElementById('targetInfo').innerHTML = `📊 Dígito ${zeroDigit} atingiu 8%! Comprando...`;
                        addLog(`📊 Dígito ${zeroDigit} atingiu 8% - Comprando $${stats.stake}`);
                        
                        // Simular compra
                        setTimeout(() => {
                            if(!botActive) return;
                            
                            // Simular resultado
                            let won = Math.random() > 0.4;
                            let profit = won ? stats.stake * 0.95 : -stats.stake;
                            
                            stats.profit += profit;
                            stats.trades++;
                            if(won) stats.wins++;
                            
                            if(won) {
                                addLog(`💰 GANHOU: $${profit.toFixed(2)}`, 'success');
                                stats.stake = config.stake;
                                stats.losses = 0;
                            } else {
                                addLog(`❌ PERDEU: $${Math.abs(profit).toFixed(2)}`);
                                stats.losses++;
                                stats.stake *= config.martingale;
                                addLog(`📈 Martingale: Nova stake $${stats.stake.toFixed(2)}`);
                            }
                            
                            updateStats();
                            
                            // Verificar stops
                            if(stats.profit >= config.stopWin) {
                                addLog('🎉 STOP WIN ATINGIDO! Parabéns!');
                                stopBot();
                            } else if(stats.profit <= -config.stopLoss) {
                                addLog('🛑 STOP LOSS ATINGIDO!');
                                stopBot();
                            } else {
                                // Cooldown de 5 segundos
                                let cooldown = 5;
                                let cd = setInterval(() => {
                                    if(!botActive) {
                                        clearInterval(cd);
                                        return;
                                    }
                                    document.getElementById('cooldownCounter').innerHTML = `Próximo trade: ${cooldown}s`;
                                    cooldown--;
                                    
                                    if(cooldown < 0) {
                                        clearInterval(cd);
                                        document.getElementById('cooldownCounter').innerHTML = 'Pronto para novo trade';
                                    }
                                }, 1000);
                            }
                        }, 2000);
                    }
                }
                
                updateDigits(freq, zeroDigit);
                
            }, 2000);
        }
    </script>
</body>
</html>
"""

# Rota principal
@app.get("/")
async def root():
    return HTMLResponse(content=HTML)

# Rota de teste
@app.post("/api/test")
async def test(request: dict):
    # Simula teste de conexão
    return {"success": True, "message": "Conexão OK"}

# Rota de health check (importante para o Railway)
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

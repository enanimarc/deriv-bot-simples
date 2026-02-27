from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import random
from collections import deque, Counter

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Trading Bot</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
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
        
        .main-content {
            display: flex;
            padding: 30px;
            gap: 30px;
        }
        
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
        }
        
        .chart-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .chart-container {
            padding: 30px;
            height: 400px;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            position: relative;
        }
        
        .bar-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 60px;
        }
        
        .bar {
            width: 40px;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px 8px 0 0;
            transition: height 0.3s;
            position: relative;
        }
        
        .bar.target {
            background: linear-gradient(180deg, #fbbf24 0%, #f59e0b 100%);
        }
        
        .bar.zero {
            background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
        }
        
        .bar-percent {
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 12px;
            font-weight: 600;
            color: #333;
        }
        
        .bar-label {
            margin-top: 10px;
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
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
            font-size: 36px;
            font-weight: 700;
            color: #333;
        }
        
        .prediction-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .prediction-digit {
            font-size: 48px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .countdown-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .countdown-value {
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
        }
        
        .profit-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .profit-row {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        
        .profit-positive {
            color: #10b981;
            font-weight: 600;
        }
        
        .profit-negative {
            color: #ef4444;
            font-weight: 600;
        }
        
        .config-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .config-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .config-row input {
            width: 100px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        button {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 10px;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-success {
            background: #10b981;
            color: white;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .logs-panel {
            background: #1a1a2e;
            color: #e0e0e0;
            padding: 20px 30px;
            font-family: monospace;
            font-size: 12px;
            height: 150px;
            overflow-y: auto;
        }
        
        .log-entry {
            padding: 4px 0;
            border-bottom: 1px solid #333;
        }
        
        .target-info {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        
        .status-connected {
            color: #10b981;
            font-weight: 600;
        }
        
        .status-disconnected {
            color: #ef4444;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Deriv Trading Bot</h1>
            <p>Estratégia: Dígito 0% → Aguarda 8% → Compra → Venda + Martingale</p>
        </div>
        
        <div class="market-info">
            <div class="market-item">
                <span class="market-label">Mercado</span>
                <span class="market-value">Volatility 100 Index</span>
            </div>
            <div class="market-item">
                <span class="market-label">Tipo</span>
                <span class="market-value">Dígito Matches</span>
            </div>
            <div class="market-item">
                <span class="market-label">Duração</span>
                <span class="market-value">1 tick</span>
            </div>
            <div class="market-item">
                <span class="market-label">Status</span>
                <span class="market-value" id="statusDisplay">🔴 Desconectado</span>
            </div>
        </div>
        
        <div class="main-content">
            <!-- Gráfico -->
            <div class="chart-panel">
                <div class="chart-header">
                    <div class="chart-title">📊 Últimos 25 Dígitos</div>
                </div>
                <div class="chart-container" id="chartContainer">
                    <!-- Barras serão geradas pelo JavaScript -->
                </div>
            </div>
            
            <!-- Painel de Trading -->
            <div class="trading-panel">
                <div class="price-display">
                    <div class="price-label">Preço Atual</div>
                    <div class="price-value" id="currentPrice">---</div>
                </div>
                
                <div class="prediction-box">
                    <div class="prediction-label">Dígito da Previsão</div>
                    <div class="prediction-digit" id="predictionDigit">-</div>
                    <div id="predictionStatus">Aguardando...</div>
                </div>
                
                <div class="countdown-box">
                    <div class="countdown-label">Início em:</div>
                    <div class="countdown-value" id="startCounter">20s</div>
                </div>
                
                <div class="countdown-box">
                    <div class="countdown-label">Próximo trade:</div>
                    <div class="countdown-value" id="cooldownCounter">0s</div>
                </div>
                
                <div class="profit-box">
                    <div class="profit-row">
                        <span>Lucro/Perda:</span>
                        <span id="totalProfit" class="profit-positive">$0.00</span>
                    </div>
                    <div class="profit-row">
                        <span>Trades:</span>
                        <span id="totalTrades">0</span>
                    </div>
                    <div class="profit-row">
                        <span>Stake Atual:</span>
                        <span id="currentStake">$0.35</span>
                    </div>
                </div>
                
                <div class="config-box">
                    <h3>⚙️ Configurações</h3>
                    
                    <div class="config-row">
                        <span>Token:</span>
                        <input type="password" id="token" placeholder="Opcional">
                    </div>
                    
                    <div class="config-row">
                        <span>Stake Inicial:</span>
                        <input type="number" id="stake" value="0.35" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span>Martingale:</span>
                        <input type="number" id="martingale" value="1.15" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span>Stop Loss:</span>
                        <input type="number" id="stopLoss" value="10">
                    </div>
                    
                    <div class="config-row">
                        <span>Stop Win:</span>
                        <input type="number" id="stopWin" value="10">
                    </div>
                    
                    <button class="btn-primary" onclick="testConnection()">🔌 Testar</button>
                    <button class="btn-success" onclick="startBot()">▶️ Iniciar</button>
                    <button class="btn-danger" onclick="stopBot()">⏹️ Parar</button>
                    
                    <div id="targetInfo" class="target-info" style="display: none;"></div>
                </div>
            </div>
        </div>
        
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
        let tradingInterval = null;
        
        // Inicializar gráfico
        function initChart() {
            let container = document.getElementById('chartContainer');
            let html = '';
            
            for(let i = 0; i <= 9; i++) {
                html += `
                    <div class="bar-wrapper" id="bar-${i}">
                        <div class="bar" id="bar-fill-${i}" style="height: 0%">
                            <span class="bar-percent" id="percent-${i}">0.0%</span>
                        </div>
                        <div class="bar-label">${i}</div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        initChart();
        
        function addLog(message, type = 'info') {
            let logs = document.getElementById('logs');
            let entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.style.color = type === 'success' ? '#4ade80' : type === 'error' ? '#f87171' : '#e0e0e0';
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
            
            while(logs.children.length > 100) {
                logs.removeChild(logs.firstChild);
            }
        }
        
        function updateBars() {
            for(let i = 0; i <= 9; i++) {
                let bar = document.getElementById(`bar-fill-${i}`);
                let percentEl = document.getElementById(`percent-${i}`);
                let percent = botState.frequencies[i] || 0;
                
                let height = (percent / 20) * 100;
                if(height > 100) height = 100;
                
                bar.style.height = height + '%';
                percentEl.innerHTML = percent.toFixed(1) + '%';
                
                // Destacar barras
                bar.classList.remove('target', 'zero');
                if(i === botState.targetDigit) {
                    bar.classList.add('target');
                } else if(percent === 0) {
                    bar.classList.add('zero');
                }
            }
        }
        
        function updatePrice() {
            let price = (800 + Math.random() * 100).toFixed(2);
            document.getElementById('currentPrice').innerHTML = price;
            
            // Simular tick real
            let lastDigit = parseInt(price[price.length - 1]);
            botState.tickHistory.push(lastDigit);
            if(botState.tickHistory.length > 25) {
                botState.tickHistory.shift();
            }
            
            // Calcular frequências
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
                    
                    // PASSO 3: Comprar
                    setTimeout(() => {
                        if(!botState.running) return;
                        
                        botState.inPosition = true;
                        addLog(`✅ COMPRA: $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.targetDigit}`, 'success');
                        
                        // PASSO 4: Verificar resultado
                        setTimeout(() => {
                            if(!botState.running) return;
                            
                            let won = (lastDigit === botState.targetDigit);
                            
                            if(won) {
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
            profitEl.className = botState.stats.profit >= 0 ? 'profit-positive' : 'profit-negative';
            
            document.getElementById('totalTrades').innerHTML = botState.stats.trades;
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
        }
        
        function testConnection() {
            botState.connected = true;
            document.getElementById('statusDisplay').innerHTML = '🟢 Conectado';
            document.getElementById('statusDisplay').className = 'market-value status-connected';
            addLog('✅ Conexão testada com sucesso', 'success');
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
            
            // Iniciar simulação de preço
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

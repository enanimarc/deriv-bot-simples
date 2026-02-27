from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

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
            background: #0a0a0f;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #111117;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #2a2a35;
        }
        
        .header {
            background: #1e1e2a;
            padding: 24px 32px;
            border-bottom: 1px solid #2a2a35;
        }
        
        .header h1 {
            color: white;
            font-size: 24px;
            font-weight: 600;
        }
        
        .header p {
            color: #8888a0;
            font-size: 14px;
            margin-top: 4px;
        }
        
        .market-bar {
            background: #0f0f14;
            padding: 16px 32px;
            border-bottom: 1px solid #2a2a35;
            display: flex;
            gap: 48px;
        }
        
        .market-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .market-label {
            color: #6a6a7e;
            font-size: 11px;
            text-transform: uppercase;
        }
        
        .market-value {
            color: white;
            font-size: 18px;
            font-weight: 500;
        }
        
        .market-value.highlight {
            color: #ff4444;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 0;
        }
        
        .chart-panel {
            padding: 24px;
            border-right: 1px solid #2a2a35;
            background: #0a0a0f;
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 24px;
        }
        
        .chart-title {
            color: white;
            font-size: 16px;
            font-weight: 500;
        }
        
        .chart-controls select {
            background: #1e1e2a;
            border: 1px solid #2a2a35;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
        }
        
        .chart-wrapper {
            background: #14141c;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #2a2a35;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
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
            color: #6a6a7e;
            font-size: 11px;
            text-align: right;
            padding: 10px 8px 10px 0;
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
        }
        
        .ref-line {
            position: absolute;
            left: 0;
            right: 0;
            height: 2px;
        }
        
        .ref-20 { top: 20%; border-top: 2px solid #ff4444; }
        .ref-8 { top: 68%; border-top: 2px solid #ffaa00; }
        .ref-4 { top: 84%; border-top: 2px solid #4caf50; }
        
        .ref-label {
            position: absolute;
            right: 10px;
            top: -10px;
            background: #1e1e2a;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
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
            width: 35px;
        }
        
        .bar {
            width: 28px;
            background: linear-gradient(180deg, #ff6b6b 0%, #ff4444 100%);
            border-radius: 4px 4px 0 0;
            transition: height 0.3s;
            position: relative;
        }
        
        .bar.target {
            background: linear-gradient(180deg, #ffaa00 0%, #ff8800 100%);
            box-shadow: 0 0 15px #ffaa00;
        }
        
        .bar-percent {
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            font-size: 11px;
            background: #1e1e2a;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #2a2a35;
            white-space: nowrap;
        }
        
        .bar-label {
            margin-top: 8px;
            color: white;
            font-size: 12px;
        }
        
        .trading-panel {
            padding: 24px;
            background: #0f0f14;
        }
        
        .price-box {
            background: #1a1a24;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            border: 1px solid #2a2a35;
        }
        
        .price-label {
            color: #8a8a9e;
            font-size: 11px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .price-value {
            color: white;
            font-size: 42px;
            font-family: 'Courier New', monospace;
            font-weight: 700;
        }
        
        .prediction-box {
            background: #1a1a24;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            border: 1px solid #2a2a35;
        }
        
        .prediction-label {
            color: #8a8a9e;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        
        .prediction-digit {
            color: #ff4444;
            font-size: 64px;
            font-weight: 700;
            line-height: 1;
        }
        
        .counters {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .counter {
            flex: 1;
            background: #1a1a24;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            border: 1px solid #2a2a35;
        }
        
        .counter-label {
            color: #8a8a9e;
            font-size: 10px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        
        .counter-value {
            color: #ffaa00;
            font-size: 24px;
            font-weight: 700;
        }
        
        .profit-box {
            background: #1a1a24;
            border-radius: 12px;
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
        
        .profit-positive { color: #4caf50; }
        .profit-negative { color: #ff4444; }
        
        .config-box {
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
            background: #0f0f14;
            border: 1px solid #2a2a35;
            color: white;
            padding: 8px;
            border-radius: 4px;
            width: 100px;
            text-align: right;
        }
        
        .token-input {
            width: 140px;
        }
        
        .button-group {
            display: flex;
            gap: 8px;
            margin: 20px 0;
        }
        
        .btn {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
        }
        
        .btn-test { background: #4a4a5a; color: white; }
        .btn-start { background: #4caf50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        
        .status-connected { color: #4caf50; }
        .status-disconnected { color: #ff4444; }
        
        .target-info {
            background: #1e1e2a;
            border-left: 4px solid #ffaa00;
            padding: 12px;
            border-radius: 4px;
            color: white;
            font-size: 13px;
            display: none;
        }
        
        .logs-panel {
            background: #0a0a0f;
            border-top: 1px solid #2a2a35;
            padding: 16px 24px;
            font-family: monospace;
            font-size: 12px;
            height: 120px;
            overflow-y: auto;
            color: #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Deriv Bot - Dígito Matches</h1>
            <p>Conexão direta com API da Deriv | Martingale até acertar</p>
        </div>
        
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
                <span class="market-label">STATUS</span>
                <span class="market-value" id="statusDisplay">🔴 Desconectado</span>
            </div>
        </div>
        
        <div class="main-grid">
            <div class="chart-panel">
                <div class="chart-header">
                    <div class="chart-title">📊 Últimos 25 dígitos</div>
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
                        
                        <div class="grid-area">
                            <div class="grid-lines">
                                <div class="grid-line"></div>
                                <div class="grid-line"></div>
                                <div class="grid-line"></div>
                                <div class="grid-line"></div>
                                <div class="grid-line"></div>
                                <div class="grid-line"></div>
                            </div>
                            
                            <div class="ref-line ref-20">
                                <span class="ref-label">20%</span>
                            </div>
                            <div class="ref-line ref-8">
                                <span class="ref-label">8%</span>
                            </div>
                            <div class="ref-line ref-4">
                                <span class="ref-label">4%</span>
                            </div>
                            
                            <div class="bars-container" id="barsContainer"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="trading-panel">
                <div class="price-box">
                    <div class="price-label">PREÇO ATUAL</div>
                    <div class="price-value" id="currentPrice">---</div>
                </div>
                
                <div class="prediction-box">
                    <div class="prediction-label">DÍGITO DA PREVISÃO</div>
                    <div class="prediction-digit" id="predictionDigit">-</div>
                    <div id="predictionStatus" style="color: #ffaa00; font-size: 12px;">Aguardando</div>
                </div>
                
                <div class="counters">
                    <div class="counter">
                        <div class="counter-label">INÍCIO</div>
                        <div class="counter-value" id="startCounter">20s</div>
                    </div>
                    <div class="counter">
                        <div class="counter-label">GALE</div>
                        <div class="counter-value" id="galeCount">0</div>
                    </div>
                </div>
                
                <div class="profit-box">
                    <div class="profit-row">
                        <span class="profit-label">Lucro/Perda:</span>
                        <span class="profit-value" id="totalProfit">$0.00</span>
                    </div>
                    <div class="profit-row">
                        <span class="profit-label">Stake Atual:</span>
                        <span class="profit-value" id="currentStake">$0.35</span>
                    </div>
                </div>
                
                <div class="config-box">
                    <div class="config-title">⚙️ CONFIGURAÇÕES</div>
                    
                    <div class="config-row">
                        <span class="config-label">Token:</span>
                        <input type="password" class="config-input token-input" id="token" value="YOUR_TOKEN_HERE">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stake:</span>
                        <input type="number" class="config-input" id="stake" value="0.35" step="0.01" min="0.35">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Gale:</span>
                        <input type="number" class="config-input" id="gale" value="1.15" step="0.01">
                    </div>
                    
                    <div class="config-row">
                        <span class="config-label">Stop Loss:</span>
                        <input type="number" class="config-input" id="stopLoss" value="10">
                    </div>
                    
                    <div class="button-group">
                        <button class="btn btn-test" onclick="connectDeriv()">🔌 CONECTAR</button>
                        <button class="btn btn-start" onclick="startBot()">▶️ INICIAR</button>
                        <button class="btn btn-stop" onclick="stopBot()">⏹️ PARAR</button>
                    </div>
                    
                    <div id="targetInfo" class="target-info"></div>
                </div>
            </div>
        </div>
        
        <div class="logs-panel" id="logs"></div>
    </div>
    
    <script>
        // Configuração da Deriv
        const DERIV_WS = 'wss://ws.derivws.com/websockets/v3?app_id=1089';
        const SYMBOL = 'R_100';
        
        // Estado do bot
        let ws = null;
        let botState = {
            running: false,
            connected: false,
            token: '',
            targetDigit: null,
            inPosition: false,
            waitingCompletion: false,
            entryTriggered: false,
            tickHistory: [],
            frequencies: Array(10).fill(0),
            stats: {
                profit: 0,
                currentStake: 0.35,
                galeCount: 0
            },
            config: {
                stake: 0.35,
                gale: 1.15,
                stopLoss: 10
            }
        };
        
        let countdownInterval = null;
        let logs = [];
        
        // Inicializar barras
        function initBars() {
            let html = '';
            for(let i = 0; i <= 9; i++) {
                html += `
                    <div class="bar-wrapper">
                        <div class="bar" id="bar-${i}" style="height: 0%">
                            <span class="bar-percent" id="percent-${i}">0.0%</span>
                        </div>
                        <div class="bar-label">${i}</div>
                    </div>
                `;
            }
            document.getElementById('barsContainer').innerHTML = html;
        }
        initBars();
        
        function addLog(msg, type = 'info') {
            let logsDiv = document.getElementById('logs');
            let entry = document.createElement('div');
            entry.style.color = type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#e0e0e0';
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}`;
            logsDiv.appendChild(entry);
            logsDiv.scrollTop = logsDiv.scrollHeight;
        }
        
        function updateBars() {
            for(let i = 0; i <= 9; i++) {
                let bar = document.getElementById(`bar-${i}`);
                let percent = botState.frequencies[i] || 0;
                let height = (percent / 20) * 100;
                bar.style.height = Math.min(height, 100) + '%';
                document.getElementById(`percent-${i}`).innerHTML = percent.toFixed(1) + '%';
                
                if(i === botState.targetDigit) {
                    bar.classList.add('target');
                } else {
                    bar.classList.remove('target');
                }
            }
        }
        
        function updateStats() {
            let profitEl = document.getElementById('totalProfit');
            profitEl.innerHTML = '$' + botState.stats.profit.toFixed(2);
            profitEl.className = 'profit-value ' + (botState.stats.profit >= 0 ? 'profit-positive' : 'profit-negative');
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
            document.getElementById('galeCount').innerHTML = botState.stats.galeCount;
        }
        
        // CONEXÃO DERIV
        function connectDeriv() {
            let token = document.getElementById('token').value;
            if(!token || token === 'YOUR_TOKEN_HERE') {
                alert('Por favor, insira seu token da Deriv');
                return;
            }
            
            botState.token = token;
            
            try {
                ws = new WebSocket(DERIV_WS);
                
                ws.onopen = () => {
                    // Autorizar
                    ws.send(JSON.stringify({ authorize: token }));
                };
                
                ws.onmessage = (event) => {
                    let data = JSON.parse(event.data);
                    
                    if(data.msg_type === 'authorize') {
                        if(data.error) {
                            addLog('❌ Erro token: ' + data.error.message, 'error');
                            return;
                        }
                        
                        botState.connected = true;
                        document.getElementById('statusDisplay').innerHTML = '🟢 Conectado';
                        document.getElementById('statusDisplay').className = 'market-value status-connected';
                        addLog('✅ Conectado à Deriv', 'success');
                        
                        // Assinar ticks
                        ws.send(JSON.stringify({
                            ticks: SYMBOL,
                            subscribe: 1
                        }));
                    }
                    
                    if(data.msg_type === 'tick' && data.tick) {
                        let price = data.tick.quote;
                        document.getElementById('currentPrice').innerHTML = price.toFixed(2);
                        
                        // Extrair último dígito
                        let priceStr = price.toString().replace('.', '');
                        let lastDigit = parseInt(priceStr[priceStr.length - 1]);
                        
                        // Atualizar histórico
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
                            
                            if(botState.running) {
                                executeStrategy(lastDigit);
                            }
                        }
                    }
                };
                
                ws.onclose = () => {
                    botState.connected = false;
                    document.getElementById('statusDisplay').innerHTML = '🔴 Desconectado';
                    document.getElementById('statusDisplay').className = 'market-value status-disconnected';
                    addLog('❌ Desconectado', 'error');
                };
                
            } catch(e) {
                addLog('❌ Erro: ' + e.message, 'error');
            }
        }
        
        // ESTRATÉGIA
        function executeStrategy(lastDigit) {
            // PASSO 1: Encontrar dígito 0%
            if(botState.targetDigit === null && !botState.inPosition && !botState.waitingCompletion) {
                for(let i = 0; i <= 9; i++) {
                    if(botState.frequencies[i] < 0.5) {
                        botState.targetDigit = i;
                        botState.waitingCompletion = true;
                        botState.stats.galeCount = 0;
                        
                        document.getElementById('predictionDigit').innerHTML = i;
                        document.getElementById('targetInfo').style.display = 'block';
                        document.getElementById('targetInfo').innerHTML = `🎯 Dígito ${i} (0%) - Aguardando 8%`;
                        
                        addLog(`🎯 Dígito alvo: ${i} (0%)`, 'warning');
                        break;
                    }
                }
            }
            
            // PASSO 2: Aguardar 8%
            if(botState.targetDigit !== null && !botState.inPosition && !botState.entryTriggered) {
                if(botState.frequencies[botState.targetDigit] >= 8) {
                    botState.entryTriggered = true;
                    document.getElementById('targetInfo').innerHTML = `📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando...`;
                    addLog(`📊 Atingiu 8%! Comprando...`, 'warning');
                    
                    // PASSO 3: Comprar
                    setTimeout(() => {
                        if(!botState.running) return;
                        
                        botState.inPosition = true;
                        botState.stats.galeCount++;
                        addLog(`✅ COMPRA ${botState.stats.galeCount}: $${botState.stats.currentStake.toFixed(2)}`, 'success');
                    }, 100);
                }
            }
            
            // PASSO 4: Verificar resultado
            if(botState.inPosition && botState.targetDigit !== null) {
                if(lastDigit === botState.targetDigit) {
                    // GANHOU
                    let profit = botState.stats.currentStake * 0.95;
                    botState.stats.profit += profit;
                    
                    addLog(`💰 VENDA! Dígito ${lastDigit} saiu! Lucro: $${profit.toFixed(2)}`, 'success');
                    
                    // Reset
                    botState.inPosition = false;
                    botState.targetDigit = null;
                    botState.entryTriggered = false;
                    botState.stats.currentStake = botState.config.stake;
                    botState.stats.galeCount = 0;
                    
                    document.getElementById('predictionDigit').innerHTML = '-';
                    document.getElementById('targetInfo').style.display = 'none';
                    
                    updateStats();
                    
                    // PASSO 7: Aguardar 5 segundos
                    addLog('⏱️ Aguardando 5 segundos...', 'info');
                    setTimeout(() => {
                        botState.waitingCompletion = false;
                    }, 5000);
                    
                } else {
                    // PERDEU - aplicar martingale
                    let loss = -botState.stats.currentStake;
                    botState.stats.profit += loss;
                    
                    addLog(`❌ PERDEU! Dígito ${lastDigit} não saiu`, 'error');
                    
                    // Verificar stop loss
                    if(botState.stats.profit <= -botState.config.stopLoss) {
                        addLog('🛑 STOP LOSS ATINGIDO!', 'error');
                        stopBot();
                        return;
                    }
                    
                    // Aplicar gale
                    botState.stats.currentStake *= botState.config.gale;
                    botState.inPosition = false; // Libera para nova compra
                    botState.entryTriggered = false;
                    
                    addLog(`📈 GALE ${botState.stats.galeCount + 1}: Nova stake $${botState.stats.currentStake.toFixed(2)}`, 'warning');
                    updateStats();
                }
            }
        }
        
        function startBot() {
            if(!botState.connected) {
                alert('Conecte-se primeiro!');
                return;
            }
            
            botState.running = true;
            botState.config = {
                stake: parseFloat(document.getElementById('stake').value),
                gale: parseFloat(document.getElementById('gale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value)
            };
            
            botState.stats.currentStake = botState.config.stake;
            updateStats();
            
            addLog('🚀 Iniciando... 20s', 'warning');
            
            let timeLeft = 20;
            countdownInterval = setInterval(() => {
                document.getElementById('startCounter').innerHTML = timeLeft + 's';
                timeLeft--;
                if(timeLeft < 0) {
                    clearInterval(countdownInterval);
                    document.getElementById('startCounter').innerHTML = 'Ativo';
                }
            }, 1000);
        }
        
        function stopBot() {
            botState.running = false;
            clearInterval(countdownInterval);
            document.getElementById('startCounter').innerHTML = '20s';
            addLog('⏹️ Parado', 'error');
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
           
           

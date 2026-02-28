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
            flex-wrap: wrap;
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
        
        /* Informações da conta */
        .account-info {
            background: #1a1a24;
            padding: 12px 24px;
            border-bottom: 1px solid #2a2a35;
            display: flex;
            gap: 32px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .account-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            background: #0f0f14;
            padding: 8px 16px;
            border-radius: 30px;
            border: 1px solid #2a2a35;
        }
        
        .badge-demo {
            color: #ffaa00;
            font-weight: 600;
        }
        
        .badge-real {
            color: #4caf50;
            font-weight: 600;
        }
        
        .account-id {
            font-family: monospace;
            color: #8888a0;
        }
        
        .balance-value {
            font-size: 24px;
            font-weight: 700;
            color: #4caf50;
        }
        
        .currency-code {
            color: #8888a0;
            margin-left: 4px;
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
            pointer-events: none;
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
            pointer-events: none;
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
            z-index: 5;
        }
        
        .bar-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 35px;
            height: 100%;
            justify-content: flex-end;
        }
        
        .bar {
            width: 28px;
            background: linear-gradient(180deg, #ff6b6b 0%, #ff4444 100%);
            border-radius: 4px 4px 0 0;
            transition: height 0.3s ease;
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
            font-weight: 600;
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
            font-weight: 500;
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
            font-weight: 700;
            font-family: 'Courier New', monospace;
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
            margin-bottom: 8px;
            text-transform: uppercase;
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
            transition: all 0.3s;
        }
        
        .btn-test { background: #4a4a5a; color: white; }
        .btn-start { background: #4caf50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        .btn:hover { transform: translateY(-2px); filter: brightness(1.1); }
        
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
            height: 200px;
            overflow-y: auto;
            color: #e0e0e0;
        }
        
        .connection-badge {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .badge-connected { background: #4caf50; box-shadow: 0 0 10px #4caf50; animation: pulse 2s infinite; }
        .badge-disconnected { background: #ff4444; }
        .badge-connecting { background: #ffaa00; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        
        .debug-info {
            margin-top: 10px;
            padding: 10px;
            background: #1a1a24;
            border: 1px solid #2a2a35;
            border-radius: 4px;
            font-size: 11px;
            color: #8888a0;
            display: none;
        }
        .freq-table {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5px;
            margin-top: 5px;
        }
        .freq-item {
            background: #0f0f14;
            padding: 3px;
            text-align: center;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Deriv Bot - Dígito Matches</h1>
            <p>Gráfico em tempo real | Martingale Forçado 1.15x tick a tick | Saldo em tempo real</p>
        </div>
        
        <div class="market-bar">
            <div class="market-item">
                <span class="market-label">MERCADO</span>
                <span class="market-value">Volatility 100 Index</span>
            </div>
            <div class="market-item">
                <span class="market-label">TIPO</span>
                <span class="market-value highlight">Dígito Matches (1-9)</span>
            </div>
            <div class="market-item">
                <span class="market-label">STATUS</span>
                <span class="market-value" id="statusDisplay">
                    <span class="connection-badge badge-disconnected" id="statusBadge"></span>
                    <span id="statusText">Desconectado</span>
                </span>
            </div>
        </div>
        
        <!-- Informações da conta -->
        <div class="account-info" id="accountInfo" style="display: none;">
            <div class="account-badge" id="accountBadge">
                <span id="accountTypeIcon">💰</span>
                <span id="accountType">Conta</span>
            </div>
            <div>
                <span class="market-label">ID DA CONTA</span>
                <div class="account-id" id="accountId">---</div>
            </div>
            <div>
                <span class="market-label">SALDO</span>
                <div>
                    <span class="balance-value" id="accountBalance">0.00</span>
                    <span class="currency-code" id="accountCurrency">USD</span>
                </div>
            </div>
        </div>
        
        <div class="main-grid">
            <div class="chart-panel">
                <div class="chart-header">
                    <div class="chart-title">📊 Frequência dos Dígitos 1-9 - Últimos 25 ticks</div>
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
                            
                            <div class="ref-line ref-20"><span class="ref-label">20%</span></div>
                            <div class="ref-line ref-8"><span class="ref-label">8%</span></div>
                            <div class="ref-line ref-4"><span class="ref-label">4%</span></div>
                            
                            <div class="bars-container" id="barsContainer"></div>
                        </div>
                    </div>
                </div>
                
                <div class="debug-info" id="debugInfo">
                    <div><strong>Ticks recebidos:</strong> <span id="tickCount">0</span>/25</div>
                    <div><strong>Último dígito:</strong> <span id="lastDigit">-</span></div>
                    <div><strong>Histórico:</strong> <span id="tickHistory">[]</span></div>
                    <div><strong>Frequências (1-9):</strong></div>
                    <div class="freq-table" id="freqTable"></div>
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
                    <div id="predictionStatus" style="color: #ffaa00; font-size: 12px;">Aguardando...</div>
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
                        <input type="password" class="config-input token-input" id="token" placeholder="Seu token">
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
                    
                    <div class="config-row">
                        <span class="config-label">Stop Win:</span>
                        <input type="number" class="config-input" id="stopWin" value="10">
                    </div>
                    
                    <div class="button-group">
                        <button class="btn btn-test" onclick="connectDeriv()">🔌 CONECTAR</button>
                        <button class="btn btn-start" onclick="startBot()">▶️ INICIAR</button>
                        <button class="btn btn-stop" onclick="stopBot()">⏹️ PARAR</button>
                        <button class="btn btn-test" onclick="toggleDebug()">🐛 DEBUG</button>
                    </div>
                    
                    <div id="targetInfo" class="target-info"></div>
                </div>
            </div>
        </div>
        
        <div class="logs-panel" id="logs"></div>
    </div>
    
    <script>
        // ============================================
        // CONFIGURAÇÃO DERIV API
        // ============================================
        const DERIV_WS_URL = 'wss://ws.derivws.com/websockets/v3?app_id=1089';
        const SYMBOL = 'R_100';
        
        // ============================================
        // ESTADO DO BOT
        // ============================================
        let ws = null;
        let reconnectTimer = null;
        let heartbeatInterval = null;
        let connectionAttempts = 0;
        let maxReconnectAttempts = 5;
        
        let botState = {
            running: false,
            connected: false,
            token: '',
            targetDigit: null,
            inPosition: false,
            waitingCompletion: false,
            entryTriggered: false,
            martingalePending: false,
            analysisStarted: false,
            tickHistory: [],
            frequencies: Array(10).fill(0),
            currentTradeDigit: null,
            purchasePrice: 0,
            stats: {
                profit: 0,
                trades: 0,
                wins: 0,
                currentStake: 0.35,
                galeCount: 0
            },
            config: {
                stake: 0.35,
                gale: 1.15,
                stopLoss: 10,
                stopWin: 10
            },
            account: {
                loginid: null,
                balance: 0,
                currency: 'USD',
                type: null
            }
        };
        
        let countdownInterval = null;
        let analysisTimer = null;
        let debugVisible = false;
        
        // ============================================
        // INICIALIZAÇÃO DO GRÁFICO
        // ============================================
        function initBars() {
            let container = document.getElementById('barsContainer');
            let html = '';
            for(let i = 1; i <= 9; i++) {
                html += `
                    <div class="bar-wrapper">
                        <div class="bar" id="bar-${i}" style="height: 0%">
                            <span class="bar-percent" id="percent-${i}">0.0%</span>
                        </div>
                        <div class="bar-label">${i}</div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }
        initBars();
        
        // ============================================
        // FUNÇÕES DE LOG
        // ============================================
        function addLog(msg, type = 'info') {
            let logsDiv = document.getElementById('logs');
            let entry = document.createElement('div');
            entry.style.color = type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#e0e0e0';
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}`;
            logsDiv.appendChild(entry);
            logsDiv.scrollTop = logsDiv.scrollHeight;
            
            while(logsDiv.children.length > 50) {
                logsDiv.removeChild(logsDiv.firstChild);
            }
        }
        
        function toggleDebug() {
            let debug = document.getElementById('debugInfo');
            debugVisible = !debugVisible;
            debug.style.display = debugVisible ? 'block' : 'none';
        }
        
        function updateDebug() {
            document.getElementById('tickCount').innerHTML = botState.tickHistory.length;
            if(botState.tickHistory.length > 0) {
                document.getElementById('lastDigit').innerHTML = botState.tickHistory[botState.tickHistory.length - 1];
            }
            document.getElementById('tickHistory').innerHTML = '[' + botState.tickHistory.join(', ') + ']';
            
            let freqHtml = '';
            for(let i = 1; i <= 9; i++) {
                freqHtml += `<div class="freq-item"><strong>${i}:</strong> ${botState.frequencies[i].toFixed(1)}%</div>`;
            }
            document.getElementById('freqTable').innerHTML = freqHtml;
        }
        
        // ============================================
        // ATUALIZAÇÃO DO GRÁFICO
        // ============================================
        function updateBars() {
            for(let i = 1; i <= 9; i++) {
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
        
        // ============================================
        // ATUALIZAÇÃO DE ESTATÍSTICAS
        // ============================================
        function updateStats() {
            let profitEl = document.getElementById('totalProfit');
            profitEl.innerHTML = '$' + botState.stats.profit.toFixed(2);
            profitEl.className = 'profit-value ' + (botState.stats.profit >= 0 ? 'profit-positive' : 'profit-negative');
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
            document.getElementById('galeCount').innerHTML = botState.stats.galeCount;
        }
        
        // ============================================
        // FUNÇÃO PARA ATUALIZAR INFORMAÇÕES DA CONTA
        // ============================================
        function updateAccountInfo(authorizeData) {
            if (!authorizeData || !authorizeData.authorize) return;
            
            let auth = authorizeData.authorize;
            let loginid = auth.loginid;
            let balance = auth.balance;
            let currency = auth.currency;
            
            botState.account.loginid = loginid;
            botState.account.balance = balance;
            botState.account.currency = currency;
            
            let accountType = '';
            let accountTypeIcon = '';
            let accountTypeClass = '';
            
            if (loginid.startsWith('VRTC') || loginid.startsWith('VRW')) {
                accountType = 'CONTA DEMO';
                accountTypeIcon = '🧪';
                accountTypeClass = 'badge-demo';
                botState.account.type = 'DEMO';
            } else if (loginid.startsWith('CR')) {
                accountType = 'CONTA REAL';
                accountTypeIcon = '💰';
                accountTypeClass = 'badge-real';
                botState.account.type = 'REAL';
            } else {
                accountType = 'CONTA';
                accountTypeIcon = '💳';
            }
            
            document.getElementById('accountInfo').style.display = 'flex';
            document.getElementById('accountTypeIcon').innerHTML = accountTypeIcon;
            document.getElementById('accountType').innerHTML = accountType;
            document.getElementById('accountType').className = accountTypeClass;
            document.getElementById('accountId').innerHTML = loginid;
            document.getElementById('accountBalance').innerHTML = balance.toFixed(2);
            document.getElementById('accountCurrency').innerHTML = currency;
            
            addLog(`📊 Conta: ${loginid} | Tipo: ${accountType} | Saldo: ${currency} ${balance.toFixed(2)}`, 'success');
        }
        
        // ============================================
        // FUNÇÃO PARA EXTRAIR O ÚLTIMO DÍGITO DO PREÇO
        // ============================================
        function getLastDigit(price) {
            let priceStr = price.toString();
            priceStr = priceStr.replace('.', '');
            let lastChar = priceStr[priceStr.length - 1];
            let digit = parseInt(lastChar, 10);
            
            if (digit === 0) {
                return null;
            }
            return digit;
        }
        
        // ============================================
        // FUNÇÃO PARA SOLICITAR SALDO
        // ============================================
        function requestBalance() {
            if (!ws || ws.readyState !== WebSocket.OPEN || !botState.connected) return;
            ws.send(JSON.stringify({ balance: 1 }));
        }
        
        // ============================================
        // FUNÇÕES DE TRANSAÇÃO REAL
        // ============================================
        
        function buyContract(digit, amount) {
            if (!ws || ws.readyState !== WebSocket.OPEN || !botState.connected) {
                addLog('❌ Não conectado à Deriv', 'error');
                return;
            }
            
            let proposalRequest = {
                proposal: 1,
                amount: amount,
                barrier: digit.toString(),
                basis: "stake",
                contract_type: "DIGITMATCH",
                currency: botState.account.currency || "USD",
                duration: 1,
                duration_unit: "t",
                symbol: SYMBOL
            };
            
            addLog(`📝 Solicitando compra: dígito ${digit} com stake $${amount.toFixed(2)}`, 'info');
            ws.send(JSON.stringify(proposalRequest));
        }
        
        // ============================================
        // CONEXÃO DERIV
        // ============================================
        function connectDeriv() {
            let token = document.getElementById('token').value;
            if(!token) {
                alert('Por favor, insira seu token da Deriv');
                return;
            }
            
            botState.token = token;
            connectionAttempts = 0;
            establishConnection();
        }
        
        function establishConnection() {
            updateConnectionStatus('connecting');
            addLog('🔄 Conectando à Deriv...', 'info');
            
            if(ws) {
                try {
                    ws.close(1000, "Reconectando");
                } catch(e) {}
                ws = null;
            }
            
            try {
                ws = new WebSocket(DERIV_WS_URL);
                
                let connectionTimeout = setTimeout(() => {
                    if(ws && ws.readyState !== WebSocket.OPEN) {
                        addLog('❌ Timeout de conexão', 'error');
                        ws.close();
                        handleReconnect();
                    }
                }, 10000);
                
                ws.onopen = () => {
                    clearTimeout(connectionTimeout);
                    connectionAttempts = 0;
                    addLog('✅ WebSocket conectado', 'success');
                    ws.send(JSON.stringify({ authorize: botState.token }));
                };
                
                ws.onmessage = (event) => {
                    let data = JSON.parse(event.data);
                    
                    if(data.msg_type === 'authorize') {
                        if(data.error) {
                            updateConnectionStatus('disconnected');
                            addLog('❌ Erro de autorização: ' + data.error.message, 'error');
                            return;
                        }
                        
                        botState.connected = true;
                        updateConnectionStatus('connected');
                        updateAccountInfo(data);
                        
                        // Inscrever para ticks e saldo
                        ws.send(JSON.stringify({ ticks: SYMBOL, subscribe: 1 }));
                        ws.send(JSON.stringify({ balance: 1, subscribe: 1 }));
                        
                        startHeartbeat();
                        addLog('📡 Inscrito em ticks e saldo', 'success');
                    }
                    
                    // Atualização de saldo
                    if(data.msg_type === 'balance' && data.balance) {
                        botState.account.balance = data.balance.balance;
                        document.getElementById('accountBalance').innerHTML = data.balance.balance.toFixed(2);
                    }
                    
                    // Processar ticks
                    if(data.msg_type === 'tick' && data.tick) {
                        let price = data.tick.quote;
                        let digit = getLastDigit(price);
                        
                        document.getElementById('currentPrice').innerHTML = price.toFixed(2);
                        
                        if (digit !== null) {
                            botState.tickHistory.push(digit);
                            if(botState.tickHistory.length > 25) botState.tickHistory.shift();
                            
                            calculateFrequencies();
                            updateDebug();
                            
                            if(botState.running && botState.analysisStarted) {
                                executeStrategy(digit);
                            }
                        }
                        
                        // Solicitar saldo a cada tick
                        requestBalance();
                    }
                    
                    // Resposta de proposta (compra executada com sucesso)
                    if(data.msg_type === 'proposal' && data.proposal) {
                        let proposal = data.proposal;
                        let stake = parseFloat(proposal.ask_price);
                        addLog(`✅ Proposta aceita! Stake: $${stake.toFixed(2)}`, 'success');
                        
                        // Executar a compra
                        ws.send(JSON.stringify({
                            buy: proposal.id,
                            price: stake
                        }));
                    }
                    
                    // Resposta de compra
                    if(data.msg_type === 'buy' && data.buy) {
                        botState.currentContractId = data.buy.contract_id;
                        botState.inPosition = true;
                        botState.purchasePrice = data.buy.buy_price;
                        addLog(`✅ Contrato comprado! ID: ${data.buy.contract_id}`, 'success');
                        
                        // Inscrever para acompanhar o contrato
                        ws.send(JSON.stringify({
                            proposal_open_contract: 1,
                            subscribe: 1,
                            contract_id: data.buy.contract_id
                        }));
                        
                        // Atualizar saldo após compra
                        setTimeout(requestBalance, 100);
                    }
                    
                    // Resultado do contrato
                    if(data.msg_type === 'proposal_open_contract' && data.proposal_open_contract) {
                        let contract = data.proposal_open_contract;
                        if (!contract.is_sold) return;
                        
                        let profit = parseFloat(contract.profit) || 0;
                        
                        botState.stats.trades++;
                        botState.stats.profit += profit;
                        
                        if (profit > 0) {
                            botState.stats.wins++;
                            addLog(`💰 GANHOU! Lucro: $${profit.toFixed(2)}`, 'success');
                            
                            // Reset após vitória
                            botState.inPosition = false;
                            botState.targetDigit = null;
                            botState.currentTradeDigit = null;
                            botState.entryTriggered = false;
                            botState.martingalePending = false;
                            botState.stats.currentStake = botState.config.stake;
                            botState.stats.galeCount = 0;
                            
                            document.getElementById('predictionDigit').innerHTML = '-';
                            document.getElementById('predictionStatus').innerHTML = 'Aguardando...';
                            document.getElementById('targetInfo').style.display = 'none';
                            
                            updateStats();
                            
                            if(botState.stats.profit >= botState.config.stopWin) {
                                addLog('🎉 STOP WIN ATINGIDO!', 'success');
                                stopBot();
                                return;
                            }
                            
                            addLog('⏱️ Aguardando 5 segundos...', 'info');
                            botState.waitingCompletion = true;
                            setTimeout(() => { 
                                botState.waitingCompletion = false; 
                                addLog('✅ Pronto para nova análise', 'success');
                            }, 5000);
                            
                        } else {
                            addLog(`❌ PERDEU! Prejuízo: $${Math.abs(profit).toFixed(2)}`, 'error');
                            
                            if(botState.stats.profit <= -botState.config.stopLoss) {
                                addLog('🛑 STOP LOSS ATINGIDO!', 'error');
                                stopBot();
                                return;
                            }
                            
                            // APLICAR MARTINGALE
                            botState.stats.currentStake *= botState.config.gale;
                            botState.stats.galeCount++;
                            
                            addLog(`📈 MARTINGALE ${botState.stats.galeCount}: Nova stake $${botState.stats.currentStake.toFixed(2)}`, 'warning');
                            
                            // FLAG PARA FORÇAR COMPRA NO PRÓXIMO TICK
                            botState.martingalePending = true;
                            botState.inPosition = false;
                            botState.entryTriggered = false;
                            
                            updateStats();
                        }
                        
                        botState.currentContractId = null;
                        requestBalance(); // Atualizar saldo
                    }
                    
                    if(data.msg_type === 'ping') {
                        ws.send(JSON.stringify({ pong: data.ping }));
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    addLog('❌ Erro na conexão', 'error');
                };
                
                ws.onclose = (event) => {
                    botState.connected = false;
                    updateConnectionStatus('disconnected');
                    document.getElementById('accountInfo').style.display = 'none';
                    
                    if(event.code !== 1000) {
                        addLog(`❌ Conexão fechada. Reconectando...`, 'error');
                        handleReconnect();
                    }
                };
                
            } catch(e) {
                addLog('❌ Erro ao conectar: ' + e.message, 'error');
                handleReconnect();
            }
        }
        
        function handleReconnect() {
            connectionAttempts++;
            if(connectionAttempts <= maxReconnectAttempts) {
                setTimeout(() => {
                    addLog(`🔄 Tentativa ${connectionAttempts}/${maxReconnectAttempts}...`, 'info');
                    establishConnection();
                }, 5000);
            }
        }
        
        function startHeartbeat() {
            if(heartbeatInterval) clearInterval(heartbeatInterval);
            heartbeatInterval = setInterval(() => {
                if(ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ ping: 1 }));
            }, 30000);
        }
        
        function updateConnectionStatus(status) {
            let badge = document.getElementById('statusBadge');
            let text = document.getElementById('statusText');
            
            badge.className = 'connection-badge';
            
            if(status === 'connected') {
                badge.classList.add('badge-connected');
                text.innerHTML = ' Conectado';
            } else if(status === 'connecting') {
                badge.classList.add('badge-connecting');
                text.innerHTML = ' Conectando...';
            } else {
                badge.classList.add('badge-disconnected');
                text.innerHTML = ' Desconectado';
            }
        }
        
        function calculateFrequencies() {
            if(botState.tickHistory.length === 0) return;
            
            let counts = Array(10).fill(0);
            for(let digit of botState.tickHistory) counts[digit]++;
            
            let total = botState.tickHistory.length;
            for(let i = 1; i <= 9; i++) {
                botState.frequencies[i] = (counts[i] / total) * 100;
            }
            
            updateBars();
        }
        
        // ============================================
        // ESTRATÉGIA PRINCIPAL - MARTINGALE FORÇADO
        // ============================================
        function executeStrategy(lastDigit) {
            // PASSO 1: VERIFICAR SE HÁ MARTINGALE PENDENTE (MÁXIMA PRIORIDADE)
            if(botState.martingalePending && !botState.inPosition && !botState.waitingCompletion) {
                
                // Garantir que temos um dígito alvo
                if (botState.currentTradeDigit !== null) {
                    botState.martingalePending = false;
                    botState.entryTriggered = true;
                    botState.targetDigit = botState.currentTradeDigit;
                    
                    document.getElementById('predictionDigit').innerHTML = botState.currentTradeDigit;
                    document.getElementById('predictionStatus').innerHTML = `📊 MARTINGALE ${botState.stats.galeCount}: Comprando FORÇADO...`;
                    document.getElementById('targetInfo').style.display = 'block';
                    document.getElementById('targetInfo').innerHTML = `📊 Tentativa ${botState.stats.galeCount} no dígito ${botState.currentTradeDigit}`;
                    
                    addLog(`🚀 MARTINGALE FORÇADO ${botState.stats.galeCount}: Comprando $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.currentTradeDigit}`, 'warning');
                    
                    // COMPRAR IMEDIATAMENTE
                    buyContract(botState.currentTradeDigit, botState.stats.currentStake);
                    return;
                }
            }
            
            // PASSO 2: MARTINGALE NORMAL (quando já temos currentTradeDigit)
            if(botState.currentTradeDigit !== null && !botState.inPosition && !botState.waitingCompletion && !botState.martingalePending) {
                
                if (!botState.entryTriggered) {
                    botState.entryTriggered = true;
                    botState.targetDigit = botState.currentTradeDigit;
                    
                    document.getElementById('predictionDigit').innerHTML = botState.currentTradeDigit;
                    document.getElementById('predictionStatus').innerHTML = `📊 MARTINGALE ${botState.stats.galeCount}: Comprando...`;
                    document.getElementById('targetInfo').style.display = 'block';
                    document.getElementById('targetInfo').innerHTML = `📊 Tentativa ${botState.stats.galeCount} no dígito ${botState.currentTradeDigit}`;
                    
                    addLog(`📊 MARTINGALE ${botState.stats.galeCount}: Comprando $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.currentTradeDigit}`, 'warning');
                    
                    buyContract(botState.currentTradeDigit, botState.stats.currentStake);
                }
                return;
            }
            
            // PASSO 3: Encontrar dígito com 0% (primeira entrada)
            if(botState.targetDigit === null && !botState.inPosition && !botState.waitingCompletion && botState.currentTradeDigit === null) {
                
                let zeroDigit = null;
                for(let i = 1; i <= 9; i++) {
                    if(botState.frequencies[i] < 0.5) {
                        zeroDigit = i;
                        break;
                    }
                }
                
                if(zeroDigit !== null) {
                    botState.targetDigit = zeroDigit;
                    botState.waitingCompletion = true;
                    botState.stats.galeCount = 0;
                    
                    document.getElementById('predictionDigit').innerHTML = zeroDigit;
                    document.getElementById('predictionStatus').innerHTML = `Aguardando 8% (atual: ${botState.frequencies[zeroDigit].toFixed(1)}%)`;
                    document.getElementById('targetInfo').style.display = 'block';
                    document.getElementById('targetInfo').innerHTML = `🎯 Dígito alvo: ${zeroDigit} (0%)`;
                    
                    addLog(`🎯 Dígito alvo: ${zeroDigit} (0%)`, 'warning');
                }
            }
            
            // PASSO 4: Aguardar 8% (primeira entrada)
            if(botState.targetDigit !== null && !botState.inPosition && !botState.entryTriggered && botState.currentTradeDigit === null) {
                let percent = botState.frequencies[botState.targetDigit];
                document.getElementById('predictionStatus').innerHTML = `Aguardando 8% (atual: ${percent.toFixed(1)}%)`;
                
                if(percent >= 8) {
                    botState.entryTriggered = true;
                    botState.currentTradeDigit = botState.targetDigit;
                    
                    document.getElementById('predictionStatus').innerHTML = `📊 Atingiu 8%! Comprando...`;
                    addLog(`📊 Dígito ${botState.targetDigit} atingiu 8%! Comprando...`, 'warning');
                    
                    buyContract(botState.targetDigit, botState.stats.currentStake);
                }
            }
        }
        
        function startBot() {
            if(!botState.connected) {
                alert('Conecte-se à Deriv primeiro!');
                return;
            }
            
            botState.running = true;
            botState.analysisStarted = false;
            botState.config = {
                stake: parseFloat(document.getElementById('stake').value),
                gale: parseFloat(document.getElementById('gale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin: parseFloat(document.getElementById('stopWin').value)
            };
            
            botState.stats.currentStake = botState.config.stake;
            updateStats();
            
            addLog('🚀 Iniciando robô... Aguardando 20s', 'warning');
            
            if(analysisTimer) clearTimeout(analysisTimer);
            analysisTimer = setTimeout(() => {
                botState.analysisStarted = true;
                addLog('✅ Análise iniciada', 'success');
                document.getElementById('predictionStatus').innerHTML = 'Analisando...';
            }, 20000);
            
            let timeLeft = 20;
            if(countdownInterval) clearInterval(countdownInterval);
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
            botState.analysisStarted = false;
            botState.targetDigit = null;
            botState.inPosition = false;
            botState.waitingCompletion = false;
            botState.currentTradeDigit = null;
            botState.martingalePending = false;
            
            if(countdownInterval) clearInterval(countdownInterval);
            if(analysisTimer) clearTimeout(analysisTimer);
            if(heartbeatInterval) clearInterval(heartbeatInterval);
            if(reconnectTimer) clearTimeout(reconnectTimer);
            if(ws) ws.close(1000, "Bot parado");
            
            document.getElementById('startCounter').innerHTML = '20s';
            document.getElementById('predictionDigit').innerHTML = '-';
            document.getElementById('predictionStatus').innerHTML = 'Parado';
            document.getElementById('targetInfo').style.display = 'none';
            
            updateConnectionStatus('disconnected');
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

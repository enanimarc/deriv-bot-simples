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
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #0a0a0f; min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: #111117; border-radius: 16px; overflow: hidden; border: 1px solid #2a2a35; }
        .header { background: #1e1e2a; padding: 24px 32px; border-bottom: 1px solid #2a2a35; }
        .header h1 { color: white; font-size: 24px; font-weight: 600; }
        .header p { color: #8888a0; font-size: 14px; margin-top: 4px; }
        .market-bar { background: #0f0f14; padding: 16px 32px; border-bottom: 1px solid #2a2a35; display: flex; gap: 48px; }
        .market-item { display: flex; flex-direction: column; gap: 4px; }
        .market-label { color: #6a6a7e; font-size: 11px; text-transform: uppercase; }
        .market-value { color: white; font-size: 18px; font-weight: 500; }
        .market-value.highlight { color: #ff4444; }
        .main-grid { display: grid; grid-template-columns: 1fr 400px; gap: 0; }
        .chart-panel { padding: 24px; border-right: 1px solid #2a2a35; background: #0a0a0f; }
        .chart-header { display: flex; justify-content: space-between; margin-bottom: 24px; }
        .chart-title { color: white; font-size: 16px; font-weight: 500; }
        .chart-wrapper { background: #14141c; border-radius: 12px; padding: 24px; border: 1px solid #2a2a35; }
        .chart-container { position: relative; height: 400px; }
        .y-axis { position: absolute; left: 0; top: 0; bottom: 0; width: 40px; display: flex; flex-direction: column; justify-content: space-between; color: #6a6a7e; font-size: 11px; text-align: right; padding: 10px 8px 10px 0; }
        .grid-area { margin-left: 40px; height: 100%; position: relative; }
        .grid-lines { position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; flex-direction: column; justify-content: space-between; pointer-events: none; }
        .grid-line { border-top: 1px dashed #2a2a35; height: 0; }
        .ref-line { position: absolute; left: 0; right: 0; height: 2px; pointer-events: none; }
        .ref-20 { top: 20%; border-top: 2px solid #ff4444; }
        .ref-8 { top: 68%; border-top: 2px solid #ffaa00; }
        .ref-4 { top: 84%; border-top: 2px solid #4caf50; }
        .ref-label { position: absolute; right: 10px; top: -10px; background: #1e1e2a; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; border: 1px solid #2a2a35; }
        .bars-container { position: absolute; bottom: 0; left: 0; right: 0; height: 100%; display: flex; align-items: flex-end; justify-content: space-around; padding: 0 5px; z-index: 5; }
        .bar-wrapper { display: flex; flex-direction: column; align-items: center; width: 35px; height: 100%; justify-content: flex-end; }
        .bar { width: 28px; background: linear-gradient(180deg, #ff6b6b 0%, #ff4444 100%); border-radius: 4px 4px 0 0; transition: height 0.3s ease; position: relative; }
        .bar.target { background: linear-gradient(180deg, #ffaa00 0%, #ff8800 100%); box-shadow: 0 0 15px #ffaa00; }
        .bar-percent { position: absolute; top: -20px; left: 50%; transform: translateX(-50%); color: white; font-size: 11px; font-weight: 600; background: #1e1e2a; padding: 2px 6px; border-radius: 4px; border: 1px solid #2a2a35; white-space: nowrap; }
        .bar-label { margin-top: 8px; color: white; font-size: 12px; font-weight: 500; }
        .trading-panel { padding: 24px; background: #0f0f14; }
        .price-box { background: #1a1a24; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px; border: 1px solid #2a2a35; }
        .price-label { color: #8a8a9e; font-size: 11px; margin-bottom: 8px; text-transform: uppercase; }
        .price-value { color: white; font-size: 42px; font-weight: 700; font-family: 'Courier New', monospace; }
        .prediction-box { background: #1a1a24; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 20px; border: 1px solid #2a2a35; }
        .prediction-label { color: #8a8a9e; font-size: 11px; margin-bottom: 8px; text-transform: uppercase; }
        .prediction-digit { color: #ff4444; font-size: 64px; font-weight: 700; line-height: 1; }
        .counters { display: flex; gap: 12px; margin-bottom: 20px; }
        .counter { flex: 1; background: #1a1a24; border-radius: 8px; padding: 16px; text-align: center; border: 1px solid #2a2a35; }
        .counter-label { color: #8a8a9e; font-size: 10px; text-transform: uppercase; margin-bottom: 8px; }
        .counter-value { color: #ffaa00; font-size: 24px; font-weight: 700; }
        .balance-box { background: #1a1a24; border-radius: 12px; padding: 16px; margin-bottom: 16px; border: 1px solid #2a2a35; display: flex; justify-content: space-between; align-items: center; }
        .balance-label { color: #8a8a9e; font-size: 12px; }
        .balance-value { color: #4caf50; font-size: 20px; font-weight: 700; }
        .profit-box { background: #1a1a24; border-radius: 12px; padding: 16px; margin-bottom: 20px; border: 1px solid #2a2a35; }
        .profit-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2a2a35; }
        .profit-row:last-child { border-bottom: none; }
        .profit-label { color: #8a8a9e; font-size: 13px; }
        .profit-value { color: white; font-weight: 600; }
        .profit-positive { color: #4caf50; }
        .profit-negative { color: #ff4444; }
        .config-box { background: #1a1a24; border-radius: 12px; padding: 20px; border: 1px solid #2a2a35; }
        .config-title { color: white; font-size: 14px; font-weight: 600; margin-bottom: 16px; }
        .config-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .config-label { color: #8a8a9e; font-size: 13px; }
        .config-input { background: #0f0f14; border: 1px solid #2a2a35; color: white; padding: 8px; border-radius: 4px; width: 110px; text-align: right; }
        .token-input { width: 150px; }
        .button-group { display: flex; gap: 8px; margin: 20px 0; flex-wrap: wrap; }
        .btn { flex: 1; padding: 12px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 12px; }
        .btn-test { background: #4a4a5a; color: white; }
        .btn-start { background: #4caf50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        .btn:hover { transform: translateY(-2px); filter: brightness(1.1); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .status-connected { color: #4caf50; }
        .status-disconnected { color: #ff4444; }
        .target-info { background: #1e1e2a; border-left: 4px solid #ffaa00; padding: 12px; border-radius: 4px; color: white; font-size: 13px; display: none; }
        .logs-panel { background: #0a0a0f; border-top: 1px solid #2a2a35; padding: 16px 24px; font-family: monospace; font-size: 12px; height: 200px; overflow-y: auto; color: #e0e0e0; }
        .connection-badge { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
        .badge-connected { background: #4caf50; box-shadow: 0 0 10px #4caf50; animation: pulse 2s infinite; }
        .badge-disconnected { background: #ff4444; }
        .badge-connecting { background: #ffaa00; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        .trade-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; margin-left: 8px; }
        .badge-real { background: #ff4444; color: white; }
        .badge-demo { background: #4a4a5a; color: #aaa; }
        .account-type-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; margin-bottom: 8px; }
        .warning-box { background: #2a1a00; border: 1px solid #ff8800; border-radius: 8px; padding: 12px; margin-bottom: 16px; color: #ffaa00; font-size: 12px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Deriv Bot - Dígito Matches <span class="trade-badge badge-demo" id="accountBadge">DEMO</span></h1>
            <p>Operações REAIS via API Deriv | Volatility 100 | Martingale 1.15x</p>
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
            <div class="market-item">
                <span class="market-label">CONTA</span>
                <span class="market-value" id="accountLogin">---</span>
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
                            <span>20%</span><span>16%</span><span>12%</span>
                            <span>8%</span><span>4%</span><span>0%</span>
                        </div>
                        <div class="grid-area">
                            <div class="grid-lines">
                                <div class="grid-line"></div><div class="grid-line"></div>
                                <div class="grid-line"></div><div class="grid-line"></div>
                                <div class="grid-line"></div><div class="grid-line"></div>
                            </div>
                            <div class="ref-line ref-20"><span class="ref-label">20%</span></div>
                            <div class="ref-line ref-8"><span class="ref-label">8%</span></div>
                            <div class="ref-line ref-4"><span class="ref-label">4%</span></div>
                            <div class="bars-container" id="barsContainer"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="trading-panel">
                <div class="balance-box">
                    <div>
                        <div class="balance-label">💰 SALDO DA CONTA</div>
                        <div class="balance-value" id="accountBalance">---</div>
                    </div>
                    <div style="text-align:right">
                        <div class="balance-label">MOEDA</div>
                        <div style="color:white;font-weight:600" id="accountCurrency">---</div>
                    </div>
                </div>

                <div class="price-box">
                    <div class="price-label">PREÇO ATUAL</div>
                    <div class="price-value" id="currentPrice">---</div>
                </div>
                
                <div class="prediction-box">
                    <div class="prediction-label">DÍGITO ALVO</div>
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
                    <div class="counter">
                        <div class="counter-label">TRADES</div>
                        <div class="counter-value" id="tradeCount">0</div>
                    </div>
                </div>
                
                <div class="profit-box">
                    <div class="profit-row">
                        <span class="profit-label">Lucro/Perda (sessão):</span>
                        <span class="profit-value" id="totalProfit">$0.00</span>
                    </div>
                    <div class="profit-row">
                        <span class="profit-label">Stake Atual:</span>
                        <span class="profit-value" id="currentStake">$0.35</span>
                    </div>
                    <div class="profit-row">
                        <span class="profit-label">Último resultado:</span>
                        <span class="profit-value" id="lastResult">---</span>
                    </div>
                </div>

                <div class="warning-box" id="warningBox">
                    ⚠️ <strong>ATENÇÃO:</strong> Conta REAL detectada! As operações serão executadas com dinheiro real.
                </div>
                
                <div class="config-box">
                    <div class="config-title">⚙️ CONFIGURAÇÕES</div>
                    <div class="config-row">
                        <span class="config-label">Token API:</span>
                        <input type="password" class="config-input token-input" id="token" placeholder="Seu token Deriv">
                    </div>
                    <div class="config-row">
                        <span class="config-label">Stake inicial (USD):</span>
                        <input type="number" class="config-input" id="stake" value="0.35" step="0.01" min="0.35">
                    </div>
                    <div class="config-row">
                        <span class="config-label">Multiplicador Gale:</span>
                        <input type="number" class="config-input" id="gale" value="1.15" step="0.01">
                    </div>
                    <div class="config-row">
                        <span class="config-label">Stop Loss ($):</span>
                        <input type="number" class="config-input" id="stopLoss" value="10">
                    </div>
                    <div class="config-row">
                        <span class="config-label">Stop Win ($):</span>
                        <input type="number" class="config-input" id="stopWin" value="10">
                    </div>
                    
                    <div class="button-group">
                        <button class="btn btn-test" id="btnConnect" onclick="connectDeriv()">🔌 CONECTAR</button>
                        <button class="btn btn-start" id="btnStart" onclick="startBot()" disabled>▶️ INICIAR</button>
                        <button class="btn btn-stop" id="btnStop" onclick="stopBot()" disabled>⏹️ PARAR</button>
                    </div>
                    
                    <div id="targetInfo" class="target-info"></div>
                </div>
            </div>
        </div>
        
        <div class="logs-panel" id="logs"></div>
    </div>
    
    <script>
        // ============================================================
        // CONFIGURAÇÃO DERIV API
        // ============================================================
        const DERIV_WS_URL = 'wss://ws.derivws.com/websockets/v3?app_id=1089';
        const SYMBOL = 'R_100';
        
        // ============================================================
        // ESTADO GLOBAL DO BOT
        // ============================================================
        let ws = null;
        let reconnectTimer = null;
        let heartbeatInterval = null;
        let connectionAttempts = 0;
        const MAX_RECONNECT = 5;

        let botState = {
            running: false,
            connected: false,
            authorized: false,
            token: '',
            accountType: 'demo',   // 'real' ou 'demo'
            currency: 'USD',
            balance: 0,

            // Análise de dígitos
            tickHistory: [],
            frequencies: Array(10).fill(0),

            // Fluxo de entrada
            targetDigit: null,
            waitingFor8pct: false,
            entryTriggered: false,
            analysisStarted: false,

            // Contrato ativo
            inPosition: false,
            currentContractId: null,
            currentTradeDigit: null,
            purchasePrice: 0,

            // Estatísticas da sessão
            stats: {
                profit: 0,
                trades: 0,
                wins: 0,
                currentStake: 0.35,
                galeCount: 0
            },

            // Configurações
            config: {
                stake: 0.35,
                gale: 1.15,
                stopLoss: 10,
                stopWin: 10
            }
        };

        let countdownInterval = null;
        let analysisTimer = null;

        // ============================================================
        // GRÁFICO DE BARRAS
        // ============================================================
        function initBars() {
            let c = document.getElementById('barsContainer');
            let html = '';
            for(let i = 1; i <= 9; i++) {
                html += `<div class="bar-wrapper">
                    <div class="bar" id="bar-${i}" style="height:0%">
                        <span class="bar-percent" id="pct-${i}">0%</span>
                    </div>
                    <div class="bar-label">${i}</div>
                </div>`;
            }
            c.innerHTML = html;
        }
        initBars();

        function updateBars() {
            for(let i = 1; i <= 9; i++) {
                let bar = document.getElementById(`bar-${i}`);
                let pct = document.getElementById(`pct-${i}`);
                let val = botState.frequencies[i] || 0;
                let h = Math.min((val / 20) * 100, 100);
                bar.style.height = h + '%';
                pct.innerHTML = val.toFixed(1) + '%';
                bar.classList.toggle('target', i === botState.targetDigit);
            }
        }

        // ============================================================
        // LOG
        // ============================================================
        function addLog(msg, type = 'info') {
            let div = document.getElementById('logs');
            let el = document.createElement('div');
            let colors = { success: '#4caf50', error: '#f44336', warning: '#ffaa00', info: '#e0e0e0' };
            el.style.color = colors[type] || '#e0e0e0';
            el.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}`;
            div.appendChild(el);
            div.scrollTop = div.scrollHeight;
            while(div.children.length > 80) div.removeChild(div.firstChild);
        }

        // ============================================================
        // ATUALIZA UI
        // ============================================================
        function updateStats() {
            let p = botState.stats.profit;
            let el = document.getElementById('totalProfit');
            el.innerHTML = (p >= 0 ? '+' : '') + '$' + p.toFixed(2);
            el.className = 'profit-value ' + (p >= 0 ? 'profit-positive' : 'profit-negative');
            document.getElementById('currentStake').innerHTML = '$' + botState.stats.currentStake.toFixed(2);
            document.getElementById('galeCount').innerHTML = botState.stats.galeCount;
            document.getElementById('tradeCount').innerHTML = botState.stats.trades;
        }

        function updateBalance(balance, currency) {
            botState.balance = balance;
            botState.currency = currency;
            document.getElementById('accountBalance').innerHTML = 
                parseFloat(balance).toFixed(2) + ' ' + currency;
        }

        function updateConnectionStatus(status) {
            let badge = document.getElementById('statusBadge');
            let text  = document.getElementById('statusText');
            badge.className = 'connection-badge';
            if(status === 'connected') {
                badge.classList.add('badge-connected');
                text.innerHTML = ' Conectado';
                document.getElementById('statusDisplay').className = 'market-value status-connected';
                document.getElementById('btnStart').disabled = false;
            } else if(status === 'connecting') {
                badge.classList.add('badge-connecting');
                text.innerHTML = ' Conectando...';
                document.getElementById('statusDisplay').className = 'market-value';
            } else {
                badge.classList.add('badge-disconnected');
                text.innerHTML = ' Desconectado';
                document.getElementById('statusDisplay').className = 'market-value status-disconnected';
                document.getElementById('btnStart').disabled = true;
                document.getElementById('btnStop').disabled = true;
            }
        }

        // ============================================================
        // EXTRAI ÚLTIMO DÍGITO (ignora 0)
        // ============================================================
        function getLastDigit(price) {
            let s = price.toString().replace('.', '');
            let d = parseInt(s[s.length - 1], 10);
            return d === 0 ? null : d;
        }

        // ============================================================
        // CALCULA FREQUÊNCIAS (apenas dígitos 1–9)
        // ============================================================
        function calculateFrequencies() {
            let counts = Array(10).fill(0);
            botState.tickHistory.forEach(d => counts[d]++);
            let total = botState.tickHistory.length;
            for(let i = 1; i <= 9; i++) {
                botState.frequencies[i] = total > 0 ? (counts[i] / total) * 100 : 0;
            }
            updateBars();
        }

        // ============================================================
        // WEBSOCKET — CONEXÃO
        // ============================================================
        function connectDeriv() {
            let token = document.getElementById('token').value.trim();
            if(!token) { alert('Insira seu token da Deriv!'); return; }
            botState.token = token;
            connectionAttempts = 0;
            establishConnection();
        }

        function establishConnection() {
            updateConnectionStatus('connecting');
            addLog('🔄 Conectando à API Deriv...', 'info');

            if(ws) { try { ws.close(1000); } catch(e) {} ws = null; }

            ws = new WebSocket(DERIV_WS_URL);

            let timeout = setTimeout(() => {
                if(ws && ws.readyState !== WebSocket.OPEN) {
                    addLog('⏱️ Timeout de conexão.', 'error');
                    ws.close();
                    handleReconnect();
                }
            }, 10000);

            ws.onopen = () => {
                clearTimeout(timeout);
                connectionAttempts = 0;
                addLog('🔗 WebSocket aberto. Autorizando...', 'info');
                ws.send(JSON.stringify({ authorize: botState.token }));
            };

            // --------------------------------------------------------
            // HANDLER DE MENSAGENS — NÚCLEO DO BOT
            // --------------------------------------------------------
            ws.onmessage = (event) => {
                let data = JSON.parse(event.data);

                // ── AUTORIZAÇÃO ──────────────────────────────────────
                if(data.msg_type === 'authorize') {
                    if(data.error) {
                        addLog('❌ Autorização falhou: ' + data.error.message, 'error');
                        updateConnectionStatus('disconnected');
                        return;
                    }
                    let acc = data.authorize;
                    botState.authorized = true;
                    botState.connected  = true;

                    // Detecta tipo de conta (real vs demo)
                    let isReal = acc.account_list
                        ? acc.account_list.some(a => a.loginid === acc.loginid && a.is_virtual === 0)
                        : !acc.loginid.startsWith('VRTC');
                    botState.accountType = isReal ? 'real' : 'demo';

                    updateConnectionStatus('connected');
                    updateBalance(acc.balance, acc.currency);
                    document.getElementById('accountLogin').innerHTML = acc.loginid;

                    // Badge e aviso
                    let badge = document.getElementById('accountBadge');
                    if(isReal) {
                        badge.textContent = 'REAL 🔴';
                        badge.className = 'trade-badge badge-real';
                        document.getElementById('warningBox').style.display = 'block';
                    } else {
                        badge.textContent = 'DEMO';
                        badge.className = 'trade-badge badge-demo';
                    }

                    addLog(`✅ Autorizado! Conta: ${acc.loginid} | Tipo: ${botState.accountType.toUpperCase()} | Saldo: ${acc.balance} ${acc.currency}`, 'success');

                    // Inscreve nos ticks
                    ws.send(JSON.stringify({ ticks: SYMBOL, subscribe: 1 }));
                    addLog(`📡 Inscrito em ticks: ${SYMBOL}`, 'info');

                    // Inscreve no saldo (atualização em tempo real)
                    ws.send(JSON.stringify({ balance: 1, subscribe: 1 }));

                    startHeartbeat();
                }

                // ── SALDO (atualização em tempo real) ────────────────
                if(data.msg_type === 'balance' && data.balance) {
                    updateBalance(data.balance.balance, data.balance.currency);
                }

                // ── TICKS ────────────────────────────────────────────
                if(data.msg_type === 'tick' && data.tick) {
                    let price = data.tick.quote;
                    let digit = getLastDigit(price);
                    document.getElementById('currentPrice').innerHTML = price.toFixed(2);

                    if(digit !== null) {
                        botState.tickHistory.push(digit);
                        if(botState.tickHistory.length > 25) botState.tickHistory.shift();
                        calculateFrequencies();

                        if(botState.running && botState.analysisStarted && !botState.inPosition) {
                            executeStrategy();
                        }
                    }
                }

                // ── COMPRA (BUY) — RESPOSTA DA ORDEM REAL ───────────
                if(data.msg_type === 'buy') {
                    if(data.error) {
                        addLog('❌ Erro na compra: ' + data.error.message, 'error');
                        // Libera posição para tentar novamente
                        botState.inPosition = false;
                        botState.entryTriggered = false;
                        return;
                    }

                    let buy = data.buy;
                    botState.currentContractId = buy.contract_id;

                    addLog(
                        `✅ [ORDEM REAL] Compra confirmada! ` +
                        `Contrato: ${buy.contract_id} | ` +
                        `Dígito: ${botState.currentTradeDigit} | ` +
                        `Pago: $${parseFloat(buy.buy_price).toFixed(2)}`,
                        'success'
                    );
                }

                // ── CONTRATO ABERTO / RESULTADO REAL ─────────────────
                if(data.msg_type === 'proposal_open_contract' && data.proposal_open_contract) {
                    let poc = data.proposal_open_contract;

                    // Só processa quando o contrato finalizou
                    if(!poc.is_sold) return;

                    let profit  = parseFloat(poc.profit);
                    let payout  = parseFloat(poc.payout || 0);
                    let isWin   = profit > 0;

                    botState.stats.trades++;
                    botState.stats.profit += profit;
                    if(isWin) botState.stats.wins++;

                    // Atualiza saldo real
                    if(poc.balance_after) {
                        updateBalance(poc.balance_after, botState.currency);
                    }

                    if(isWin) {
                        addLog(
                            `💰 [RESULTADO REAL] GANHOU! ` +
                            `Dígito ${poc.entry_tick_display_value ? poc.entry_tick_display_value.slice(-1) : '?'} → ` +
                            `Lucro: +$${profit.toFixed(2)} | ` +
                            `Saldo: ${botState.balance} ${botState.currency}`,
                            'success'
                        );
                        document.getElementById('lastResult').innerHTML = `✅ +$${profit.toFixed(2)}`;
                        document.getElementById('lastResult').style.color = '#4caf50';

                        // Reset após vitória
                        botState.inPosition       = false;
                        botState.currentContractId = null;
                        botState.targetDigit       = null;
                        botState.currentTradeDigit = null;
                        botState.entryTriggered    = false;
                        botState.waitingFor8pct    = false;
                        botState.stats.currentStake = botState.config.stake;
                        botState.stats.galeCount   = 0;

                        document.getElementById('predictionDigit').innerHTML = '-';
                        document.getElementById('predictionStatus').innerHTML = 'Aguardando...';
                        document.getElementById('targetInfo').style.display = 'none';

                        updateStats();

                        // Verifica Stop Win
                        if(botState.stats.profit >= botState.config.stopWin) {
                            addLog('🎉 STOP WIN ATINGIDO! Encerrando bot.', 'success');
                            stopBot(); return;
                        }

                        // Pausa 5s antes da próxima análise
                        addLog('⏱️ Pausa de 5s antes da próxima análise...', 'info');
                        botState.running = false;
                        setTimeout(() => {
                            if(botState.connected) {
                                botState.running = true;
                                addLog('🔍 Retomando análise...', 'info');
                            }
                        }, 5000);

                    } else {
                        // PERDEU — Aplica Martingale
                        addLog(
                            `❌ [RESULTADO REAL] PERDEU! ` +
                            `Prejuízo: $${Math.abs(profit).toFixed(2)} | ` +
                            `Saldo: ${botState.balance} ${botState.currency}`,
                            'error'
                        );
                        document.getElementById('lastResult').innerHTML = `❌ $${profit.toFixed(2)}`;
                        document.getElementById('lastResult').style.color = '#f44336';

                        // Verifica Stop Loss
                        if(botState.stats.profit <= -botState.config.stopLoss) {
                            addLog('🛑 STOP LOSS ATINGIDO! Encerrando bot.', 'error');
                            stopBot(); return;
                        }

                        // Aplica martingale e compra de novo
                        botState.stats.currentStake *= botState.config.gale;
                        botState.stats.galeCount++;
                        botState.inPosition  = false;
                        botState.entryTriggered = false;

                        updateStats();

                        addLog(
                            `📈 MARTINGALE #${botState.stats.galeCount} → ` +
                            `Nova stake: $${botState.stats.currentStake.toFixed(2)} ` +
                            `no dígito ${botState.currentTradeDigit}`,
                            'warning'
                        );

                        // Recompra imediata no mesmo dígito
                        setTimeout(() => {
                            if(botState.running && !botState.inPosition) {
                                placeBuyOrder(botState.currentTradeDigit, botState.stats.currentStake);
                            }
                        }, 200);
                    }
                }

                // ── PONG ─────────────────────────────────────────────
                if(data.msg_type === 'ping') {
                    ws.send(JSON.stringify({ pong: data.ping }));
                }
            };

            ws.onerror = () => addLog('⚠️ Erro no WebSocket.', 'error');

            ws.onclose = (e) => {
                botState.connected  = false;
                botState.authorized = false;
                updateConnectionStatus('disconnected');
                if(e.code !== 1000) {
                    addLog(`❌ Conexão fechada (${e.code}). Tentando reconectar...`, 'error');
                    handleReconnect();
                } else {
                    addLog('🔌 Conexão encerrada.', 'info');
                }
            };
        }

        function handleReconnect() {
            connectionAttempts++;
            if(connectionAttempts <= MAX_RECONNECT) {
                reconnectTimer = setTimeout(() => {
                    addLog(`🔄 Tentativa ${connectionAttempts}/${MAX_RECONNECT}...`, 'info');
                    establishConnection();
                }, 5000);
            } else {
                addLog('❌ Máximo de tentativas. Clique CONECTAR para tentar novamente.', 'error');
            }
        }

        function startHeartbeat() {
            if(heartbeatInterval) clearInterval(heartbeatInterval);
            heartbeatInterval = setInterval(() => {
                if(ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ ping: 1 }));
                }
            }, 25000);
        }

        // ============================================================
        // *** FUNÇÃO QUE ENVIA ORDEM REAL PARA A DERIV API ***
        // ============================================================
        function placeBuyOrder(digit, stake) {
            if(!ws || ws.readyState !== WebSocket.OPEN) {
                addLog('❌ WebSocket fechado. Não foi possível enviar ordem.', 'error');
                return;
            }

            botState.inPosition        = true;
            botState.currentTradeDigit = digit;
            botState.purchasePrice     = stake;

            // Monta o payload de compra real via API Deriv
            let buyPayload = {
                buy: 1,
                subscribe: 1,           // Monitora o contrato em tempo real
                price: stake,           // Valor máximo que aceita pagar
                parameters: {
                    amount:        stake,
                    basis:         'stake',
                    contract_type: 'DIGITMATCH',
                    currency:      botState.currency,
                    duration:      1,
                    duration_unit: 't',    // 't' = ticks
                    symbol:        SYMBOL,
                    prediction:    digit   // ← DÍGITO ALVO
                }
            };

            ws.send(JSON.stringify(buyPayload));

            addLog(
                `📤 [ORDEM ENVIADA] DIGITMATCH | ` +
                `Dígito: ${digit} | ` +
                `Stake: $${stake.toFixed(2)} | ` +
                `Conta: ${botState.accountType.toUpperCase()}`,
                'warning'
            );

            document.getElementById('predictionStatus').innerHTML =
                `⏳ Ordem enviada | Aguardando resultado...`;
        }

        // ============================================================
        // ESTRATÉGIA PRINCIPAL
        // ============================================================
        function executeStrategy() {
            // ── PASSO 1: Encontrar dígito com ~0% ────────────────────
            if(botState.targetDigit === null && !botState.waitingFor8pct) {
                let zeroDigit = null;
                for(let i = 1; i <= 9; i++) {
                    if(botState.frequencies[i] < 0.5) { zeroDigit = i; break; }
                }
                if(zeroDigit !== null) {
                    botState.targetDigit   = zeroDigit;
                    botState.waitingFor8pct = true;
                    botState.stats.galeCount = 0;

                    document.getElementById('predictionDigit').innerHTML = zeroDigit;
                    document.getElementById('predictionStatus').innerHTML =
                        `Aguardando 8% (atual: ${botState.frequencies[zeroDigit].toFixed(1)}%)`;
                    document.getElementById('targetInfo').style.display = 'block';
                    document.getElementById('targetInfo').innerHTML =
                        `🎯 Dígito ${zeroDigit} (0%) — Aguardando atingir 8%`;

                    addLog(`🎯 Dígito alvo encontrado: ${zeroDigit} (0%)`, 'warning');
                }
            }

            // ── PASSO 2: Aguardar 8% ─────────────────────────────────
            if(botState.targetDigit !== null && botState.waitingFor8pct && !botState.entryTriggered) {
                let cur = botState.frequencies[botState.targetDigit];
                document.getElementById('predictionStatus').innerHTML =
                    `Aguardando 8% (atual: ${cur.toFixed(1)}%)`;

                if(cur >= 8) {
                    botState.entryTriggered = true;
                    botState.waitingFor8pct = false;

                    addLog(
                        `📊 Dígito ${botState.targetDigit} atingiu ${cur.toFixed(1)}%! Enviando ordem real...`,
                        'warning'
                    );

                    // ─── ENVIA ORDEM REAL À DERIV ───
                    placeBuyOrder(botState.targetDigit, botState.stats.currentStake);
                }
            }
        }

        // ============================================================
        // INICIAR / PARAR BOT
        // ============================================================
        function startBot() {
            if(!botState.connected) { alert('Conecte-se à Deriv primeiro!'); return; }

            botState.running        = true;
            botState.analysisStarted = false;
            botState.config = {
                stake:    parseFloat(document.getElementById('stake').value),
                gale:     parseFloat(document.getElementById('gale').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                stopWin:  parseFloat(document.getElementById('stopWin').value)
            };
            botState.stats.currentStake = botState.config.stake;
            updateStats();

            document.getElementById('btnStart').disabled = true;
            document.getElementById('btnStop').disabled  = false;

            addLog('🚀 Bot iniciado. Coletando 25 ticks (20s) para análise...', 'warning');

            if(analysisTimer) clearTimeout(analysisTimer);
            analysisTimer = setTimeout(() => {
                botState.analysisStarted = true;
                addLog('🔍 Análise iniciada — Buscando dígito com 0%...', 'success');
                document.getElementById('predictionStatus').innerHTML = 'Analisando...';
            }, 20000);

            let t = 20;
            if(countdownInterval) clearInterval(countdownInterval);
            countdownInterval = setInterval(() => {
                document.getElementById('startCounter').innerHTML = t + 's';
                if(--t < 0) {
                    clearInterval(countdownInterval);
                    document.getElementById('startCounter').innerHTML = '✅';
                }
            }, 1000);
        }

        function stopBot() {
            botState.running         = false;
            botState.analysisStarted = false;
            botState.targetDigit     = null;
            botState.inPosition      = false;
            botState.waitingFor8pct  = false;
            botState.currentTradeDigit = null;
            botState.entryTriggered  = false;

            if(countdownInterval) clearInterval(countdownInterval);
            if(analysisTimer)     clearTimeout(analysisTimer);
            if(heartbeatInterval) clearInterval(heartbeatInterval);
            if(reconnectTimer)    clearTimeout(reconnectTimer);

            if(ws) { try { ws.close(1000, 'Bot parado'); } catch(e) {} ws = null; }

            document.getElementById('startCounter').innerHTML   = '20s';
            document.getElementById('predictionDigit').innerHTML = '-';
            document.getElementById('predictionStatus').innerHTML = 'Parado';
            document.getElementById('targetInfo').style.display  = 'none';
            document.getElementById('btnStart').disabled = false;
            document.getElementById('btnStop').disabled  = true;

            updateConnectionStatus('disconnected');
            addLog(`⏹️ Bot parado. Resultado da sessão: $${botState.stats.profit.toFixed(2)} | Trades: ${botState.stats.trades}`, 'error');
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

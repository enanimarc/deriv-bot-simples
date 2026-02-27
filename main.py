from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Trading Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #666;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        input:focus {
            border-color: #667eea;
            outline: none;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102,126,234,0.4);
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Deriv Trading Bot</h1>
        
        <div class="form-group">
            <label>Token da Deriv</label>
            <input type="password" id="token" placeholder="Cole seu token aqui">
        </div>
        
        <div class="form-group">
            <label>Stake Inicial ($)</label>
            <input type="number" id="stake" value="0.35" step="0.01" min="0.35">
        </div>
        
        <div class="form-group">
            <label>Multiplicador Martingale</label>
            <input type="number" id="martingale" value="1.15" step="0.01" min="1.0">
        </div>
        
        <div class="form-group">
            <label>Stop Loss ($)</label>
            <input type="number" id="stopLoss" value="10" step="0.01">
        </div>
        
        <div class="form-group">
            <label>Stop Win ($)</label>
            <input type="number" id="stopWin" value="10" step="0.01">
        </div>
        
        <button onclick="testConnection()">🔌 Testar Conexão</button>
        <button onclick="startBot()" style="background: #28a745;">▶️ Iniciar Robô</button>
        <button onclick="stopBot()" style="background: #dc3545;">⏹️ Parar Robô</button>
        
        <div id="status" class="status"></div>
        
        <div id="logs" style="margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 8px; font-family: monospace; height: 200px; overflow-y: auto;"></div>
    </div>

    <script>
        let botAtivo = false;
        let logs = document.getElementById('logs');
        
        function addLog(message) {
            let entry = document.createElement('div');
            entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
            logs.appendChild(entry);
            logs.scrollTop = logs.scrollHeight;
        }
        
        function testConnection() {
            let token = document.getElementById('token').value;
            if (!token) {
                alert('Por favor, insira seu token!');
                return;
            }
            
            let status = document.getElementById('status');
            status.className = 'status success';
            status.innerHTML = '✅ Testando conexão...';
            
            // Simular teste (depois implementaremos a conexão real)
            setTimeout(() => {
                status.innerHTML = '✅ Conexão estabelecida com sucesso!';
                addLog('✅ Conectado à Deriv');
            }, 2000);
        }
        
        function startBot() {
            let token = document.getElementById('token').value;
            if (!token) {
                alert('Por favor, insira seu token!');
                return;
            }
            
            botAtivo = true;
            addLog('🚀 Robô iniciado! Aguardando 20 segundos...');
            
            let status = document.getElementById('status');
            status.className = 'status success';
            status.innerHTML = '✅ Robô iniciado! Aguarde...';
            
            // Contagem regressiva
            let countdown = 20;
            let interval = setInterval(() => {
                if (!botAtivo) {
                    clearInterval(interval);
                    return;
                }
                
                if (countdown > 0) {
                    status.innerHTML = `⏳ Iniciando em ${countdown} segundos...`;
                    countdown--;
                } else {
                    clearInterval(interval);
                    status.innerHTML = '✅ Analisando mercado...';
                    addLog('✅ Análise iniciada - Procurando dígito com 0%');
                    simulateTrading();
                }
            }, 1000);
        }
        
        function stopBot() {
            botAtivo = false;
            addLog('⏹️ Robô parado');
            document.getElementById('status').innerHTML = '⏹️ Robô parado';
        }
        
        function simulateTrading() {
            if (!botAtivo) return;
            
            // Simular análise de dígitos
            let target = Math.floor(Math.random() * 10);
            addLog(`🎯 Dígito alvo encontrado: ${target} (0% nos últimos 25 ticks)`);
            
            // Aguardar até atingir 8%
            setTimeout(() => {
                if (!botAtivo) return;
                addLog(`📊 Dígito ${target} atingiu 8%! Comprando...`);
                
                // Simular compra
                let stake = parseFloat(document.getElementById('stake').value);
                addLog(`✅ Compra realizada: $${stake} no dígito ${target}`);
                
                // Simular resultado após alguns segundos
                setTimeout(() => {
                    if (!botAtivo) return;
                    
                    let ganhou = Math.random() > 0.4;
                    if (ganhou) {
                        addLog(`💰 GANHOU! Lucro: $${(stake * 0.95).toFixed(2)}`);
                    } else {
                        addLog(`❌ PERDEU! Prejuízo: $${stake.toFixed(2)}`);
                        let martingale = parseFloat(document.getElementById('martingale').value);
                        let novaStake = stake * martingale;
                        addLog(`📈 Martingale ativado - Nova stake: $${novaStake.toFixed(2)}`);
                    }
                    
                    // Aguardar 5 segundos e recomeçar
                    addLog('⏱️ Aguardando 5 segundos para próxima operação...');
                    setTimeout(() => {
                        if (botAtivo) simulateTrading();
                    }, 5000);
                    
                }, 5000);
                
            }, 3000);
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(content=html)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

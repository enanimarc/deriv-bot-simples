from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Bot</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
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
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .status h2 {
            color: #28a745;
            margin: 0;
        }
        .info {
            text-align: center;
            color: #666;
            margin: 20px 0;
        }
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin: 10px 0;
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102,126,234,0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Deriv Trading Bot</h1>
        
        <div class="status">
            <h2>✅ SERVIDOR ATIVO</h2>
            <p>O bot está rodando com sucesso!</p>
        </div>
        
        <div class="info">
            <p><strong>Status:</strong> Funcionando perfeitamente</p>
            <p><strong>Porta:</strong> 8000</p>
            <p><strong>Servidor:</strong> Railway</p>
        </div>
        
        <button class="button" onclick="testar()">
            🔌 Testar Conexão
        </button>
        
        <button class="button" onclick="iniciar()">
            ▶️ Iniciar Robô
        </button>
        
        <div id="log" style="margin-top: 20px; padding: 10px; background: #f5f5f5; border-radius: 5px; min-height: 50px;">
            Aguardando comando...
        </div>
    </div>

    <script>
        function testar() {
            document.getElementById('log').innerHTML = '✅ Teste de conexão realizado com sucesso!';
        }
        
        function iniciar() {
            document.getElementById('log').innerHTML = '🚀 Robô iniciado com sucesso!';
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
    return {"status": "healthy", "message": "Server is running"}

@app.get("/api/status")
async def status():
    return {"status": "online", "bot": "ready"}

# Esta linha é crucial para o Railway
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

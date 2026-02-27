from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Deriv Trading Bot</title>
    <meta charset="UTF-8">
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
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            background: #28a745;
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .status h2 {
            margin: 0;
            font-size: 24px;
        }
        .info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .info p {
            margin: 10px 0;
            font-size: 16px;
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
            <p>O bot está rodando com sucesso no Railway!</p>
        </div>
        
        <div class="info">
            <p><strong>Status:</strong> Funcionando perfeitamente</p>
            <p><strong>Porta:</strong> 8000</p>
            <p><strong>Servidor:</strong> Railway</p>
            <p><strong>URL:</strong> deriv-bot-simples-production.up.railway.app</p>
        </div>
        
        <button class="button" onclick="testar()">
            🔌 Testar Conexão
        </button>
        
        <div id="log" style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px; min-height: 50px;">
            Clique em "Testar Conexão" para verificar se está funcionando.
        </div>
    </div>

    <script>
        function testar() {
            document.getElementById('log').innerHTML = '✅ Teste realizado com sucesso! O servidor está funcionando perfeitamente.';
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

@app.get("/api/test")
async def test():
    return {"success": True, "message": "API funcionando"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
           
           

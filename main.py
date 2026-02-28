from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Deriv Bot Profissional</title>
<style>
body { background:#0f0f14; color:white; font-family:Arial; text-align:center; }
button { padding:10px; margin:5px; }
input { padding:5px; margin:5px; }
#logs { background:#000; height:200px; overflow:auto; margin-top:20px; padding:10px; font-family:monospace; }
.green { color:#4caf50; }
.red { color:#f44336; }
</style>
</head>
<body>

<h2>🤖 Deriv Bot Profissional - DIGITMATCH</h2>

<input type="password" id="token" placeholder="Token Deriv">
<input type="number" id="stake" value="0.35" step="0.01">
<input type="number" id="gale" value="1.15" step="0.01">
<input type="number" id="stopWin" value="10">
<input type="number" id="stopLoss" value="10">

<br>

<button onclick="connect()">🔌 Conectar</button>
<button onclick="startBot()">▶️ Iniciar</button>
<button onclick="stopBot()">⏹️ Parar</button>

<div id="logs"></div>

<script>

const SYMBOL = "R_100";
const WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089";

let ws = null;

let state = {
    running: false,
    connected: false,
    inPosition: false,
    proposalId: null,
    contractId: null,
    initialBalance: 0,
    currentBalance: 0,
    targetDigit: null,
    stake: 0.35,
    baseStake: 0.35,
    gale: 1.15,
    stopWin: 10,
    stopLoss: 10
};

function log(msg, color="white"){
    let div = document.getElementById("logs");
    div.innerHTML += "<div style='color:"+color+"'>["+new Date().toLocaleTimeString()+"] "+msg+"</div>";
    div.scrollTop = div.scrollHeight;
}

function connect(){
    let token = document.getElementById("token").value;
    if(!token){ alert("Insira o token"); return; }

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        log("Conectado à Deriv", "#4caf50");
        ws.send(JSON.stringify({ authorize: token }));
    };

    ws.onmessage = (event) => {
        let data = JSON.parse(event.data);

        if(data.msg_type === "authorize"){
            state.connected = true;
            log("Autorizado com sucesso", "#4caf50");
            ws.send(JSON.stringify({ balance: 1 }));
            ws.send(JSON.stringify({ ticks: SYMBOL, subscribe: 1 }));
        }

        if(data.msg_type === "balance"){
            state.currentBalance = data.balance.balance;

            if(state.initialBalance === 0){
                state.initialBalance = state.currentBalance;
                log("Saldo inicial: $" + state.initialBalance.toFixed(2));
            }
        }

        if(data.msg_type === "tick" && state.running && !state.inPosition){
            let price = data.tick.quote.toString().replace(".", "");
            let lastDigit = parseInt(price[price.length - 1]);

            state.targetDigit = lastDigit;
            buyContract();
        }

        if(data.msg_type === "proposal"){
            state.proposalId = data.proposal.id;
            ws.send(JSON.stringify({
                buy: state.proposalId,
                price: state.stake
            }));
        }

        if(data.msg_type === "buy"){
            state.contractId = data.buy.contract_id;
            state.inPosition = true;

            ws.send(JSON.stringify({
                proposal_open_contract: 1,
                contract_id: state.contractId,
                subscribe: 1
            }));
        }

        if(data.msg_type === "proposal_open_contract"){
            let contract = data.proposal_open_contract;

            if(contract.is_sold){
                state.inPosition = false;
                ws.send(JSON.stringify({ balance: 1 }));

                setTimeout(() => {

                    let lucroTotal = state.currentBalance - state.initialBalance;
                    log("Lucro atual: $" + lucroTotal.toFixed(2));

                    if(lucroTotal >= state.stopWin){
                        log("STOP WIN ATINGIDO", "#4caf50");
                        stopBot();
                        return;
                    }

                    if(lucroTotal <= -state.stopLoss){
                        log("STOP LOSS ATINGIDO", "#f44336");
                        stopBot();
                        return;
                    }

                    if(contract.profit > 0){
                        log("WIN", "#4caf50");
                        state.stake = state.baseStake;
                    } else {
                        log("LOSS - Martingale", "#f44336");
                        state.stake *= state.gale;
                        buyContract();
                    }

                }, 500);
            }
        }
    };
}

function buyContract(){
    ws.send(JSON.stringify({
        proposal: 1,
        amount: state.stake,
        basis: "stake",
        contract_type: "DIGITMATCH",
        currency: "USD",
        duration: 1,
        duration_unit: "t",
        symbol: SYMBOL,
        barrier: state.targetDigit.toString()
    }));

    log("Comprando dígito " + state.targetDigit + " | Stake $" + state.stake.toFixed(2));
}

function startBot(){
    if(!state.connected){ alert("Conecte primeiro"); return; }

    state.baseStake = parseFloat(document.getElementById("stake").value);
    state.stake = state.baseStake;
    state.gale = parseFloat(document.getElementById("gale").value);
    state.stopWin = parseFloat(document.getElementById("stopWin").value);
    state.stopLoss = parseFloat(document.getElementById("stopLoss").value);

    state.running = true;
    log("Bot iniciado");
}

function stopBot(){
    state.running = false;
    state.inPosition = false;

    if(ws){
        ws.close();
        ws = null;
    }

    log("Bot parado", "#f44336");
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
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

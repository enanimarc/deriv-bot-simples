import os
import json
import time
import websocket

# ================= CONFIGURAÇÕES =================

TOKEN = os.getenv("DERIV_TOKEN")  # Definir no Railway
SYMBOL = "R_100"
BASE_STAKE = 1
GALE_MULTIPLIER = 2
STOP_WIN = 20
STOP_LOSS = 20
CURRENCY = "USD"

# =================================================

initial_balance = 0
current_balance = 0
stake = BASE_STAKE
target_digit = None
in_position = False
running = True


def log(msg):
    print(f"[BOT] {msg}", flush=True)


def buy_contract(ws):
    global stake, target_digit

    log(f"Comprando DIGITMATCH | Dígito: {target_digit} | Stake: {stake}")

    ws.send(json.dumps({
        "proposal": 1,
        "amount": stake,
        "basis": "stake",
        "contract_type": "DIGITMATCH",
        "currency": CURRENCY,
        "duration": 1,
        "duration_unit": "t",
        "symbol": SYMBOL,
        "barrier": str(target_digit)
    }))


def on_open(ws):
    log("Conectado à Deriv")

    ws.send(json.dumps({
        "authorize": TOKEN
    }))

    ws.send(json.dumps({
        "ticks": SYMBOL,
        "subscribe": 1
    }))


def on_message(ws, message):
    global initial_balance, current_balance
    global stake, target_digit
    global in_position, running

    data = json.loads(message)

    if "error" in data:
        log(f"Erro: {data['error']['message']}")
        return

    msg_type = data.get("msg_type")

    # Autorização
    if msg_type == "authorize":
        log("Autorizado com sucesso")
        ws.send(json.dumps({"balance": 1}))

    # Saldo
    if msg_type == "balance":
        current_balance = data["balance"]["balance"]

        if initial_balance == 0:
            initial_balance = current_balance
            log(f"Saldo inicial: {initial_balance}")

    # Recebendo tick
    if msg_type == "tick" and running:
        if not in_position:
            last_digit = int(str(data["tick"]["quote"])[-1])
            target_digit = last_digit
            buy_contract(ws)

    # Proposta recebida
    if msg_type == "proposal":
        ws.send(json.dumps({
            "buy": data["proposal"]["id"],
            "price": stake
        }))

    # Compra confirmada
    if msg_type == "buy":
        in_position = True

        ws.send(json.dumps({
            "proposal_open_contract": 1,
            "contract_id": data["buy"]["contract_id"],
            "subscribe": 1
        }))

    # Resultado contrato
    if msg_type == "proposal_open_contract":

        contract = data["proposal_open_contract"]

        if contract["is_sold"]:

            in_position = False
            ws.send(json.dumps({"balance": 1}))
            time.sleep(1)

            lucro_total = current_balance - initial_balance
            log(f"Lucro total atual: {lucro_total}")

            # STOP WIN
            if lucro_total >= STOP_WIN:
                log("STOP WIN ATINGIDO - BOT ENCERRADO")
                running = False
                ws.close()
                return

            # STOP LOSS
            if lucro_total <= -STOP_LOSS:
                log("STOP LOSS ATINGIDO - BOT ENCERRADO")
                running = False
                ws.close()
                return

            # WIN
            if contract["profit"] > 0:
                log("WIN")
                stake = BASE_STAKE

            # LOSS
            else:
                log("LOSS - Aplicando Martingale")
                stake *= GALE_MULTIPLIER
                buy_contract(ws)


def on_error(ws, error):
    log(f"Erro conexão: {error}")


def on_close(ws, close_status_code, close_msg):
    log("Conexão encerrada")


# ================= EXECUÇÃO =================

if not TOKEN:
    raise Exception("Defina DERIV_TOKEN nas variáveis do Railway")

log("Iniciando BOT profissional 24h...")

ws = websocket.WebSocketApp(
    "wss://ws.derivws.com/websockets/v3?app_id=1089",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()

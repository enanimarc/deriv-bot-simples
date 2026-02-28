// ============================================
// ESTRATÉGIA PRINCIPAL - CORRIGIDA (OPÇÃO B)
// ============================================
function executeStrategy(lastDigit) {
    // PASSO 1: Encontrar dígito com 0% (apenas 1-9)
    if(botState.targetDigit === null && !botState.inPosition && !botState.waitingCompletion) {
        
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
            document.getElementById('targetInfo').innerHTML = `🎯 Dígito alvo: ${zeroDigit} (0%) - Aguardando 8%`;
            
            addLog(`🎯 Dígito alvo: ${zeroDigit} (0%)`, 'warning');
        }
    }
    
    // PASSO 2: Aguardar atingir 8%
    if(botState.targetDigit !== null && !botState.inPosition && !botState.entryTriggered) {
        let currentPercent = botState.frequencies[botState.targetDigit];
        document.getElementById('predictionStatus').innerHTML = `Aguardando 8% (atual: ${currentPercent.toFixed(1)}%)`;
        document.getElementById('targetInfo').innerHTML = `📊 Dígito ${botState.targetDigit}: ${currentPercent.toFixed(1)}% - Aguardando 8%`;
        
        if(currentPercent >= 8) {
            botState.entryTriggered = true;
            
            document.getElementById('predictionStatus').innerHTML = `📊 Atingiu 8%! Comprando...`;
            document.getElementById('targetInfo').innerHTML = `📊 Dígito ${botState.targetDigit} atingiu ${currentPercent.toFixed(1)}%! Comprando...`;
            
            addLog(`📊 Dígito ${botState.targetDigit} atingiu ${currentPercent.toFixed(1)}%! Comprando...`, 'warning');
            
            // PASSO 3: Comprar no próximo tick
            setTimeout(() => {
                if(!botState.running) return;
                
                botState.inPosition = true;
                botState.currentTradeDigit = botState.targetDigit;
                botState.purchasePrice = botState.stats.currentStake;
                botState.galeAttempts = 0;
                
                addLog(`✅ COMPRA: $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.targetDigit}`, 'success');
                
            }, 100);
        }
    }
    
    // PASSO 4: Se está em posição, verificar resultado TICK A TICK
    if(botState.inPosition && botState.currentTradeDigit !== null) {
        
        if(lastDigit === botState.currentTradeDigit) {
            // GANHOU! Dígito alvo apareceu
            let profit = botState.purchasePrice * 0.95;
            botState.stats.profit += profit;
            botState.stats.trades++;
            botState.stats.wins++;
            
            addLog(`💰 VENDA! Dígito ${lastDigit} saiu! Lucro: $${profit.toFixed(2)}`, 'success');
            
            // Reset após vitória
            botState.inPosition = false;
            botState.targetDigit = null;
            botState.currentTradeDigit = null;
            botState.entryTriggered = false;
            botState.stats.currentStake = botState.config.stake; // Volta à stake inicial
            botState.stats.galeCount = 0;
            
            document.getElementById('predictionDigit').innerHTML = '-';
            document.getElementById('predictionStatus').innerHTML = 'Aguardando...';
            document.getElementById('targetInfo').style.display = 'none';
            
            updateStats();
            
            // Verificar STOP WIN
            if(botState.stats.profit >= botState.config.stopWin) {
                addLog('🎉 PARABÉNS! STOP WIN ATINGIDO!', 'success');
                stopBot();
                return;
            }
            
            // PASSO 5: Aguardar 5 segundos para nova análise
            addLog('⏱️ Aguardando 5 segundos para nova análise...', 'info');
            botState.waitingCompletion = true;
            
            setTimeout(() => {
                botState.waitingCompletion = false;
                addLog('✅ Pronto para nova análise', 'success');
            }, 5000);
            
        } else {
            // PERDEU! Dígito alvo NÃO apareceu neste tick
            
            // Calcular prejuízo da compra atual
            let loss = -botState.purchasePrice;
            botState.stats.profit += loss;
            botState.stats.trades++;
            
            addLog(`❌ PERDEU! Dígito ${lastDigit} não saiu (alvo era ${botState.currentTradeDigit}) - Prejuízo: $${Math.abs(loss).toFixed(2)}`, 'error');
            
            // Verificar STOP LOSS
            if(botState.stats.profit <= -botState.config.stopLoss) {
                addLog('🛑 STOP LOSS ATINGIDO!', 'error');
                stopBot();
                return;
            }
            
            // APLICAR MARTINGALE: aumentar stake para a próxima tentativa
            botState.stats.currentStake *= botState.config.gale;
            botState.stats.galeCount++;
            
            addLog(`📈 MARTINGALE ${botState.stats.galeCount}: Nova stake $${botState.stats.currentStake.toFixed(2)} para o mesmo dígito ${botState.currentTradeDigit}`, 'warning');
            
            // Reset para nova compra no MESMO DÍGITO (sem aguardar)
            botState.inPosition = false;
            botState.entryTriggered = false;
            
            // Já agendar a PRÓXIMA COMPRA para o próximo tick
            setTimeout(() => {
                if(!botState.running || botState.inPosition) return;
                
                botState.inPosition = true;
                botState.purchasePrice = botState.stats.currentStake;
                
                addLog(`✅ NOVA COMPRA (GALE ${botState.stats.galeCount}): $${botState.stats.currentStake.toFixed(2)} no dígito ${botState.currentTradeDigit}`, 'success');
                
            }, 100); // Próximo tick
            
            updateStats();
        }
    }
}

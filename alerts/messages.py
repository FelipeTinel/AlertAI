class AlertMessage:
    _CONFIGS = {
        "normal": {
            "emoji": "⚪",
            "titulo": "SITUAÇÃO NORMAL: FLUXO HABITUAL",
            "condicao": "Chuva fraca ou ausente | Sem impactos",
            "acao": "O sistema semafórico opera normalmente. Tenha uma boa viagem!"
        },
        "moderado": {
            "emoji": "🟢",
            "titulo": "Aviso de Chuva: Trânsito Monitorado",
            "condicao": "Chuva Moderada (25-50 mm/h)",
            "acao": "Para ajudar no deslocamento, aumentamos em +20s o sinal verde nos pontos mais movimentados. Dirija com atenção e mantenha uma distância segura!"
        },
        "forte": {
            "emoji": "🟡",
            "titulo": "ATENÇÃO: ALTERAÇÃO EM ROTAS DE ESCAPE",
            "condicao": "Chuva Forte (50-100 mm/h) | Risco de Retenção",
            "acao": "Adicionados +40s de sinal verde e rotas de escape ativadas. Evite trechos alagados e planeje seu trajeto com antecedência."
        },
        "extremo": {
            "emoji": "🔴",
            "titulo": "ALERTA MÁXIMO: CONTROLE DE EMERGÊNCIA",
            "condicao": "Chuva Extrema (>100 mm/h) | Alto Risco de Alagamento",
            "acao": "Operação de escoamento máximo ativada. Rotas de risco foram BLOQUEADAS. Se puder, permaneça em local seguro e evite deslocamentos pela região."
        }
    }

    @classmethod
    def emitir(cls, nivel, periodo):
        # Busca a config
        config = cls._CONFIGS.get(nivel.lower())
        
        if not config:
            return "Nível de alerta inválido."

        return (
            f"{config['emoji']} *{config['titulo']}*\n\n"
            f"⏰ *Período:* {periodo}\n"
            f"{'🚨' if nivel == 'critico' else '⛈️'} *Condição:* {config['condicao']}\n\n"
            f"🚦 *Ação do Sistema:* {config['acao']}"
        )
    
# if __name__ == "__main__":
#     print(AlertMessage.emitir("moderado", "14:00 - 16:00"))
#     print(AlertMessage.emitir("alto", "16:00 - 18:00"))
#     print(AlertMessage.emitir("critico", "18:00 - 20:00"))
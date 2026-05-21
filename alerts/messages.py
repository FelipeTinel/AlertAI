class AlertMessage:
    _CONFIGS = {
        "normal": {
            "emoji": "⚪",
            "titulo": "TRÂNSITO NORMAL",
            "condicao": "Até 25 mm/h",
            "acao": "Sem alterações no trânsito."
        },

        "moderado": {
            "emoji": "🟢",
            "titulo": "CHUVA MODERADA",
            "condicao": "25–50 mm/h",
            "acao": "+20s no verde em vias principais. Dirija com atenção."
        },

        "forte": {
            "emoji": "🟡",
            "titulo": "CHUVA FORTE",
            "condicao": "50–100 mm/h",
            "acao": "+40s no verde e rotas de escape ativadas."
        },

        "extremo": {
            "emoji": "🔴",
            "titulo": "ALERTA MÁXIMO",
            "condicao": "Acima de 100 mm/h",
            "acao": "Fluxo emergencial ativo. Evite áreas de risco."
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
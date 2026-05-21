# Modelos de mensagens predefinidas

class AlertMessage:

    @staticmethod
    def _moderado(local, periodo):
        return (
            f"🟡 *ATENÇÃO: CHUVA PREVISTA*\n\n"
            f"📍 *Local:* {local}\n"
            f"⏰ *Período:* {periodo}\n"
            f"💧 *Intensidade:* Moderada\n\n"
            f"Aviso: Redobre a atenção no trânsito e evite áreas com histórico de alagamento."0
        )

    @staticmethod
    def _alto(local, periodo):
        return (
            f"🟠 *ALERTA: RISCO DE ALAGAMENTO*\n\n"
            f"📍 *Localidade:* {local}\n"
            f"⛈️ *Intensidade:* Alta\n"
            f"⏰ *Previsão:* {periodo}\n\n"
            f"⚠️ *Segurança:* Não atravesse ruas alagadas e evite estacionar sob árvores."
        )

    @staticmethod
    def _critico(local, periodo):
        return (
            f"🔴 *EMERGÊNCIA: RISCO DE DESLIZAMENTO*\n\n"
            f"📍 *ÁREA AFETADA:* {local}\n"
            f"🚨 *Nível de Perigo:* Máximo\n\n"
            f"📢 *INSTRUÇÕES:* Moradores de encostas devem sair imediatamente ao notar rachaduras. "
            f"Ligue 199 (CODESAL)."
        )

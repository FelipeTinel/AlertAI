# Código que dispara mensagem de alerta para o contato em questão
import os
from twilio.rest import Client
from dotenv import load_dotenv
from alerts.messages import AlertMessage

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
FROM        = os.getenv("TWILIO_FROM")
TO          = os.getenv("TWILIO_TO")

def send_alert(level: str, date: str = 'date not defined'):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    mensagem = AlertMessage.send_alert(level, date)

    message = client.messages.create(
        from_=FROM,
        body=mensagem,
        to=TO
    )
    print(f"  Alerta enviado [{level.upper()}]: {mensagem}")
    return message

# send_alert("moderado", "22/05/2026")
# Código que dispara o modelo treinado para o contato em questão
from twilio.rest import Client
from alerts.messages import AlertMessage

account_sid = 'AccountSID'
auth_token = 'AuthToken'

client = Client(account_sid, auth_token)

nivel_alerta = AlertMessage.moderado("Alagoinhe", "Hoje à tarde")

def send_alert():
  message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=' Vai chover ai viu painho\n'+ nivel_alerta,
    to='whatsapp:+557182372739'
  )
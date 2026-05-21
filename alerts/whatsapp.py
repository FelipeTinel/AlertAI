# Código que dispara o modelo treinado para o contato em questão
from twilio.rest import Client
from alerts.messages import AlertMessage

account_sid = 'Acc'
auth_token = 'AuthToken'

client = Client(account_sid, auth_token)

niveis = ["normal", "moderado", "forte", "extremo"]

for i in range(4):
  nivel_alerta = AlertMessage.emitir(niveis[i], "16:00 - 18:00")  

  message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=' Nem te conto dog...\n'+ nivel_alerta,
    to='whatsapp:+557182372739'
    )

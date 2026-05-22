import pandas as pd
import os
from model.predict import generate_csv_for_date
from pipeline.risk_engine import risk_calculate
from alerts.whatsapp import send_alert
from traffic.simulator import simulate

def run_pipeline(date_str: str):
    print('Generating predictions...')
    output_path, df = generate_csv_for_date(date_str)

    print('Calculating risk...')
    df = df.rename(columns={'Previsao_Precipitacao_mm': 'precipitacao'})
    risks = risk_calculate(df)

    LEVEL = ['fraco', 'moderado', 'forte', 'extremo']
    
    print('Sending alerts...')

    try:
        for _, risk in risks.iterrows():
            if LEVEL.index(risk['nivel']) >= LEVEL.index('moderado'):
                send_alert(risk['nivel'], date_str)
    except Exception as e:
        print(f"[AVISO] Não foi possível enviar o WhatsApp: {e}")
        print("[INFO] Certifique-se de configurar as credenciais do Twilio no arquivo .env")


    print('Running traffic_light simulation:')

    pior_nivel = max(risks['nivel'], key=lambda x: LEVEL.index(x))
    simulate(pior_nivel)
    
    print('Finished.')

if __name__ == '__main__':
    data = input('Digite uma data (ex: 2025-05-22):')
    run_pipeline('2025-05-22')

import pandas as pd
import os
import model
from pipeline.risk_engine import risk_calculate
from alerts.whatsapp import send_alert


def run_pipeline():

    print('Loading data...')
    
    DATA = [f for f in os.listdir('data') if f.endwith('.csv')][0]
    df = pd.read_csv(DATA)

    print('Generating predictions...')
    predicts = model.predict(df)

    print('Calculating risk...')
    risks = risk_calculate(predicts)

    print ('Send alerts...')
    for risk in risks:
            if risk['nivel'] >= 'moderado':
                send_alert(risk['nivel'])

    print ('Saving outputs...')
    df['predicts'] = predicts
    df.to_csv('outputs/results.csv', index=False)

    print ('Finished.')
                
if __name__ == '__main__':
     run_pipeline()

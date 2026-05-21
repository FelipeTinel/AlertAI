# Decide o nível de alerta

# pipeline/risk_engine.py

def storm_classification(precipitacao_mm: float) -> dict:
    """
    Classifica a força da chuva com base na precipitação em mm.
    
    Escala baseada no INMET:
    - Fraca:    < 5mm
    - Moderada: 5mm a 25mm
    - Forte:    25mm a 50mm
    - Muito Forte: 50mm a 100mm
    - Extrema:  > 100mm
    """
    if precipitacao_mm > 100:
        nivel = 'extremo'

    elif precipitacao_mm > 50:
        nivel = 'forte'

    elif precipitacao_mm > 25:
        nivel = 'moderado'

    else:
        nivel = 'fraco'
        

    return {
        "precipitacao_mm": precipitacao_mm,
        "nivel": nivel,
        "alerta": nivel in ('extremo', 'forte', 'moderado', 'fraco')
    }


def risk_calculate(df):
    
    df = df.copy()

    resultados = df['precipitacao'].apply(storm_classification)
    df['nivel']   = resultados.apply(lambda x: x['nivel'])
    df['alerta']  = resultados.apply(lambda x: x['alerta'])

    return df
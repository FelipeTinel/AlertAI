"""Rotinas de predição para precipitação na Estação A401.

Este módulo carrega os artefatos gerados por `model/train.py` e expõe a
função `predict_precipitation_A401` que aceita um DataFrame com as colunas
originais do dataset e retorna a precipitação prevista em mm.
"""

import os
import json
import pandas as pd
import numpy as np
import joblib


def load_artifacts(artifacts_dir="model/artifacts"):
    features_path = os.path.join(artifacts_dir, "features.json")
    mean_path = os.path.join(artifacts_dir, "mean_features.json")
    template_path = os.path.join(artifacts_dir, "template_columns.json")
    clf_path = os.path.join(artifacts_dir, "clf_A401.joblib")
    reg_path = os.path.join(artifacts_dir, "reg_A401.joblib")

    with open(features_path, 'r', encoding='utf-8') as f:
        features = json.load(f)
    with open(mean_path, 'r', encoding='utf-8') as f:
        mean_features = json.load(f)
    with open(template_path, 'r', encoding='utf-8') as f:
        template_columns = json.load(f)

    clf = joblib.load(clf_path)
    reg = None
    if os.path.exists(reg_path):
        try:
            reg = joblib.load(reg_path)
        except Exception:
            reg = None

    return {
        'features': features,
        'mean_features': mean_features,
        'template_columns': template_columns,
        'clf': clf,
        'reg': reg
    }


def _preprocess_input(df_input, features):
    # Aplicar transformações compatíveis com o treino
    df = df_input.copy()
    columns_to_drop = [
        "PRESSAO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)",
        "PRESSAO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)",
        "TEMPERATURA DO AR - BULBO SECO, HORARIA (C)",
        "TEMPERATURA MAXIMA NA HORA ANT. (AUT) (C)",
        "TEMPERATURA MINIMA NA HORA ANT. (AUT) (C)",
        "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (C)",
        "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (C)",
        "UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)",
        "UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)",
        "VENTO, DIRECAO HORARIA (gr)",
        "VENTO, RAJADA MAXIMA (m/s)",
        "VENTO, VELOCIDADE HORARIA (m/s)",
        "ESTACAO",
        "DATA (YYYY-MM-DD)"
    ]

    df = df.drop(columns=columns_to_drop, errors='ignore')
    df['HORA'] = df['HORA (UTC)'] / 100
    df['HORA'] = pd.to_numeric(df['HORA'], errors='coerce')
    df['sin_hour'] = np.sin(2 * np.pi * df['HORA'].values / 24)
    df['cos_hour'] = np.cos(2 * np.pi * df['HORA'].values / 24)
    df = df.drop(columns=["HORA (UTC)", "HORA"], errors='ignore')

    # Remover colunas completamente NaN
    df = df.dropna(axis=1)

    # Garantir ordem e presença das features esperadas
    df = df.reindex(columns=features, fill_value=0)
    return df


def predict_precipitation_A401(new_data_df, artifacts):
    features = artifacts['features']
    clf = artifacts['clf']
    reg = artifacts['reg']

    processed = _preprocess_input(new_data_df, features)

    # Classificação
    rain_pred = clf.predict(processed)
    if rain_pred[0] == 1:
        if reg is None:
            # Regressor não disponível: retornar 0 e avisar
            return 0.0
        amt = reg.predict(processed)
        return float(amt[0])
    else:
        return 0.0


def generate_day_predictions(date_str, artifacts, output_path=None):
    """Gera previsões horárias para uma data inteira (0-23h) e salva um CSV.

    Args:
        date_str (str): Data no formato YYYY-MM-DD.
        artifacts (dict): Artefatos retornados por `load_artifacts()`.
        output_path (str|None): Caminho do CSV de saída. Se None, usa
            `predicoes_{date_str}.csv` no diretório atual.

    Returns:
        pd.DataFrame: DataFrame contendo as colunas originais e a coluna
        `Previsao_Precipitacao_mm` com as previsões por hora.
    """
    template_cols = artifacts['template_columns']
    mean_feats = artifacts['mean_features']
    features = artifacts['features']
    clf = artifacts['clf']
    reg = artifacts['reg']

    rows = []
    for hour in range(24):
        row = {col: pd.NA for col in template_cols}
        row['ESTACAO'] = 'A401'
        row['PRECIPITACAO TOTAL HORARIO (mm)'] = 0.0
        # preencher médias das features conhecidas
        for k, v in mean_feats.items():
            row[k] = v
        row['DATA (YYYY-MM-DD)'] = date_str
        row['HORA (UTC)'] = int(hour) * 100
        rows.append(row)

    df_all = pd.DataFrame(rows, columns=template_cols)

    # Adicionar coluna de hora legível (0-23)
    # 'HORA (UTC)' está no formato 0,100,200,... então dividimos por 100
    utc_hour = (df_all['HORA (UTC)'] / 100).astype(int)
    # Converter para horário de Brasília (UTC-3)
    df_all['HORA'] = ((utc_hour - 3) % 24).astype(int)

    # Preprocessar para o formato das features
    processed = _preprocess_input(df_all, features)

    # Prever chuva (classificação)
    rain_pred = clf.predict(processed)

    # Preencher previsões de quantidade com 0 e ajustar onde há chuva prevista
    preds = np.zeros(len(df_all), dtype=float)
    if reg is not None:
        rain_indices = np.where(rain_pred == 1)[0]
        if len(rain_indices) > 0:
            preds[rain_indices] = reg.predict(processed.iloc[rain_indices])

    df_all['Previsao_Precipitacao_mm'] = preds

    # Reordenar/selecionar colunas para saída mais legível
    out_cols = ['DATA (YYYY-MM-DD)', 'HORA', 'HORA (UTC)'] + [c for c in template_cols if c not in ('DATA (YYYY-MM-DD)', 'HORA (UTC)')] + ['Previsao_Precipitacao_mm']
    out_cols = [c for c in out_cols if c in df_all.columns]
    df_out = df_all[out_cols]

    if output_path is None:
        output_path = f'output/predicoes_{date_str}.csv'

    df_out.to_csv(output_path, index=False)
    return df_out


def generate_csv_for_date(date_str, artifacts_dir="model/artifacts", output_path=None):
    """Wrapper conveniente: carrega artefatos e gera o CSV para a data.

    Args:
        date_str (str): Data no formato YYYY-MM-DD.
        artifacts_dir (str): Diretório onde os artefatos foram salvos.
        output_path (str|None): Caminho do CSV de saída. Se None, usa
            `predicoes_{date_str}.csv` no diretório atual.

    Returns:
        tuple: (output_path, pd.DataFrame) onde `output_path` é o caminho
               do CSV salvo e `DataFrame` contém as previsões.
    """
    artifacts = load_artifacts(artifacts_dir)
    df = generate_day_predictions(date_str, artifacts, output_path=output_path)
    if output_path is None:
        output_path = f'predicoes_{date_str}.csv'
    return output_path, df


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Gerar CSV de previsões horárias (Estação A401)')
    parser.add_argument('date', nargs='?', help='Data no formato YYYY-MM-DD')
    parser.add_argument('-o', '--output', help='Caminho do CSV de saída (opcional)', default=None)
    parser.add_argument('-a', '--artifacts', help='Diretório dos artefatos (padrão: model/artifacts)', default='model/artifacts')
    args = parser.parse_args()

    if args.date:
        out_path, df_day = generate_csv_for_date(args.date, artifacts_dir=args.artifacts, output_path=args.output)
        print(f"CSV de previsões salvo em: {out_path}")
        print(df_day[['DATA (YYYY-MM-DD)','HORA','Previsao_Precipitacao_mm']])
    else:
        # fallback interativo
        artifacts = load_artifacts()
        input_date_str = input("Por favor, insira a data para previsão (YYYY-MM-DD): ")
        output_file = input("Nome do CSV de saída (enter para padrão): ")
        if output_file.strip() == '':
            output_file = None
        df_day = generate_day_predictions(input_date_str, artifacts, output_path=output_file)
        print(f"CSV de previsões salvo em: {output_file or f'predicoes_{input_date_str}.csv'}")
        print(df_day[['DATA (YYYY-MM-DD)','HORA','Previsao_Precipitacao_mm']])


# from model.predict import generate_csv_for_date
# path, df = generate_csv_for_date('2025-05-22')  
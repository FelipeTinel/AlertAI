"""Treino de modelos para previsão de precipitação (Estação A401).

Este módulo agora contém as rotinas de carregamento, pré-processamento,
treino e persistência dos artefatos (modelos e metadados) usados pelo
`model/predict.py` para realizar previsões.
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, mean_absolute_error, r2_score
import joblib


def load_data(csv_path="model/clima_bahia_hackathon.csv"):
    dados = pd.read_csv(csv_path)
    # Preencher NaNs de precipitação com 0
    dados.loc[dados["PRECIPITACAO TOTAL HORARIO (mm)"].isnull(), "PRECIPITACAO TOTAL HORARIO (mm)"] = 0
    return dados


def preprocess_A401(dados):
    dados_A401 = dados[dados["ESTACAO"] == "A401"].copy()

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

    df = dados_A401.drop(columns=columns_to_drop, errors='ignore')

    # Converter HORA (UTC) para 0-23
    df['HORA'] = df['HORA (UTC)'] / 100
    df['sin_hour'] = np.sin(2 * np.pi * df['HORA'] / 24)
    df['cos_hour'] = np.cos(2 * np.pi * df['HORA'] / 24)
    df = df.drop(columns=["HORA (UTC)", "HORA"], errors='ignore')

    # Remover linhas com NaNs
    df = df.dropna(axis=0)

    X = df.drop("PRECIPITACAO TOTAL HORARIO (mm)", axis=1)
    y = df["PRECIPITACAO TOTAL HORARIO (mm)"]
    return X, y, dados_A401


def train_and_save(csv_path="clima_bahia_hackathon.csv", artifacts_dir="model/artifacts"):
    os.makedirs(artifacts_dir, exist_ok=True)

    dados = load_data(csv_path)
    X_A401, y_A401, dados_A401 = preprocess_A401(dados)

    # Classificação (se chove ou não)
    y_class = (y_A401 > 0).astype(int)
    X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(X_A401, y_class, test_size=0.33, random_state=42)

    clf = RandomForestClassifier(random_state=42, n_estimators=100, max_depth=10, min_samples_split=5, class_weight='balanced')
    clf.fit(X_train_clf, y_train_clf)

    # Avaliação simples da classificação
    y_pred_clf = clf.predict(X_test_clf)
    print("--- Avaliação do Modelo de Classificação para Estação A401 ---")
    print(f"Acurácia: {accuracy_score(y_test_clf, y_pred_clf):.4f}")
    print(f"F1-Score: {f1_score(y_test_clf, y_pred_clf):.4f}")

    # Regressão apenas para instâncias com precipitação > 0
    X_reg = X_A401[y_A401 > 0]
    y_reg = y_A401[y_A401 > 0]

    reg = None
    if len(y_reg) > 0:
        test_size_reg = 0.33 if len(y_reg) * 0.33 >= 1 else 0.5
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=test_size_reg, random_state=42)
        reg = RandomForestRegressor(random_state=42, n_estimators=100, max_depth=10, min_samples_split=5)
        reg.fit(X_train_reg, y_train_reg)
        y_pred_reg = reg.predict(X_test_reg)
        print("--- Avaliação do Modelo de Regressão para Estação A401 ---")
        print(f"MAE: {mean_absolute_error(y_test_reg, y_pred_reg):.4f}")
        print(f"R2: {r2_score(y_test_reg, y_pred_reg):.4f}")
    else:
        print("Nenhuma amostra com precipitação não-zero para treinar o regressor.")

    # Persistir artefatos
    clf_path = os.path.join(artifacts_dir, "clf_A401.joblib")
    joblib.dump(clf, clf_path)

    reg_path = None
    if reg is not None:
        reg_path = os.path.join(artifacts_dir, "reg_A401.joblib")
        joblib.dump(reg, reg_path)

    # Salvar lista de features (ordem esperada pelo modelo)
    features = X_A401.columns.tolist()
    features_path = os.path.join(artifacts_dir, "features.json")
    with open(features_path, 'w', encoding='utf-8') as f:
        json.dump(features, f, ensure_ascii=False)

    # Salvar média das features e colunas originais para facilitar inputs de exemplo
    mean_features = X_A401.mean().to_dict()
    mean_path = os.path.join(artifacts_dir, "mean_features.json")
    with open(mean_path, 'w', encoding='utf-8') as f:
        json.dump(mean_features, f, ensure_ascii=False)

    template_columns = dados_A401.columns.tolist()
    template_path = os.path.join(artifacts_dir, "template_columns.json")
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template_columns, f, ensure_ascii=False)

    print(f"Modelos e metadados salvos em: {artifacts_dir}")
    return {
        'clf_path': clf_path,
        'reg_path': reg_path,
        'features_path': features_path,
        'mean_path': mean_path,
        'template_path': template_path
    }


if __name__ == '__main__':
    artifacts = train_and_save()
    print(artifacts)
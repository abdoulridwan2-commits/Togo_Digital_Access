#!/usr/bin/env bash
# Exécute tout le pipeline de données dans l'ordre, puis lance le dashboard.
set -e
cd "$(dirname "$0")"
echo "1/5  Vérification des données brutes..."
python src/check_data.py
echo "2/5  Nettoyage des données..."
python src/clean_data.py
echo "3/5  Analyse géospatiale (jointures + population WorldPop)..."
python src/analyze_data.py
echo "4/5  Calcul du score de priorité..."
python src/score_priorite.py
echo "5/5  Lancement du dashboard Streamlit..."
streamlit run app/main.py

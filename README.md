# Togo Digital Access 🇹🇬

## Dashboard d'analyse de l'accès aux services numériques au Togo

Projet réalisé dans le cadre du **Togo AI Lab Data Challenge – Économie numérique | Défi 1**.

L'objectif est d'analyser la répartition des infrastructures et services numériques au Togo afin d'identifier les territoires où les besoins en connectivité et en accès aux services sont prioritaires.

## 📊 Analyses réalisées

Le projet permet d'analyser :

- les agences Moov, Togocom, Télécom et CANAL+ ;
- les datacenters ;
- les agents Mobile Money ;
- la densité de population par préfecture ;
- les antennes mobiles recensées par OpenCelliD ;
- la répartition des infrastructures et services numériques ;
- les zones prioritaires pour améliorer l'accès numérique.

Le dashboard propose également une **cartographie interactive** et un **score de priorité par préfecture**. La carte permet d'activer les couches des agences Moov et Togocom, des datacenters, des antennes OpenCelliD et du Mobile Money par préfecture, avec filtres, tableau détaillé et export CSV.

## 🎯 Réponse aux critères d'évaluation

Le livrable est conçu pour couvrir les critères du challenge :

- **C1 — Ergonomie et navigation :** cinq onglets distincts, synthèse exécutive visible dès l'ouverture, KPI nationaux, titres explicites et lecture méthodologique accessible.
- **C2 — Analyses et conclusions :** indicateurs calculés à l'échelle des 37 préfectures, score reproductible, classement, diagnostic individuel et recommandations territoriales.
- **C3 — Interactions :** filtres par priorité, préfecture et indicateur, filtres dédiés à la carte, tableau associé, recherche/téléchargement CSV et diagnostic à la préfecture.
- **C4 — Rapport et méthodologie :** pipeline documenté, sources explicitées, limites signalées, rapport PowerPoint de 10 diapositives et résultats clés vérifiables.

Le dashboard distingue volontairement **observation**, **interprétation** et **recommandation** : le score aide à présélectionner les territoires, mais ne remplace pas une mesure officielle de couverture ni une validation terrain.

## 🗂️ Données utilisées

Les analyses reposent sur plusieurs sources de données :

- agences Moov ;
- agences Togocom ;
- agences Télécom ;
- agences CANAL+ ;
- datacenters ;
- agents Mobile Money ;
- limites administratives des préfectures ;
- population WorldPop 2020 ;
- antennes mobiles OpenCelliD.

Les données ont été nettoyées et préparées avant leur utilisation dans les analyses et le dashboard.

## 🔎 Méthodologie

Les données ont été nettoyées et contrôlées avant l'analyse.

Pour chaque préfecture, plusieurs indicateurs ont été calculés :

- population estimée ;
- nombre d'agents Mobile Money ;
- nombre d'agents Mobile Money pour 10 000 habitants ;
- nombre d'agences télécom ;
- nombre d'antennes mobiles recensées ;
- nombre d'antennes pour 10 000 habitants.

Les « zones blanches » sont opérationnellement repérées comme les préfectures
où aucune antenne n'est observée dans OpenCelliD. Cette définition est
volontairement prudente : OpenCelliD est collaboratif et incomplet ; ces zones
doivent être confirmées par des données opérateurs ou des mesures terrain.

Un **score de priorité** est ensuite calculé en combinant :

- la population : **40 %** ;
- le déficit en agents Mobile Money : **40 %** ;
- le déficit en antennes recensées : **20 %**.

Les préfectures sont ensuite classées en trois niveaux :

- 🟢 **Faible**
- 🟠 **Moyenne**
- 🔴 **Forte**

## 🚀 Installation et lancement

### 1. Cloner le projet

```bash
git clone https://github.com/abdoulridwan2-commits/Togo_Digital_Access.git
cd Togo_Digital_Access
```

### 2. Installer les dépendances

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Pour exécuter également le pipeline géospatial complet :

```bash
pip install -r requirements-pipeline.txt
```

### 3. Exécuter le pipeline de données puis lancer le dashboard

```bash
bash run_pipeline.sh
```

Sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
.\run_pipeline.ps1
```

Le pipeline fonctionne quel que soit le dossier depuis lequel le script est
lancé. Il vérifie les sources, reconstruit les données préparées, recalcule les
indicateurs et ouvre ensuite le dashboard Streamlit.

Ou étape par étape :

```bash
python src/check_data.py       # vérifie que les 9 fichiers bruts sont présents
python src/clean_data.py       # nettoie et standardise les données
python src/analyze_data.py     # jointures spatiales + population WorldPop (zonal stats)
python src/score_priorite.py   # calcule le score et le niveau de priorité
streamlit run app/main.py      # lance le dashboard interactif
```

## 📈 Résultats clés

- **9 568 508** habitants estimés (WorldPop 2020, 37 préfectures)
- **90** agences télécom (Moov + Togocom), **0** agence CANAL+ recensée (export source vide)
- **3** datacenters, tous situés dans la région Maritime (Golfe / Lomé)
- **19 619** agents Mobile Money affectés à une préfecture (sur 19 788 au total)
- **21 préfectures sur 37** classées en priorité **🔴 Forte**
- Top 5 préfectures prioritaires : **Blitta, Dankpen, Haho, Tchamba, Zio**

## 🗂️ Structure du projet

```
Togo_Digital_Access/
├── app/
│   └── main.py                  # Dashboard Streamlit (5 onglets)
├── src/
│   ├── check_data.py            # 1. Vérifie les fichiers bruts
│   ├── clean_data.py            # 2. Nettoyage (dédoublonnage, CRS, décompression)
│   ├── analyze_data.py          # 3. Jointures spatiales + zonal stats WorldPop
│   └── score_priorite.py        # 4. Score de priorité par préfecture
├── data/
│   ├── raw/                     # Données sources telles que téléchargées
│   └── processed/                # Données nettoyées + indicateurs calculés
├── outputs/
│   ├── cartes/                  # Cartes exportées pour le rapport
│   ├── graphiques/               # Graphiques exportés pour le rapport
│   └── tableaux/                 # Tableaux exportés pour le rapport
├── presentation/                 # Rapport PowerPoint (livrable du challenge)
├── run_pipeline.sh               # Lance tout le pipeline + le dashboard
└── requirements.txt
```

## ⚠️ Limites méthodologiques

- La densité de population est une **estimation** WorldPop 2020, pas un recensement.
- Les données OpenCelliD (33 antennes) proviennent d'une base collaborative et ne
  constituent **pas un inventaire exhaustif** du réseau mobile réel : une absence
  d'antenne dans une préfecture signifie une absence dans la donnée, pas
  nécessairement une absence réelle de couverture.
- Aucune agence CANAL+ n'a pu être analysée : l'export du portail geodata.gouv.tg
  pour cette couche est vide.
- Le dataset "Agences - Télécom" est le référentiel agrégé = union exacte de
  Moov + Togocom (vérifié sur les géométries) : il ne doit jamais être additionné
  aux couches Moov/Togocom séparées sous peine de double comptage.
- Le score de priorité est un outil d'aide à la décision, pas une mesure absolue ;
  il doit être complété par des validations terrain.

## 🧑‍💻 Stack technique

Python · Pandas · GeoPandas · Rasterio · Rasterstats · Streamlit · Folium · Plotly

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

Le dashboard propose également une **cartographie interactive** et un **score de priorité par préfecture**.

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

# MarcheSpot  
**Données du marché spot de l’électricité en France**

## Contexte
Ce dépôt a pour objectif de récupérer, stocker et mettre à disposition des **données du marché spot de l’électricité en France**, via l’API open data de **RTE**.  
Les données publiées par RTE sont issues des échanges réalisés sur la bourse de l’électricité **EPEX Spot**.


---

## Données disponibles
Les données correspondent au marché spot français et contiennent, pour chaque période de livraison :

- `start_date` : début de la période
- `end_date` : fin de la période
- `volume_mwh` : volume échangé (en MWh)
- `price_eur_mwh` : prix spot (en €/MWh)

### Pas de temps des données (point important)
⚠️ Le pas de temps des données a évolué :
- **jusqu’à septembre 2024** : pas **horaire**
- **depuis septembre 2024** : pas **15 minutes**

Ce changement doit être pris en compte dans toute analyse temporelle (agrégation, comparaison interannuelle, etc.).

---

## 🔗 Source des données
- **API RTE – France Power Exchanges**
- Marché sous-jacent : **EPEX Spot**
- Authentification : OAuth2 (client credentials)

Documentation RTE :  
https://data.rte-france.com

---

## Fonctionnement du pipeline
Le pipeline de données fonctionne de la manière suivante :

1. Authentification auprès de l’API RTE
2. Récupération quotidienne des données spot pour la France
3. Ajout incrémental des nouvelles observations
4. Évitement des doublons (clé : `start_date`, `end_date`)
5. Stockage dans un fichier CSV
6. Automatisation via **GitHub Actions** (exécution quotidienne)

---

## Structure du projet

```text
MarcheSpot/
├── data/
│   └── marche_spot.csv      # Données spot mises à jour automatiquement
├── src/
│   └── fetch_spot_rte.py    # Script de récupération des données
├── .github/
│   └── workflows/
│       └── update_data.yml  # Automatisation GitHub Actions
├── README.md
├── requirements.txt
└── .gitignore

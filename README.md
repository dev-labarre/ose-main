# Opportunity Scoring Engine (OSE)

Moteur de scoring d'opportunité (0–100 %) basé sur les signaux d'activité, articles, attributs entreprise et référentiels métier.

---

## Architecture du Repository

Cette structure de repository est organisée selon les principes de séparation des responsabilités et de modularité pour faciliter le développement en équipe.

### Structure des dossiers

```
OSE main/
├── README.md                    # Ce fichier
├── .gitignore                   # Fichiers à ignorer par Git
│
├── src/                         # Code source principal
│   └── ose_core/                # Package principal OSE
│       ├── config/              # Configuration (chemins, paramètres)
│       ├── data_ingestion/      # Pipelines d'ingestion des données
│       ├── feature_engineering/ # Construction des features ML-ready
│       ├── model/               # Entraînement et évaluation du modèle
│       ├── scoring/             # Logique de scoring et ranking
│       ├── api/                 # API REST (FastAPI)
│       ├── mlops/               # Versioning, monitoring, déploiement
│       └── utils/               # Utilitaires partagés
│
├── docs/                        # Documentation technique
│   ├── architecture.md          # Architecture globale du projet
│   ├── api_spec.md              # Spécification des endpoints API
│   └── data_dictionary.md       # Dictionnaire des données
│
├── tests/                       # Tests unitaires et E2E
│   ├── test_data_ingestion.py
│   ├── test_feature_engineering.py
│   ├── test_model.py
│   ├── test_scoring.py
│   └── test_api.py
│
├── data/                        # Données (non versionnées dans Git)
│   ├── raw/                     # Données raw (signals, articles, company JSON)
│   ├── processed/               # Données nettoyées et normalisées
│   ├── feature_store/           # Tables de features par entreprise
│   └── modeling/                # Datasets d'entraînement/validation
│
├── config/                      # Fichiers de configuration
│   ├── logging.yaml
│   ├── api_config.yaml
│   └── model_config.yaml
│
├── notebooks/                   # Notebooks Jupyter pour exploration
│   ├── 01_exploration_signaux.ipynb
│   ├── 02_feature_prototyping.ipynb
│   └── 03_model_experiments.ipynb
│
└── deployment/                  # Scripts et configs de déploiement
    ├── docker/
    │   ├── Dockerfile.api
    │   └── Dockerfile.training
    └── scripts/
        ├── run_api.sh
        └── run_training.sh
```

---

## Description des modules

### `src/ose_core/`

**Package principal** contenant toute la logique métier du moteur de scoring.

- **`config/`** : Gestion centralisée de la configuration (chemins de données, paramètres de modèles, config API).
- **`data_ingestion/`** : Chargement et normalisation des sources de données (signals, articles, company JSON, référentiels NAF/géo).
- **`feature_engineering/`** : Construction des features ML-ready (recency, volumétrie 3/6/12 mois, diversité, intensité, signaux positifs/red flags).
- **`model/`** : Entraînement, évaluation, calibration et génération d'explications du modèle de scoring.
- **`scoring/`** : Fonctions de scoring d'entreprise et logique de ranking (Top 10 opportunités).
- **`api/`** : Application FastAPI exposant les endpoints REST (`/health`, `/api/v1/score`, `/api/v1/top-opportunities`).
- **`mlops/`** : Versioning des données et modèles, monitoring de drift, jobs batch.
- **`utils/`** : Utilitaires partagés (logging, I/O, validations).

### `docs/`

Documentation technique de référence pour l'équipe.

- **`architecture.md`** : Vue d'ensemble de l'architecture, découpage en composants, plan de travail priorisé.
- **`api_spec.md`** : Spécification détaillée des endpoints API (schémas request/response).
- **`data_dictionary.md`** : Dictionnaire des données (champs, types, sources).

### `tests/`

Suite de tests automatisés (pytest).

- Tests unitaires par module (data ingestion, features, modèle, scoring, API).
- Tests E2E du pipeline complet et de l'API.

### `data/`

Stockage des données (à ajouter dans `.gitignore`).

- **`raw/`** : Données sources brutes.
- **`processed/`** : Données nettoyées et normalisées.
- **`feature_store/`** : Tables de features par entreprise.
- **`modeling/`** : Datasets d'entraînement/validation/test.

### `config/`

Fichiers de configuration (YAML, JSON) pour logging, API, modèles.

### `notebooks/`

Notebooks Jupyter pour exploration, prototypage de features, expérimentations de modèles.

### `deployment/`

Scripts et configurations pour le déploiement (Docker, scripts shell, éventuellement Kubernetes).

---

## Plan de développement (phases)

1. **Phase 1 – Fondations data** : Implémenter `data_ingestion/` et normaliser les sources.
2. **Phase 2 – Features ML-ready** : Construire les features dans `feature_engineering/`.
3. **Phase 3 – Modèle explicable** : Entraîner et calibrer le modèle dans `model/`.
4. **Phase 4 – API REST** : Exposer les endpoints dans `api/`.
5. **Phase 5 – MLOps & prod** : Ajouter versioning, monitoring, déploiement dans `mlops/`.

---

## Prochaines étapes

1. Initialiser le projet Python (`pyproject.toml` ou `requirements.txt`).
2. Implémenter les modules dans l'ordre des phases.
3. Compléter la documentation au fur et à mesure.

---

**Note** : Cette structure est la base initiale du repository. Elle sera enrichie au fil du développement.


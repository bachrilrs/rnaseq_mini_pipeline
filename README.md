# RNA-seq Automated QC Pipeline

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

## Présentation du Projet

Ce projet est un pipeline **ETL (Extract, Transform, Load)** industrialisé dédié au contrôle qualité (QC) de données de séquençage d'ARN (RNA-seq). À partir du dataset public **GSE60450**, le pipeline automatise l'ingestion de données brutes, leur validation, et leur stockage dans une base de données relationnelle.

L'objectif est de démontrer une maîtrise de l'orchestration de services (Docker Compose), du développement Python pour la donnée et de l'automatisation de workflows complexes (DevOps/Data Engineering).

---

## Architecture et Fonctionnalités

* **Orchestration Multi-Services** : Utilisation de Docker Compose pour isoler l'application Python du serveur PostgreSQL.
* **Automatisation "Zero-Friction"** : Un script de lancement intelligent (`run_project.sh`) gère la configuration des variables d'environnement et le déploiement.
* **Synchronisation Robuste** : L'entrypoint utilise des sockets réseau pour garantir que PostgreSQL est prêt avant l'insertion des données.
* **Pipeline ETL Pipeline** :
* **Extract** : Ingestion de fichiers TSV via Pandas.
* **Transform** : Nettoyage des métadonnées GEO, validation des types et calculs de qualité.
* **Load** : Ingestion sécurisée via `psycopg2` avec gestion des transactions atomiques.
* **Observabilité** : Affichage automatique d'un **Dashboard de KPIs** SQL dès la fin du traitement.

---

## Modèle de Données (SQL)

La base de données est structurée pour assurer la traçabilité complète des analyses :

* **`runs`** : Historique des exécutions du pipeline (version du code, dataset source, horodatage).
* **`samples`** : Référentiel des échantillons (Conditions biologiques, GEO Accession).
* **`qc_metrics`** : Métriques techniques (Library Size, Mean Counts) liées à un échantillon et un run spécifiques.

---

## Installation et Lancement (One-Click)

Le projet a été conçu pour être testé en une seule commande. Aucun prérequis n'est nécessaire à part Docker.

## Cloner le projet

```bash
git clone https://github.com/bachrilrs/rnaseq_mini_pipeline.git
cd rnaseq_mini_pipeline
```

## Lancer le pipeline

```bash
chmod +x run_project.sh
./run_project.sh
```

Cela construira les images Docker, démarrera les services, exécutera le pipeline ETL, et affichera un dashboard SQL avec les KPIs

Dashboard de KPIs

À la fin de l'exécution, un résumé statistique s'affiche automatiquement dans votre terminal :

Nombre total de runs et d'échantillons traités.

Moyenne de la taille des librairies par condition biologique (Treatment vs Control).

Console Interactive

Le script run_project.sh vous laisse directement la main sur une console PostgreSQL interactive à la fin du processus. Vous pouvez tester vos propres requêtes immédiatement :

```sql
-- Exemple : Vérifier les 5 premiers échantillons
SELECT * FROM samples LIMIT 5;
````

-- Quitter la console
\q

## Sécurité des Injections SQL

Lors de l'insertion des données dans la base PostgreSQL, le pipeline utilise des requêtes paramétrées avec `psycopg2` pour prévenir les risques d'injection SQL.
Par exemple, au lieu de construire une requête SQL en concaténant des chaînes de caractères, le code utilise des placeholders `%s` :

```python
insert_query = """INSERT INTO samples (sample_id, condition, replicate, geo_accession)
VALUES (%s, %s, %s, %s)"""
cursor.execute(insert_query, (sample_id, condition, replicate, geo_accession))
```

Stack Technique
Langage : Python 3.11 (Pandas, SQLAlchemy, PyYAML)

Base de données : PostgreSQL 16

Infrastructure : Docker, Docker Compose.

Contact
LinkedIn : [Laroussi Bachri](https://www.linkedin.com/in/laroussi-bachri)
GitHub : [bachrilrs](https://github.com/bachrilrs)

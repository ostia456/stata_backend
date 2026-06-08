uvicorn app.main:app --reload
npm run dev front
# Windows PowerShell
fast_env\Scripts\Activate.ps1

# Windows Command Prompt
fast_env\Scripts\activate.bat

# Mac/Linux
source fast_env/bin/activate



# Backend AutoEDA — Rôle de chaque fichier

# Racine backend/

## run.py

Lance l’application FastAPI.

Contient :

* démarrage uvicorn,
* configuration host/port,
* mode debug.

---

## requirements.txt

Toutes les dépendances Python.

Exemples :

* fastapi
* uvicorn
* pandas
* scipy
* plotly
* pydantic
* python-multipart
* weasyprint
* openpyxl
* jinja2

---

## .env

Variables sensibles.

Exemple :

* SECRET_KEY
* DEBUG
* MAX_UPLOAD_SIZE
* REPORT_FOLDER

---

## .env.example

Version exemple du .env.

---

## Dockerfile

Conteneur Docker backend.

---

# app/

## main.py

Point d’entrée principal FastAPI.

Contient :

* création app FastAPI,
* ajout middlewares,
* inclusion routers,
* configuration CORS,
* gestion erreurs globales.

---

## config.py

Configuration centralisée.

Contient :

* chemins dossiers,
* limites upload,
* constantes globales,
* lecture variables environnement.

---

## dependencies.py

Dépendances injectables FastAPI.

Exemple :

* accès config,
* validation auth,
* accès cache.

---

## utils.py

Fonctions utilitaires globales.

Exemples :

* génération UUID,
* formatage tailles,
* conversion datetime,
* helpers généraux.

---

# core/

Le coeur analytique pur.

IMPORTANT :
Aucun accès API ici.
Aucune logique frontend.
Seulement la logique Data/Stats.

---

## constants.py

Toutes les constantes.

Exemple :

```python
SUPPORTED_EXTENSIONS = ["csv", "xlsx"]
MAX_COLUMNS = 1000
```

---

## enums.py

Enums centralisés.

Exemple :

```python
class ColumnType(Enum):
    NUMERICAL = "numerical"
```

---

## exceptions.py

Exceptions personnalisées.

Exemple :

* InvalidDatasetError
* UnsupportedFileError
* EmptyDatasetError

---

## type_detector.py

Détecte automatiquement le type des colonnes.

Détermine :

* numérique,
* catégorielle,
* booléenne,
* datetime,
* texte.

---

## file_analyzer.py

Lecture des fichiers.

Contient :

* pd.read_csv,
* pd.read_excel,
* gestion encodage,
* validation initiale.

---

## dataset_profiler.py

Vue globale du dataset.

Retourne :

* nombre lignes,
* colonnes,
* mémoire utilisée,
* types colonnes.

---

## column_analyzer.py

Analyse détaillée colonne par colonne.

Calcule :

* cardinalité,
* valeurs uniques,
* types,
* statistiques.

---

## statistics.py

Statistiques descriptives.

Calcule :

* moyenne,
* médiane,
* variance,
* quartiles,
* écart-type,
* skewness,
* kurtosis.

---

## correlations.py

Calcul des corrélations.

Contient :

* Pearson,
* Spearman,
* matrices corrélation.

---

## normality.py

Tests de normalité.

Contient :

* Shapiro-Wilk,
* interprétation p-value.

---

## missing_values.py

Analyse valeurs manquantes.

Retourne :

* nombre NaN,
* pourcentage,
* colonnes impactées.

---

## outliers.py

Détection des valeurs aberrantes.

Méthodes :

* IQR,
* Z-score.

---

## distributions.py

Analyse des distributions.

Détecte :

* asymétrie,
* dispersion,
* distributions particulières.

---

## categorical_analysis.py

Analyse variables catégorielles.

Calcule :

* fréquence,
* mode,
* top catégories.

---

## datetime_analysis.py

Analyse des colonnes temporelles.

Détecte :

* tendances,
* périodes,
* plages temporelles.

---

## data_quality.py

Évalue la qualité du dataset.

Score basé sur :

* données manquantes,
* doublons,
* cohérence,
* bruit.

---

## data_insights.py

Génère des constatations automatiques.

Exemple :

* forte corrélation,
* dataset déséquilibré,
* colonne suspecte.

---

# schemas/

Schémas Pydantic.
Validation API.

---

## dataset.py

Schemas liés aux datasets.

Exemple :

* DatasetInfo,
* DatasetSummary.

---

## analysis.py

Schemas résultats analyses.

---

## report.py

Schemas export rapport.

---

## visualization.py

Schemas graphiques.

---

## common.py

Schemas réutilisables.

---

# models/

Structures internes métier.

---

## dataset_summary.py

Objet résumé dataset.

---

## column_profile.py

Structure profil colonne.

---

## correlation_result.py

Objet corrélation.

---

## quality_report.py

Structure qualité dataset.

---

## missing_report.py

Objet valeurs manquantes.

---

## outlier_report.py

Objet anomalies.

---

## chart_metadata.py

Métadonnées graphiques.

---

## report_metadata.py

Métadonnées rapports.

---

# validators/

Validation données.

---

## file_validator.py

Vérifie :

* extension,
* taille,
* corruption fichier.

---

## dataframe_validator.py

Validation DataFrame.

Vérifie :

* dataframe vide,
* colonnes invalides,
* doublons.

---

## schema_validator.py

Validation structure dataset.

---

# services/

Orchestration métier.

IMPORTANT :
Les services utilisent les modules core.

---

## analysis_service.py

Pipeline complet d’analyse.

Coordonne :

* stats,
* corrélations,
* qualité,
* insights.

---

## visualization_service.py

Construit toutes les visualisations.

---

## interpretation_service.py

Produit les interprétations automatiques.

---

## report_service.py

Construit le rapport final.

---

## export_service.py

Gère export HTML/PDF.

---

## upload_service.py

Gestion uploads utilisateurs.

---

## cache_service.py

Gestion cache.

---

## metadata_service.py

Sauvegarde historique rapports.

---

## cleanup_service.py

Suppression automatique anciens fichiers.

---

# visualization/

Modules Plotly.

Chaque fichier construit un type de graphique.

---

## histograms.py

Histogrammes.

---

## boxplots.py

Boxplots.

---

## heatmaps.py

Heatmaps corrélation.

---

## scatterplots.py

Scatter plots.

---

## piecharts.py

Graphiques circulaires.

---

## linecharts.py

Courbes temporelles.

---

## missing_visuals.py

Visualisation NaN.

---

## categorical_charts.py

Graphiques catégories.

---

## correlation_plots.py

Visualisations corrélations.

---

## dashboard_builder.py

Assemble dashboard complet.

---

# interpretation/

Interprétation automatique.

---

## correlation_interpreter.py

Interprète corrélations.

---

## normality_interpreter.py

Interprète tests normalité.

---

## outlier_interpreter.py

Interprète anomalies.

---

## quality_interpreter.py

Interprète qualité données.

---

## missing_interpreter.py

Interprète valeurs manquantes.

---

## distribution_interpreter.py

Interprète distributions.

---

## recommendation_engine.py

Produit recommandations automatiques.

---

# reports/

Génération rapports.

---

## html_generator.py

Construit HTML rapport.

---

## pdf_generator.py

Conversion HTML → PDF.

---

## sections_builder.py

Construit sections rapport.

---

## report_styling.py

Style rapports.

---

## report_exporter.py

Export fichiers finaux.

---

# api/

Routes FastAPI.

---

## routes/home.py

Route accueil.

---

## routes/upload.py

Routes upload fichiers.

---

## routes/analysis.py

Routes analyses.

---

## routes/visualization.py

Routes graphiques.

---

## routes/reports.py

Routes téléchargement rapports.

---

## routes/metadata.py

Historique rapports.

---

## routes/health.py

Healthcheck API.

---

## router.py

Centralise tous les routers.

---

# middleware/

Middlewares FastAPI.

---

## logging.py

Logs requêtes.

---

## timing.py

Mesure temps exécution.

---

## security.py

Headers sécurité.

---

## error_handler.py

Gestion erreurs globales.

---

# logs/

## app.log

Fichier logs application.

---

# uploads/

## temp/

Stockage temporaire.

---

## processed/

Datasets déjà analysés.

---

# reports_output/

## html/

Rapports HTML générés.

---

## pdf/

Rapports PDF générés.

---

# metadata/

## reports_metadata.json

Historique rapports générés.

---

# cache/

Résultats temporaires.

---

# tests/

Tests automatisés.

---

## test_api.py

Tests endpoints.

---

## test_statistics.py

Tests statistiques.

---

## test_correlations.py

Tests corrélations.

---

## test_normality.py

Tests normalité.

---

## test_visualizations.py

Tests graphiques.

---

## test_reports.py

Tests génération rapports.

---

## test_validators.py

Tests validations.

---

## test_services.py

Tests services métier.

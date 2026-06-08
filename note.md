Tu dois construire ton projet comme une pipeline stable.

# Ordre intelligent de développement

## PHASE 1 — Faire fonctionner le backend minimal ⭐⭐⭐

Objectif :

```text
Uploader un fichier → lire dataframe → retourner infos
```

Tant que ça ne marche pas parfaitement :
❌ pas de Plotly
❌ pas de PDF
❌ pas d’interprétation IA

---

# ÉTAPE 1 — Initialiser FastAPI

## À faire

Créer :

```text
backend/app/main.py
```

Contenu minimal :

* création app FastAPI,
* CORS,
* route test `/`.

---

## Résultat attendu

Quand tu fais :

```bash
uvicorn app.main:app --reload
```

tu dois voir :

```json
{
  "message": "AutoEDA API running"
}
```

---

# ÉTAPE 2 — Gestion upload fichiers ⭐⭐⭐

C’est la vraie première grosse étape.

## Fichiers à coder

### `api/routes/upload.py`

Route upload :

```python
POST /upload
```

---

### `services/upload_service.py`

Sauvegarde fichier.

---

### `validators/file_validator.py`

Valide :

* extension,
* taille,
* format.

---

### `core/file_analyzer.py`

Lit :

* CSV,
* Excel.

Retourne :

```python
pd.DataFrame
```

---

# Pipeline à réussir

```text
Frontend
↓
POST fichier
↓
FastAPI upload route
↓
validator
↓
upload service
↓
file analyzer
↓
DataFrame chargé
```

---

# ÉTAPE 3 — Profil dataset ⭐⭐⭐

Maintenant tu analyses le dataframe.

## Fichiers à coder

---

## `core/dataset_profiler.py`

Retourne :

```python
{
    "rows": 1000,
    "columns": 12,
    "memory_usage": "...",
}
```

---

## `core/type_detector.py`

Détecte :

* numérique,
* catégoriel,
* datetime,
* bool.

---

## `core/column_analyzer.py`

Analyse chaque colonne.

---

# Résultat attendu

API retourne :

```json
{
  "rows": 891,
  "columns": 12,
  "column_types": {
      "Age": "numerical",
      "Sex": "categorical"
  }
}
```

---

# ÉTAPE 4 — Statistiques descriptives ⭐⭐⭐⭐

Maintenant :

## `core/statistics.py`

Fonctions :

```python
calculate_mean()
calculate_median()
calculate_std()
calculate_variance()
```

Puis :

```python
generate_descriptive_statistics(df)
```

---

# ÉTAPE 5 — Valeurs manquantes ⭐⭐⭐

## `core/missing_values.py`

Retourne :

```python
{
   "Age": 177,
   "Cabin": 687
}
```

---

# ÉTAPE 6 — Corrélations ⭐⭐⭐⭐

## `core/correlations.py`

Fonctions :

* Pearson,
* Spearman,
* matrice corrélation.

---

# ÉTAPE 7 — Tests normalité ⭐⭐⭐⭐

## `core/normality.py`

Implémenter :

* Shapiro-Wilk.

---

# ÉTAPE 8 — API d’analyse complète ⭐⭐⭐⭐⭐

Maintenant seulement :

## `services/analysis_service.py`

Pipeline globale :

```text
dataset
↓
stats
↓
missing values
↓
correlations
↓
normality
↓
result final
```

---

# ÉTAPE 9 — Frontend React minimal ⭐⭐⭐

Ne fais PAS un frontend complexe au début.

---

## Première page :

### Upload simple

Bouton :

```text
Choisir fichier
```

Puis :

```text
Envoyer
```

Puis afficher :

```text
dataset summary
```

---

# ÉTAPE 10 — Graphiques Plotly ⭐⭐⭐⭐

Maintenant :

* histogrammes,
* heatmaps,
* boxplots.

---

# ÉTAPE 11 — Dashboard React ⭐⭐⭐⭐⭐

Construire :

* cards stats,
* tableaux,
* charts.

---

# ÉTAPE 12 — Génération HTML/PDF ⭐⭐⭐⭐⭐

Seulement à la fin.

---

# Ce que tu dois coder EN PREMIER exactement

# PRIORITÉ ABSOLUE

## Backend

### 1

`main.py`

### 2

`upload.py`

### 3

`upload_service.py`

### 4

`file_validator.py`

### 5

`file_analyzer.py`

---

# Puis

## Analyse dataframe

### 6

`dataset_profiler.py`

### 7

`type_detector.py`

### 8

`statistics.py`

---

# Ensuite seulement

* corrélations,
* normalité,
* graphiques,
* React avancé,
* PDF.

---

# Très important

## Au début :

❌ PAS d’architecture compliquée
❌ PAS de microservices
❌ PAS d’async compliqué
❌ PAS de Redux
❌ PAS d’authentification

---

# Construis comme ça

## Version 1

```text
Upload → Analyse → Résultat JSON
```

---

## Version 2

```text
Ajouter graphiques
```

---

## Version 3

```text
Ajouter dashboard React
```

---

## Version 4

```text
Ajouter PDF
```

---

# Ton premier vrai objectif

Quand tu uploades un CSV :

tu dois obtenir :

```json
{
  "rows": 100,
  "columns": 5,
  "missing_values": {...},
  "statistics": {...}
}
```

Quand ça marche :
➡️ ton projet est officiellement lancé correctement.

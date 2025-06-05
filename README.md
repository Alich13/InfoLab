# InfoLab - Dashboard de Suivi d'Activité

## 📊 Description du Projet

InfoLab est un tableau de bord interactif développé avec Streamlit pour le suivi d'activité globale des laboratoires et l'aide au développement. Cette application permet d'analyser et de visualiser des données de contrats de recherche, incluant les acteurs, financeurs, structures et phases de projets.

### Fonctionnalités Principales

- **Upload du fichier d'extraction InfoLab** : Support des formats Excel (.xlsx), CSV et TSV
- **Filtrage interactif** : Filtres dynamiques par structure, acteurs, type de contrat, etc.
- **Visualisations avancées** : Graphiques interactifs avec Altair et Plotly
- **Interface intuitive** : Interface web responsive et conviviale

## 🚀 Installation

### Prérequis

- Python 3.13 ou supérieur
- Conda ou Miniconda installé

### Installation via Conda (Recommandé)

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd InfoLab
   ```

2. **Créer l'environnement Conda**
   ```bash
   conda env create -f environment.yml
   ```

3. **Activer l'environnement**
   ```bash
   conda activate streamlit-env
   ```

## 📋 Dépendances Principales

- **Streamlit** (1.42.0) - Framework web pour l'application
- **Pandas** (2.2.3) - Manipulation et analyse de données
- **Altair** (5.5.0) - Visualisations déclaratives
- **Plotly** (6.0.0) - Graphiques interactifs
- **OpenPyXL** (3.1.5) - Lecture de fichiers Excel
- **Matplotlib** (3.10.0) - Visualisations supplémentaires
- **NumPy** (2.2.2) - Calculs numériques

## 🔄 Préprocessing des Données

L'application effectue plusieurs étapes de préprocessing automatique pour optimiser l'analyse et l'affichage des données :

### Gestion des Valeurs Manquantes
- Toutes les colonnes textuelles avec des valeurs manquantes sont remplacées par `"Introuvable"`
- Les dates invalides sont converties en `NaT` (Not a Time)

### Conversion des Dates
- **Format attendu** : `DD/MM/YYYY`
- **Colonnes traitées** :
  - `Date Création` → conversion en datetime
  - `Date Premier Contact` → conversion en datetime
  - `Date Signature` → conversion en datetime  
  - `Date de l'action` → conversion en datetime
- **Création automatique** : colonne `Year` extraite de `Date Création`

### Normalisation des Valeurs Catégorielles

#### Phase des Projets
- Les projets avec `Action` = "Abandonné" ou "Refusé" → `Phase` = "Abandonné"

#### Outils du Cadre
- Les valeurs "Introuvable" ou "Autres" → "Autres cadres"

#### Financeurs
- `Financeurs::Sous-type` "Introuvable" → "Non spécifié"
- `Financeurs::Pays` → normalisé en majuscules avec suppression des espaces

### Explosion des Colonnes Multi-Valeurs
Certaines colonnes contiennent des valeurs multiples séparées par `" // "`. L'application les sépare automatiquement :
- `Intitule structure`
- `Code structure` 
- `Acteurs::Dénomination`
- `Acteurs::Type`

### Noms de Colonnes pour l'Affichage

L'application modifie l'affichage de certains noms de colonnes pour améliorer la lisibilité :

| Nom Technique | Nom Affiché |
|---------------|-------------|
| `Intitule structure` | **Unité** |
| `Contact princpal DR&I` | **Contact principal DR&I** |
| `Year` | **Année** |
| `Type contrat` | **Type de contrat** |
| `Acteurs::Dénomination` | **Dénomination d'acteurs** |
| `Acteurs::Type` | **Type d'acteurs** |

### Valeurs par Défaut des Filtres

L'application applique des filtres par défaut pour faciliter l'analyse :
- **Service** : `"DRV FSI développement"`
- **Outil du cadre** : `["CIFRE", "CDDP"]`
- **Année** : À partir de 2020

## 🎯 Utilisation

### Démarrage de l'Application

```bash
streamlit run 📊_Dashbord.py
```

L'application sera accessible à l'adresse indiquée sur la terminale . 

### Exemple d'Utilisation

1. **Upload des Données d'extraction InfoLab**
   - Cliquez sur "Upload your Excel/CSV/TSV file"
   - Sélectionnez votre fichier de données (formats supportés : .xlsx, .csv, .tsv)

2. **Application des Filtres**
   - Utilisez les filtres interactifs pour affiner votre analyse
   - Les filtres incluent : Service, Structure, Type de contrat, Acteurs, etc.

3. **Exploration des Visualisations**
   - Consultez les différents onglets pour explorer vos données
   - Analysez les distributions par type de contrat, structure, acteurs
   - Examinez les montants par financeur

### Format des Données Attendu

Votre fichier doit contenir au minimum les colonnes suivantes :
- `Numero contrat` (identifiant unique)
- `Type contrat`
- `Phase`
- `Intitule structure`
- `Acteurs::Dénomination`
- `Acteurs::Type`
- `Montant Global`
- `Date Création`

## 📁 Structure du Projet

```
InfoLab/
├── 📊_Dashbord.py          # Application principale Streamlit
├── aux1.py                 # Fonctions utilitaires et de préprocessing
├── 00_explore.ipynb        # Notebook d'exploration des données
├── app_test.py             # Application de test
├── environment.yml         # Configuration de l'environnement Conda
├── datasym/                # Lien symbolique vers les données
├── pages/                  # Pages additionnelles Streamlit
└── README.md              # Ce fichier
```

### Description des Fichiers

- **📊_Dashbord.py** : Interface principale de l'application avec tous les composants de visualisation
- **aux1.py** : Contient les fonctions de traitement des données, filtrage et création de graphiques
- **00_explore.ipynb** : Notebook Jupyter pour l'exploration préliminaire des données
- **app_test.py** : Version de test de l'application
- **environment.yml** : Définition complète de l'environnement Conda avec toutes les dépendances

## 🔧 Fonctionnalités Techniques

### Gestion des Données

- **Lecture multi-format** : Support automatique CSV, TSV et Excel
- **Normalisation** : Explosion des colonnes contenant des valeurs multiples (séparées par "//")
- **Filtrage dynamique** : Mise à jour en temps réel des visualisations
- **Cache intelligent** : Optimisation des performances avec `@st.cache_data`




Développé pour le suivi d'activité des laboratoires de recherche et l'aide au développement de projets scientifiques.
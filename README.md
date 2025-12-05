# OSE Project

🎯 **Goal**: Classify companies as "Good Business Opportunity" vs "Not Good Opportunity" by combining article text analysis with company features using sklearn Pipeline.

## 📁 Project Structure

```
ose-main/
├── Notebooks/
│   └── 01_dataset_visualization_v2.ipynb
├── src/
│   └── ose_core/
│       ├── config/
│       ├── data/
│       │   └── extracted_datasets/
│       ├── feature_engineering/
│       ├── mlops/
│       ├── model/
│       ├── scoring/
│       └── utils/
├── tests/
│   ├── test_api.py
│   ├── test_data.py
│   ├── test_feature_engineering.py
│   ├── test_model.py
│   └── test_scoring.py
├── QUICK_SETUP.md
├── README.md
├── requirements.txt
└── Makefile
```

## 🚀 Setup Instructions

### Python 3.10 Environment Setup (pyenv)

#### 📋 Prerequisites

Ensure you have `pyenv` installed. If not, install it:

**macOS (via Homebrew):**
```bash
brew install pyenv
```

**Linux:**
Follow the [pyenv installation guide](https://github.com/pyenv/pyenv#installation)

---

#### 1️⃣ Quick Setup (Recommended)

```bash
# Run the setup Makefile target (does everything automatically)
make setup
```

This will:
- Install Python 3.10.6 (if not already installed)
- Create virtualenv named `ose-env`
- Upgrade pip
- Install all project requirements
- Register Jupyter kernel

---

#### 2️⃣ Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Install Python 3.10.6 (if not already installed)
pyenv install -s 3.10.6

# Create virtualenv named ose-env
pyenv virtualenv 3.10.6 ose-env

# Activate the environment
pyenv activate ose-env

# Upgrade pip first
python -m pip install --upgrade pip

# Install project requirements
pip install -r requirements.txt

# Register kernel for Jupyter (named ose-env)
python -m ipykernel install --user --name ose-env --display-name "Python (ose-env)"
```

---

#### 3️⃣ Verify Installation

Run the verification command:

```bash
# Quick verification using Makefile
make verify
```

Or verify manually:

```bash
# Verify Python version
python -V  # Should show Python 3.10.x

# Verify all imports work
python -c "import pandas, sklearn, xgboost, keras, tensorflow, shap; print('✓ All imports OK')"

# Verify sklearn components
python -c "from sklearn.pipeline import Pipeline; from sklearn.impute import SimpleImputer, KNNImputer; from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder; from sklearn.decomposition import PCA; from sklearn.cluster import KMeans; from sklearn.neighbors import NearestNeighbors; print('✓ sklearn components OK')"

# Verify Keras
python -c "from keras.layers import Normalization; print('✓ Keras OK')"

# Verify Jupyter kernel
jupyter kernelspec list  # Should show Python (ose-env)
```

---

#### 5️⃣ Run the Notebook

Open and run the notebook:

```bash
jupyter notebook notebooks/05_business_opportunity_classifier.ipynb
```

> **Note:** Make sure to select the "Python (ose-env)" kernel in Jupyter.

## 📦 Key Components

- **`Notebooks/`** - Jupyter notebooks for data visualization and analysis
- **`src/ose_core/`** - Core project modules:
  - `data/` - Data loading utilities and extracted datasets
  - `config/` - Configuration files
  - `feature_engineering/` - Feature engineering modules
  - `model/` - Model definitions and training
  - `scoring/` - Scoring and evaluation modules
  - `mlops/` - MLOps utilities
  - `utils/` - Utility functions
- **`tests/`** - Unit tests for all modules
- **`requirements.txt`** - Python dependencies

## Key Features

- ✅ sklearn Pipeline with ColumnTransformer for mixed data types
- ✅ Pipeline visualization using sklearn's diagram display
- ✅ Text features from article titles (TF-IDF)
- ✅ Company features (financial, workforce, structure, flags, contacts)
- ✅ Binary classification with comprehensive evaluation
- ✅ Top 10 companies ranked by opportunity score

## Data Extraction Pipeline

- The fast extraction pipeline lives in `src/ose_core/pipelines/` and mirrors the v3.1 workflow from `_Data_Extract_Viz_agro`.
- It produces the 9 datasets consumed by `DataLoader` (`src/ose_core/data`), preserving the same schema (`company_name`, `siren`, `siret` + dataset-specific columns).
- Default settings live in `src/ose_core/config/extraction_config.yaml` (chunk size, output directory, dataset names).
- Example usage is available in `Notebooks/00_data_extraction.ipynb`:
  - set JSONL input paths (`company`, `article`, `project`)
  - run `make_extract_pipeline(...)`
  - save with `save_datasets_to_dir(...)` to `src/ose_core/data/extracted_datasets/`

## Business Logic

- Positive signals: Investissements, Recrutement, Construction, Levée de fonds
- Negative signals: Vente & Cession, RJ & LJ, Restructuration, Licenciement
- Target: Good opportunity if (positive > negative) OR (positive >= 2)


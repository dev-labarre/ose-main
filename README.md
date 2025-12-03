# Business Opportunity Classifier

🎯 **Goal**: Classify companies as "Good Business Opportunity" vs "Not Good Opportunity" by combining article text analysis with company features using sklearn Pipeline.

## Setup Instructions

### Python 3.10 Environment Setup (pyenv)

#### Prerequisites
Ensure you have `pyenv` installed. If not, install it:
```bash
# macOS (via Homebrew)
brew install pyenv

# Linux - follow pyenv installation guide
# https://github.com/pyenv/pyenv#installation
```

#### 1. Create Python 3.10 Virtual Environment

```bash
# Install Python 3.10.6 (if not already installed)
pyenv install -s 3.10.6

# Create virtualenv named ose-env
pyenv virtualenv 3.10.6 ose-env

# Activate the environment
pyenv activate ose-env
```

#### 2. Upgrade pip and Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install project requirements
pip install -r requirements.txt
```

#### 3. Register Jupyter Kernel

```bash
# Register kernel for Jupyter (named ose-env)
python -m ipykernel install --user --name ose-env --display-name "Python (ose-env)"
```

#### 4. Verify Installation

```bash
# Verify Python version
python -V  # Should show Python 3.10.x

# Verify all imports work
python -c "import pandas, sklearn, xgboost, keras, tensorflow; print('✓ All imports OK')"

# Verify sklearn components
python -c "from sklearn.pipeline import Pipeline; from sklearn.impute import SimpleImputer, KNNImputer; from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder; from sklearn.decomposition import PCA; from sklearn.cluster import KMeans; from sklearn.neighbors import NearestNeighbors; print('✓ sklearn components OK')"

# Verify Keras
python -c "from keras.layers import Normalization; print('✓ Keras OK')"

# Verify Jupyter kernel
jupyter kernelspec list  # Should show Python (ose-env)
```

#### 5. Run the Notebook

Open and run the notebook:
```bash
jupyter notebook notebooks/05_business_opportunity_classifier.ipynb
```

**Note:** Make sure to select the "Python (ose-env)" kernel in Jupyter.

## Project Structure

- `notebooks/` - Jupyter notebooks for the classifier
- `data/` - Dataset files
- `requirements.txt` - Python dependencies

## Key Features

- ✅ sklearn Pipeline with ColumnTransformer for mixed data types
- ✅ Pipeline visualization using sklearn's diagram display
- ✅ Text features from article titles (TF-IDF)
- ✅ Company features (financial, workforce, structure, flags, contacts)
- ✅ Binary classification with comprehensive evaluation
- ✅ Top 10 companies ranked by opportunity score

## Business Logic

- Positive signals: Investissements, Recrutement, Construction, Levée de fonds
- Negative signals: Vente & Cession, RJ & LJ, Restructuration, Licenciement
- Target: Good opportunity if (positive > negative) OR (positive >= 2)


# Quick Setup - Copy-Paste Commands

## A) Shell Setup (Copy-Paste)

```bash
# Python 3.10 env via pyenv
pyenv install -s 3.10.6
pyenv virtualenv 3.10.6 ose-env
pyenv activate ose-env

# Upgrade pip first
python -m pip install --upgrade pip

# Install project requirements
pip install -r requirements.txt

# Register kernel for Jupyter
python -m ipykernel install --user --name ose-env --display-name "Python (ose-env)"
```

## B) Verification Commands

```bash
# Verify Python version
python -V  # Should show Python 3.10.x

# Verify all imports work
python -c "import pandas, sklearn, xgboost, keras, tensorflow; print('OK')"

# Verify shap
python -c "import shap; print('OK')"

# Verify sklearn components
python -c "from sklearn.pipeline import Pipeline; from sklearn.impute import SimpleImputer, KNNImputer; from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder; from sklearn.decomposition import PCA; from sklearn.cluster import KMeans; from sklearn.neighbors import NearestNeighbors; print('OK')"

# Verify Keras
python -c "from keras.layers import Normalization; print('OK')"

# Verify Jupyter kernel
jupyter kernelspec list  # Should show Python (ose-env)
```

## Alternative: Use Makefile

```bash
# Full setup (recommended)
make setup

# Or just install/upgrade requirements
make install

# Verify installation
make verify

# Show all available commands
make help
```


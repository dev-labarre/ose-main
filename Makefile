.PHONY: help env setup install verify clean

# Default target
.DEFAULT_GOAL := setup

# Variables
PYTHON_VERSION := 3.10.6
VENV_NAME := ose-env

help: ## Show this help message
	@echo "🚀 OSE Project - Makefile Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make env     - Install Python via pyenv and create the ose-env virtualenv only"
	@echo "  make setup   - Full environment setup (pyenv install, venv creation, pip upgrade, requirements install, jupyter kernel)"
	@echo "  make install - Install/upgrade requirements only (assumes venv exists)"
	@echo "  make verify  - Run verification commands (Python version, imports, jupyter kernel)"
	@echo "  make clean   - Cleanup (remove venv, uninstall jupyter kernel)"
	@echo "  make help    - Show this help message"
	@echo ""

env: ## Install Python and create the virtualenv only
	@echo "🚀 Ensuring Python $(PYTHON_VERSION) and virtualenv $(VENV_NAME) exist..."
	@echo "📦 Installing Python $(PYTHON_VERSION)..."
	@pyenv install -s $(PYTHON_VERSION) || true
	@echo "🔧 Creating virtualenv $(VENV_NAME)..."
	@pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME) || echo "ℹ️  virtualenv '$(VENV_NAME)' already exists, continuing..."
	@echo "✅ Environment bootstrap complete. You can now run 'make setup' or 'make install'."

setup: ## Full environment setup
	@echo "🚀 Setting up Python 3.10 environment for OSE project..."
	@echo "📦 Installing Python $(PYTHON_VERSION)..."
	@pyenv install -s $(PYTHON_VERSION) || true
	@echo "🔧 Creating virtualenv $(VENV_NAME)..."
	@pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME) || echo "ℹ️  virtualenv '$(VENV_NAME)' already exists, continuing..."
	@echo "✅ Activating $(VENV_NAME)..."
	@eval "$$(pyenv init -)" && pyenv activate $(VENV_NAME) && \
		echo "⬆️  Upgrading pip..." && \
		python -m pip install --upgrade pip && \
		echo "📚 Installing project requirements..." && \
		pip install -r requirements.txt && \
		echo "🔗 Registering Jupyter kernel..." && \
		python -m ipykernel install --user --name $(VENV_NAME) --display-name "Python ($(VENV_NAME))"
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "📋 Run 'make verify' to verify the installation"
	@echo "🎯 To activate the environment in the future:"
	@echo "  pyenv activate $(VENV_NAME)"

install: ## Install/upgrade requirements only (assumes venv exists)
	@echo "📚 Installing project requirements..."
	@eval "$$(pyenv init -)" && pyenv activate $(VENV_NAME) && \
		python -m pip install --upgrade pip && \
		pip install -r requirements.txt
	@echo "✅ Requirements installed!"

verify: ## Run verification commands
	@echo "🔍 Verifying installation..."
	@eval "$$(pyenv init -)" && pyenv activate $(VENV_NAME) && \
		echo "" && \
		echo "📋 Python version:" && \
		python -V && \
		echo "" && \
		echo "📋 Testing imports..." && \
		python -c "import pandas, sklearn, xgboost, keras, tensorflow, shap; print('✓ All core imports OK')" && \
		python -c "from sklearn.pipeline import Pipeline; from sklearn.impute import SimpleImputer, KNNImputer; from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder; from sklearn.decomposition import PCA; from sklearn.cluster import KMeans; from sklearn.neighbors import NearestNeighbors; print('✓ sklearn components OK')" && \
		python -c "from keras.layers import Normalization; print('✓ Keras OK')" && \
		echo "" && \
		echo "📋 Jupyter kernel:" && \
		jupyter kernelspec list | grep $(VENV_NAME) || echo "⚠️  Kernel not found"
	@echo ""
	@echo "✅ Verification complete!"

clean: ## Cleanup (remove venv, uninstall jupyter kernel)
	@echo "🧹 Cleaning up..."
	@echo "🗑️  Removing virtualenv $(VENV_NAME)..."
	@pyenv uninstall -f $(VENV_NAME) || echo "ℹ️  virtualenv '$(VENV_NAME)' not found"
	@echo "🗑️  Uninstalling Jupyter kernel..."
	@jupyter kernelspec uninstall -y $(VENV_NAME) || echo "ℹ️  Jupyter kernel '$(VENV_NAME)' not found"
	@echo "✅ Cleanup complete!"


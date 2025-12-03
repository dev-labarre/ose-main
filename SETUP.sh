#!/bin/bash
# Python 3.10 env setup via pyenv for OSE project
# Copy-paste these commands or run: bash SETUP.sh

set -e  # Exit on error

echo "🚀 Setting up Python 3.10 environment for OSE project..."

# Install Python 3.10.6 (if not already installed)
echo "📦 Installing Python 3.10.6..."
pyenv install -s 3.10.6

# Create virtualenv named ose-env
echo "🔧 Creating virtualenv ose-env..."
pyenv virtualenv 3.10.6 ose-env

# Activate the environment
echo "✅ Activating ose-env..."
pyenv activate ose-env

# Upgrade pip first
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install project requirements
echo "📚 Installing project requirements..."
pip install -r requirements.txt

# Register kernel for Jupyter
echo "🔗 Registering Jupyter kernel..."
python -m ipykernel install --user --name ose-env --display-name "Python (ose-env)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Verification commands:"
echo "  python -V"
echo "  python -c \"import pandas, sklearn, xgboost, keras, tensorflow; print('OK')\""
echo "  jupyter kernelspec list"
echo ""
echo "🎯 To activate the environment in the future:"
echo "  pyenv activate ose-env"


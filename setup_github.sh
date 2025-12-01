#!/bin/bash

set -e

echo "🚀 Setting up GitHub repository for OSE project..."

# Initialize git if not already done
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📝 Adding files..."
git add .

# Commit
echo "💾 Committing..."
git commit -m "Initial commit: OSE project structure" || echo "No changes to commit"

# Create GitHub repo and push
echo "🔨 Creating GitHub repository..."
gh repo create ose-main \
    --public \
    --description "Opportunity Scoring Engine (OSE) - Moteur de scoring d'opportunité basé sur signaux d'activité" \
    --source=. \
    --remote=origin \
    --push

echo "✅ Repository created and pushed!"
echo "📍 Repository URL: https://github.com/dev-labarre/ose-main"


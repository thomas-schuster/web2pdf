#!/bin/bash
set -e

echo "🚀 Running local CI simulation..."

echo "📁 Working directory: $(pwd)"

echo "🐍 Python version:"
python3 --version

echo "📦 Installing dependencies..."
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -r requirements-dev.txt

echo "🔍 Running flake8 linting..."
.venv/bin/flake8 . --count --statistics

echo "⚫ Checking code formatting with black..."
.venv/bin/black --check --diff .

echo "📝 Checking import sorting with isort..."
.venv/bin/isort --check-only --diff .

echo "🧪 Running tests with pytest..."
.venv/bin/pytest tests/ -v

echo "✅ All checks passed! GitHub Actions should work."

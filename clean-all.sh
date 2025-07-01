#!/bin/bash
# Limpa caches e arquivos temporários do projeto (backend e frontend)

# Limpa cache do npm (frontend)
cd frontend && npm cache clean --force && cd ..

# Limpa cache do pip (backend)
pip cache purge

# Limpa cache do pytest
rm -rf .pytest_cache

# Limpa arquivos de cobertura
rm -f .coverage

# Limpa banco de dados de teste
rm -f test.db

# Limpa pycache
find . -type d -name '__pycache__' -exec rm -rf {} +

echo "Cache e arquivos temporários limpos."

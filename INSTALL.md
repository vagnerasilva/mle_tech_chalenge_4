# 📦 Instalação de Dependências

## 🎯 Quick Start

### Opção 1: Desenvolvimento (Recomendado para trabalhar localmente)

```bash
# Setup inicial
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou: venv\Scripts\activate  # Windows

# Instalar TUDO (produção + testes + dev tools)
pip install -r requirements-dev.txt

# Pronto! Agora pode:
uvicorn app.main:app --reload      # Rodar API
pytest tests/ -v                    # Rodar testes
black .                             # Formatar código
```

### Opção 2: Produção (Render.com e deploy)

```bash
# Instalar APENAS produção (sem testes, sem overhead)
pip install -r requirements.txt

# Rodar API
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📋 O que está em cada arquivo?

### `requirements.txt` (PRODUÇÃO - 11 libs)
✅ Essencial para rodar a API

```
fastapi              → Framework web
uvicorn              → Servidor ASGI
pydantic-settings    → Configurações
yfinance             → Dados financeiros
pandas               → Manipulação de dados
numpy                → Cálculos
joblib               → Serialização
scikit-learn==1.6.1  → Preprocessing (fixado!)
tensorflow           → Deep Learning (LSTM)
sqlalchemy           → Banco de dados
```

### `requirements-dev.txt` (DESENVOLVIMENTO - 14 libs)
✅ Inclui produção + ferramentas de dev/teste

**Produção**: (tudo acima)

**Testes**:
```
pytest==7.4.3        → Framework de testes
pytest-cov==4.1.0    → Cobertura
pytest-asyncio==0.23 → Testes async
httpx==0.25.2        → Client HTTP
```

**Dev Tools**:
```
black                → Formatação de código
flake8               → Linting
mypy                 → Type checking
```

---

## 🚀 Instalação por Cenário

### 1️⃣ Desenvolvimento Local (Você agora)

```bash
pip install -r requirements-dev.txt
```

**Inclui**: API + Testes + Tools  
**Uso**: Desenvolver, testar, formatar código

---

### 2️⃣ Apenas API (sem testes)

```bash
pip install -r requirements.txt
```

**Inclui**: API apenas  
**Uso**: Rodar em produção, staging

---

### 3️⃣ CI/CD (GitHub Actions, etc)

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

**Ou**:

```bash
pip install -r requirements-dev.txt
```

**Inclui**: Tudo para rodar testes  
**Uso**: Pipeline de validação

---

### 4️⃣ Render.com (Automático)

```bash
# Render detecta requirements.txt automaticamente
# Não instala requirements-dev.txt
pip install -r requirements.txt
```

---

## 📊 Tamanho das Dependências

| Arquivo | Libs | Tamanho | Uso |
|---------|------|---------|-----|
| **requirements.txt** | 11 | ~500MB | Produção ✅ |
| **requirements-dev.txt** | 14 | ~550MB* | Dev + Testes ✅ |

*Com pytest e dev tools adicionados

---

## ✅ Verificação

Após instalação:

```bash
# Verificar instalação (produção)
python -c "from fastapi import FastAPI; import tensorflow; print('✅ Produção OK')"

# Verificar instalação (desenvolvimento)
python -c "import pytest; import black; print('✅ Desenvolvimento OK')"
```

---

## 🔧 Atualizações

### Adicionar nova lib de PRODUÇÃO

```bash
# 1. Edite requirements.txt e adicione a lib
echo "nova-lib" >> requirements.txt

# 2. Instale
pip install -r requirements.txt

# 3. Teste
python -c "import nova_lib"

# 4. Commit
git add requirements.txt
git commit -m "feat: adicionar nova-lib"
```

### Adicionar nova lib de DESENVOLVIMENTO

```bash
# 1. Edite requirements-dev.txt e adicione a lib
echo "nova-lib-dev" >> requirements-dev.txt

# 2. Instale
pip install -r requirements-dev.txt

# 3. Teste
python -c "import nova_lib_dev"

# 4. Commit
git add requirements-dev.txt
git commit -m "feat: adicionar nova-lib-dev para desenvolvimento"
```

---

## ⚠️ Importante: Scikit-learn Fixado

```
scikit-learn==1.6.1
```

- Usado para treinar o modelo (ml/scaler.pkl)
- **NÃO MUDE** sem retreinar o modelo
- Alterar causa `InconsistentVersionWarning`
- Pode afetar precisão das predições

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'pytest'"

```bash
# Você instalou apenas requirements.txt
# Para testes, instale requirements-dev.txt também:
pip install -r requirements-dev.txt
```

### "InconsistentVersionWarning" (scikit-learn)

```bash
# Versão de scikit-learn está diferente
pip install scikit-learn==1.6.1
```

### Limpar e reinstalar tudo

```bash
# Remover venv
rm -rf venv/

# Recrear
python -m venv venv
source venv/bin/activate

# Reinstalar (dev completo)
pip install -r requirements-dev.txt
```

---

**Status**: ✅ Pronto para usar  
**Data**: 2026-07-13

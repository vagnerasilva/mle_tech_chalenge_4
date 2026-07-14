# 🔧 Configuração de Variáveis de Ambiente

Este guia explica como configurar a API para diferentes ambientes (local vs. produção).

## 📋 Arquivos

- **`.env.example`** — Template com todas as variáveis disponíveis
- **`.env`** — Configuração LOCAL (ignorado pelo git)
- **Render.com Dashboard** — Configuração PRODUÇÃO (via web UI)

---

## 🏠 Ambiente Local (Desenvolvimento)

### Setup Inicial

```bash
# 1. Copie o template (se ainda não tiver .env)
cp .env.example .env

# 2. Edite .env com valores locais
# (arquivo já vem com defaults apropriados)

# 3. Ative o ambiente virtual
source venv/bin/activate

# 4. Instale dependências
pip install -r requirements.txt

# 5. Rode a API
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Variáveis Locais (`.env`)

```bash
# App básico
APP_APP_NAME=Previsão de Preços de Ações — LSTM
APP_CORS_ORIGINS=["*"]  # Aceita qualquer origem em dev

# Caminhos (relativo ao repo root)
APP_MODEL_PATH=ml/modelo_lstm.keras
APP_SCALER_PATH=ml/scaler.pkl
APP_DB_PATH=app_logs.db

# Modelo
APP_LOOK_BACK=30
APP_FEATURE_COLS=["Close", "High", "Low", "Open", "Volume"]

# Rate Limiting (máximo 10 req por IP em 5 minutos)
APP_RATE_LIMIT_MAX_REQUESTS=10
APP_RATE_LIMIT_WINDOW_SECONDS=300

# Server
PORT=8000
HOST=127.0.0.1  # Apenas localhost em dev

# Debug
LOG_LEVEL=INFO
DEBUG=False  # Mude para True se precisar debug
```

### Como Funciona

```python
# app/core/config.py usa pydantic-settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",  # Prefixo das variáveis
        env_file=".env"     # Carrega de .env na raiz
    )
```

**Precedência** (do maior para menor):
1. Variáveis de ambiente do sistema (`export APP_*=...`)
2. Arquivo `.env` na raiz do projeto
3. Valores padrão no código (`app_name: str = "..."`)

---

## 🚀 Ambiente Produção (Render.com)

### Configuração no Render Dashboard

1. Acesse seu serviço no Render.com
2. Vá para **Settings** → **Environment**
3. Adicione as variáveis conforme abaixo

### Variáveis de Produção

```bash
# App básico
APP_APP_NAME=Previsão de Preços de Ações — LSTM
APP_CORS_ORIGINS=["https://seu-frontend.com"]  # Apenas domínios confiáveis

# Caminhos (IGUAIS ao local, mas resolvedidos do repo root)
APP_MODEL_PATH=ml/modelo_lstm.keras
APP_SCALER_PATH=ml/scaler.pkl
APP_DB_PATH=/tmp/app_logs.db  # Temp no Render (não persiste)

# Modelo (CRÍTICO: não mudar sem retreinar!)
APP_LOOK_BACK=30
APP_FEATURE_COLS=["Close", "High", "Low", "Open", "Volume"]

# Server (Render.com passa PORT automaticamente)
# NÃO DEFINA PORT aqui — Render já a configura
# Deixe HOST como 0.0.0.0 para aceitar conexões externas
HOST=0.0.0.0

# Debug
LOG_LEVEL=WARNING  # Menos verbose em produção
DEBUG=False        # NUNCA ativar em produção
```

### Configuração de Rate Limiting

As variáveis `APP_RATE_LIMIT_*` controlam a proteção contra abuso:

**APP_RATE_LIMIT_MAX_REQUESTS** (padrão: 10)
- Número máximo de requisições permitidas por IP
- Janela de tempo: APP_RATE_LIMIT_WINDOW_SECONDS
- **Exemplo**: 10 = máximo 10 requisições por IP

**APP_RATE_LIMIT_WINDOW_SECONDS** (padrão: 300 = 5 minutos)
- Duração da janela de contagem em segundos
- **Exemplo**: 300 = 5 minutos, 600 = 10 minutos
- 11ª requisição na mesma janela retorna **429 Too Many Requests**

**Exemplos de Configuração:**

```bash
# Padrão (produção recomendado)
APP_RATE_LIMIT_MAX_REQUESTS=10
APP_RATE_LIMIT_WINDOW_SECONDS=300  # 5 min

# Menos restritivo (testes)
APP_RATE_LIMIT_MAX_REQUESTS=50
APP_RATE_LIMIT_WINDOW_SECONDS=600  # 10 min

# Muito restritivo (segurança máxima)
APP_RATE_LIMIT_MAX_REQUESTS=5
APP_RATE_LIMIT_WINDOW_SECONDS=60   # 1 min
```

**Endpoints NÃO afetados por rate limit:**
- `/health` — sempre permitido (monitoramento)
- `/readiness` — sempre permitido (orchestração)

Para mais detalhes: 📖 [rate-limiting.md](rate-limiting.md)

---

### Observações Importantes

#### 1. **PORT em Produção**
- Render.com **passa automaticamente** via variável `PORT`
- Não defina PORT no dashboard — deixe que Render controle
- `app/main.py` detecta automaticamente:
  ```python
  port = int(os.environ.get("PORT", 8000))  # Default 8000, Render define PORT
  ```

#### 2. **HOST em Produção**
- **Local**: `127.0.0.1` (apenas máquina local)
- **Produção**: `0.0.0.0` (aceita requisições externas)

#### 3. **Banco de Dados**
- **Local**: `app_logs.db` (arquivo local, persiste)
- **Produção**: `/tmp/app_logs.db` (temp no Render, limpo ao deploy)
  - Para persistência real, use PostgreSQL ou similar

#### 4. **CORS**
- **Local**: `["*"]` (aceita qualquer origem para testes)
- **Produção**: `["https://seu-frontend.com"]` (apenas domínios confiáveis)

#### 5. **Model & Scaler**
- **OBRIGATÓRIO** existir em `ml/modelo_lstm.keras` e `ml/scaler.pkl`
- Se não existirem, `GET /readiness` retorna 503
- Nunca mude esses caminhos sem retreinar!

---

## 🔐 Segurança — Boas Práticas

### ✅ Faça:

```bash
# ✅ Adicione .env ao .gitignore
echo ".env" >> .gitignore

# ✅ Commite .env.example (template)
git add .env.example
git commit -m "docs: adicionar template de variáveis de ambiente"

# ✅ Use variáveis secretas no Render
# - Senhas, API keys, tokens → Render Settings → Environment

# ✅ Configure CORS restritivamente em produção
APP_CORS_ORIGINS=["https://seu-frontend.com","https://app.seu-domain.com"]
```

### ❌ Não Faça:

```bash
# ❌ NÃO commite .env
git add .env  # Evite!

# ❌ NÃO coloque segredos no .env.example
# Deixe como exemplo genérico

# ❌ NÃO use CORS=["*"] em produção
# Aceita requisições de qualquer lugar

# ❌ NÃO deixe DEBUG=True em produção
# Expõe informações sensíveis em erros

# ❌ NÃO mude LOOK_BACK, FEATURE_COLS ou paths sem retreinar
# Invalida previsões
```

---

## 📋 Checklist de Deploy

Antes de fazer push para produção:

- [ ] Arquivo `.env` NÃO foi commitado (está em `.gitignore`)
- [ ] `.env.example` foi commitado (serve de referência)
- [ ] Variáveis críticas foram definidas no Render dashboard:
  - [ ] `APP_MODEL_PATH` e `APP_SCALER_PATH` corretos
  - [ ] `APP_LOOK_BACK=30` (mesmo do treino)
  - [ ] `APP_FEATURE_COLS` bate com features do notebook
- [ ] `CORS_ORIGINS` está restritivo (não `["*"]`)
- [ ] `DEBUG=False`
- [ ] `LOG_LEVEL=WARNING`
- [ ] Modelo e scaler existem em `ml/`
- [ ] Testes passam localmente: `pytest -v`
- [ ] API inicia sem erros localmente: `uvicorn app.main:app`

---

## 🔍 Diagnóstico

### API não encontra modelo

```bash
# Erro esperado:
GET /readiness → 503 {"ready": false, "detail": "Artefatos do modelo não encontrados"}

# Solução:
# 1. Verifique APP_MODEL_PATH no .env (local) ou Render (produção)
# 2. Confirme que ml/modelo_lstm.keras e ml/scaler.pkl existem
# 3. Teste com: python -c "from ml.model import artifacts_available; print(artifacts_available(...))"
```

### Variáveis não carregam

```bash
# Debug: print das variáveis carregadas
python -c "from app.core.config import get_settings; s = get_settings(); print(vars(s))"

# Checklist:
# 1. .env está na raiz do projeto (mesmo nível de requirements.txt)
# 2. Nomes das variáveis têm prefixo APP_ (ex: APP_LOOK_BACK)
# 3. Tipos estão corretos (int para números, list/string para valores)
# 4. Ativou venv? (às vezes .env não é lido sem venv ativo)
```

### CORS bloqueando requisições

```bash
# Erro esperado em dev tools:
# "Access to XMLHttpRequest blocked by CORS policy"

# Solução local:
APP_CORS_ORIGINS=["*"]

# Solução produção:
APP_CORS_ORIGINS=["https://seu-frontend.com"]

# Teste curl:
curl -H "Origin: https://seu-frontend.com" http://localhost:8000/health -v
```

---

## 📚 Referências

- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Render.com Environment Variables](https://render.com/docs/environment-variables)
- [CORS em FastAPI](https://fastapi.tiangolo.com/tutorial/cors/)

---

## 💡 Exemplo: Adicionar Nova Variável

Se precisar adicionar uma nova configuração:

### 1. Adicione em `app/core/config.py`

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")
    
    app_name: str = "..."
    my_new_setting: str = "valor_padrao"  # ← nova variável
```

### 2. Atualize `.env.example`

```bash
# Nova seção em .env.example
APP_MY_NEW_SETTING=valor_padrao
```

### 3. Atualize `.env` (local)

```bash
APP_MY_NEW_SETTING=valor_local
```

### 4. Configure no Render

Dashboard → Settings → Environment:
```
APP_MY_NEW_SETTING=valor_producao
```

### 5. Use no código

```python
from app.core.config import get_settings

settings = get_settings()
print(settings.my_new_setting)  # "valor_producao" (Render) ou "valor_local" (dev)
```

---

**Última atualização**: 2026-07-13  
**Status**: ✅ Pronto para uso

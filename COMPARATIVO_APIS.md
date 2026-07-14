# 📊 Comparativo: Nossa API vs Referência (referencia2)

## 🎯 Resumo Executivo

| Aspecto | Nossa API | Referência |
|---------|-----------|-----------|
| **Foco** | Simples, com rate limiting | Completa, com monitoramento full-stack |
| **Rate Limiting** | ✅ SQLite (implementado) | ❌ Não presente |
| **Logging** | ✅ Simples (request/response) | ✅ Detalhado (duração, IPs, erro stack) |
| **Frontend** | ❌ Não | ✅ React/Vite (SPA) |
| **Database** | ✅ Centralizado (database.db) | ✅ Separado (models/scalers/data) |
| **Configuração** | ✅ .env com APP_* prefix | ⚠️ Mínima (apenas ENVIRONMENT) |
| **Routers** | 2 (predict, metrics) | 7+ (predict, model, data, monitoring, ml, health, home) |
| **Requirements** | 11 (prod) + 4 (dev) | 11 base |

---

## 📁 Estrutura de Diretórios

### Nossa API (`mle_tech_chalenge_4/`)

```
mle_tech_chalenge_4/
├── app/
│   ├── core/
│   │   └── config.py              # Pydantic Settings com env_prefix="APP_"
│   ├── api/
│   │   └── v1/
│   │       ├── predict.py          # Routes: /predict/single, /predict/sequence
│   │       └── metrics.py          # Routes: /metrics/latest
│   ├── models/
│   │   └── logs.py                # SQLAlchemy: ApiLog, RateLimitLog
│   ├── services/
│   │   ├── prediction_service.py
│   │   └── rate_limit_service.py  # ⭐ Rate Limiting (SQL-based)
│   └── main.py                    # FastAPI setup + middleware
├── ml/
│   ├── model.py                   # load_model(), load_scaler()
│   ├── inference.py               # predict_next_close(), predict_sequence()
│   ├── data.py                    # fetch_ohlcv()
│   └── preprocessing.py           # apply_log1p(), inverse_close()
├── artifacts/                     # ⭐ Centralized artifacts
│   ├── modelo_lstm.keras
│   └── scaler.pkl
├── data/                          # ⭐ Centralized database
│   └── database.db               # Rate limit logs + API logs
├── tests/
│   └── test_rate_limit.py
├── .env                          # ✅ Local config with rate limit vars
├── .env.example                  # Template
├── requirements.txt              # Produção
├── requirements-dev.txt          # Dev + testes
├── INSTALL.md
└── README.md
```

### Referência (`referencia/referencia2/`)

```
referencia2/
├── app/
│   ├── settings.py               # Minimal: apenas ENVIRONMENT
│   ├── dependencies.py           # Injeção de deps
│   ├── app.py                    # FastAPI + middleware + static
│   ├── models/
│   │   ├── base.py              # SQLAlchemy Base + engine
│   │   ├── logs.py              # ApiLog model
│   │   └── predict.py           # Request/Response Pydantic
│   ├── routers/                 # 7+ routers
│   │   ├── predict.py
│   │   ├── model.py
│   │   ├── data.py
│   │   ├── monitoring.py
│   │   ├── ml.py
│   │   ├── health.py
│   │   └── home.py
│   ├── services/
│   │   ├── model_service.py
│   │   ├── log.py
│   │   └── ...
│   ├── utils/
│   │   └── constants.py          # API_PREFIX, logger
│   └── static/                   # React/Vite build (SPA)
│       └── index.html
├── ml/
│   ├── model.py
│   ├── inference.py
│   ├── data.py
│   └── preprocessing.py
├── models/
│   ├── saved/                    # Modelos treinados
│   └── scalers/                  # Scalers separados
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── train_model.py
│   ├── collect_data.py
│   └── evaluate_model.py
├── notebooks/                    # Análise/exploração
├── tests/
│   ├── test_predict.py
│   ├── test_health.py
│   ├── test_logs.py
│   └── ...
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuração

### Nossa API: Pydantic Settings (Robusto)

**`app/core/config.py`:**
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")
    
    # Modelados explicitamente com tipos
    model_path: Path = REPO_ROOT / "artifacts" / "modelo_lstm.keras"
    scaler_path: Path = REPO_ROOT / "artifacts" / "scaler.pkl"
    db_path: Path = REPO_ROOT / "data" / "database.db"
    look_back: int = 30
    rate_limit_max_requests: int = 10
    rate_limit_window_seconds: int = 300

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**`.env` (exemplo):**
```
APP_MODEL_PATH=artifacts/modelo_lstm.keras
APP_SCALER_PATH=artifacts/scaler.pkl
APP_DB_PATH=data/database.db
APP_RATE_LIMIT_MAX_REQUESTS=10
APP_RATE_LIMIT_WINDOW_SECONDS=300
```

**Vantagens:**
- ✅ Type-safe (Pydantic valida tipos)
- ✅ Env prefix (`APP_*`) evita poluição de namespace
- ✅ Valores padrão bem definidos
- ✅ Validação automática

---

### Referência: Minimal

**`app/settings.py`:**
```python
class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    model_config = SettingsConfigDict(env_file="app/.env")

settings = Settings()
```

**Vantagens:**
- ✅ Simples, sem overhead
- ❌ Sem type hints para outros configs
- ❌ Sem valores padrão para caminhos (hardcoded em múltiplos places)

---

## 🔒 Rate Limiting

### Nossa API: ✅ Implementado

**`app/services/rate_limit_service.py`:**
- SQLite backend (não Redis)
- Middleware em `app/main.py`
- Retorna HTTP 429 com `Retry-After` header
- Tabela `RateLimitLog` com IP e timestamp
- Janelas deslizantes de 5 minutos

**Middleware (app/main.py):**
```python
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/readiness"]:
        return await call_next(request)
    
    ip = request.client.host
    allowed, retry_after = rate_limit_service.check_and_log(ip)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(retry_after)},
            content={"detail": "Rate limit exceeded"}
        )
    return await call_next(request)
```

**Configuração via .env:**
```
APP_RATE_LIMIT_MAX_REQUESTS=10
APP_RATE_LIMIT_WINDOW_SECONDS=300
```

---

### Referência: ❌ Não Implementado

- Sem middleware de rate limiting
- Sem proteção contra abuso
- Sem controle de requisições por IP

---

## 📊 Logging & Monitoramento

### Nossa API: Básico

**`app/main.py` - Middleware simples:**
```python
async def log_requests_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    # Log armazenado em ApiLog no database.db
    return response
```

**Database único:**
- `data/database.db` centraliza:
  - `ApiLog` (requisições/respostas)
  - `RateLimitLog` (IPs e timestamps)

---

### Referência: Detalhado

**`app/app.py` - Middleware sofisticado:**
```python
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    req_body = await request.json()  # Captura body da requisição
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    
    res_body = [section async for section in response.body_iterator]
    # Converte response body para string
    
    # Write log em background
    response.background = BackgroundTask(
        write_log,
        request,
        response,
        req_body,
        res_body,
        process_time,
    )
```

**Vantagens:**
- ✅ Captura body completo (request + response)
- ✅ Tempo de processamento preciso
- ✅ Background tasks (não bloqueia response)
- ✅ Exception handling centralizado

---

## 🗄️ Database

### Nossa API: Centralizado

**Arquivo único:** `data/database.db`

**Tabelas:**
```python
class ApiLog(Base):
    id: UUID
    timestamp: datetime
    method: str
    path: str
    status_code: int
    response_time_ms: float
    ip_address: str

class RateLimitLog(Base):
    id: UUID
    ip_address: str (indexed)
    requested_at: datetime (indexed)
```

**Vantagens:**
- ✅ Único arquivo de banco
- ✅ Simples de backup/migração
- ✅ Logs + rate limit juntos

---

### Referência: Distribuído

**Estrutura:**
```
models/
├── saved/       # Modelos treinados (.keras, .h5)
├── scalers/     # Scalers (.pkl, .joblib)
data/
├── raw/         # Dados brutos (CSV)
└── processed/   # Dados processados
```

**Database:**
- `app.db` (ou similar)
- Apenas para `ApiLog`

---

## 🛣️ Routers (Endpoints)

### Nossa API: Minimalista

| Rota | Método | Função |
|------|--------|--------|
| `/api/v1/predict/single` | POST | Prevê próximo día |
| `/api/v1/predict/sequence` | POST | Prevê N dias |
| `/api/v1/metrics/latest` | GET | Últimas métricas |

**Uso:**
```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol": "PETR4.SA"}'
```

---

### Referência: Completa (7+ routers)

| Router | Endpoints | Função |
|--------|-----------|--------|
| `predict.py` | POST `/api/v1/predict` | Predição |
| `model.py` | GET/POST `/api/v1/model/*` | Treinar, info modelo |
| `data.py` | GET/POST `/api/v1/data/*` | Coletar, processar dados |
| `ml.py` | GET `/api/v1/ml/*` | Features, métricas ML |
| `monitoring.py` | GET `/api/v1/monitoring/*` | Dashboard, health |
| `health.py` | GET `/api/v1/health` | Status da API |
| `home.py` | GET `/api/v1/home` | Info geral |
| `log.py` | GET `/api_logs` | Recuperar logs |

**Endpoints extras:**
- `GET /` → Serve SPA (React frontend)
- `GET /static/*` → Arquivos estáticos
- `GET /{full_path:path}` → Catch-all para SPA

---

## 📦 Dependências

### Nossa API

**`requirements.txt` (11 libs):**
```
fastapi
uvicorn
pydantic-settings
yfinance
pandas
numpy
joblib
scikit-learn==1.6.1
tensorflow
sqlalchemy
```

**`requirements-dev.txt` (adiciona testes):**
```
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.23.0
httpx==0.25.2
black
flake8
mypy
```

---

### Referência

**`requirements.txt` (11 libs):**
```
yfinance
pandas
fastapi
uvicorn
numpy
matplotlib
seaborn
pandas
scikit-learn
tensorflow
joblib
```

**Diferenças:**
- ✅ Referência: inclui `matplotlib` e `seaborn` (visualização)
- ✅ Referência: sem `pydantic-settings` (usa Settings manual)
- ✅ Referência: sem `sqlalchemy` (usa ORM diferente ou raw SQL)
- ✅ Nossa: mais tooling de dev (black, flake8, mypy)

---

## 🔑 Principais Diferenças

### 1️⃣ Rate Limiting

| Aspecto | Nossa | Referência |
|---------|-------|-----------|
| **Implementado** | ✅ Sim | ❌ Não |
| **Backend** | SQLite | - |
| **Limite** | 10 req/IP/5min | - |
| **Resposta** | 429 + Retry-After | - |

**Conclusão:** Nossa API tem proteção contra abuso; referência não.

---

### 2️⃣ Configuração

| Aspecto | Nossa | Referência |
|---------|-------|-----------|
| **Tipo** | Pydantic Settings completo | Minimal |
| **Env prefix** | `APP_*` | Nenhum |
| **Type hints** | ✅ Completo | ❌ Apenas ENVIRONMENT |
| **Validação** | ✅ Automática | ❌ Manual |
| **Padrões** | ✅ Bem definidos | ⚠️ Hardcoded |

**Conclusão:** Nossa API é mais robusta; referência é mais simples.

---

### 3️⃣ Database

| Aspecto | Nossa | Referência |
|---------|-------|-----------|
| **Artefatos** | Centralizados (artifacts/) | Separados (models/saved, models/scalers) |
| **Dados** | Centralizados (data/) | Separados (data/raw, data/processed) |
| **Logs** | Uma tabela (database.db) | Uma tabela (app.db?) |
| **Rate limit** | Sim (RateLimitLog) | Não existe |

**Conclusão:** Nossa é mais centralizada; referência é mais modular.

---

### 4️⃣ Frontend

| Aspecto | Nossa | Referência |
|---------|-------|-----------|
| **Frontend** | ❌ Não tem | ✅ React/Vite (SPA) |
| **Rota** | - | `GET /` → index.html |
| **Catch-all** | - | `GET /{path}` → SPA |
| **Static files** | - | `/static` (assets) |

**Conclusão:** Referência é um full-stack; nossa é API-only.

---

### 5️⃣ Routers

| Aspecto | Nossa | Referência |
|---------|-------|-----------|
| **Quantidade** | 2 (predict, metrics) | 7+ (predict, model, data, monitoring, ml, health, home) |
| **Funcionalidade** | Predição apenas | Predição + treino + monitoramento |
| **Scope** | Inference | Full ML lifecycle |

**Conclusão:** Referência é mais completa; nossa é focused.

---

### 6️⃣ Logging

| Aspecto | Nossa | Referência |
|---------|-------|-----------|
| **Captura body** | ❌ Não | ✅ Sim |
| **Request** | ✅ Header | ✅ Header + body |
| **Response** | ✅ Status | ✅ Status + body |
| **Timing** | ✅ Response time | ✅ Process time |
| **Exceptions** | ⚠️ Básico | ✅ Completo (SQLAlchemyError, etc) |
| **Background** | ❌ Síncrono | ✅ BackgroundTask |

**Conclusão:** Referência tem logging mais sofisticado.

---

## 🎯 Quando Usar Cada Uma?

### Nossa API é Melhor Para:
✅ Produção com rate limiting mandatório  
✅ Projetos simples de predição  
✅ Quando não precisa treinar modelos via API  
✅ Deployment rápido em Render  
✅ Quando `APP_*` prefix evita conflicts  

### Referência é Melhor Para:
✅ Desenvolvimento completo de ML models  
✅ Treino de modelos via API (`POST /api/v1/model/train`)  
✅ Interface web para monitoramento  
✅ Coleta de dados contínua  
✅ Análise exploratória (notebooks)  
✅ Full-stack (backend + frontend)  

---

## 🔄 Lições Aprendidas

### Do Comparativo

| Conceito | Nossa | Melhor | Razão |
|----------|-------|--------|-------|
| **Configuração** | Pydantic Settings | ✅ Nossa | Type-safe |
| **Database** | Centralizado | ✅ Nossa | Simples |
| **Rate limiting** | SQLite | ✅ Nossa | Implementado |
| **Logging** | Básico | ❌ Referência | Captura bodies |
| **Frontend** | Não tem | ❌ Referência | UX melhor |
| **ML lifecycle** | Inference só | ❌ Referência | Mais features |

### O Que Nossa API Faz Bem
1. **Rate Limiting** — Proteção contra abuso com SQLite
2. **Configuração Robusta** — Pydantic Settings com validação
3. **Database Centralizado** — Um arquivo para tudo
4. **Requirements Separados** — Prod vs Dev claros
5. **Documentação** — .env.example, INSTALL.md, etc

### O Que Poderíamos Melhorar
1. **Logging Completo** — Capturar bodies como referência faz
2. **Frontend** — Adicionar SPA para monitoramento
3. **ML Lifecycle** — Endpoint para treinar modelos
4. **Exceções** — Middleware mais sofisticado como referência

---

## 📝 Conclusão

**Nossa API** é uma implementação **focada e segura**:
- ✅ Rate limiting (diferencial)
- ✅ Configuração robusta
- ✅ Pronta para produção
- ✅ Sem overhead desnecessário

**Referência** é uma implementação **completa e exploratória**:
- ✅ Full-stack (backend + frontend)
- ✅ Treino de modelos via API
- ✅ Monitoramento visual
- ✅ Ideal para desenvolvimento

**Nossa API é mais production-ready; a referência é mais educational.**


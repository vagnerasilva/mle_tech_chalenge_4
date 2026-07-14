| ![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg) ![TensorFlow](https://img.shields.io/badge/framework-TensorFlow-FF6F00?logo=tensorflow) ![FastAPI](https://img.shields.io/badge/api-FastAPI-009688?logo=fastapi) ![LSTM](https://img.shields.io/badge/model-LSTM-blue.svg) ![Test Coverage](https://img.shields.io/badge/test%20coverage-target%3A70%25-green.svg) ![Render](https://img.shields.io/badge/deployed-Render.com-46E3B7?logo=render) ![MIT License](https://img.shields.io/badge/license-MIT-yellow.svg) |
|:-----------------------------------------------:|

# 📈 Tech Challenge Fase 4 - API de Previsão de Preços de Ações – Modelo LSTM

## 📌 Descrição

Este projeto faz parte do **Tech Challenge Fase 4** do programa Pós Tech MLET, cuja objetivo é aplicar conhecimentos avançados em **Deep Learning** e **Inteligência Artificial**, desenvolvendo uma solução completa e em produção para previsão de séries temporais financeiras.

O desafio consiste em criar uma **API RESTful** que serve um modelo de rede neural **LSTM (Long Short-Term Memory)** para predição de preços de fechamento de ações, com toda a pipeline de desenvolvimento: desde a coleta de dados históricos até o deploy em um ambiente de produção.

A arquitetura integra:
- 📊 **Coleta de dados** via [yfinance](https://finance.yahoo.com/) — histórico de preços de ações
- 🧠 **Modelo LSTM** para capturar padrões temporais em séries financeiras
- 🔄 **Pipeline de treinamento** com checkpoints e logs estruturados
- ⚡ **API FastAPI** para inferência em tempo real
- ✅ **Testes automatizados** para validação robusta

### 🌐 API em Produção

A API está deployada em **[https://mle-tech-chalenge-4.onrender.com/](https://mle-tech-chalenge-4.onrender.com/)** via Render.com

**Endpoints Principais:**
- **Health Check**: https://mle-tech-chalenge-4.onrender.com/health
- **Root Endpoint**: https://mle-tech-chalenge-4.onrender.com/
- **Documentação Swagger**: https://mle-tech-chalenge-4.onrender.com/docs
- **ReDoc**: https://mle-tech-chalenge-4.onrender.com/redoc

### 📊 Dashboard de Monitoramento em Produção

O dashboard de monitoramento está **disponível em produção**:

- **URL**: [https://mle-tech-chalenge-4-streamlit.onrender.com/](https://mle-tech-chalenge-4-streamlit.onrender.com/)
- **Repositório**: [mle_tech_chalenge_4_streamlit](https://github.com/vagnerasilva/mle_tech_chalenge_4_streamlit)
- **Features**:
  - 📈 Visualização de predições vs. valores reais
  - 📊 Gráficos de métricas do modelo (MAE, RMSE, MAPE)
  - 🔄 Histórico de treinamentos
  - ⚡ Performance e tempo de resposta da API
  - 📉 Análise de séries temporais

---

## 🎯 Objetivos do Projeto

✓ Coletar e pré-processar dados históricos de preços de ações  
✓ Construir e treinar um modelo LSTM robusto  
✓ Implementar uma API RESTful escalável e bem documentada  
✓ Disponibilizar endpoints de predição em lote e single-shot  
✓ Monitorar performance e métricas do modelo em produção  
✓ Garantir reprodutibilidade via Docker e documentação clara  

---

## ⚡ Acesso Rápido (Produção)

| O quê | Link | Descrição |
|--------|------|-----------|
| **API FastAPI** | [https://mle-tech-chalenge-4.onrender.com/](https://mle-tech-chalenge-4.onrender.com/) | Endpoints para predição e inferência |
| **Dashboard** | [https://mle-tech-chalenge-4-streamlit.onrender.com/](https://mle-tech-chalenge-4-streamlit.onrender.com/) | Visualização de métricas e performance |
| **Docs Swagger** | [https://mle-tech-chalenge-4.onrender.com/docs](https://mle-tech-chalenge-4.onrender.com/docs) | Documentação interativa |
| **Health Check** | [https://mle-tech-chalenge-4.onrender.com/health](https://mle-tech-chalenge-4.onrender.com/health) | Status da API |

---

## 🔐 Rate Limiting — Proteção contra Abuso

A API implementa **rate limiting automático** para proteger contra abusos:

### Limite Padrão
- **10 requisições por IP** em uma **janela de 5 minutos**
- 11ª requisição retorna **429 Too Many Requests**
- Contador reseta automaticamente após 5 minutos

### Comportamento

**Requisição Permitida (1-10):**
```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BBD"}'

# Response: 200 OK (ou 422 se dados insuficientes)
```

**Requisição Bloqueada (11+):**
```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BBD"}'

# Response: 429 Too Many Requests
# Header: Retry-After: 287
{
  "detail": "Limite de taxa excedido. Aguarde 287 segundos.",
  "retry_after": 287
}
```

### Endpoints Protegidos
- ✅ `POST /api/v1/predict/single` — Rate limited
- ✅ `POST /api/v1/predict/batch` — Rate limited
- ✅ `POST /api/v1/predict/sequence` — Rate limited
- ✅ `GET /api/v1/metrics/latest` — Rate limited
- ✅ `GET /api/v1/logs` — Rate limited

### Endpoints NÃO Afetados (Monitoramento)
- ❌ `GET /health` — Sem limite
- ❌ `GET /readiness` — Sem limite

**💡 Tip:** Usar `/health` para monitoramento contínuo sem preocupação com rate limit.

### Detalhes Técnicos
- **Storage**: SQLite (`rate_limit_logs`)
- **Janela deslizante**: Rastreia últimas 5 minutos
- **IP Detection**: Suporta proxies (X-Forwarded-For, X-Real-IP)
- **Limpeza automática**: Registros > 5 min removidos

Para mais detalhes: 📖 [docs/rate-limiting.md](docs/rate-limiting.md)

---

## 📊 Coleta de Dados

### Fonte de Dados
O script de coleta localizado em `script.py` utiliza a biblioteca **yfinance** para extrair dados históricos de preços de ações diretamente do Yahoo Finance.

**Exemplo de uso:**
```python
import yfinance as yf

# Configurar símbolo da empresa, data de início e fim
symbol = 'PETR4.SA'  # Petrobras (exemplo)
start_date = '2018-01-01'
end_date = '2024-07-20'

# Download dos dados
df = yf.download(symbol, start=start_date, end=end_date)
```

### Dados Coletados
Para cada dia de pregão, capturamos:
- **Open** — preço de abertura
- **High** — preço máximo do dia
- **Low** — preço mínimo do dia
- **Close** — preço de fechamento *(target)*
- **Volume** — volume de transações
- **Adj Close** — preço ajustado

### Pré-processamento
Os dados passam por transformações essenciais antes do treinamento:
- **Normalização**: Escalamento min-max para valores entre [0, 1]
- **Limpeza**: Remoção de valores faltantes e outliers
- **Janelas deslizantes**: Criação de sequências temporais (ex.: 60 dias → 1 predição)
- **Train/Val/Test split**: Divisão mantendo ordem temporal (80% treino, 10% validação, 10% teste)

---

## 🧠 Modelo LSTM

### 📓 Notebook de Desenvolvimento
O modelo LSTM é desenvolvido e validado no notebook disponível em [docs/fase4_pos_mlet_organizado_(1).ipynb](docs/fase4_pos_mlet_organizado_(1).ipynb).

**Este notebook inclui:**
- Coleta de dados via yfinance (NVDA como exemplo)
- Feature engineering com 17 indicadores técnicos
- Busca de hiperparâmetros com TimeSeriesSplit (5 folds)
- Treinamento robusto com callbacks avançados
- Avaliação completa com múltiplas métricas

### Arquitetura
O modelo usa **Bidirectional LSTM** para capturar padrões em ambas as direções temporais, com regularização L2 e BatchNormalization para estabilidade e redução de overfitting.

**Camadas (Otimizadas via TimeSeriesSplit):**
```
Input (Batch, LOOK_BACK, 17 Features)
    ↓
Bidirectional LSTM (units, return_sequences=True, L2 regularizer)
    ↓
BatchNormalization + Dropout
    ↓
LSTM (units // 2, return_sequences=True, L2 regularizer)
    ↓
BatchNormalization + Dropout
    ↓
LSTM (units // 4, return_sequences=False)
    ↓
BatchNormalization + Dropout (reduzido)
    ↓
Dense Layer (32, activation='relu', L2 regularizer)
    ↓
Output Layer (1) — Predição de Preço
```

### Feature Engineering (17 Features)
O modelo utiliza **17 features** construídas a partir dos dados OHLCV:

| Categoria | Features | Descrição |
|-----------|----------|----------|
| **Preço** | Close, High, Low, Open | OHLC direto |
| **Volume** | Volume, Volume_MA_7, Volume_Ratio | Liquidez e intensidade |
| **Tendência** | MA_7, MA_21, Ratio_MA7_MA21, Return_1d | Médias móveis e retorno |
| **Volatilidade** | Volatility_7d, RSI_14, MACD, MACD_Signal | Indicadores técnicos |
| **Bandas** | BB_Upper, BB_Lower | Bandas de Bollinger (20 dias) |

**Preprocessamento:**
- ✅ `RobustScaler` fit apenas no treino (sem data leakage)
- ✅ Sequências deslizantes com `LOOK_BACK` otimizado (60+ dias)
- ✅ Split temporal: 70% treino | 15% validação | 15% teste

### Hiperparâmetros Otimizados
- **LOOK_BACK**: 60-90 dias (otimizado via TimeSeriesSplit)
- **Units**: 64-128 (camada Bidirectional)
- **Dropout**: 0.2-0.3 (com redução nas camadas posteriores)
- **Batch Size**: 32
- **Learning Rate**: 0.001 (Adam optimizer)
- **Loss Function**: Huber (robusto a outliers)
- **Validation Split**: 15% independente

### Métricas de Avaliação

| Métrica | Descrição | Escala |
|---------|-----------|--------|
| **MAE** | Erro Médio Absoluto | USD |
| **RMSE** | Raiz do Erro Quadrático Médio | USD |
| **MAPE** | Erro Percentual Absoluto Médio | % |
| **Directional Accuracy** | Taxa de acerto da direção do movimento | % |

**Exemplo de Resultado (Teste):**
```
MAE:                $X.XXXX
RMSE:               $X.XXXX
MAPE:               X.XX%
Direcional Accuracy: XX.XX%
```

Todas as métricas são calculadas na **escala original (USD)** para melhor interpretação.

### 🔄 Pipeline: Do Notebook para a API

**Fluxo de Produção:**

```
┌─────────────────────────────────────────────────────────────┐
│  1. Notebook (docs/fase4_pos_mlet_organizado_(1).ipynb)    │
│     ✓ Carrega dados via yfinance                            │
│     ✓ Constrói 17 features com engenharia de features      │
│     ✓ Busca hiperparâmetros (TimeSeriesSplit 5-fold)       │
│     ✓ Treina Bidirectional LSTM com callbacks              │
│     ✓ Salva: best_lstm_model.keras + scaler.pkl           │
└────────────────────┬────────────────────────────────────────┘
                     │ Artifacts gerados
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Produção (models/)                                       │
│     ├── best_lstm_model.keras  (modelo treinado)           │
│     └── scaler.pkl             (RobustScaler persistido)   │
└────────────────────┬────────────────────────────────────────┘
                     │ Carregado na inicialização
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  3. FastAPI (app/services/model.py)                         │
│     ✓ Carrega modelo e scaler                               │
│     ✓ Preprocessa input com as mesmas 17 features          │
│     ✓ Normaliza com scaler salvo (consistência)            │
│     ✓ Realiza predição com LOOK_BACK sequências            │
│     ✓ Desnormaliza resultado para USD                      │
└────────────────────┬────────────────────────────────────────┘
                     │ Response
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Dashboard (Streamlit)                                   │
│     📊 Visualiza predições vs. reais                        │
│     📈 Monitora métricas (MAE, RMSE, MAPE, Directional)   │
│     ⚡ Tempo de resposta da API                            │
└─────────────────────────────────────────────────────────────┘
```

**Garantias de Consistência:**
- ✅ Features construídas identicamente (mesmo código)
- ✅ RobustScaler persistent preserva parâmetros fit
- ✅ LOOK_BACK e architecture idênticos entre notebook e API
- ✅ Sem divergência entre treinamento e inferência

### Estratégia de Treinamento

**Callbacks Avançados:**
- 🛑 **EarlyStopping** (patience=15): interrompe se `val_loss` não melhorar por 15 épocas
- 📉 **ReduceLROnPlateau** (factor=0.5, patience=7): divide learning rate em platôs
- 💾 **ModelCheckpoint**: salva melhor modelo automaticamente em `best_lstm_model.keras`

**Validação:**
- ✅ **TimeSeriesSplit (5-fold)**: busca de hiperparâmetros mantendo ordem temporal
- ✅ Épocas até 150 com early stopping dinâmico
- ✅ Logs estruturados em `logs/train.log`
- ✅ Checkpoints em `models/checkpoints/`

---

## ⚡ API FastAPI

A API foi projetada pensando em **flexibilidade**, **escalabilidade** e **facilidade de integração** com sistemas de análise e trading automatizado.

### Organização do Código
```
app/
├── main.py              # Orquestração da API
├── routers/
│   ├── health.py        # Health check
│   ├── predict.py       # Endpoints de predição
│   ├── train.py         # Endpoints de treinamento
│   └── metrics.py       # Endpoints de métricas
├── services/
│   ├── model.py         # Carregamento e gerenciamento do modelo
│   ├── data.py          # Pipeline de pré-processamento
│   └── training.py      # Lógica de treinamento
├── schemas/             # Validação de payloads (Pydantic)
└── config.py            # Configurações e variáveis de ambiente
```

### 📡 Endpoints da API — Implementação Atual

> **Nota Importante:** O modelo LSTM carregado nestes endpoints é **treinado especificamente para BBD (Bradesco ADR - NYSE)**, conforme documentado em `docs/documentacao_lstm_tech_challenge.md`.
> 
> O pipeline de predição:
> 1. **Fetch via yfinance** — Busca últimos `look_back` pregões (padrão: 30)
> 2. **Feature Engineering** — Aplica transformações (log1p) → StandardScaler
> 3. **LSTM Inference** — Modelo bidirectional LSTM treinado
> 4. **Desnormalização** — Converte resultado: inverse_transform → expm1

### 1️⃣ **Health & Status** — Verificação de Saúde

#### `GET /health` — Status da API
**Response (200 OK):**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

#### `GET /readiness` — Readiness Probe
Valida se os artefatos do modelo estão carregados (modelo_lstm.keras / scaler.pkl).

**Response (200 OK):**
```json
{
  "ready": true
}
```

**Response (503 Service Unavailable):**
```json
{
  "ready": false,
  "detail": "Artefatos do modelo (modelo_lstm.keras / scaler.pkl) não encontrados."
}
```

---

### 2️⃣ **Predição — Endpoints de Inferência**

#### `POST /api/v1/predict/single` — Prevê o próximo pregão

**Descrição:** 
- Busca via `yfinance` os últimos `look_back` (30) pregões de um símbolo
- Aplica o pipeline de normalização idêntico ao treinamento
- Retorna a previsão de fechamento (`Close`) do próximo pregão

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BBD"}'
```

**Response (200 OK):**
```json
{
  "symbol": "BBD",
  "predicted_close": 3.4482,
  "last_trading_date": "2026-07-10",
  "look_back": 30
}
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": "yfinance não retornou dados suficientes para 'INVALID' (requisito: 30)"
}
```

---

#### `POST /api/v1/predict/batch` — Predição em lote

**Descrição:**
- Aplica `/predict/single` a uma lista de símbolos
- Erros são isolados por símbolo (não derruba o lote inteiro)
- Cada símbolo é resolvido independentemente

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BBD", "PETR4.SA"]}'
```

**Response (200 OK):**
```json
{
  "results": {
    "BBD": {
      "predicted_close": 3.4482,
      "last_trading_date": "2026-07-10",
      "error": null
    },
    "PETR4.SA": {
      "predicted_close": null,
      "last_trading_date": null,
      "error": "yfinance não retornou dados suficientes para 'PETR4.SA' (requisito: 30)"
    }
  },
  "generated_at": "2026-07-13T23:48:18.640903"
}
```

---

#### `POST /api/v1/predict/sequence` — Previsão multi-passo (forecast recursivo)

**Descrição:**
- Prevê `days_ahead` pregões à frente (1-60)
- Modelo foi treinado para prever apenas **1 passo à frente**
- Para `days_ahead > 1`: cada previsão é realimentada (recursive forecast)
  - `High = Low = Open = Close` previsto
  - `Volume` é mantido no último valor observado
- **Qualidade degrada com o horizonte** — usar como tendência aproximada

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/predict/sequence \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BBD", "days_ahead": 5}'
```

**Response (200 OK):**
```json
{
  "symbol": "BBD",
  "days_ahead": 5,
  "predictions": [3.4482, 3.4003, 3.3657, 3.3402, 3.3188],
  "method": "recursive_close_only",
  "note": "Previsão recursiva: a partir do 2º passo, High/Low/Open assumem o Close previsto e o Volume é mantido no último valor observado. A qualidade da previsão degrada com o horizonte."
}
```

---

### 3️⃣ **Métricas — Avaliação do Modelo**

#### `GET /api/v1/metrics/latest` — Métricas do teste

**Descrição:**
- Retorna métricas da avaliação offline no conjunto de teste (treinamento)
- **Não são recalculadas em tempo real**
- Valores referem-se ao modelo BBD conforme seção 6 de `docs/documentacao_lstm_tech_challenge.md`

**Response (200 OK):**
```json
{
  "symbol": "BBD",
  "mae": 0.0297,
  "rmse": 0.0386,
  "mape": 1.94,
  "directional_accuracy": 40.31,
  "source": "avaliação offline no conjunto de teste (treinamento do modelo)"
}
```

**Legenda de Métricas:**
- **MAE** (Mean Absolute Error): Erro médio absoluto (USD)
- **RMSE** (Root Mean Square Error): Raiz do erro quadrático médio (USD)
- **MAPE** (Mean Absolute Percentage Error): Erro percentual absoluto médio (%)
- **Directional Accuracy**: Taxa de acerto da direção do movimento (%)

---

### 4️⃣ **Logs & Auditoria**

#### `GET /api/v1/logs?limit=500` — Histórico de acessos

**Descrição:**
- Retorna registros de auditoria de todas as requisições à API
- Gravado automaticamente via middleware global (ver `app/main.py`)
- Cada entry contém: método, rota, status, tempo de resposta, IP, data/hora
- Limite máximo: 500 registros, mais recentes primeiro

**Query Parameters:**
- `limit` (int, 1-500, default=500): Quantidade de registros

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "method": "POST",
    "path": "/api/v1/predict/single",
    "status_code": 200,
    "process_time": 0.842,
    "ip_address": "127.0.0.1",
    "created_at": "2026-07-13T23:48:18.640903+00:00"
  }
]
```

---

### 📊 **Resumo de Endpoints**

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| **GET** | `/health` | Status da API e modelo | ✅ |
| **GET** | `/readiness` | Readiness probe | ✅ |
| **POST** | `/api/v1/predict/single` | Predição 1 pregão à frente | ✅ |
| **POST** | `/api/v1/predict/batch` | Predição em lote | ✅ |
| **POST** | `/api/v1/predict/sequence` | Previsão recursiva (multi-passo) | ✅ |
| **GET** | `/api/v1/metrics/latest` | Métricas do modelo (offline) | ✅ |
| **GET** | `/api/v1/logs` | Histórico de acessos (auditoria) | ✅ |

---

## 🏗️ Arquitetura Atual

### Visão Geral da API

```
┌─────────────────────────────────────────────────┐
│           Cliente (Web, Mobile, CLI)             │
│  curl / Postman / Python requests / etc.         │
└──────────────────────┬──────────────────────────┘
                       │ HTTP REST
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (uvicorn)                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Middleware de Auditoria (logs_middleware)            │  │
│  │  - Registra cada requisição (method, path, status)    │  │
│  │  - Mede tempo de resposta e IP do cliente             │  │
│  └───────────────────────────────────────────────────────┘  │
│                       ↓                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Routers (app/api/v1/)                  │   │
│  ├─ health.py       → /health, /readiness             │   │
│  ├─ predict.py      → /api/v1/predict/single|batch    │   │
│  ├─ metrics.py      → /api/v1/metrics/latest          │   │
│  └─ logs.py         → /api/v1/logs                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                       ↓                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Services (app/services/)                 │   │
│  ├─ prediction_service.py                             │   │
│  │  ├─ predict_single(symbol)      → 1 pregão         │   │
│  │  ├─ predict_batch(symbols)      → múltiplos        │   │
│  │  └─ predict_sequence(symbol, days) → forecast      │   │
│  └─ log_service.py                                     │   │
│  │  └─ Persistência em SQLite (api_logs)              │   │
│  └──────────────────────────────────────────────────────┘   │
│                       ↓                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            ML Pipeline (ml/)                        │   │
│  ├─ inference.py                                       │   │
│  │  ├─ predict_next_close()   → busca yfinance        │   │
│  │  ├─ aplica log1p transform                         │   │
│  │  ├─ normaliza com scaler.pkl                       │   │
│  │  ├─ passa por LSTM                                 │   │
│  │  └─ desnormaliza (expm1)                           │   │
│  ├─ model.py        → carrega modelo_lstm.keras       │   │
│  └─ data.py         → feature engineering, yfinance   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                       ↓
      ┌────────────────────────────────────┐
      │      Storage Persistence           │
      ├─ ml/modelo_lstm.keras              │
      ├─ ml/scaler.pkl                     │
      ├─ app_logs.db (SQLite)              │
      └────────────────────────────────────┘
```

### Fluxo de uma Predição (End-to-End)

```
1. POST /api/v1/predict/single
   {"symbol": "BBD"}
        ↓
2. PredictionService.predict_single(symbol)
   - Cria InsufficientDataError se algo falhar
        ↓
3. ml.inference.predict_next_close(symbol, settings)
   - yfinance.download(symbol) → últimos look_back (30) dias
   - Feature engineering: cria features OHLCV
   - Log1p transform (proteção a outliers)
   - StandardScaler.transform() (usando ml/scaler.pkl)
        ↓
4. Modelo LSTM Bidirectional
   - Input: (1, look_back, features)
   - Output: preço previsto (normalizado)
        ↓
5. Inverse Transform
   - StandardScaler.inverse_transform()
   - expm1 (desfaz log1p)
        ↓
6. PredictResponse
   {
     "symbol": "BBD",
     "predicted_close": 3.4482,
     "last_trading_date": "2026-07-10",
     "look_back": 30
   }
        ↓
7. Middleware registra acesso em SQLite
   - INSERT INTO api_logs (method, path, status_code, ...)
```

### Estrutura de Diretórios

```
app/
├── __init__.py
├── main.py                 # Orquestração FastAPI + middleware
├── core/
│   ├── __init__.py
│   └── config.py          # Settings, variáveis de ambiente
├── api/v1/
│   ├── __init__.py
│   ├── router.py          # Include de todos os routers
│   ├── health.py          # GET /health, /readiness
│   ├── predict.py         # POST /api/v1/predict/*
│   ├── metrics.py         # GET /api/v1/metrics/latest
│   └── logs.py            # GET /api/v1/logs
├── services/
│   ├── __init__.py
│   ├── prediction_service.py  # Orquestração de predições
│   └── log_service.py         # CRUD logs em SQLite
├── models/
│   ├── __init__.py
│   ├── base.py            # Base SQLAlchemy + engine
│   └── logs.py            # ORM de api_logs
├── schemas/
│   ├── __init__.py
│   ├── health.py          # HealthResponse, ReadinessResponse
│   ├── predict.py         # PredictRequest/Response, etc.
│   ├── metrics.py         # MetricsResponse
│   └── logs.py            # ApiLogEntry
├── dependencies.py        # get_db()
├── static/                # Frontend React (servido pelo root)
│   ├── index.html
│   ├── js/
│   └── css/
└── app.py                 # App antigo (compatibilidade)

ml/
├── __init__.py
├── model.py               # artifacts_available(), carregamento
├── inference.py           # predict_next_close(), predict_sequence()
└── data.py                # Feature engineering, yfinance

tests/
├── conftest.py
├── test_predict.py        # Testes do router /predict
├── test_logs.py           # Testes do router /logs
└── test_health.py         # Testes do router /health

models/
├── modelo_lstm.keras      # Modelo treinado (BBD)
└── checkpoints/           # Checkpoints intermediários (treino)

docs/
├── documentacao_lstm_tech_challenge.md
├── fase4_pos_mlet_organizado_(1).ipynb  # Notebook principal
└── oquefazer.md           # Requisitos do tech challenge
```

---

## 🚀 Roadmap

### **Fase 1: Setup & Fundação** ✅
- [x] Estrutura de pastas e configuração do projeto
- [x] Setup do ambiente Python e dependências
- [x] Scripts de coleta de dados (yfinance)
- [x] Pré-processamento básico

### **Fase 2: Modelo LSTM** ✅
- [x] Implementação da arquitetura LSTM Bidirectional
- [x] Pipeline de treinamento com checkpoints
- [x] Validação e tuning de hiperparâmetros (TimeSeriesSplit)
- [x] Avaliação com métricas (MAE, RMSE, MAPE, Directional Accuracy)
- [x] Salvar modelo em `ml/modelo_lstm.keras` + scaler em `ml/scaler.pkl`

### **Fase 3: API & Endpoints** ✅
- [x] Setup FastAPI com estrutura modular
- [x] Implementar routers (health, predict, metrics, logs)
- [x] Validação com Pydantic schemas
- [x] Documentação Swagger/ReDoc automática
- [x] Testes de endpoints (unit + integração)

### **Fase 4: Monitoramento & Deploy** ✅
- [x] Logs estruturados (auditoria em SQLite)
- [x] Health checks e readiness probes
- [x] Documentação completa
- [x] Dashboard de monitoramento (Streamlit em repo separado)
- [x] Deploy em produção (Render.com)

### **Fase 5: Otimizações & Produção** 🔄
- [x] Deploy em produção (Render.com)
- [ ] Caching de predições (Redis)
- [ ] Rate limiting e autenticação (JWT/API Key)
- [ ] Métricas de observabilidade (Prometheus)
- [ ] CI/CD com GitHub Actions
- [ ] Versionamento de modelos (Model Registry)

---

## 🛠️ Tecnologias

| Componente | Tecnologia | Versão | Uso |
|------------|------------|---------|-----|
| **Linguagem** | Python | 3.10+ | Desenvolvimento |
| **API** | FastAPI | 0.104+ | Servidor web |
| **Deep Learning** | TensorFlow + Keras | 2.13+ | Modelo LSTM Bidirectional |
| **Preprocessamento** | scikit-learn | 1.3+ | RobustScaler, feature engineering |
| **Dados** | Pandas | 2.0+ | Manipulação de séries temporais |
| **Requisição HTTP** | yfinance | 0.2.32+ | Coleta de dados de ações |
| **Testes** | pytest | 7.4+ | Testes unitários e integração |
| **Logging** | Python logging | built-in | Logs estruturados |

**Dependências do Modelo:**
- `TensorFlow>=2.13` — Bidirectional LSTM, BatchNormalization, Callbacks
- `keras>=2.13` — Carregamento do modelo `.keras` (novo formato padrão)
- `scikit-learn>=1.3` — RobustScaler (fit no notebook, used na API)
- `numpy` — Operações matemáticas nas sequências

---

## 📦 Como Rodar

### **Pré-requisitos**
- Python 3.10+
- pip (ou conda)
- Conexão com a internet (para yfinance)

### **Setup do Ambiente Local**

```bash
# 1. Clonar repositório (ou já estar no diretório)
cd mle_tech_chalenge_4

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências

# DESENVOLVIMENTO (com testes):
pip install -r requirements-dev.txt

# OU APENAS PRODUÇÃO (sem testes):
pip install -r requirements.txt
```

**📌 Recomendação**: Use `requirements-dev.txt` em desenvolvimento para ter pytest e tools de dev.

### **Opção A: Rodar a API (Modo Desenvolvimento)**

```bash
# Iniciar o servidor com auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Acessar a API:**
- 🏠 **Root**: http://localhost:8000/
- 📋 **Swagger Docs**: http://localhost:8000/docs
- 📚 **ReDoc**: http://localhost:8000/redoc
- ✅ **Health**: http://localhost:8000/health

### **Opção B: Rodar a API (Modo Produção)**

```bash
# Sem auto-reload, mais otimizado
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Ou com gunicorn (requer instalação extra)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Opção C: Testes Automatizados**

```bash
# Rodar todos os testes
pytest -v

# Com cobertura de código
pytest --cov=app --cov-report=html tests/

# Modo rápido (sem output verboso)
pytest -q --tb=short
```

**Meta de cobertura:** >= 70%

### **Artefatos Necessários (Automático)**

Ao iniciar a API, são verificados:
- ✅ `ml/modelo_lstm.keras` — Modelo treinado (BBD)
- ✅ `ml/scaler.pkl` — StandardScaler (fit no treinamento)
- ✅ `app_logs.db` — Banco SQLite para auditoria (criado automaticamente)

Se algum artefato estiver faltando, o endpoint `/readiness` retornará `ready: false`.

### **Frontend Integrado (React)**

Um frontend React leve foi adicionado em `app/static` e é servido pela API:

**Acessar:**
```
http://localhost:8000/
```

O painel permite:
- ✔️ Enviar requisições ao endpoint `/api/v1/predict/single`
- 📊 Visualizar predições em tempo real
- 🔍 Testar o health check rapidamente
- 📜 Consultar histórico de acessos (`/api/v1/logs`)

---

## 📝 Exemplos de Uso (cURL)

### 🌐 Ambientes

| Ambiente | URL |
|----------|-----|
| **Local** | http://localhost:8000 |
| **Produção** | https://mle-tech-chalenge-4.onrender.com |

---

### ✅ Health Check

```bash
# Status da API
curl http://localhost:8000/health

# Resposta esperada:
# {"status":"ok","model_loaded":true}
```

### 🔍 Readiness Check

```bash
# Verifica se modelo está carregado
curl http://localhost:8000/readiness

# Resposta esperada:
# {"ready":true}
```

---

### 🎯 Predição Single-Shot (Próximo Pregão)

```bash
# Prevê o preço de fechamento de BBD para o próximo pregão
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BBD"}'

# Resposta esperada:
# {
#   "symbol": "BBD",
#   "predicted_close": 3.4482,
#   "last_trading_date": "2026-07-10",
#   "look_back": 30
# }
```

---

### 📦 Predição em Lote (Batch)

```bash
# Prevê para múltiplos símbolos (erros isolados)
curl -X POST http://localhost:8000/api/v1/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BBD", "PETR4.SA"]}'

# Resposta esperada:
# {
#   "results": {
#     "BBD": {"predicted_close": 3.4482, "last_trading_date": "2026-07-10", "error": null},
#     "PETR4.SA": {"predicted_close": null, "last_trading_date": null, "error": "..."}
#   },
#   "generated_at": "2026-07-13T23:48:18.640903"
# }
```

---

### 📈 Previsão Multi-Passo (Forecast Recursivo)

```bash
# Prevê 5 pregões à frente (forecast recursivo)
curl -X POST http://localhost:8000/api/v1/predict/sequence \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BBD", "days_ahead": 5}'

# Resposta esperada:
# {
#   "symbol": "BBD",
#   "days_ahead": 5,
#   "predictions": [3.4482, 3.4003, 3.3657, 3.3402, 3.3188],
#   "method": "recursive_close_only",
#   "note": "Previsão recursiva: a partir do 2º passo, High/Low/Open assumem o Close previsto..."
# }
```

**Atenção:** Qualidade degrada com o horizonte — use como tendência aproximada.

---

### 📊 Métricas do Modelo

```bash
# Retorna métricas de avaliação offline (teste set)
curl http://localhost:8000/api/v1/metrics/latest

# Resposta esperada:
# {
#   "symbol": "BBD",
#   "mae": 0.0297,
#   "rmse": 0.0386,
#   "mape": 1.94,
#   "directional_accuracy": 40.31,
#   "source": "avaliação offline no conjunto de teste (treinamento do modelo)"
# }
```

---

### 📜 Histórico de Acessos (Auditoria)

```bash
# Lista últimos 50 acessos à API
curl "http://localhost:8000/api/v1/logs?limit=50"

# Resposta esperada:
# [
#   {
#     "id": 1,
#     "method": "POST",
#     "path": "/api/v1/predict/single",
#     "status_code": 200,
#     "process_time": 0.842,
#     "ip_address": "127.0.0.1",
#     "created_at": "2026-07-13T23:48:18.640903+00:00"
#   }
# ]
```

---

### 📚 Documentação Interativa

```bash
# Swagger UI (desenvolvimento)
open http://localhost:8000/docs

# ReDoc (desenvolvimento)
open http://localhost:8000/redoc

# Em produção:
open https://mle-tech-chalenge-4.onrender.com/docs
```

### 🔄 Lógica das Rotas — Detalhado

#### **1. Health & Readiness**

**`GET /health`** (app/api/v1/health.py:11)
```python
def health_check():
    model_loaded = artifacts_available(model_path, scaler_path)
    return HealthResponse(status="ok", model_loaded=model_loaded)
```
- Valida se `ml/modelo_lstm.keras` e `ml/scaler.pkl` existem
- Sempre retorna 200 (status="ok")
- Indica se modelo está carregado

**`GET /readiness`** (app/api/v1/health.py:16)
```python
def readiness_check():
    if artifacts_available(model_path, scaler_path):
        return ReadinessResponse(ready=True)
    return ReadinessResponse(
        ready=False, 
        detail="Artefatos não encontrados"
    )
```
- Probe para orchestração (Kubernetes, etc.)
- Retorna 503 se modelo não carregado

---

#### **2. Predição Single**

**`POST /api/v1/predict/single`** (app/api/v1/predict.py:16)

**Fluxo de Execução:**

```python
def predict_single(symbol: str):
    1. PredictionService.predict_single(symbol)
    
    2. ml.inference.predict_next_close(symbol, settings)
       ├─ yfinance.download(symbol, start_date, end_date)
       │  └─ Busca últimos `look_back` (30) pregões
       │
       ├─ ml.data.prepare_single_sequence(df, settings)
       │  ├─ log1p(close_prices)  # Transform para estabilidade
       │  ├─ StandardScaler.fit() — NÃO FAZE! Usa scaler.pkl
       │  ├─ StandardScaler.transform()
       │  └─ Cria janela deslizante (look_back, features)
       │
       ├─ model.predict(sequence)  # LSTM
       │  └─ Saída: preço normalizado
       │
       ├─ StandardScaler.inverse_transform()
       └─ expm1(prediction)  # Desfaz log1p
    
    3. Captura InsufficientDataError se yfinance retorna < look_back dias
       └─ Retorna 422 Unprocessable Entity
    
    4. Return PredictResponse
       {
         "symbol": "BBD",
         "predicted_close": 3.4482,
         "last_trading_date": "2026-07-10",
         "look_back": 30
       }
```

**Casos de Erro:**
- **422 Unprocessable Entity**: Símbolo inválido, IPO recente, ou < 30 dias de histórico
- **500 Internal Server Error**: Modelo não carregado

---

#### **3. Predição Batch**

**`POST /api/v1/predict/batch`** (app/api/v1/predict.py:44)

**Fluxo:**

```python
def predict_batch(symbols: list[str]):
    results = {}
    
    for symbol in symbols:
        try:
            price, last_date = inference.predict_next_close(symbol)
            results[symbol] = BatchPredictItem(
                predicted_close=price,
                last_trading_date=last_date,
                error=None
            )
        except InsufficientDataError as exc:
            results[symbol] = BatchPredictItem(
                predicted_close=None,
                last_trading_date=None,
                error=str(exc)  # Erro isolado
            )
    
    return BatchPredictResponse(
        results=results,
        generated_at=datetime.utcnow()
    )
```

**Características:**
- ✅ Erros são isolados por símbolo
- ✅ Um símbolo ruim não afeta os outros
- ✅ Retorna sempre 200 (nem que com erros dentro do results)

---

#### **4. Predição Sequence (Forecast Recursivo)**

**`POST /api/v1/predict/sequence`** (app/api/v1/predict.py:68)

**Fluxo:**

```python
def predict_sequence(symbol: str, days_ahead: int):
    # ml.inference.predict_sequence(symbol, days_ahead)
    
    preds = []
    current_df = yfinance.download(symbol)  # Últimos 30 dias
    
    for _ in range(days_ahead):
        # 1. Prepara sequência atual
        sequence = prepare_sequence(current_df[-30:])
        
        # 2. Prediz próximo Close
        next_close = model.predict(sequence)
        preds.append(next_close)
        
        # 3. Alimenta predição de volta (recursive forecasting)
        # Artifício: assume High = Low = Open = Close previsto
        # Volume mantém último valor observado
        current_df = append_synthetic_day(
            current_df,
            open_price=next_close,
            high=next_close,
            low=next_close,
            close=next_close,
            volume=current_df[-1].volume
        )
    
    return SequencePredictResponse(
        symbol=symbol,
        days_ahead=days_ahead,
        predictions=preds,
        method="recursive_close_only",
        note="Qualidade degrada com horizonte..."
    )
```

**⚠️ Aviso Importante:**
- Modelo treinado para 1 passo à frente APENAS
- Para `days_ahead > 1`: cada passo alimenta o próximo (acumula erro)
- Use como **tendência aproximada**, não previsão precisa

---

#### **5. Métricas**

**`GET /api/v1/metrics/latest`** (app/api/v1/metrics.py:8)

```python
def metrics_latest():
    # Valores HARDCODED — não recalculados em tempo real
    # Gerados na avaliação offline do notebook
    return MetricsResponse(
        symbol="BBD",
        mae=0.0297,          # USD
        rmse=0.0386,         # USD
        mape=1.94,           # %
        directional_accuracy=40.31,  # %
        source="avaliação offline no conjunto de teste"
    )
```

**Nota:**
- Métricas são **estáticas** (offline)
- Referem-se ao modelo BBD conforme treino no notebook
- Para métricas em tempo real: implementar callback ou job assíncrono

---

#### **6. Logs & Auditoria**

**`GET /api/v1/logs?limit=500`** (app/api/v1/logs.py:11)

**Middleware (app/main.py:46):**
```python
@app.middleware("http")
async def log_requests_middleware(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    
    # Evita log infinito (requisição para /logs não gera novo log)
    if request.url.path != "/api/v1/logs":
        response.background = BackgroundTask(
            write_log, request, response, process_time
        )
    return response
```

**Dados Capturados (SQLite):**
- `method`: HTTP method (GET, POST, etc.)
- `path`: URL path
- `status_code`: Response code (200, 422, etc.)
- `process_time`: Tempo de resposta (segundos)
- `ip_address`: IP do cliente
- `created_at`: Timestamp UTC

**Query:**
- `limit` (1-500, default=500): Limita resultados, mais recentes primeiro

---

### 📊 Tratamento de Erros — Padrão

```
InsufficientDataError (ml/data.py)
    ↓
PredictionService.predict_single() captura
    ↓
raise HTTPException(
    status_code=422,  # Unprocessable Entity
    detail="yfinance não retornou dados suficientes..."
)
    ↓
Response: 422 Unprocessable Entity
{
  "detail": "erro detalhado"
}
```

**Códigos HTTP Usados:**
- **200 OK**: Sucesso
- **422 Unprocessable Entity**: Dados insuficientes, símbolo inválido
- **500 Internal Server Error**: Modelo não carregado, erro inesperado

---

## ✅ Testes

### Execução Completa
```bash
# Rodar todos os testes
pytest -v

# Com cobertura
pytest --cov=app --cov-report=html tests/

# Modo rápido
pytest -q --tb=short
```

### Testes Incluídos
- ✓ Testes de pré-processamento (data.py)
- ✓ Testes de inferência (model.py)
- ✓ Testes de endpoints (routers)
- ✓ Testes de integração (treino + predição)

**Meta de cobertura**: >= 70%

---

## � Reprodutibilidade e Rastreabilidade do Modelo

### Como Rastrear o Modelo da API até o Notebook

1. **API Carrega:** `models/best_lstm_model.keras` + `scaler.pkl`
2. **Estes artifacts foram salvos por:** `docs/fase4_pos_mlet_organizado_(1).ipynb`
3. **Reproduzir exatamente:** Execute todas as células do notebook com o mesmo hardware/seed

### Verificação de Consistência

```python
# No notebook (após treino):
model.save('models/best_lstm_model.keras')
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Na API (ao carregar):
model = tf.keras.models.load_model('models/best_lstm_model.keras')
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
# → Garante mesmos pesos e parâmetros de normalização
```

### Seeds e Configurações Fixas

Para garantir reprodutibilidade total:
```bash
# No notebook:
tf.random.set_seed(42)
np.random.seed(42)
```

### Artefatos Críticos

| Arquivo | Origem | Célula | Uso |
|---------|--------|--------|-----|
| `models/best_lstm_model.keras` | Notebook | ~40 | Carregado na API para inferência |
| `scaler.pkl` | Notebook | ~18 | Normalização consistente na API e notebook |
| `logs/train.log` | Notebook | Cada execução | Rastreabilidade completa de hiperparâmetros |

---

## �📚 Documentação da API

Após iniciar a API localmente, acesse a documentação interativa:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Em Produção
A documentação completa da API em produção está disponível em:

- **Swagger UI**: https://mle-tech-chalenge-4.onrender.com/docs
- **ReDoc**: https://mle-tech-chalenge-4.onrender.com/redoc

A documentação é gerada automaticamente a partir das docstrings FastAPI.

---

## 📊 Estrutura de Arquivos

```
mle_tech_chalenge_4/
├── docs/
│   ├── fase4_pos_mlet_organizado_(1).ipynb  # 🔴 NOTEBOOK PRINCIPAL DO MODELO
│   ├── db_models.md
│   ├── scraping_architecture.drawio
│   └── uml/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Orquestração da API
│   ├── config.py               # Variáveis de ambiente
│   ├── routers/
│   │   ├── health.py
│   │   ├── predict.py
│   │   ├── train.py
│   │   └── metrics.py
│   ├── services/
│   │   ├── model.py            # Carrega best_lstm_model.keras
│   │   ├── data.py             # 17 features (idêntico ao notebook)
│   │   └── training.py         # Lógica de treinamento
│   └── schemas/                # Validação Pydantic
├── models/
│   ├── best_lstm_model.keras   # 🟢 MODELO TREINADO (salvo do notebook)
│   ├── scaler.pkl              # 🟢 SCALER PERSISTIDO (salvo do notebook)
│   └── checkpoints/            # Checkpoints intermediários
├── logs/
│   ├── train.log               # Logs de treinamento
│   └── api.log                 # Logs da API
├── data/
│   └── precos_fechamento.csv   # Dataset histórico (yfinance)
├── tests/
│   ├── test_model.py
│   ├── test_data.py
│   ├── test_routers.py
│   └── test_integration.py
├── scripts/
│   ├── train.sh                # Script de treinamento
│   └── download_data.py        # Download via yfinance
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt            # Dependências Python
├── pytest.ini                  # Configuração pytest
└── README.md                   # Este arquivo
```

**Legenda:**
- 🔴 **NOTEBOOK PRINCIPAL** — Onde o modelo é desenvolvido e validado
- 🟢 **ARTIFACTS PERSISTIDOS** — Gerados pelo notebook, usados pela API

---

## 🔄 Versionamento da API

Esta API utiliza **versionamento por URL**, identificado pelo prefixo `/api/v1`.

### Estratégia adotada

**v1** — Primeira versão estável
- Endpoints core: predict, train, metrics, health
- Covos modelos (Transformer, GRU, etc.)
- NoDashboard de Monitoramento
O monitoramento da API e análise de predições é realizado através de um **dashboard Streamlit** hospedado separadamente:

```
Repositório: https://github.com/vagnerasilva/mle_tech_chalenge_4_streamlit
```

**Funcionalidades do Dashboard:**
- 📊 Visualização em tempo real de predições
- 📈 Gráficos de performance do modelo
- 🔍 Análise comparativa de métricas
- 📉 Histórico de treinamentos
- ⚡ Monitoramento de latência e throughput da API

### vos tipos de dados (multi-asset, multi-timeframe)
- Autenticação e rate limiting

### Benefícios
- Evita quebra de integrações existentes
- Facilita evolução da API
- Garante reprodutibilidade de experimentos

---

## 🔒 Segurança & Monitoramento

### Logs Estruturados
```json
{
  "timestamp": "2024-07-20T14:30:00Z",
  "level": "INFO",
  "service": "predict",
  "symbol": "PETR4.SA",
  "inference_time_ms": 45.3,
  "model_version": "1.0",
  "status": "success"
}
```

### Health Checks
- Verifica status do modelo carregado
- Valida acesso a dados
- Monitora tempo de resposta

### Readiness Probe
- Indica se API está pronta para tráfego
- Aguarda modelo completar carregamento

---

## � Deploy em Produção (Render.com)

A API está **deployada e disponível** no Render.com:

### URL de Produção
```
https://mle-tech-chalenge-4.onrender.com/
```

### Endpoints de Produção

**Health Check:**
```bash
curl https://mle-tech-chalenge-4.onrender.com/health
```

**Predição (Production):**
```bash
curl -X POST https://mle-tech-chalenge-4.onrender.com/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "PETR4.SA",
    "days_back": 60,
    "days_ahead": 5
  }'
```

**Documentação Swagger (Production):**
```
https://mle-tech-chalenge-4.onrender.com/docs
```

### Observações sobre Produção
- ✅ Modelo pré-carregado e otimizado
- ✅ Logs estruturados em produção
- ✅ Health checks contínuos
- ✅ Tempo de resposta: ~50-100ms para predições
## 📦 Repositórios Relacionados & Ambientes em Produção

### Repositórios
- **[mle_tech_chalenge_4](https://github.com/vagnerasilva/mle_tech_chalenge_4)** — API FastAPI com modelo LSTM *(este repositório)*
- **[mle_tech_chalenge_4_streamlit](https://github.com/vagnerasilva/mle_tech_chalenge_4_streamlit)** — Dashboard de monitoramento e análise
- **[mle_tech_chalenge_1](https://github.com/vagnerasilva/mle_tech_chalenge_1)** — API de consulta de livros (projeto anterior)

### Ambientes em Produção (Render.com)
| Ambiente | URL | Descrição |
|----------|-----|-----------|
| **API FastAPI** | [https://mle-tech-chalenge-4.onrender.com/](https://mle-tech-chalenge-4.onrender.com/) | Endpoints de predição e inferência |
| **Dashboard Streamlit** | [https://mle-tech-chalenge-4-streamlit.onrender.com/](https://mle-tech-chalenge-4-streamlit.onrender.com/) | Monitoramento e análise de performance |
| **Docs Swagger** | [https://mle-tech-chalenge-4.onrender.com/docs](https://mle-tech-chalenge-4.onrender.com/docs) | Documentação interativa da API |

---

## �📞 Suporte & Contribuição

- **Issues & PRs**: Abrir no repositório GitHub
- **Documentação**: Ver `docs/` e docstrings do código
- **Contato**: Vagner Antônio da Silva

---

## 📄 Licença

Este projeto está sob licença **MIT**.

---

## 🎯 Próximos Passos

1. Finalizar implementação da arquitetura LSTM
2. Criar suite completa de testes
3. Deploy em produção (Heroku / Cloud)
4. Implementar monitoramento e alertas
5. Otimizar performance (GPU, caching)

---

**Tech Challenge Fase 4 — Deep Learning & IA**  
*Pós Tech MLET | Desenvolvido com ❤️ em Python*
- Cecilia
- Pedro 

ç

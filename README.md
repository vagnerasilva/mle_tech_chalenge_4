# 📈 Tech Challenge Fase 4 — Previsão de Preços de Ações com Deep Learning

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11+-009688.svg)
![LSTM](https://img.shields.io/badge/Model-Bidirectional%20LSTM-blue.svg)
![Tests](https://img.shields.io/badge/tests-25%2B%20cases-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-~75%25-green.svg)
![Rate Limiting](https://img.shields.io/badge/rate%20limiting-SQLite-informational.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📌 Sobre o Projeto

Este projeto foi desenvolvido como parte do **Tech Challenge – Fase 4** da Pós-Tech em Machine Learning Engineering.

O objetivo consiste em construir uma solução completa para previsão do preço de fechamento de ações utilizando redes neurais recorrentes (**Long Short-Term Memory – LSTM**), contemplando todo o ciclo de desenvolvimento de um sistema de Machine Learning, desde a coleta dos dados históricos até a disponibilização do modelo em produção através de uma API REST.

Diferentemente de um notebook exclusivamente voltado para experimentação, este projeto implementa uma pipeline completa de Machine Learning Engineering, incluindo:

- coleta automática dos dados;
- análise exploratória;
- pré-processamento;
- busca e ajuste de hiperparâmetros;
- treinamento;
- avaliação;
- persistência do modelo;
- API de inferência;
- dashboard de monitoramento.

---

# 🎯 Objetivos

O projeto busca atender às seguintes etapas do ciclo de vida de um modelo de Machine Learning:

- Coletar automaticamente dados históricos de ações;
- Realizar análise exploratória dos dados (EDA);
- Construir uma pipeline de pré-processamento sem data leakage;
- Treinar uma rede neural LSTM para previsão do preço de fechamento;
- Avaliar o modelo utilizando métricas de regressão;
- Exportar o modelo para produção;
- Disponibilizar uma API REST utilizando FastAPI;
- Disponibilizar dashboard para monitoramento das predições.

---

# 🏗 Arquitetura Geral

O fluxo completo do projeto pode ser resumido conforme o diagrama abaixo.

```

Yahoo Finance

↓

Coleta dos dados

↓

Análise Exploratória (EDA)

↓

Pré-processamento

• log1p

• StandardScaler

↓

Construção das Sequências

↓

Bidirectional LSTM

↓

Avaliação

↓

Exportação

(modelo + scaler)

↓

FastAPI

↓

Dashboard Streamlit

```

Todo o pipeline de inferência utilizado pela API reproduz exatamente o fluxo utilizado durante o treinamento, garantindo consistência entre ambiente de desenvolvimento e produção.

---

# 📂 Estrutura do Projeto

```

mle_tech_challenge_4/

├── app.py
├── app/
│   ├── __init__.py
│   └── static/
│       ├── index.html
│       └── assets/
│           ├── index-DJh4hmGh.js
│           └── index-DsDejwUj.css
├── artifacts/
│   ├── modelo_lstm.keras
│   └── scaler.pkl
├── docs/
│   ├── documentacao_lstm_tech_challenge.md
│   ├── oquefazer.md
│   └── Pos_Tech - MLET - Tech Challenge Fase 4.pdf
├── imgs/
├── modelagem/
│   └── fase4_MLET.ipynb
├── README.md
├── requirements copy.txt
├── requirements-dev.txt
└── requirements.txt

```

---

# 📊 Base de Dados

Os dados históricos são obtidos diretamente do **Yahoo Finance**, utilizando a biblioteca **yfinance**.

Neste projeto foi utilizado o ativo:

**Ticker:** BBD (Banco Bradesco ADR — NYSE)

Período analisado:

**Junho de 2020 até Junho de 2026**

---

# 📈 Variáveis Utilizadas

O modelo utiliza apenas informações históricas do próprio ativo.

| Feature | Descrição |
|----------|-----------|
| Open | Preço de abertura |
| High | Maior preço do dia |
| Low | Menor preço do dia |
| Close | Preço de fechamento |
| Volume | Volume negociado |

O alvo do modelo consiste em prever o **preço de fechamento do próximo pregão**.

---

# 📊 Análise Exploratória

Foi realizada uma análise exploratória completa da série temporal antes do treinamento.

As principais etapas foram:

- análise da série histórica;
- histogramas;
- boxplots;
- estatísticas descritivas;
- identificação de assimetria;
- análise de outliers.

A análise mostrou que:

- as distribuições apresentavam forte assimetria positiva;
- o Volume possuía cauda longa;
- não foram encontrados outliers relevantes pelo método IQR;
- as oscilações observadas representam regimes naturais do mercado e não erros de coleta.

Dessa forma, optou-se por manter todos os registros da série temporal.

---

# ⚙️ Pipeline de Pré-processamento

Após a análise exploratória foi definida a seguinte estratégia de pré-processamento.

## 1. Transformação Logarítmica

Todas as variáveis OHLCV recebem:

```python
np.log1p()
```

Essa transformação reduz a assimetria das distribuições e melhora a estabilidade do treinamento.

---

## 2. Normalização

Após a transformação logarítmica é aplicado um:

```python
StandardScaler
```

O scaler é ajustado **exclusivamente no conjunto de treinamento**.

Posteriormente os conjuntos de validação, teste e produção utilizam apenas:

```python
transform()
```

garantindo ausência de data leakage.

---

## 3. Divisão Temporal

Os dados são divididos cronologicamente em:

| Conjunto | Percentual |
|-----------|-----------:|
| Treino | 70% |
| Validação | 15% |
| Teste | 15% |

Não é realizado embaralhamento dos dados (shuffle), preservando a ordem temporal da série.
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
- ✅ `POST /api/v1/predict/next_close` — Rate limited
- ✅ `GET /api/v1/metrics/latest` — Rate limited
- ✅ `GET /api/v1/logs` — Rate limited
- ✅ `POST /api/v1/validation/validate` — Rate limited
- ✅ `GET /api/v1/validation/summary` — Rate limited
- ✅ `GET /api/v1/validation/metrics` — Rate limited

### Endpoints NÃO Afetados (Monitoramento)
- ❌ `GET /api/v1/health/check` — Sem limite
- ❌ `GET /api/v1/health/readiness` — Sem limite

**💡 Tip:** Usar `/health` para monitoramento contínuo sem preocupação com rate limit.

### Detalhes Técnicos
- **Storage**: SQLite (`rate_limit_logs`)
- **Janela deslizante**: Rastreia últimas 5 minutos
- **IP Detection**: Suporta proxies (X-Forwarded-For, X-Real-IP)
- **Limpeza automática**: Registros > 5 min removidos

Para mais detalhes: 📖 [docs/rate-limiting.md](docs/rate-limiting.md)

---

## 📊 Monitoramento de Desempenho — Sistema de Validação

A API implementa um **sistema completo de validação** que permite medir como o modelo LSTM está performando em produção.

### O que é o Sistema de Validação?

Compara **predições do modelo** com **preços reais do mercado** para calcular métricas de erro:
- **MAE** (Mean Absolute Error) — Erro absoluto médio em USD
- **RMSE** (Root Mean Squared Error) — Raiz do erro quadrado médio
- **MAPE** (Mean Absolute Percentage Error) — Erro percentual médio (%)
- **Directional Accuracy** — Taxa de acerto da direção do movimento (%)
- **Error Percentage** — Erro percentual simples (%)

### Endpoints de Validação

#### **1. Validar Predições Pendentes**

```bash
curl -X POST http://localhost:8000/api/v1/validation/validate
```

**Response:**
```json
{
  "total_pending": 50,
  "updated": 48,
  "failed": 2,
  "updated_records": [...]
}
```

#### **2. Resumo de Validações (Por Período)**

```bash
curl "http://localhost:8000/api/v1/validation/summary?symbol=BBD&start_date=2026-07-01&end_date=2026-07-14"
```

**Response:**
```json
{
  "symbol": "BBD",
  "total_predictions": 50,
  "validated": 48,
  "pending": 2,
  "avg_mae": 0.15,
  "avg_mape": 2.3,
  "avg_directional_accuracy": 0.67
}
```

#### **3. Estatísticas Agregadas do Modelo**

```bash
curl "http://localhost:8000/api/v1/validation/metrics"
```

**Response:**
```json
{
  "total_predictions": 150,
  "avg_mae": 0.15,
  "avg_mape": 2.8,
  "avg_directional_accuracy": 0.65
}
```

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

### 📡 Endpoints da API

> **Nota Importante:** O modelo LSTM carregado nestes endpoints é **exatamente o modelo treinado no notebook** [docs/fase4_pos_mlet_organizado_(1).ipynb](docs/fase4_pos_mlet_organizado_(1).ipynb). 
> 
> Quando a API inicia, carrega o arquivo `models/best_lstm_model.keras` (melhor checkpoint do treinamento) e reutiliza o `RobustScaler` persistido para normalização consistente.

#### **Core — Health & Status**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| **GET** | `/health` | Status da API e modelo |
| **GET** | `/readiness` | Verifica se modelo está carregado |

#### **Predição — Inferência**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| **POST** | `/api/v1/predict/single` | Predição single-shot (1 preço futuro) |
| **POST** | `/api/v1/predict/batch` | Predição em lote (múltiplas amostras) |
| **POST** | `/api/v1/predict/sequence` | Predição de múltiplos passos futuros |

**Exemplo de Request (Single):**
```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "PETR4.SA",
    "days_back": 60,
    "days_ahead": 5
  }'
```

**Exemplo de Response:**
```json
{
  "symbol": "PETR4.SA",
  "predictions": [25.45, 25.67, 25.89, 26.12, 26.34],
  "confidence": 0.92,
  "timestamp": "2024-07-20T14:30:00Z"
}
```

#### **Treinamento — Modelo**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| **POST** | `/api/v1/train/start` | Inicia treinamento com parâmetros customizáveis |
| **GET** | `/api/v1/train/status/{job_id}` | Status do treinamento em andamento |
| **POST** | `/api/v1/train/stop/{job_id}` | Para um treinamento em execução |
| **GET** | `/api/v1/train/history` | Histórico de treinamentos |

**Exemplo de Request (Train):**
```bash
curl -X POST http://localhost:8000/api/v1/train/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "PETR4.SA",
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001,
    "test_size": 0.1
  }'
```

**Exemplo de Response:**
```json
{
  "job_id": "train_20240720_143000",
  "status": "running",
  "progress": 35,
  "current_epoch": 35,
  "total_epochs": 100,
  "loss": 0.0045,
  "val_loss": 0.0052
}
```

#### **Métricas — Avaliação**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| **GET** | `/api/v1/metrics/latest` | Métricas do último treinamento |
| **GET** | `/api/v1/metrics/model` | Métricas do modelo em produção |
| **GET** | `/api/v1/metrics/inference` | Tempo de resposta e throughput |
| **GET** | `/api/v1/metrics/comparison` | Comparação entre modelos |

---

## 🏗️ Arquitetura

### Visão Geral
```
┌─────────────────────────────────────────────────────────────┐
│                    Cliente / Aplicação                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI (uvicorn)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Routers (health, predict, train, metrics)          │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                        │                                     │
│  ┌────────────────────┴──────────────────────────────┐  │   │
│  ↓                                                   ↓  │   │
│ ┌──────────────────┐  ┌──────────────────────────┐   │   │
│ │ Model Service    │  │ Data Service             │   │   │
│ │ ✓ Load/Cache     │  │ ✓ Fetch (yfinance)       │   │   │
│ │ ✓ Inference      │  │ ✓ Normalize/Preprocess   │   │   │
│ │ ✓ Batch predict  │  │ ✓ Windowing              │   │   │
│ └────────┬─────────┘  └──────────────┬───────────┘   │   │
│          │                           │               │   │
│          ↓                           ↓               │   │
│  ┌────────────────────────────────────────────┐      │   │
│  │  Models / Storage                          │      │   │
│  │  ✓ best_model.h5                           │      │   │
│  │  ✓ checkpoints/                            │      │   │
│  │  ✓ scaler (pkl)                            │      │   │
│  └────────────────────────────────────────────┘      │   │
└─────────────────────────────────────────────────────┘   │
                                                           │
┌───────────────────────────────────────────────────────┐  │
│  Persistent Storage                                   │  │
│  ✓ logs/train.log                                     │  │
│  ✓ data/precos_fechamento.csv                         │  │
│  ✓ models/                                            │  │
└───────────────────────────────────────────────────────┘  │
```

---

## 🚀 Roadmap

### **Fase 1: Setup & Fundação** ✅
- [x] Estrutura de pastas e configuração do projeto
- [x] Setup do ambiente Python e dependências
- [x] Scripts de coleta de dados (yfinance)
- [x] Pré-processamento básico

### **Fase 2: Modelo LSTM** 🔄
- [ ] Implementação da arquitetura LSTM
- [ ] Pipeline de treinamento com checkpoints
- [ ] Validação e tuning de hiperparâmetros
- [ ] Avaliação com métricas (MAE, RMSE, MAPE, R²)
- [ ] Salvar e versionamento do modelo

### **Fase 3: API & Endpoints** 📋
- [ ] Setup FastAPI
- [ ] Implementar routers (health, predict, train, metrics)
- [ ] Validação com Pydantic schemas
- [ ] Documentação Swagger automática
- [ ] Testes de endpoints (unit + integração)

### **Fase 4: Monitoramento & Deploy** �
- [x] Logs estruturados (JSON)
- [x] Health checks e readiness probes
- [x] Scripts de exemplo (curl, Postman)
- [x] Documentação completa de deploy
- [x] Dashboard de monitoramento (Streamlit)

### **Fase 5: Otimizações & Produção** ⚡
- [x] Deploy em produção (Render.com)
- [ ] Caching de predições
- [ ] Rate limiting e autenticação (opcional)
- [ ] Métricas de observabilidade (Prometheus/Grafana)
- [ ] CI/CD com GitHub Actions

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

### **Opção 0: Treinar o Modelo (Desenvolvimento)**

Se quiser reproduzir o treinamento do modelo localmente:

```bash
# 1. Clonar e setup
git clone <repo-url>
cd mle_tech_chalenge_4
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# 2. Abrir o Jupyter Notebook
jupyter notebook docs/fase4_pos_mlet_organizado_(1).ipynb

# 3. Executar todas as células para:
#    - Baixar dados via yfinance
#    - Fazer feature engineering
#    - Buscar hiperparâmetros (TimeSeriesSplit)
#    - Treinar o Bidirectional LSTM
#    - Salvar modelo em models/best_lstm_model.keras
#    - Gerar métricas e visualizações
```

**Nota:** Este processo pode levar 10-30 minutos dependendo do hardware (GPU recomendada).

### **Opção 1: Rodar a API (Com Modelo Pré-treinado)**

```bash
# 1. Clonar repositório
git clone <repo-url>
cd mle_tech_chalenge_4

# 2. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Executar API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Testes (em outro terminal)
pytest -v --cov=app tests/
```

A API carregará o modelo treinado (`models/best_lstm_model.keras`) ao iniciar.

### Frontend Integrado (React)

Um frontend React leve foi adicionado em `app/static` e é servido pela API. Após iniciar a API localmente, abra:

```
http://localhost:8000/web
```

Ou acesse diretamente os assets estáticos em:

```
http://localhost:8000/static/index.html
```

O painel permite enviar requisições ao endpoint `/api/v1/predict/single`, visualizar predições e testar o `health` rapidamente.

---

## 📝 Exemplos de Uso

### Produção (Render.com)
> Use `https://mle-tech-chalenge-4.onrender.com` para a API em produção

### Local (Desenvolvimento)
> Use `http://localhost:8000` para ambiente local

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Predição Single-Shot**
```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "PETR4.SA",
    "days_back": 60,
    "days_ahead": 5
  }'
```

### **Treinamento**
```bash
curl -X POST http://localhost:8000/api/v1/train/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "VALE3.SA",
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 0.001
  }'
```

### **Verificar Métricas**
```bash
curl http://localhost:8000/api/v1/metrics/latest
```

### 🔄 Entendendo o Fluxo de Predição

Quando você faz uma requisição POST para `/api/v1/predict/single`, internamente acontece:

1. **Fetch de Dados** (via yfinance)
   - Baixa últimas N séries de preços (últimos 60+ dias)
   - Mesma fonte que o notebook utiliza

2. **Feature Engineering**
   - Constrói as mesmas **17 features** (MA_7, MA_21, RSI_14, MACD, Bollinger Bands, etc.)
   - Código idêntico ao do notebook (`app/services/data.py`)

3. **Normalização**
   - Aplica o `RobustScaler` salvo do treinamento
   - Garante consistência: mesmos parâmetros (min, max, quartis)
   - **Sem data leakage** — não refaz o fit nos dados de predição

4. **Predição LSTM**
   - Carrega o modelo `best_lstm_model.keras` (salvo do notebook)
   - Usa o mesmo `LOOK_BACK` otimizado
   - Bidirectional LSTM + BatchNorm + Regularização L2

5. **Desnormalização**
   - Converte predição de volta para USD
   - Usa inverso do scaler persistido

**Resultado:** Predição consistente com métricas de validação do notebook.

---

## Dropout

Foi utilizado Dropout em diferentes pontos da arquitetura para reduzir a dependência entre neurônios e minimizar overfitting.

A taxa escolhida foi:

```
0.30
```

nas camadas recorrentes.

---

## Regularização L2

As camadas LSTM utilizam penalização L2 sobre os pesos da rede.

Essa estratégia reduz o crescimento excessivo dos parâmetros durante o treinamento e melhora a capacidade de generalização.

---

# ⚙ Processo de Treinamento

O treinamento foi realizado utilizando o otimizador **Adam**, amplamente empregado em problemas de Deep Learning devido à sua estabilidade e rápida convergência.

Configuração utilizada:

| Parâmetro | Valor |
|------------|------:|
| Optimizer | Adam |
| Learning Rate | 0.0001 |
| Loss | MAE |
| Batch Size | 16 |

O treinamento foi monitorado continuamente utilizando métricas calculadas na escala original do problema.

---

# 🔄 Callbacks

Para tornar o treinamento mais eficiente foram utilizados quatro callbacks principais.

## EarlyStopping

Interrompe automaticamente o treinamento quando não há melhoria significativa na métrica monitorada.

Benefícios:

- evita overfitting;
- reduz tempo de treinamento;
- restaura automaticamente os melhores pesos.

---

## ReduceLROnPlateau

Quando o treinamento atinge um platô, o learning rate é reduzido automaticamente.

Essa estratégia melhora o refinamento da solução nas últimas épocas.

---

## ModelCheckpoint

Salva automaticamente o melhor modelo encontrado durante o treinamento.

O arquivo exportado é:

```
modelo_lstm.keras
```

---

## RealMapeCallback

Foi implementado um callback personalizado responsável por calcular o MAPE na escala original dos preços.

A cada época o callback realiza automaticamente:

- inverse_transform do StandardScaler;
- aplicação de expm1;
- cálculo do MAPE em USD.

Dessa forma, todas as decisões de treinamento são tomadas utilizando uma métrica diretamente interpretável pelo negócio.

---

# 📈 Curvas de Aprendizado

Durante o treinamento foram monitoradas duas métricas principais:

- Loss (MAE normalizado);
- MAPE em escala real.

As curvas obtidas indicaram:

- convergência estável;
- ausência de overfitting severo;
- boa capacidade de generalização;
- redução consistente do erro ao longo das épocas.

O EarlyStopping interrompeu o treinamento automaticamente quando não havia mais ganho significativo de desempenho.

---

# 📊 Avaliação do Modelo

Após o treinamento, o modelo foi avaliado em um conjunto de teste completamente isolado, nunca utilizado durante o ajuste dos pesos ou dos hiperparâmetros.

As métricas foram calculadas na escala original (USD).

| Métrica | Resultado |
|----------|----------:|
| MAE | **0.0297 USD** |
| RMSE | **0.0386 USD** |
| MAPE | **1.94%** |
| Acurácia Direcional | **40.31%** |

O baixo valor de MAPE indica que o modelo apresenta elevada precisão na previsão do preço de fechamento do ativo.

---

# 📉 Análise dos Resultados

A análise visual das previsões mostrou que o modelo consegue acompanhar adequadamente a tendência geral da série temporal.

Observou-se que:

- o modelo acompanha bem movimentos de médio prazo;
- erros maiores concentram-se em períodos de alta volatilidade;
- ocorre pequena defasagem em pontos de reversão abrupta, comportamento esperado em modelos autoregressivos baseados em LSTM.

O gráfico de dispersão entre valores reais e previstos apresentou forte correlação linear, indicando boa capacidade preditiva.

---

# 🚶 Walk-Forward Validation

Além da divisão tradicional entre treino, validação e teste, foi implementada uma estratégia de **Walk-Forward Validation**.

Nessa abordagem o modelo é avaliado em múltiplas janelas temporais sucessivas, simulando o comportamento encontrado em ambiente de produção.

Embora a implementação esteja presente no notebook, a execução completa não foi finalizada durante os experimentos devido ao elevado tempo computacional.

Ainda assim, a estrutura permanece disponível para futuras reavaliações do modelo.

---

# 💾 Exportação do Modelo

Após o treinamento são persistidos dois artefatos fundamentais:

```
modelo_lstm.keras
```

Modelo treinado contendo arquitetura e pesos.

```
scaler.pkl
```

Objeto `StandardScaler` utilizado durante o treinamento.

A API utiliza exatamente esses mesmos artefatos durante a inferência, garantindo que o pipeline de produção seja idêntico ao utilizado no desenvolvimento do modelo.
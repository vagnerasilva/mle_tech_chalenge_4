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

## 📊 Coleta de Dados

Esta seção resume a coleta de dados e o pré-processamento utilizado no notebook principal `modelagem/fase4_MLET.ipynb` e na documentação técnica `docs/documentacao_lstm_tech_challenge.md`.

### Fonte de Dados
Os dados históricos são obtidos a partir do Yahoo Finance usando a biblioteca **yfinance**. A coleta preserva a sequência temporal dos pregões para evitar vazamento de informação e garantir que o modelo treine apenas com dados do passado.

**Principais features coletadas:**
- `Open` — preço de abertura
- `High` — preço máximo do pregão
- `Low` — preço mínimo do pregão
- `Close` — preço de fechamento *(target principal)*
- `Volume` — volume de negociação

### Pipeline de Coleta e Preparação
1. **Download via yfinance**
   - O notebook baixa dados OHLCV para o ticker selecionado.
   - Caso o retorno venha em MultiIndex, as colunas são desdobradas e o índice de data é convertido em coluna.
2. **Limpeza básica**
   - Remoção de linhas com valores faltantes (`dropna()`).
   - Reset do índice para manter o dataframe limpo.
3. **Transformação de escala**
   - Aplica `np.log1p` em `Close`, `High`, `Low`, `Open` e `Volume` para reduzir skewness e suavizar outliers.
   - Em seguida, utiliza `StandardScaler` ajustado apenas no conjunto de treino e aplicado a validação e teste.
4. **Split temporal**
   - O dataset é dividido de forma cronológica em:
     - **70% treino**
     - **15% validação**
     - **15% teste**
   - O split preserva a ordem dos dados para evitar que o modelo veja o futuro durante o treinamento.
5. **Criação de sequências**
   - As janelas de entrada `X` são construídas com `look_back` passos históricos.
   - O target `y` é o valor normalizado de `Close` no próximo passo.

### Consistência entre Notebook e API
O notebook e a API compartilham o mesmo pipeline de dados, garantindo:
- uso das mesmas features OHLCV
- normalização com scaler persistido do treino
- processamento cronológico sem shuffle
- inversão de escala (`inverse_transform` + `np.expm1`) para métricas em reais

### Referências no Repositório
- `modelagem/fase4_MLET.ipynb` — notebook de desenvolvimento e validação do modelo
- `docs/documentacao_lstm_tech_challenge.md` — documentação técnica do fluxo de coleta e modelagem
- `docs/oquefazer.md` — notas de acompanhamento e próximos passos

---

## 🧠 Modelo LSTM

### 📓 Notebook de Desenvolvimento
O modelo LSTM é desenvolvido e validado no notebook principal localizado em `modelagem/fase4_MLET.ipynb` e documentado em `docs/documentacao_lstm_tech_challenge.md`.

**Principais arquivos de suporte:**
- `modelagem/fase4_MLET.ipynb` — notebook completo com coleta de dados, pré-processamento, busca de hiperparâmetros, treinamento, avaliação e inferência.
- `docs/documentacao_lstm_tech_challenge.md` — documentação técnica detalhada do fluxo de modelagem e resultados.
- `docs/oquefazer.md` — notas de acompanhamento e próximos passos da modelagem.

**Este notebook inclui:**
- Coleta de dados via yfinance (NVDA como exemplo)
- Feature engineering com 5 indicadores técnicos
- Busca de hiperparâmetros com TimeSeriesSplit (5 folds)
- Treinamento robusto com callbacks avançados
- Avaliação completa com múltiplas métricas

### Arquitetura
O modelo usa **Bidirectional LSTM** para capturar padrões em ambas as direções temporais, com regularização L2 e BatchNormalization para estabilidade e redução de overfitting.

**Camadas (Otimizadas via TimeSeriesSplit):**
```
Input (Batch, LOOK_BACK, 5 Features)
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

> **Nota Importante:** O modelo LSTM carregado nestes endpoints é **exatamente o modelo treinado no notebook** `modelagem/fase4_MLET.ipynb`.
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
┌───────────────────────────────────────────────┐
│              Cliente / Aplicação              │
└───────────────────────────┬───────────────────┘
                            │ HTTP/REST
                            ↓
┌───────────────────────────────────────────────┐
│             FastAPI + Uvicorn (app.main)      │
│  ┌─────────────────────┬─────────────────────┐│
│  │ Routers             │ Services           ││
│  │ - health.py         │ - model.py         ││
│  │ - predict.py        │ - data.py          ││
│  │ - train.py          │ - training.py      ││
│  │ - metrics.py        │                     │
│  └─────────┬───────────┴─────────┬───────────┘│
│            │                     │            │
│            ↓                     ↓            │
│  ┌───────────────────┐  ┌──────────────────┐│
│  │ Model Artifacts    │  │ Data Pipeline     ││
│  │ - models/          │  │ - yfinance       ││
│  │   • best_lstm_model.keras │  │ - preprocessing ││
│  │   • scaler.pkl      │  │ - feature eng.   ││
│  │   • checkpoints/    │  │ - windowing      ││
│  └───────────────────┘  └──────────────────┘│
└───────────────────────────────────────────────┘
            │
            ↓
┌───────────────────────────────────────────────┐
│      Frontend estático / UI leve (app/static)│
│      Recursos servidos pela API               │
└───────────────────────────────────────────────┘
```

### Componentes Principais
- **API Layer**: recebe requisições REST, valida payloads e retorna respostas JSON.
- **Routers**: saúde, predição, treinamento e métricas distribuídos em arquivos separados.
- **Service Layer**: encapsula lógica de inferência (`model.py`), pré-processamento (`data.py`) e treinamento (`training.py`).
- **Model Artifacts**: a API consome o modelo e o scaler salvos em `models/`.
- **Data Pipeline**: mantém a mesma preparação de dados do notebook e evita data leakage.
- **Frontend estático**: arquivos em `app/static/` para interface e demonstração.

### Consistência com o Notebook
- O notebook `modelagem/fase4_MLET.ipynb` gera os artifacts que a API consome.
- `docs/documentacao_lstm_tech_challenge.md` descreve o mesmo fluxo de coleta, engenharia de features e validação.
- A API reutiliza o mesmo `LOOK_BACK`, as mesmas features OHLCV e a mesma lógica de inversão de escala.

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

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

- **Documentação Swagger**: https://mle-tech-chalenge-4.onrender.com/docs
- **ReDoc**: https://mle-tech-chalenge-4.onrender.com/redoc
- **Health Check**: https://mle-tech-chalenge-4.onrender.com/health

### 📊 Dashboard de Monitoramento

O dashboard de monitoramento e análise de performance é desenvolvido em **Streamlit** em repositório separado:

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

### Arquitetura
O modelo LSTM é ideal para capturar dependências de longo prazo em séries temporais financeiras.

**Camadas principais:**
```
Input (Batch, Seq_Length, Features)
    ↓
LSTM Layer 1 (units=64, return_sequences=True)
    ↓
Dropout (rate=0.2)
    ↓
LSTM Layer 2 (units=32, return_sequences=False)
    ↓
Dropout (rate=0.2)
    ↓
Dense Layer (units=16, activation='relu')
    ↓
Output Layer (units=1, activation='linear')
    ↓
Predição de Preço (escalar)
```

### Hiperparâmetros
- **Epochs**: 50-100 (com early stopping)
- **Batch Size**: 32-64
- **Learning Rate**: 0.001 (Adam optimizer)
- **Sequence Length**: 60 dias
- **Loss Function**: Mean Squared Error (MSE)
- **Validation Split**: 10%

### Métricas de Avaliação
- **MAE (Mean Absolute Error)** — erro médio absoluto
- **RMSE (Root Mean Squared Error)** — raiz do erro quadrático médio
- **MAPE (Mean Absolute Percentage Error)** — erro percentual absoluto médio
- **R² Score** — coeficiente de determinação

### Treinamento e Checkpoints
- Logs estruturados salvos em `logs/train.log`
- Checkpoints automáticos em `models/checkpoints/` a cada epoch
- Melhor modelo persistido em `models/best_model.h5`
- Early stopping para evitar overfitting

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

| Componente | Tecnologia | Versão |
|------------|------------|---------|
| **Linguagem** | Python | 3.10+ |
| **API** | FastAPI | 0.104+ |
| **Deep Learning** | TensorFlow | 2.13+ |
| **Dados** | Pandas | 2.0+ |
| **Requisição HTTP** | yfinance | 0.2.32+ |
| **Testes** | pytest | 7.4+ |
| **Logging** | Python logging | built-in |

---

## 📦 Como Rodar

### **Opção 1: Com Docker (Recomendado)**
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

---

## 📝 Exemplos de Uso

> **Nota**: Todos os exemplos abaixo usam `localhost:8000`. Para usar a API em produção, substitua por `https://mle-tech-chalenge-4.onrender.com/`

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

## 📚 Documentação da API

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
│   │   ├── model.py            # Gerenciamento de modelo
│   │   ├── data.py             # Pipeline de dados
│   │   └── training.py         # Lógica de treinamento
│   └── schemas/                # Validação Pydantic
├── models/
│   ├── best_model.h5           # Modelo treinado
│   ├── checkpoints/            # Checkpoints de treino
│   └── scaler.pkl              # Normalização (Min-Max)
├── logs/
│   ├── train.log               # Logs de treinamento
│   └── api.log                 # Logs da API
├── data/
│   └── precos_fechamento.csv   # Dataset histórico
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
## 📦 Repositórios Relacionados

- **[mle_tech_chalenge_4](https://github.com/vagnerasilva/mle_tech_chalenge_4)** — API FastAPI com modelo LSTM *(este repositório)*
- **[mle_tech_chalenge_4_streamlit](https://github.com/vagnerasilva/mle_tech_chalenge_4_streamlit)** — Dashboard de monitoramento e análise
- **[mle_tech_chalenge_1](https://github.com/vagnerasilva/mle_tech_chalenge_1)** — API de consulta de livros (projeto anterior)

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

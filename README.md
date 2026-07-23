# Tech Challenge Fase 4 - Previsão de Preços de Ações com LSTM

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11+-009688.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![React](https://img.shields.io/badge/Frontend-React-61DAFB.svg)
![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Visao geral

Este repositório implementa uma solução completa para previsão do próximo fechamento de ação com um modelo LSTM treinado sobre dados históricos do Yahoo Finance. A aplicação exposta em produção e em ambiente local é uma API FastAPI que também serve um frontend React compilado para `app/static`.

O projeto foi organizado para reproduzir a mesma pipeline usada no treinamento durante a inferência: os artefatos versionados em `artifacts/` são carregados pela API, o pipeline usa `log1p` e `StandardScaler`, e o modelo foi validado para o ticker `BBD`.

Para uma explicação mais completa sobre como as partes se encaixam, veja [docs/visao_geral_repositorio.md](docs/visao_geral_repositorio.md). A documentação de treino e deploy continua disponível em [docs/documentacao_lstm_tech_challenge.md](docs/documentacao_lstm_tech_challenge.md), [docs/render-deployment.md](docs/render-deployment.md) e [docs/env-config.md](docs/env-config.md).

## O que existe neste repositório

- `app/main.py`: entrada principal da API FastAPI.
- `app/app.py`: shim de compatibilidade para deploys antigos que ainda usam `app.app:app`.
- `app/api/v1/`: rotas de health, predição, métricas, logs e validação.
- `app/services/`: lógica de predição, monitoramento, logs e rate limit.
- `app/static/`: frontend compilado e servido pela API.
- `frontend/`: código-fonte do frontend React com Vite.
- `artifacts/modelo_lstm.keras`: modelo treinado.
- `artifacts/scaler.pkl`: scaler usado no treinamento e na inferência.
- `docs/`: documentação complementar do projeto e do deploy.
- `tests/`: testes automatizados da API.

## Arquitetura

```text
Yahoo Finance
  -> coleta histórica
  -> preprocessamento com log1p
  -> StandardScaler
  -> janela temporal com look_back = 30
  -> modelo LSTM
  -> desnormalizacao
  -> API FastAPI
  -> frontend React
```

O endpoint de predição carrega os dados históricos do ativo, aplica o mesmo fluxo do treino e retorna a estimativa do próximo fechamento.

## Dados e modelo

- Ativo principal validado: `BBD`.
- Janela temporal: `look_back = 30`.
- Features usadas na inferencia: `Close`, `High`, `Low`, `Open`, `Volume`.
- Artefatos de produção: `artifacts/modelo_lstm.keras` e `artifacts/scaler.pkl`.

## Endpoints principais

### Health e status

- `GET /health`
- `GET /readiness`

### Predicao

- `POST /api/v1/predict/next_close`

### Monitoramento

- `GET /api/v1/metrics/latest`
- `GET /api/v1/logs`

### Validacao

- `POST /api/v1/validation/validate`
- `GET /api/v1/validation/get-metrics`
- `GET /api/v1/validation/history`
- `GET /api/v1/validation/summary`
- `GET /api/v1/validation/stats`

## Passo a passo de uso local

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar as dependencias

```bash
pip install -r requirements-dev.txt
```

### 3. Subir a API

```bash
python -m app.main
```

Ou, se preferir, com Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Abrir a aplicacao

- API: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- Docs Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Testar a predicao

```bash
curl -X POST http://localhost:8000/api/v1/predict/next_close
```

Resposta esperada:

```json
{
  "symbol": "BBD",
  "predicted_close": 3.4482,
  "last_trading_date": "2026-07-10",
  "look_back": 30
}
```

### 6. Executar os testes

```bash
pytest -v tests/
```

Se quiser cobertura:

```bash
pytest -v --cov=app tests/
```

## Frontend React

O frontend fica no diretório `frontend/` e compila para `app/static/`, que e servido pela própria API.

### Desenvolvimento do frontend

```bash
cd frontend
npm install
npm run dev
```

### Build para produção local

```bash
cd frontend
npm install
npm run build
```

Depois do build, volte para a raiz e suba a API. O FastAPI vai servir a SPA em `/` e os assets compilados em `/static/`.

## Deploy

O deploy em produção é configurado por `render.yaml`.

- Build do frontend: `cd frontend && npm install && npm run build`
- Instalação do backend: `pip install -r requirements-prod.txt`
- Start da API: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Estrutura resumida

```text
mle_tech_chalenge_4/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── static/
│   ├── app.py
│   └── main.py
├── artifacts/
├── data/
├── docs/
├── frontend/
├── tests/
├── requirements.txt
├── requirements-dev.txt
├── requirements-prod.txt
└── render.yaml
```

## Observacao

Algumas seções antigas do README misturavam outra versao do projeto, com rotas e comandos que nao existem mais neste repositorio. Esta versao resume apenas o que esta implementado hoje.

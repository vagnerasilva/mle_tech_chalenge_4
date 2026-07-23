# Visao Geral do Repositorio

Este documento resume o que este repositório faz hoje, como as partes se conectam e qual e o fluxo recomendado de uso.

## Objetivo

O projeto entrega uma solução completa para previsão do próximo fechamento de uma ação usando um modelo LSTM treinado com dados históricos do Yahoo Finance. A aplicação exposta pelo repositório é composta por:

- uma API FastAPI em [app/main.py](../app/main.py);
- um frontend React em [frontend/](../frontend/);
- artefatos de produção em [artifacts/](../artifacts/);
- documentação complementar em [docs/](.).

## O que a aplicação faz

O fluxo principal é o seguinte:

1. busca os dados históricos do ativo no Yahoo Finance;
2. aplica o preprocessamento usado no treino, com `log1p` e `StandardScaler`;
3. monta sequências temporais com janela de `look_back = 30`;
4. executa a inferência com o modelo salvo em `artifacts/modelo_lstm.keras`;
5. grava logs, métricas e registros de validação quando aplicável;
6. expõe a resposta pela API e pelo frontend servido em `app/static`.

## Componentes do repositório

### Backend

O backend principal vive em `app/`:

- `app/main.py` cria a aplicação FastAPI, registra middleware e monta rotas.
- `app/api/v1/health.py` expõe `GET /health` e `GET /readiness`.
- `app/api/v1/predict.py` expõe `POST /api/v1/predict/next_close`.
- `app/api/v1/metrics.py` expõe métricas da avaliação offline do modelo.
- `app/api/v1/logs.py` consulta o histórico de acessos.
- `app/api/v1/validation.py` cuida da validação das predições pendentes e dos agregados de monitoramento.
- `app/services/` concentra a lógica de negócio e o acesso aos artefatos.

### Frontend

O frontend React fica em `frontend/` e é compilado para `app/static/`.

- em desenvolvimento, ele roda com Vite;
- em produção, o build gera `index.html` e os assets em `app/static/assets/`;
- a API FastAPI serve essa SPA diretamente na rota `/`.

### Artefatos

Os artefatos carregados pela API são:

- `artifacts/modelo_lstm.keras`;
- `artifacts/scaler.pkl`.

Sem esses arquivos, o endpoint de health vai indicar que o modelo nao esta carregado.

## Rotas principais

- `GET /health`
- `GET /readiness`
- `POST /api/v1/predict/next_close`
- `GET /api/v1/metrics/latest`
- `GET /api/v1/logs`
- `POST /api/v1/validation/validate`
- `GET /api/v1/validation/get-metrics`
- `GET /api/v1/validation/history`
- `GET /api/v1/validation/summary`
- `GET /api/v1/validation/stats`

## Passo a passo de uso local

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python -m app.main
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Build para servir pela API

```bash
cd frontend
npm install
npm run build
```

Depois do build, volte para a raiz do projeto e suba a API. O FastAPI vai servir a SPA e os arquivos estáticos automaticamente.

## Deploy

O deploy em produção usa [render.yaml](../render.yaml):

- primeiro faz build do frontend;
- depois instala as dependências Python de produção;
- por fim inicia `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## Relação com os outros documentos

- [documentacao_lstm_tech_challenge.md](documentacao_lstm_tech_challenge.md): explica o treinamento e a pipeline do modelo.
- [render-deployment.md](render-deployment.md): detalha o deploy no Render.
- [env-config.md](env-config.md): mostra as variáveis de ambiente.
- [oquefazer.md](oquefazer.md): registra o enunciado original e o contexto do desafio.

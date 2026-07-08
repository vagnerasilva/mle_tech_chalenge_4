# Testes — Stock LSTM Forecast API

Suite de testes da API de previsão de fechamento de ações (Tech Challenge Fase 4).

## Estrutura

- `conftest.py` — fixtures `test_db` (SQLite em memória, usado só pela tabela de
  logs/monitoramento) e `client` (TestClient FastAPI).
- `test_health.py` — `GET /api/v1/health`.
- `test_model_info.py` — `GET /api/v1/model/info`, `GET /api/v1/model/metrics`,
  e o caso de modelo não carregado (503).
- `test_predict.py` — `POST /api/v1/predict`: payload inválido (nem symbol nem
  historical_data / os dois ao mesmo tempo), dados históricos insuficientes
  para `sequence_length`, modelo não carregado, opção B (historical_data) e um
  teste de integração real com yfinance para o ticker oficial (BBD).
- `test_data_collect.py` — `POST /api/v1/data/collect`: datas inválidas, ticker
  inválido, coleta válida.
- `test_ml_features_and_monitoring.py` — `GET /api/v1/ml/features` e
  `GET /api/v1/monitoring/metrics`.

## Executar

```bash
pip install -r requirements-dev.txt
pytest -v
```

Alguns testes (`test_predict_with_symbol_fetches_live_data`,
`test_collect_valid_symbol_returns_summary`) fazem chamadas reais à yfinance —
precisam de acesso à internet para passar.

Com cobertura:
```bash
pytest --cov=app --cov=ml --cov-report=term-missing
```

# mle_tech_chalenge_4
TECH CHALLENGE Deep Learning e IA 




## Visão geral
Repositório com a solução proposta para o Tech Challenge — Fase 4 (Pós Tech / MLET). 

Objetivo: implementar uma API/serviço que treina e serve um modelo de Deep Learning para o problema descrito no enunciado (preprocessamento, treinamento, inferência e avaliação).

## Principais requisitos 
- Ingestão e pré-processamento dos dados fornecidos.
- Treinamento de modelo de Deep Learning com logs de treino e checkpoints.
- Endpoint de inferência para previsões em lote e single-shot.
- Testes automatizados (unit + integração) e script de avaliação.
- Documentação completa e instruções para rodar localmente e em contêiner.
- Critérios de avaliação: corretude das previsões, arquitetura, qualidade do código, cobertura de testes e reprodutibilidade.

## Entregáveis
- Código-fonte com separação clara (src, tests, scripts).
- README (este arquivo) com instruções de execução.
- Dockerfile e docker-compose para facilitar execução.
- Scripts de migração/seed (se usar BD) e scripts para reproduzir experimentos.
- Postman collection / exemplos curl para endpoints.
- Relatório breve com métricas do modelo (ex.: Accuracy, Precision, Recall, F1) e decisões arquiteturais.

## Arquitetura proposta
- Monolito organizado por camadas (api, core/model, data, tests) ou microserviço simples.
- Componentes:
  - API (FastAPI / Express) — serve endpoints de health, predict, train, metrics.
  - Pipeline de treino (PyTorch / TensorFlow) com checkpoints.
  - Armazenamento de modelos (local / S3).
  - Banco de dados leve (SQLite / PostgreSQL) para metadados (opcional).
  - Docker para reprodutibilidade.

## Endpoints (exemplo)
- GET /health — status do serviço
- POST /predict — body JSON com amostra(s) -> retorna predição(s)
- POST /train — inicia treino (sync/async) com parâmetros opcionais
- GET /metrics — retorna métricas do último treino

## Tecnologias sugeridas
- Linguagem: Python 3.10+
- Framework API: FastAPI
- DL: PyTorch ou TensorFlow (escolher 1)
- Testes: pytest
- Container: Docker + docker-compose
- CI: GitHub Actions (opcional)

## Como rodar
1. Clonar:
   git clone <repo-url>
   cd mle_tech_chalenge_4
2. Fazer build com Docker:
   docker-compose up --build -d
3. Rodar local sem Docker:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
4. Testes:
   pytest --maxfail=1 --disable-warnings -q

## Execução rápida de exemplos (curl)
- Health:
  curl http://localhost:8000/health
- Predict (single):
  curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"data": [...]}'

## Treino e reprodutibilidade
- Script de treino: scripts/train.sh (aceita parâmetros: --epochs, --batch, --lr)
- Checkpoints salvos em models/
- Log de treino em logs/train.log
- Fixar seed para reprodutibilidade e documentar ambiente (requirements.txt / environment.yml)

## Testes e cobertura
- Meta: cobertura >= 80% (ajustar conforme requisitos)
- Executar: pytest
- Incluir testes para: pré-processamento, inferência, endpoints, integração simples de treino/inferência

## Observabilidade e deploy
- Logs estruturados em JSON.
- Health/Readiness endpoints para orquestração.
- Dockerfile otimizado para produção; manifests Kubernetes (opcional).

## Critérios de aceitação
- Implementa requisitos funcionais do enunciado.
- Código limpo, documentado e testado.
- Reprodutibilidade via Docker.
- Métricas e checkpoints disponíveis para avaliação.

## Próximos passos
- Extrair detalhes específicos do PDF (ex.: formatos de input/output, métricas esperadas, dataset) e ajustar payloads/endpoints.
- Escolher stack definitivo (PyTorch vs TensorFlow, DB se necessário).
- Implementar pipeline e testes automatizados.

## Contato
- Autor/Equipe: adicionar nome e contato.
- Vagner
- Cecilia
- Pedro 
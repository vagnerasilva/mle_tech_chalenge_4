# 🚀 Deploy no Render.com — Configuração de Variáveis

Guia prático para configurar e fazer deploy da API no Render.com.

---

## 📋 Pré-requisitos

- Conta ativa no [Render.com](https://render.com)
- Repositório GitHub pushado
- API rodando localmente sem erros

---

## 🔧 Passo 1: Criar/Atualizar o Serviço

### 1.1 Acessar Render.com

1. Faça login em [https://dashboard.render.com](https://dashboard.render.com)
2. Clique em **New** → **Web Service**
3. Conecte seu repositório GitHub

### 1.2 Configurar o Serviço

| Campo | Valor |
|-------|-------|
| **Repository** | `vagnerasilva/mle_tech_chalenge_4` |
| **Branch** | `main` (ou sua branch) |
| **Runtime** | `Python 3.10` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0` |
| **Instance Type** | Free (ou pago se quiser melhor performance) |
| **Auto-deploy** | ✅ Ativado (opcional) |

---

## 🔐 Passo 2: Configurar Variáveis de Ambiente

### No Dashboard do Render

1. Vá até seu serviço
2. Clique em **Settings** (ou a engrenagem ⚙️)
3. Scroll até **Environment Variables**
4. Clique em **Add Environment Variable**

### 2.1 Variáveis Obrigatórias

Adicione estas variáveis exatamente como abaixo:

#### **Modelo & Scaler** (CRÍTICO)

```
APP_MODEL_PATH = ml/modelo_lstm.keras
APP_SCALER_PATH = ml/scaler.pkl
```

⚠️ **OBRIGATÓRIO**: Os arquivos `ml/modelo_lstm.keras` e `ml/scaler.pkl` devem estar no repositório! Sem eles, `/readiness` retornará 503.

#### **Database** (Logs de Auditoria)

```
APP_DB_PATH = /tmp/app_logs.db
```

⚠️ Nota: `/tmp` é limpado ao deploy (não persiste). Para persistência real, use PostgreSQL do Render.

#### **Hiperparâmetros do Modelo** (CRÍTICO — não mudar!)

```
APP_LOOK_BACK = 30
APP_FEATURE_COLS = ["Close", "High", "Low", "Open", "Volume"]
```

### 2.2 Variáveis Recomendadas

#### **App Básico**

```
APP_APP_NAME = Previsão de Preços de Ações — LSTM
```

#### **CORS** (Segurança)

```
APP_CORS_ORIGINS = ["https://seu-frontend-url.com"]
```

Replace `seu-frontend-url.com` com seu domínio real (ex: `mle-tech-chalenge-4-streamlit.onrender.com`).

Se precisar de múltiplos domínios:
```
APP_CORS_ORIGINS = ["https://seu-frontend-url.com", "https://outro-dominio.com"]
```

#### **Rate Limiting** (Proteção contra Abuso)

```
APP_RATE_LIMIT_MAX_REQUESTS = 10
APP_RATE_LIMIT_WINDOW_SECONDS = 300
```

Máximo 10 requisições por IP em 5 minutos. 11ª retorna 429.

#### **Debug & Logging** (Segurança)

```
LOG_LEVEL = WARNING
DEBUG = False
```

### 2.3 Variáveis Opcionais

#### **Host** (geralmente não precisa alterar)

```
HOST = 0.0.0.0
```

⚠️ Deixe como `0.0.0.0` para aceitar requisições externas.

#### **Port** (Render.com define automaticamente)

```
# NÃO ADICIONE PORT — Render.com a configura automaticamente
# A API detecta em: port = int(os.environ.get("PORT", 8000))
```

---

## 📋 Exemplo Completo de Variáveis

Quando tudo estiver configurado, suas variáveis devem parecer assim:

```
APP_APP_NAME = Previsão de Preços de Ações — LSTM
APP_CORS_ORIGINS = ["https://mle-tech-chalenge-4-streamlit.onrender.com"]
APP_MODEL_PATH = ml/modelo_lstm.keras
APP_SCALER_PATH = ml/scaler.pkl
APP_DB_PATH = /tmp/app_logs.db
APP_LOOK_BACK = 30
APP_FEATURE_COLS = ["Close", "High", "Low", "Open", "Volume"]
APP_RATE_LIMIT_MAX_REQUESTS = 10
APP_RATE_LIMIT_WINDOW_SECONDS = 300
LOG_LEVEL = WARNING
DEBUG = False
HOST = 0.0.0.0
```

---

## 🚀 Passo 3: Deploy

### Primeira Vez

```bash
# 1. Commite e push suas mudanças
git add .
git commit -m "feat: configurar variáveis de ambiente para Render"
git push origin main

# 2. Render.com detecta push automaticamente
# - Clique em "Deploy" no dashboard
# - Aguarde ~5-10 minutos
```

### Deploys Subsequentes

- Após configurar as variáveis, **todo push** ao `main` triggera deploy automático
- Veja logs em **Logs** aba do dashboard

---

## ✅ Validar Deploy

### 1. Health Check

```bash
curl https://mle-tech-chalenge-4.onrender.com/health
```

Resposta esperada:
```json
{"status":"ok","model_loaded":true}
```

### 2. Readiness Check

```bash
curl https://mle-tech-chalenge-4.onrender.com/readiness
```

Resposta esperada:
```json
{"ready":true}
```

### 3. Predição Test

```bash
curl -X POST https://mle-tech-chalenge-4.onrender.com/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BBD"}'
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

### 4. Documentação

- **Swagger**: https://mle-tech-chalenge-4.onrender.com/docs
- **ReDoc**: https://mle-tech-chalenge-4.onrender.com/redoc

---

## 🔍 Troubleshooting

### Erro: "Artefatos do modelo não encontrados"

```json
{"ready":false,"detail":"Artefatos do modelo não encontrados"}
```

**Solução:**
1. Confirme que `ml/modelo_lstm.keras` e `ml/scaler.pkl` existem no repo
2. Confirme que `APP_MODEL_PATH` e `APP_SCALER_PATH` estão corretos
3. Faça push dos arquivos: `git add ml/`
4. Trigger deploy manual no Render

### Erro: "model_loaded: false"

```json
{"status":"ok","model_loaded":false}
```

**Mesmo procedimento acima** — arquivos não encontrados.

### Erro: CORS bloqueando requisições

```
Access to XMLHttpRequest from origin 'https://meu-frontend.com' 
blocked by CORS policy
```

**Solução:**
1. Vá para Settings → Environment
2. Edite `APP_CORS_ORIGINS`
3. Adicione seu domínio:
   ```
   APP_CORS_ORIGINS = ["https://meu-frontend.com"]
   ```
4. Salve e aguarde redeploy

### Erro: Timeout ou slow response

**Possíveis causas:**
- Plano Free do Render (recursos limitados)
- API espera yfinance responder (rede lenta)

**Soluções:**
- Use Render Paid Instance (melhor performance)
- Implemente caching de predições
- Monitore em `/api/v1/logs`

### Erro: 500 Internal Server Error

**Causas comuns:**
- Modelo não carregado (veja "Artefatos não encontrados")
- Variáveis de configuração erradas
- Erro na pipeline de predição

**Como debugar:**
1. Verifique os logs: Render Dashboard → Logs
2. Teste localmente: `uvicorn app.main:app`
3. Confirme `.env` tem valores corretos
4. Execute testes: `pytest -v`

---

## 🔄 Atualizar Variáveis Existentes

Se precisar alterar uma variável:

1. Vá para Settings → Environment Variables
2. Clique no ✏️ (edit) de uma variável
3. Altere o valor
4. Clique em **Save**
5. Render redeploy automaticamente (2-5 min)

---

## 📊 Monitorar Logs em Produção

### Via Render Dashboard

1. Acesse seu serviço
2. Clique em **Logs**
3. Veja logs em tempo real (últimos deploys, requisições, erros)

### Via cURL

```bash
# Ver últimas 50 requisições
curl https://mle-tech-chalenge-4.onrender.com/api/v1/logs?limit=50
```

---

## 🔐 Boas Práticas de Segurança

### ✅ Faça:

- ✅ Mantenha `.env` fora do git (`.gitignore`)
- ✅ Configure `CORS_ORIGINS` apenas para seus domínios
- ✅ Use `DEBUG=False` em produção
- ✅ Use `LOG_LEVEL=WARNING` em produção
- ✅ Monitore logs regularmente

### ❌ Não Faça:

- ❌ Comite arquivo `.env`
- ❌ Use `CORS_ORIGINS = ["*"]` em produção
- ❌ Deixe `DEBUG=True` em produção
- ❌ Compartilhe variáveis secretas em issues/PRs

---

## 📚 Referências

- [Render.com Web Service Docs](https://render.com/docs/web-services)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 💡 Próximos Passos

1. **Conectar Dashboard Streamlit** — Mesmo padrão, outro Web Service
2. **Implementar Caching** — Redis para cache de predições
3. **Monitoramento Avançado** — Prometheus/Grafana
4. **CI/CD com GitHub Actions** — Testes automáticos antes de deploy

---

**Última atualização**: 2026-07-13  
**Status**: ✅ Pronto para uso

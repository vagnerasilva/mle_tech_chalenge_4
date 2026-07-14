# 🔐 Rate Limiting — Proteção contra Abuso

Documentação sobre o sistema de rate limiting da API.

---

## 📋 Configuração

**Limite Padrão:**
- 📊 **Máximo**: 10 requisições por IP
- ⏱️ **Janela**: 5 minutos (300 segundos)
- 🚫 **Rejeição**: 11ª requisição e subsequentes retornam **429 Too Many Requests**

**Storage:**
- 💾 **Banco**: SQLite (tabela `rate_limit_logs`)
- 🧹 **Limpeza**: Automática de registros > 5 minutos

---

## 🎯 Behavior

### Requisição Permitida

```
Requisição 1-10 do mesmo IP numa janela de 5 min
    ↓
✅ Status 200 (ou outro status conforme endpoint)
Requisição é processada normalmente
Entrada criada em `rate_limit_logs`
```

### Requisição Bloqueada

```
Requisição 11+ do mesmo IP na mesma janela
    ↓
❌ Status 429 Too Many Requests
Header: Retry-After: <segundos>
Response Body:
{
  "detail": "Limite de taxa excedido. Aguarde X segundos.",
  "retry_after": X
}
```

### Exemplo Prático

```bash
# Minuto 0 — Cliente X faz requisições
curl http://localhost:8000/api/v1/predict/single  # 1 ✅
curl http://localhost:8000/api/v1/predict/single  # 2 ✅
curl http://localhost:8000/api/v1/predict/single  # 3 ✅
...
curl http://localhost:8000/api/v1/predict/single  # 10 ✅

# 11ª requisição
curl http://localhost:8000/api/v1/predict/single  # ❌ 429 (aguarde ~300 seg)

# Minuto 5 (300+ segundos depois)
curl http://localhost:8000/api/v1/predict/single  # ✅ Contador resetou!
```

---

## 📌 Endpoints NÃO Afetados

Rate limiting NÃO é aplicado a:
- `GET /health` — Status da API
- `GET /readiness` — Probe de disponibilidade

Estes podem ser chamados continuamente (ex: monitoramento automático).

---

## 🔍 Endpoints Protegidos

Rate limiting é aplicado a TODOS os outros endpoints:

| Endpoint | Proteção |
|----------|----------|
| `POST /api/v1/predict/single` | ✅ Rate limited |
| `POST /api/v1/predict/batch` | ✅ Rate limited |
| `POST /api/v1/predict/sequence` | ✅ Rate limited |
| `GET /api/v1/metrics/latest` | ✅ Rate limited |
| `GET /api/v1/logs` | ✅ Rate limited |

---

## 🛡️ Como Funciona

### 1. Extração do IP

O middleware detecta o IP real do cliente com prioridade:
1. Header `X-Forwarded-For` (reverse proxy)
2. Header `X-Real-IP` (proxy alternativo)
3. `request.client.host` (conexão direta)

```python
# Em produção (Render.com):
# X-Forwarded-For: 192.168.1.1, 10.0.0.1
# Usa: 192.168.1.1 (primeira entrada)

# Localmente:
# Usa: 127.0.0.1
```

### 2. Consulta do Banco

```sql
-- Contar requisições do IP nos últimos 300 segundos
SELECT COUNT(*) FROM rate_limit_logs
WHERE ip_address = '192.168.1.1'
  AND requested_at >= NOW() - INTERVAL '300 seconds'
```

### 3. Decisão

- **Contagem < 10**: ✅ Permitir + registrar em `rate_limit_logs`
- **Contagem >= 10**: ❌ Rejeitar com 429 + calcular tempo de espera

### 4. Limpeza Automática

```sql
-- Executado antes de cada verificação
DELETE FROM rate_limit_logs
WHERE requested_at < NOW() - INTERVAL '300 seconds'
```

---

## 💻 Exemplos de Uso

### cURL — Requisição Permitida

```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BBD"}'

# Resposta: 200 OK
{
  "symbol": "BBD",
  "predicted_close": 3.4482,
  "last_trading_date": "2026-07-10",
  "look_back": 30
}
```

### cURL — Requisição Bloqueada

```bash
# Após 10 requisições rápidas...
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BBD"}'

# Resposta: 429 Too Many Requests
{
  "detail": "Limite de taxa excedido. Aguarde 287 segundos.",
  "retry_after": 287
}

# Header também contém:
# Retry-After: 287
```

### cURL — Health Check (não afetado)

```bash
# Posso chamar infinitas vezes
curl http://localhost:8000/health
curl http://localhost:8000/health
curl http://localhost:8000/health
# Todas retornam 200 OK — sem rate limiting!
```

### Python Requests — Com Retry

```python
import time
import requests

def predict_with_retry(symbol: str, max_retries: int = 3):
    url = "http://localhost:8000/api/v1/predict/single"
    payload = {"symbol": symbol}

    for attempt in range(max_retries):
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:
            # Rate limit atingido — aguardar
            retry_after = response.headers.get("Retry-After", 300)
            retry_after = int(retry_after)
            print(f"Rate limited. Aguardando {retry_after}s...")
            time.sleep(retry_after)
            # Tentar novamente

        else:
            raise Exception(f"Erro {response.status_code}: {response.text}")

    raise Exception("Máximo de tentativas atingido")

# Usar
result = predict_with_retry("BBD")
print(result)
```

---

## 📊 Monitorar Rate Limit

### Via Banco SQLite

```bash
# Conectar ao banco
sqlite3 app_logs.db

# Ver requisições recentes por IP
SELECT ip_address, COUNT(*) as count, MAX(requested_at) as latest
FROM rate_limit_logs
WHERE requested_at >= datetime('now', '-5 minutes')
GROUP BY ip_address
ORDER BY count DESC;

# Exemplo de output:
# ip_address    | count | latest
# 192.168.1.1   | 10    | 2026-07-13 14:30:45
# 10.0.0.5      | 3     | 2026-07-13 14:30:22
```

### Via cURL (logs da API)

```bash
# Ver últimas requisições (incluindo rejeitadas)
curl http://localhost:8000/api/v1/logs?limit=100 | jq '.[] | select(.status_code == 429)'

# Buscar por IP específico
curl http://localhost:8000/api/v1/logs?limit=100 | jq '.[] | select(.ip_address == "127.0.0.1")'
```

---

## ⚙️ Configuração Customizada

### Mudar Limite Padrão

Editar em `app/services/rate_limit_service.py`:

```python
class RateLimitService:
    # Padrão: 10 requisições
    MAX_REQUESTS = 20  # ← Alterar para 20

    # Padrão: 5 minutos (300 seg)
    WINDOW_SECONDS = 600  # ← Alterar para 10 min
```

**Depois:**
```bash
# Reinstalar e rodar
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Excluir Rota de Rate Limiting

Editar `app/main.py`, função `rate_limit_middleware`:

```python
# Adicionar mais rotas que não querem rate limiting
if request.url.path in ("/health", "/readiness", "/nova-rota"):
    return await call_next(request)
```

---

## 🔒 Segurança

### ✅ Proteção Contra

- 🚨 **DDoS simples**: Bloqueio por IP após 10 req/5min
- 🤖 **Scrapers/Bots**: Limite força redução de abusos
- 😈 **Brute Force**: Limite em endpoints de predição

### ⚠️ NÃO Protege Contra

- 🌍 **DDoS distribuído**: Múltiplos IPs → bypass
- 🔄 **Proxy rotation**: Trocar IP frequentemente → bypass
- 🏢 **Corporate networks**: Múltiplos usuários = 1 IP

**Recomendação**: Para proteção real contra DDoS, usar:
- Cloudflare (DDoS mitigation)
- AWS WAF (Web Application Firewall)
- Rate limiting em reverse proxy (Nginx)

---

## 🐛 Troubleshooting

### Problema: Recebo 429 mas não fiz tantas requisições

**Causa Provável:**
- Seu IP é compartilhado (corporate proxy, VPN, shared network)
- Múltiplos usuários no mesmo IP fazem requisições
- Cliente com retry automático amplificando requisições

**Solução:**
- Se desenvolvedor: use `localhost` em dev local
- Se produção: configure IP exclusivo ou whitelist

### Problema: Rate limit não funciona

**Checklist:**
1. Tabela `rate_limit_logs` existe? → `sqlite3 app_logs.db ".tables"`
2. Middleware foi iniciado? → Veja logs do uvicorn
3. Banco está corrompido? → Remova `app_logs.db` e reinicie

```bash
# Debug: ativar logs verbosos
LOG_LEVEL=DEBUG uvicorn app.main:app
```

### Problema: Aguarde X segundos é inexato

**Esperado**: O cálculo é aproximado (baseado em timestamp do primeiro acesso).
- Requisição 1 às 14:30:00.500
- Requisição 11 às 14:30:05.200 → "aguarde ~294 seg"
- Requisição 11 pode ser feita ~294s depois (14:35:00)

Variação de 1-2 segundos é normal.

---

## 📚 Referências

- [HTTP 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)
- [Retry-After Header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

---

**Última atualização**: 2026-07-13  
**Status**: ✅ Implementado e testado

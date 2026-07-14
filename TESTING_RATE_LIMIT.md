# 🧪 Guia de Testes — Rate Limiting

Instruções para testar o sistema de rate limiting localmente antes do commit.

---

## 📋 Setup Pré-teste

### 1. Verificar Configurações

Confirme que `.env` tem rate limiting ativado:

```bash
cat .env | grep RATE_LIMIT
```

**Output esperado:**
```
APP_RATE_LIMIT_MAX_REQUESTS=10
APP_RATE_LIMIT_WINDOW_SECONDS=300
```

### 2. Limpar Banco (Importante!)

```bash
# Remover banco antigo para começar limpo
rm app_logs.db 2>/dev/null || true
echo "✅ Banco limpo"
```

### 3. Iniciar a API

```bash
# Terminal 1 — API
source venv/bin/activate
pip install -r requirements.txt  # Se precisar
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 4. Validar Health Check

```bash
# Terminal 2 — Teste
curl http://localhost:8000/health
```

**Output esperado:**
```json
{"status":"ok","model_loaded":true}
```

---

## 🧪 Teste 1: Health Check (Sem Rate Limit)

Health check **não deve** ter rate limiting:

```bash
# Fazer 20 requisições
for i in {1..20}; do
    curl -s http://localhost:8000/health | jq .
done

# Esperado: Todas retornam 200 OK
```

---

## 🧪 Teste 2: Predição (Com Rate Limit)

### 2A — Requisições Permitidas (1-10)

```bash
# Fazer 10 requisições
for i in {1..10}; do
    echo "Requisição $i:"
    curl -s -w "Status: %{http_code}\n" -X POST http://localhost:8000/api/v1/predict/single \
        -H "Content-Type: application/json" \
        -d '{"symbol":"BBD"}' | jq .
done

# Esperado: Todas retornam 200 ou 422 (não 429)
```

### 2B — Requisição Bloqueada (11+)

```bash
# Fazer 11ª requisição
echo "Requisição 11 (deve ser bloqueada):"
curl -s -w "Status: %{http_code}\n" -X POST http://localhost:8000/api/v1/predict/single \
    -H "Content-Type: application/json" \
    -d '{"symbol":"BBD"}'

# Esperado: Retorna 429 com Retry-After
```

**Output esperado:**
```
Status: 429
{
  "detail": "Limite de taxa excedido. Aguarde 287 segundos.",
  "retry_after": 287
}
```

### 2C — Verificar Header Retry-After

```bash
curl -s -w "Retry-After: %{http_header{retry-after}}\n" -X POST http://localhost:8000/api/v1/predict/single \
    -H "Content-Type: application/json" \
    -d '{"symbol":"BBD"}'

# Esperado: Retry-After: 287 (ou similar)
```

---

## 🧪 Teste 3: Usar Script Automatizado

```bash
# Executar script que faz 15 requisições automaticamente
./test_rate_limit_manual.sh

# Esperado: Primeiras 10 com ✅, 11ª+ com 🚫 429
```

---

## 🧪 Teste 4: Batch Predict (Com Rate Limit)

```bash
# Fazer 11 requisições em lote
for i in {1..11}; do
    echo "Requisição $i:"
    curl -s -w "Status: %{http_code}\n" -X POST http://localhost:8000/api/v1/predict/batch \
        -H "Content-Type: application/json" \
        -d '{"symbols":["BBD"]}'
done

# Esperado: Primeiras 10 com 200, 11ª com 429
```

---

## 🧪 Teste 5: Monitorar Banco SQLite

Enquanto testa, visualize os registros de rate limit:

```bash
# Terminal 3 — Monitorar banco
while true; do
    clear
    echo "=== Rate Limit Logs ==="
    sqlite3 app_logs.db "
        SELECT ip_address, COUNT(*) as count, MAX(requested_at) as latest
        FROM rate_limit_logs
        WHERE requested_at >= datetime('now', '-5 minutes')
        GROUP BY ip_address
        ORDER BY latest DESC;
    "
    sleep 1
done
```

---

## 🧪 Teste 6: Verificar Logs da API

```bash
# Ver últimas requisições (incluindo bloqueadas)
curl -s http://localhost:8000/api/v1/logs?limit=20 | jq '.[] | {method, path, status_code, ip_address}'

# Esperado: Ver requisições com status_code 429
```

---

## 🧪 Teste 7: Configuração Customizada

### 7A — Aumentar Limite para Testes

Se quiser testar com limite menor, edite `.env`:

```bash
# .env — deixar mais permissivo para debug
APP_RATE_LIMIT_MAX_REQUESTS=3      # Apenas 3 requisições
APP_RATE_LIMIT_WINDOW_SECONDS=60   # Janela de 1 minuto
```

Reinicie a API:
```bash
# Ctrl+C para parar
# Depois:
uvicorn app.main:app --reload
```

Teste novamente:
```bash
for i in {1..5}; do
    curl -s -w "[$i] Status: %{http_code}\n" -X POST http://localhost:8000/api/v1/predict/single \
        -H "Content-Type: application/json" \
        -d '{"symbol":"BBD"}'
done

# Esperado: 429 na 4ª requisição (índice 3)
```

### 7B — Desativar Rate Limiting (Teste sem limite)

```bash
# .env — muito permissivo
APP_RATE_LIMIT_MAX_REQUESTS=1000   # Limite muito alto
APP_RATE_LIMIT_WINDOW_SECONDS=1    # Janela muito curta
```

Todas as requisições passam sem bloqueio.

---

## ✅ Checklist de Validação

Após testes, confirme:

- [ ] Health check funciona infinitas vezes (sem rate limit)
- [ ] Readiness funciona infinitas vezes (sem rate limit)
- [ ] Requisições 1-10 de `/predict/*` retornam 200/422
- [ ] Requisição 11+ retorna 429 Too Many Requests
- [ ] Header `Retry-After` está presente e > 0
- [ ] Response body inclui `retry_after` e `detail`
- [ ] Banco `rate_limit_logs` é criado automaticamente
- [ ] Limpeza automática de registros > 5 min funciona
- [ ] Configurações via `.env` são respeitadas

---

## 🐛 Troubleshooting

### Não vejo 429 na 11ª requisição

**Causas possíveis:**
1. Banco `app_logs.db` não foi limpado antes
2. Rate limit está desativado (.env não carregado)
3. Middleware não foi registrado

**Solução:**
```bash
# 1. Parar API (Ctrl+C)
# 2. Limpar banco
rm app_logs.db

# 3. Verificar .env
cat .env | grep RATE_LIMIT

# 4. Reiniciar API
uvicorn app.main:app --reload
```

### Ver erro "rate_limit_logs table doesn't exist"

**Solução:**
```bash
# A tabela é criada automaticamente por Base.metadata.create_all()
# Se isso não aconteceu:

# 1. Parar API
# 2. Remover banco
rm app_logs.db

# 3. Reiniciar (vai recriar tudo)
uvicorn app.main:app --reload
```

### Script test_rate_limit_manual.sh não funciona

```bash
# Dar permissão de execução
chmod +x test_rate_limit_manual.sh

# Executar
./test_rate_limit_manual.sh
```

---

## 📊 Dados Esperados

### Tabela rate_limit_logs

```sql
SELECT * FROM rate_limit_logs LIMIT 5;

-- id | ip_address  | requested_at
-- 1  | 127.0.0.1   | 2026-07-13 14:30:00.123
-- 2  | 127.0.0.1   | 2026-07-13 14:30:01.456
-- 3  | 127.0.0.1   | 2026-07-13 14:30:02.789
-- ...
```

### Resposta 429

```json
{
  "detail": "Limite de taxa excedido. Aguarde 287 segundos.",
  "retry_after": 287
}
```

Com headers:
```
HTTP/1.1 429 Too Many Requests
Retry-After: 287
```

---

## 🎯 Próximos Passos (Após Testes Bem-sucedidos)

```bash
# 1. Restaurar .env ao padrão
APP_RATE_LIMIT_MAX_REQUESTS=10
APP_RATE_LIMIT_WINDOW_SECONDS=300

# 2. Rodar testes automatizados
pytest tests/test_rate_limit.py -v

# 3. Fazer commit
git add -A
git commit -m "feat: implementar rate limiting com SQLite"

# 4. Push
git push origin feature/rate-limiting
```

---

**Status**: 🔄 Pronto para testes  
**Última atualização**: 2026-07-13

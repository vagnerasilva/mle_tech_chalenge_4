# ⚡ TESTE RÁPIDO — Rate Limiting (5 minutos)

## 🚀 Setup (2 min)

```bash
cd /Users/vagnerantononiodasilva/projetos_new/mle_tech_chalenge_4

# Terminal 1: Iniciar API
source venv/bin/activate
rm app_logs.db 2>/dev/null  # Limpar banco antigo
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Aguarde até ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## ✅ Validar Setup (1 min)

```bash
# Terminal 2: Health check
curl http://localhost:8000/health

# Esperado: {"status":"ok","model_loaded":true}
```

## 🧪 Teste Rate Limit (2 min)

```bash
# Terminal 2: Executar script de teste
cd /Users/vagnerantononiodasilva/projetos_new/mle_tech_chalenge_4
./test_rate_limit_manual.sh
```

### Esperado:
```
Requisição 1: ✅ 200 OK
Requisição 2: ✅ 200 OK
...
Requisição 10: ✅ 200 OK
Requisição 11: 🚫 429 Too Many Requests (aguarde ~295 seg)
Requisição 12: 🚫 429 Too Many Requests (aguarde ~294 seg)
...
Requisição 15: 🚫 429 Too Many Requests (aguarde ~290 seg)
```

## ✨ Se tudo passou:

```bash
# Voltar para Terminal 1 (API) e ver Ctrl+C

# Fazer commit
git add -A
git commit -m "feat: implementar rate limiting com SQLite - 10 req/5min/IP"
```

---

## 🐛 Se algo deu errado:

**429 não apareceu na 11ª?**
```bash
# Parar API (Ctrl+C)
rm app_logs.db
uvicorn app.main:app --reload  # Reiniciar
```

**Erro "rate_limit_logs table doesn't exist"?**
```bash
# Limpar e reiniciar (tabela é criada automaticamente)
rm app_logs.db
```

---

## 📚 Para mais detalhes:
- `TESTING_RATE_LIMIT.md` — Guia completo com 7 testes
- `docs/rate-limiting.md` — Documentação técnica
- `docs/env-config.md` — Configurações

---

**⏱️ Tempo total: ~5 minutos**  
**✅ Status: Pronto para testar agora**

# 🎯 Configuração do Front-end para BBD

## Informações do Modelo

**Ticker Específico:** BBD (Banco Bradesco ADR)  
**Exchange:** NYSE (New York Stock Exchange)  
**Tipo de Modelo:** LSTM Bidirecional  
**Dados de Treinamento:** Histórico completo do BBD

---

## Configurações Aplicadas

### 1. **Ticker Fixo**
```jsx
const TRAINED_TICKER = 'BBD'
const TRAINED_COMPANY = 'Banco Bradesco ADR (NYSE)'
```

- O ticker é **fixo** no formulário (não é alterável)
- Não há campo de entrada para selecionar outras ações
- Evita erros ao tentar prever preços de ações não treinadas

### 2. **Header com Badge**
Na página principal, um badge exibe:
```
🎯 Modelo Treinado Para: BBD (Banco Bradesco ADR - NYSE)
```

### 3. **Informação no Formulário**
O componente `PredictionForm` mostra:
- ℹ️ "Este modelo foi treinado especificamente para BBD"
- Informações sobre a rede LSTM Bidirecional
- Aviso de que a precisão é otimizada para BBD

### 4. **Resultado da Previsão**
O `ResultCard` exibe:
- Ticker + Empresa completa (Banco Bradesco ADR)
- Preço atual do BBD
- Tabela de previsões com variação percentual

---

## Estrutura de Dados Esperados

A API retorna dados da forma:

```json
{
  "ticker": "BBD",
  "last_price": 12.50,
  "predictions": [12.55, 12.60, 12.52, ...],
  "rmse": 0.2345,
  "mae": 0.1234,
  "prediction_date": "2026-07-21T10:30:00Z"
}
```

---

## Por que BBD é Específico?

1. **Dados de Treinamento:** O modelo foi treinado com dados históricos específicos do BBD
2. **Normalização:** O scaler foi treinado com a distribuição de preços do BBD
3. **Performance:** A rede é otimizada para os padrões de comportamento do BBD
4. **Generalização:** Usar com outros tickers resultaria em previsões imprecisas

---

## Modificando para Outra Ação

Se retrainer o modelo para outra ação (ex: PETR4, VALE5):

1. **Atualizar constantes em `PredictionForm.jsx`:**
```jsx
const TRAINED_TICKER = 'PETR4'
const TRAINED_COMPANY = 'Petróleo Brasileiro S/A'
```

2. **Atualizar badge em `App.jsx`:**
```jsx
🎯 Modelo Treinado Para: PETR4 (Petróleo Brasileiro)
```

3. **Rebuild do frontend:**
```bash
npm run build
```

---

## Interface Visual

### Header
- Mostra o ticker específico em destaque
- Cor primária (azul) para identificação visual

### Formulário
- Campo de ticker desabilitado (read-only)
- Informações sobre o modelo
- Selector de dias (1-30)

### Resultados
- Última cotação do BBD
- Previsões para próximos dias
- Indicadores de variação (% positiva/negativa)
- Métricas de erro (RMSE, MAE)

---

## Testes Locais

```bash
# Dev (com proxy)
npm run dev

# Build
npm run build

# Test com FastAPI
python -m app.main
# Acesse: http://localhost:8000
```

---

## Deploy em Produção

1. BBD é o ticker padrão no front-end
2. API deve estar preparada para aceitar apenas BBD
3. Validar que o modelo em `artifacts/modelo_lstm.keras` é para BBD

Para mais informações sobre o modelo, veja: `../docs/documentacao_lstm_tech_challenge.md`


http://localhost:5173/api/v1/predict
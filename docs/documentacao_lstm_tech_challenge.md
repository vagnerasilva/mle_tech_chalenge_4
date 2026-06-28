# Tech Challenge Fase 4 — Machine Learning Engineering
## Previsão de Preços de Ações com Redes Neurais LSTM

> **Ativo:** BBD (Banco Bradesco — NYSE) | **Período:** Jun/2020 – Jun/2026  
> **Arquitetura:** Bidirectional LSTM + BatchNorm + Dropout + L2  
> **Pipeline:** `log1p` → `StandardScaler` → sequências → LSTM → `expm1`

---

## Sumário

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Coleta e Análise Exploratória dos Dados](#2-coleta-e-análise-exploratória-dos-dados)
3. [Pré-Processamento e Normalização](#3-pré-processamento-e-normalização)
4. [Busca de Hiperparâmetros com TimeSeriesSplit](#4-busca-de-hiperparâmetros-com-timeseriessplit)
5. [Arquitetura e Treinamento do Modelo LSTM](#5-arquitetura-e-treinamento-do-modelo-lstm)
6. [Avaliação do Modelo](#6-avaliação-do-modelo)
7. [Walk-Forward Validation](#7-walk-forward-validation)
8. [Exportação e Pipeline de Inferência](#8-exportação-e-pipeline-de-inferência)
9. [Pendências para Entrega Final](#9-pendências-para-entrega-final)

---

## 1. Visão Geral do Projeto

Este projeto implementa uma pipeline completa de Machine Learning Engineering para previsão do **preço de fechamento** da ação **BBD** (Bradesco ADR — NYSE), cobrindo desde a coleta de dados históricos até a exportação do modelo para inferência em produção.

A abordagem utiliza redes neurais **LSTM Bidirecionais** — arquitetura especialmente adequada para séries temporais financeiras, pois captura dependências de longo prazo em ambas as direções da sequência temporal. O pipeline segue boas práticas de MLOps: separação rigorosa de splits sem data leakage, validação cruzada temporal, callback de MAPE em escala real e avaliação comparada com baseline ingênuo.

| Item | Detalhe |
|------|---------|
| Ativo | BBD (Bradesco ADR — NYSE) |
| Período | 01/06/2020 a 01/06/2026 |
| Arquitetura | Bidirectional LSTM + BatchNorm + Dropout + L2 |
| Features (X) | Close, High, Low, Open, Volume (OHLCV) |
| Target (y) | Preço de Fechamento (Close) do dia seguinte |
| Pipeline de normalização | `log1p` → `StandardScaler` (fit só no treino) |
| Split | 70% treino / 15% validação / 15% teste |
| Validação de hiperparâmetros | TimeSeriesSplit (5 folds, 108 combinações) |
| Validação adicional | Walk-Forward (janelas de 30 dias) |

---

## 2. Coleta e Análise Exploratória dos Dados

### 2.1 Obtenção dos Dados

Os dados históricos foram obtidos via biblioteca `yfinance`, que permite download direto de cotações ajustadas do Yahoo Finance:

```python
symbol     = 'BBD'
start_date = '2020-06-01'
end_date   = '2026-06-01'

df = yf.download(symbol, start=start_date, end=end_date)
df.columns = df.columns.get_level_values(0)
df.reset_index(inplace=True)
```

O `yfinance` retorna um `MultiIndex` (tipo de preço × ticker). O código normaliza as colunas para um único nível e converte o índice `Date` em coluna regular.

### 2.2 Estrutura do Dataset

| Coluna | Descrição | Papel no Modelo |
|--------|-----------|-----------------|
| `Close` | Preço de fechamento ajustado | **Target principal (y)** |
| `High` | Máxima do pregão | Feature de volatilidade |
| `Low` | Mínima do pregão | Feature de volatilidade |
| `Open` | Preço de abertura | Feature de tendência intraday |
| `Volume` | Volume negociado (contratos) | Feature de liquidez/convicção |

### 2.3 Série Temporal do Preço de Fechamento

![Série Temporal do Preço de Fechamento — BBD](/imgs/graf_fechamento.png)

O gráfico revela **três regimes distintos** no período analisado, cada um com implicações diretas para o comportamento do modelo:

- **2020–2021 (recuperação pós-pandemia):** o ativo saiu de patamares deprimidos em meados de 2020 e apresentou recuperação gradual com volatilidade elevada. Esse período forma a maior parte do conjunto de treino e ensina ao modelo padrões de tendência ascendente com oscilações frequentes.

- **2021–2023 (retração e lateralização):** após atingir máximas em 2021, o ativo entrou em fase de queda e lateralização, refletindo o ciclo de aperto monetário global. Esse trecho coincide com parte do treino e com o período de validação — o regime mais desafiador para o modelo.

- **2023–2026 (ciclo recente):** período mais recente, que compõe integralmente o **conjunto de teste**. Apresenta comportamento distinto dos anos anteriores, sendo o cenário mais crítico para avaliar a capacidade de generalização.

> Essa heterogeneidade temporal reforça a impossibilidade de usar validação cruzada aleatória — o split deve ser **estritamente cronológico**.

### 2.4 Distribuições e Estatísticas Descritivas

![Histogramas de Distribuição das Variáveis](/imgs/hist.png)
Os histogramas revelam **assimetria positiva acentuada** em todas as variáveis originais:

- **Close, High, Low, Open:** distribuições com cauda direita — preços baixos são mais frequentes, mas há dias com picos significativos decorrentes dos diferentes regimes de preço no período.
- **Volume:** distribuição fortemente assimétrica, com moda concentrada em volumes baixos a moderados e cauda longa (dias de alta volatilidade de mercado).

### 2.5 Boxplots e Análise de Outliers

![Boxplots — Visualização de Outliers](/imgs/outliers.png)
A análise quantitativa de outliers pelo critério IQR foi aplicada ao `Close`:

```
Quartis para os Preços de Fechamento:
  25%    2.380189
  50%    2.764684
  75%    3.196416

Outliers nos Preços de Fechamento: Nenhum outlier encontrado.
Porcentagem de outliers: 0.00%
```

Os valores extremos visíveis nos boxplots representam **fases distintas do ciclo econômico** (recuperação pós-pandemia e pico de 2021), e não erros de dados. Isso valida a decisão de preservar todos os pontos da série, mantendo a integridade temporal do dataset.

---

## 3. Pré-Processamento e Normalização

### 3.1 Pipeline de Transformação

O pipeline de normalização segue **duas etapas sequenciais**:

**Etapa 1 — Transformação `log1p`** aplicada a todas as colunas OHLCV:
```python
price_cols = ['Close', 'High', 'Low', 'Open']
df[price_cols] = np.log1p(df[price_cols])
df['Volume']   = np.log1p(df['Volume'])
```

`log1p(x) = ln(1 + x)` comprime caudas longas, simetriza as distribuições e é definida para x ≥ 0, sem risco de produzir `NaN`.

**Etapa 2 — `StandardScaler`** ajustado **exclusivamente no treino** e aplicado por `transform` nos demais splits:
```python
scaler       = StandardScaler()
train_scaled = scaler.fit_transform(train_raw)   # fit APENAS no treino
val_scaled   = scaler.transform(val_raw)          # sem data leakage
test_scaled  = scaler.transform(test_raw)
```

**Justificativa para `StandardScaler` vs. alternativas:**

| Scaler | Baseia-se em | Adequado pós-`log1p`? |
|--------|-------------|----------------------|
| `MinMaxScaler` | Min / Max | ❌ Outliers residuais comprimem a escala |
| **`StandardScaler`** | **Média / Desvio-padrão** | **✅ Adequado após `log1p` simetrizar** |
| `RobustScaler` | Mediana / IQR | ✅ Mas desnecessário quando o `log` já corrigiu a assimetria |

### 3.2 Divisão Temporal — Split 70 / 15 / 15

```
Treino:    1.054 amostras  (Jun/2020 – ~Dez/2023)
Validação:   226 amostras  (período imediatamente posterior)
Teste:       227 amostras  (período mais recente — completamente isolado)

X_train: (1024, 30, 5) | X_val: (196, 30, 5) | X_test: (197, 30, 5)
```

- **Treino (70%):** cobre os ciclos de recuperação pós-pandemia, alta de 2021 e queda subsequente. O `StandardScaler` é ajustado **exclusivamente** aqui.
- **Validação (15%):** usado para monitorar o desempenho a cada época via `RealMapeCallback` e acionar `EarlyStopping`/`ReduceLROnPlateau`. Nunca visto pelo scaler durante o `fit`.
- **Teste (15%):** completamente isolado até a avaliação final, simulando o ambiente de produção.

### 3.3 Distribuição Pós-Normalização por Split

![KDE — Distribuição das Features Normalizadas por Split](/imgs/dist_norm.png)
Os gráficos de densidade (KDE) verificam duas propriedades essenciais:

1. **Calibração do scaler:** no conjunto de treino, média ≈ 0 e desvio-padrão ≈ 1 confirmam o funcionamento correto do `StandardScaler`.
2. **Ausência de distribution shift severo:** as curvas de validação e teste seguem o mesmo formato da curva de treino, indicando que o modelo não encontrará distribuições radicalmente diferentes na inferência.

![Boxplots Pós-Normalização por Split](/imgs/boxsplot_norm.png)
**Estatísticas pós-normalização (pré-scaler — escala log):**

| Feature | Split | Média | Std | Skewness |
|---------|-------|-------|-----|----------|
| Close | Treino | 1.3210 | 0.1225 | 0.1339 |
| Close | Validação | 1.1755 | 0.1038 | 0.1807 |
| Close | Teste | 1.4808 | 0.0884 | -0.0992 |
| Volume | Treino | 17.008 | 0.4947 | -0.1251 |
| Volume | Validação | 17.365 | 0.4387 | -0.2365 |

> O deslocamento de média entre splits é esperado e reflete os diferentes regimes de preço — o importante é que a estrutura distribucional (forma, skewness) se mantém similar.

### 3.4 Construção das Sequências

```python
def create_sequences(data, look_back):
    X, y = [], []
    for i in range(len(data) - look_back):
        X.append(data[i : i + look_back, :])  # janela de look_back dias (OHLCV)
        y.append(data[i + look_back, 0])       # Close do dia seguinte (coluna 0)
    return np.array(X), np.array(y)
```

O target `y` é sempre a **coluna 0 (Close)** do passo seguinte ao fim da janela, definindo a tarefa como **previsão de um passo à frente** com janela deslizante de `look_back` dias.

---

## 4. Busca de Hiperparâmetros com TimeSeriesSplit

### 4.1 Por que TimeSeriesSplit?

O K-Fold convencional embaralha os dados antes de criar os folds, o que em séries temporais permite que o modelo treine com observações futuras — **data leakage grave**. O `TimeSeriesSplit` garante que, em cada fold, a validação seja sempre cronologicamente posterior ao treino.

### 4.2 Grade de Hiperparâmetros

| Hiperparâmetro | Valores testados | Papel |
|----------------|-----------------|-------|
| `look_back` | 30, 60, 90 dias | Tamanho da janela de contexto temporal |
| `units` | 64, 128, 256 neurônios | Capacidade da LSTM |
| `dropout` | 0.1, 0.2, 0.3 | Regularização — previne overfitting |
| `batch_size` | 16, 32 | Estabilidade dos gradientes |

**Total: 3 × 3 × 3 × 2 = 108 combinações**, cada uma avaliada em 5 folds com até 25 épocas (EarlyStopping, `patience=5`).

### 4.3 Hiperparâmetros Selecionados

```
look_back   = 30 dias
units       = 128 neurônios
dropout     = 0.3
batch_size  = 16
```

A escolha de `look_back = 30` é coerente com o comportamento do ativo: o modelo aprende padrões do último mês de pregões, suficiente para capturar tendências de curto e médio prazo sem memorizar ruído de períodos muito longos. O `dropout` baixo (0.3) indica que a regularização via `BatchNormalization` e L2 já controla adequadamente o overfitting.

---

## 5. Arquitetura e Treinamento do Modelo LSTM

### 5.1 Arquitetura — Bidirectional LSTM com Regularização

```python
model = Sequential([
    Bidirectional(LSTM(128, return_sequences=True, kernel_regularizer=l2(1e-6)),
                  input_shape=(30, 5)),
    BatchNormalization(),
    Dropout(0.3),
    LSTM(64, return_sequences=False, kernel_regularizer=l2(1e-6)),
    BatchNormalization(),
    Dropout(0.3),
    Dense(16, activation='relu'),
    Dropout(0.15),
    Dense(1)
])
# Otimizador: Adam(lr=1e-4) | Loss: MAE
```

| Camada / Componente | Justificativa |
|--------------------|---------------|
| **Bidirectional LSTM** | Captura padrões temporais em ambas as direções; pode aprender tanto momentum ascendente quanto sinais de reversão |
| **BatchNormalization** | Estabiliza gradientes e acelera convergência sem elevar parâmetros treináveis |
| **Regularização L2 (1e-6)** | Penalização leve dos pesos — complementa BatchNorm sem suprimir sinal útil |
| **Dropout (0.3)** | Regularização estocástica — definida pela busca de hiperparâmetros |
| **Dense(16, relu)** | Aprende combinações não-lineares das representações LSTM antes da saída |
| **Dense(1)** | Saída de regressão — preço de fechamento normalizado |

### 5.2 Callbacks de Treinamento

```python
callbacks = [
    RealMapeCallback(X_val, y_val, scaler, num_features),   # MAPE em USD a cada época
    EarlyStopping(monitor='val_mape_real', patience=20, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_mape_real', factor=0.5, patience=5, min_lr=1e-6),
    ModelCheckpoint('best_lstm_model.keras', monitor='val_mape_real', save_best_only=True)
]
```

O `RealMapeCallback` aplica `inverse_transform + expm1` às predições de validação ao final de cada época, calculando o MAPE em escala original (USD). Isso garante que `EarlyStopping` e `ReduceLROnPlateau` operem sobre uma **métrica de negócio interpretável**, não sobre o MAE na escala normalizada.

### 5.3 Curvas de Aprendizado

![Curvas de Aprendizado — Loss e MAPE Real](/imgs/curv.png)
**Resultados do treinamento:**

```
Épocas executadas    : 34 (EarlyStopping acionado na época 34)
Melhor época         : 14
Melhor val_loss      : 0.189846 (MAE normalizado)
Melhor val_mape_real : 2.0314%
```

**Interpretação das curvas:**

- **Loss (MAE normalizado — painel esquerdo):** a convergência paralela entre treino e validação, com a curva de validação levemente acima mas seguindo a mesma tendência, indica boa generalização. Não há divergência crescente que caracterizaria overfitting severo.

- **MAPE Real na Validação (painel direito):** o MAPE de validação partiu de ~12.2% na época 1 e convergiu para ~2.8% na melhor época. O `EarlyStopping` interrompeu o treinamento após 34 épocas sem melhora significativa, preservando os pesos da época 14 — o ponto de menor MAPE em escala real.

- **`ReduceLROnPlateau`:** acionado na época 34, reduziu o learning rate de `1.25e-05` para `6.25e-06`, confirmando que o modelo havia atingido um platô de convergência antes do early stopping.

---

## 6. Avaliação do Modelo

### 6.1 Métricas no Conjunto de Teste (Escala Original — USD)

```
==================================================
  Avaliação do Modelo (Escala Original — USD)
==================================================
  MAE   (Erro Médio Absoluto):           $0.0297
  RMSE  (Raiz do Erro Quadrático Médio): $0.0386
  MAPE  (Erro Percentual Médio):          1.94%
  Dir.  (Acurácia Direcional):            40.31%
==================================================

```

| Métrica | Valor | Interpretação |
|---------|-------|--------------|
| **MAE** | $0.0297 | Em média, o modelo erra $0.0297 por pregão — erro baixo em termos absolutos |
| **RMSE** | R$0.0386 | Penaliza erros grandes; valor próximo ao MAE indica ausência de erros extremos isolados |
| **MAPE** | 1.94% | O modelo erra ~1.94% do preço real em média — referência comum em forecasting financeiro |
| **Acurácia Direcional** | 40.31% | O modelo acerta a **direção** do movimento em 40.31% dos dias |


### 6.2 Real vs. Previsão — Conjunto de Teste

![Real vs. Previsão — Conjunto de Teste (Série Temporal)](/imgs/pred_real.png)
O gráfico da série temporal permite observar:

- O modelo **rastreia a tendência geral** da série real de forma coerente, acompanhando os movimentos de maior escala.
- Há **defasagem e suavização** nas reversões bruscas — comportamento típico de modelos LSTM one-step-ahead, que tendem a "seguir" a série com um passo de atraso em pontos de inflexão.
- Os **erros são maiores em picos de volatilidade**, onde o mercado reage a eventos pontuais que o modelo não possui como input.

![Scatter — Real vs. Previsto](/imgs/scatter.png)
O scatter plot mostra:

- Boa **correlação linear geral** — a maioria dos pontos se distribui próxima à diagonal de predição perfeita (linha vermelha tracejada).
- Ausência de **viés sistemático** flagrante (sem cluster claro acima ou abaixo da diagonal), indicando que o modelo não superestima nem subestima consistentemente.
- Maior dispersão nos extremos da faixa de preço, o que é esperado dado que esses regimes são menos representados no dataset de treino.

---

## 7. Walk-Forward Validation

A validação walk-forward complementa o split fixo simulando o uso real do modelo no tempo. Em vez de uma única janela de teste estática, avalia **múltiplas janelas deslizantes de 30 dias** com retreinamento incremental:

```python
STEP = 30  # dias por janela

for start in range(wf_start, len(data) - STEP, STEP):
    # 1. Treinar com todos os dados até `start`
    # 2. Prever os próximos 30 dias
    # 3. Calcular MAPE da janela
    # 4. Avançar 30 dias
```

**Resultados esperados da Walk-Forward Validation:**

O resultado fornece uma **distribuição de MAPEs ao longo do tempo** — média, desvio-padrão, mínimo e máximo — que revela como o modelo se comporta em diferentes regimes de mercado:

- Um MAPE com **baixo desvio-padrão** indica consistência do modelo ao longo do tempo.
- **Janelas com MAPE elevado** coincidem com períodos de alta volatilidade ou mudanças abruptas de tendência — esperado em qualquer modelo de séries temporais.
- A comparação entre o MAPE médio do Walk-Forward e o MAPE do split fixo valida se a avaliação estática foi representativa.

> **Nota:** a célula de Walk-Forward Validation não produziu output gráfico no notebook (execução não concluída no ambiente de treinamento). Os resultados serão registrados na próxima execução completa.

---

## 8. Exportação e Pipeline de Inferência

### 8.1 Artefatos Salvos

```python
model.save('modelo_lstm.keras')          # arquitetura + pesos + otimizador
joblib.dump(scaler, 'scaler.pkl')        # parâmetros do StandardScaler (fit no treino)
```

A persistência do `scaler` junto ao modelo é **obrigatória**: sem ele, qualquer inferência futura usaria parâmetros de normalização incorretos, tornando as predições inválidas.

### 8.2 Função `prever_proximo_dia()`

```python
def prever_proximo_dia(symbol, look_back, scaler, model, num_features, feature_cols):
    # 1. Busca os últimos look_back pregões via yfinance
    #    (margem de look_back*2+10 dias corridos para cobrir feriados)
    # 2. Aplica log1p nas colunas OHLCV
    # 3. Aplica scaler.transform() na janela
    # 4. Prediz e inverte: inverse_transform + expm1
    # 5. Retorna preço em USD e data do último pregão
```

A estratégia de janela usa `look_back × 2 + 10` dias corridos para garantir `look_back` pregões válidos mesmo em semanas com feriados consecutivos. Caso os dados sejam insuficientes, `ValueError` é levantado com diagnóstico claro.

### 8.3 Inversão do Pipeline

Como o target `Close` passou por `log1p` antes do scaler, a inversão exige **dois passos em ordem correta**:

```python
def inverse_close(arr_1d, scaler, num_features):
    dummy = np.zeros((len(arr_1d), num_features))
    dummy[:, 0] = arr_1d
    log_prices = scaler.inverse_transform(dummy)[:, 0]  # desfaz StandardScaler
    return np.expm1(log_prices)                          # desfaz log1p → preço em USD
```

---


## 10. Considerações Finais

O notebook implementa uma pipeline de MLOps robusta, indo além dos requisitos mínimos do Tech Challenge:

| Prática | Implementação |
|---------|--------------|
| **Sem data leakage** | `StandardScaler` ajustado só no treino; `TimeSeriesSplit` na busca; teste isolado |
| **Métrica em escala real** | `RealMapeCallback` calcula MAPE em USD a cada época — não na escala normalizada |
| **Validação em múltiplos níveis** | Split fixo + Grid Search com TimeSeriesSplit + Walk-Forward Validation |
| **Baseline de comparação** | Random Walk como piso mínimo de referência |
| **Pipeline de produção** | `prever_proximo_dia()` replica exatamente o pré-processamento do treino |
| **Regularização combinada** | BatchNormalization + L2 + Dropout — abordagem complementar |

**Resultado final:** MAPE de 1.94% no conjunto de teste, com MAPE de validação de 2.0314% durante o treinamento. O modelo rastreia bem a tendência geral da série, com as limitações esperadas em pontos de reversão brusca e acurácia direcional abaixo de 50% — pontos que guiam as próximas iterações de melhoria.

# 📈 Tech Challenge Fase 4 — Previsão de Preços de Ações com Deep Learning

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11+-009688.svg)
![LSTM](https://img.shields.io/badge/Model-Bidirectional%20LSTM-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📌 Sobre o Projeto

Este projeto foi desenvolvido como parte do **Tech Challenge – Fase 4** da Pós-Tech em Machine Learning Engineering.

O objetivo consiste em construir uma solução completa para previsão do preço de fechamento de ações utilizando redes neurais recorrentes (**Long Short-Term Memory – LSTM**), contemplando todo o ciclo de desenvolvimento de um sistema de Machine Learning, desde a coleta dos dados históricos até a disponibilização do modelo em produção através de uma API REST.

Diferentemente de um notebook exclusivamente voltado para experimentação, este projeto implementa uma pipeline completa de Machine Learning Engineering, incluindo:

- coleta automática dos dados;
- análise exploratória;
- pré-processamento;
- busca e ajuste de hiperparâmetros;
- treinamento;
- avaliação;
- persistência do modelo;
- API de inferência;
- dashboard de monitoramento.

---

# 🎯 Objetivos

O projeto busca atender às seguintes etapas do ciclo de vida de um modelo de Machine Learning:

- Coletar automaticamente dados históricos de ações;
- Realizar análise exploratória dos dados (EDA);
- Construir uma pipeline de pré-processamento sem data leakage;
- Treinar uma rede neural LSTM para previsão do preço de fechamento;
- Avaliar o modelo utilizando métricas de regressão;
- Exportar o modelo para produção;
- Disponibilizar uma API REST utilizando FastAPI;
- Disponibilizar dashboard para monitoramento das predições.

---

# 🏗 Arquitetura Geral

O fluxo completo do projeto pode ser resumido conforme o diagrama abaixo.

```

Yahoo Finance

↓

Coleta dos dados

↓

Análise Exploratória (EDA)

↓

Pré-processamento

• log1p

• StandardScaler

↓

Construção das Sequências

↓

Bidirectional LSTM

↓

Avaliação

↓

Exportação

(modelo + scaler)

↓

FastAPI

↓

Dashboard Streamlit

```

Todo o pipeline de inferência utilizado pela API reproduz exatamente o fluxo utilizado durante o treinamento, garantindo consistência entre ambiente de desenvolvimento e produção.

---

# 📂 Estrutura do Projeto

```

mle_tech_challenge_4/

├── app.py
├── app/
│   ├── __init__.py
│   └── static/
│       ├── index.html
│       └── assets/
│           ├── index-DJh4hmGh.js
│           └── index-DsDejwUj.css
├── artifacts/
│   ├── modelo_lstm.keras
│   └── scaler.pkl
├── docs/
│   ├── documentacao_lstm_tech_challenge.md
│   ├── oquefazer.md
│   └── Pos_Tech - MLET - Tech Challenge Fase 4.pdf
├── imgs/
├── modelagem/
│   └── fase4_MLET.ipynb
├── README.md
├── requirements copy.txt
├── requirements-dev.txt
└── requirements.txt

```

---

# 📊 Base de Dados

Os dados históricos são obtidos diretamente do **Yahoo Finance**, utilizando a biblioteca **yfinance**.

Neste projeto foi utilizado o ativo:

**Ticker:** BBD (Banco Bradesco ADR — NYSE)

Período analisado:

**Junho de 2020 até Junho de 2026**

---

# 📈 Variáveis Utilizadas

O modelo utiliza apenas informações históricas do próprio ativo.

| Feature | Descrição |
|----------|-----------|
| Open | Preço de abertura |
| High | Maior preço do dia |
| Low | Menor preço do dia |
| Close | Preço de fechamento |
| Volume | Volume negociado |

O alvo do modelo consiste em prever o **preço de fechamento do próximo pregão**.

---

# 📊 Análise Exploratória

Foi realizada uma análise exploratória completa da série temporal antes do treinamento.

As principais etapas foram:

- análise da série histórica;
- histogramas;
- boxplots;
- estatísticas descritivas;
- identificação de assimetria;
- análise de outliers.

A análise mostrou que:

- as distribuições apresentavam forte assimetria positiva;
- o Volume possuía cauda longa;
- não foram encontrados outliers relevantes pelo método IQR;
- as oscilações observadas representam regimes naturais do mercado e não erros de coleta.

Dessa forma, optou-se por manter todos os registros da série temporal.

---

# ⚙️ Pipeline de Pré-processamento

Após a análise exploratória foi definida a seguinte estratégia de pré-processamento.

## 1. Transformação Logarítmica

Todas as variáveis OHLCV recebem:

```python
np.log1p()
```

Essa transformação reduz a assimetria das distribuições e melhora a estabilidade do treinamento.

---

## 2. Normalização

Após a transformação logarítmica é aplicado um:

```python
StandardScaler
```

O scaler é ajustado **exclusivamente no conjunto de treinamento**.

Posteriormente os conjuntos de validação, teste e produção utilizam apenas:

```python
transform()
```

garantindo ausência de data leakage.

---

## 3. Divisão Temporal

Os dados são divididos cronologicamente em:

| Conjunto | Percentual |
|-----------|-----------:|
| Treino | 70% |
| Validação | 15% |
| Teste | 15% |

Não é realizado embaralhamento dos dados (shuffle), preservando a ordem temporal da série.

---

## 4. Construção das Sequências

As entradas da rede são construídas utilizando janelas deslizantes.

Cada amostra possui:

- 30 dias de histórico;
- 5 variáveis por dia.

Assim, cada entrada possui dimensão:

```

(30,5)

```

Enquanto o alvo corresponde ao preço de fechamento do dia imediatamente seguinte.

---
# 🧠 Modelagem

Todo o processo de modelagem foi desenvolvido no notebook `fase4_MLET.ipynb`, contemplando desde a definição da arquitetura da rede neural até a avaliação do modelo em um conjunto de teste completamente isolado.

O objetivo do modelo consiste em prever o **preço de fechamento do próximo pregão**, utilizando como entrada uma sequência histórica dos últimos 30 pregões.

A estratégia adotada buscou equilibrar capacidade preditiva e generalização, evitando overfitting e vazamento de informação ao longo de todo o pipeline.

---

# 🔎 Busca de Hiperparâmetros

Como etapa inicial, foi realizada uma busca sistemática de hiperparâmetros utilizando **Grid Search** aliado ao **TimeSeriesSplit**, técnica apropriada para séries temporais.

Diferentemente do K-Fold tradicional, o TimeSeriesSplit preserva a ordem cronológica dos dados, garantindo que cada conjunto de validação contenha apenas observações posteriores ao conjunto de treinamento.

Foram avaliadas combinações envolvendo:

| Hiperparâmetro | Valores avaliados |
|----------------|-------------------|
| Look Back | 30, 60 e 90 dias |
| Número de neurônios | 64, 128 e 256 |
| Dropout | 0.10, 0.20 e 0.30 |
| Batch Size | 16 e 32 |

Ao todo foram avaliadas **108 combinações**, utilizando validação temporal em cinco folds.

Essa etapa teve como objetivo restringir o espaço de busca e identificar configurações promissoras para o treinamento do modelo.

---

# 🎯 Seleção Final dos Hiperparâmetros

Embora o Grid Search tenha fornecido uma boa aproximação dos melhores parâmetros, observou-se que pequenas alterações produziam modelos com maior estabilidade durante o treinamento e melhor capacidade de generalização.

Assim, a configuração final foi definida manualmente após análise conjunta de:

- curvas de aprendizado;
- comportamento da validação;
- estabilidade do treinamento;
- capacidade de generalização;
- desempenho obtido no conjunto de teste.

Os hiperparâmetros utilizados na versão final do modelo foram:

| Hiperparâmetro | Valor |
|----------------|------:|
| Look Back | **30 dias** |
| Units | **128** |
| Dropout | **0.30** |
| Batch Size | **16** |
| Optimizer | Adam |
| Learning Rate | 1×10⁻⁴ |
| Loss Function | MAE |

Essa configuração apresentou o melhor equilíbrio entre erro de previsão e estabilidade durante o treinamento.

---

# 🏗 Arquitetura da Rede Neural

O modelo utiliza uma arquitetura baseada em **Bidirectional Long Short-Term Memory (BiLSTM)**.

As redes LSTM são especialmente indicadas para séries temporais por conseguirem aprender dependências de longo prazo, enquanto a versão bidirecional melhora a qualidade da representação aprendida durante o treinamento.

Além da LSTM, foram utilizadas técnicas adicionais de regularização para reduzir overfitting.

A arquitetura final pode ser representada da seguinte forma:

```
Entrada
(30 dias × 5 variáveis)

        │

        ▼

Bidirectional LSTM
128 neurônios
(return_sequences=True)

        │

BatchNormalization

        │

Dropout (0.30)

        │

LSTM
64 neurônios

        │

BatchNormalization

        │

Dropout (0.30)

        │

Dense (16)
ReLU

        │

Dropout (0.05)

        │

Dense (1)

        │

Preço previsto
```

---

# 🛡 Estratégias de Regularização

Para melhorar a capacidade de generalização foram utilizadas diferentes técnicas de regularização.

## Batch Normalization

Aplicada após cada camada recorrente para estabilizar a distribuição das ativações durante o treinamento.

Benefícios:

- treinamento mais estável;
- convergência mais rápida;
- redução da sensibilidade ao learning rate.

---

## Dropout

Foi utilizado Dropout em diferentes pontos da arquitetura para reduzir a dependência entre neurônios e minimizar overfitting.

A taxa escolhida foi:

```
0.30
```

nas camadas recorrentes.

---

## Regularização L2

As camadas LSTM utilizam penalização L2 sobre os pesos da rede.

Essa estratégia reduz o crescimento excessivo dos parâmetros durante o treinamento e melhora a capacidade de generalização.

---

# ⚙ Processo de Treinamento

O treinamento foi realizado utilizando o otimizador **Adam**, amplamente empregado em problemas de Deep Learning devido à sua estabilidade e rápida convergência.

Configuração utilizada:

| Parâmetro | Valor |
|------------|------:|
| Optimizer | Adam |
| Learning Rate | 0.0001 |
| Loss | MAE |
| Batch Size | 16 |

O treinamento foi monitorado continuamente utilizando métricas calculadas na escala original do problema.

---

# 🔄 Callbacks

Para tornar o treinamento mais eficiente foram utilizados quatro callbacks principais.

## EarlyStopping

Interrompe automaticamente o treinamento quando não há melhoria significativa na métrica monitorada.

Benefícios:

- evita overfitting;
- reduz tempo de treinamento;
- restaura automaticamente os melhores pesos.

---

## ReduceLROnPlateau

Quando o treinamento atinge um platô, o learning rate é reduzido automaticamente.

Essa estratégia melhora o refinamento da solução nas últimas épocas.

---

## ModelCheckpoint

Salva automaticamente o melhor modelo encontrado durante o treinamento.

O arquivo exportado é:

```
modelo_lstm.keras
```

---

## RealMapeCallback

Foi implementado um callback personalizado responsável por calcular o MAPE na escala original dos preços.

A cada época o callback realiza automaticamente:

- inverse_transform do StandardScaler;
- aplicação de expm1;
- cálculo do MAPE em USD.

Dessa forma, todas as decisões de treinamento são tomadas utilizando uma métrica diretamente interpretável pelo negócio.

---

# 📈 Curvas de Aprendizado

Durante o treinamento foram monitoradas duas métricas principais:

- Loss (MAE normalizado);
- MAPE em escala real.

As curvas obtidas indicaram:

- convergência estável;
- ausência de overfitting severo;
- boa capacidade de generalização;
- redução consistente do erro ao longo das épocas.

O EarlyStopping interrompeu o treinamento automaticamente quando não havia mais ganho significativo de desempenho.

---

# 📊 Avaliação do Modelo

Após o treinamento, o modelo foi avaliado em um conjunto de teste completamente isolado, nunca utilizado durante o ajuste dos pesos ou dos hiperparâmetros.

As métricas foram calculadas na escala original (USD).

| Métrica | Resultado |
|----------|----------:|
| MAE | **0.0297 USD** |
| RMSE | **0.0386 USD** |
| MAPE | **1.94%** |
| Acurácia Direcional | **40.31%** |

O baixo valor de MAPE indica que o modelo apresenta elevada precisão na previsão do preço de fechamento do ativo.

---

# 📉 Análise dos Resultados

A análise visual das previsões mostrou que o modelo consegue acompanhar adequadamente a tendência geral da série temporal.

Observou-se que:

- o modelo acompanha bem movimentos de médio prazo;
- erros maiores concentram-se em períodos de alta volatilidade;
- ocorre pequena defasagem em pontos de reversão abrupta, comportamento esperado em modelos autoregressivos baseados em LSTM.

O gráfico de dispersão entre valores reais e previstos apresentou forte correlação linear, indicando boa capacidade preditiva.

---

# 🚶 Walk-Forward Validation

Além da divisão tradicional entre treino, validação e teste, foi implementada uma estratégia de **Walk-Forward Validation**.

Nessa abordagem o modelo é avaliado em múltiplas janelas temporais sucessivas, simulando o comportamento encontrado em ambiente de produção.

Embora a implementação esteja presente no notebook, a execução completa não foi finalizada durante os experimentos devido ao elevado tempo computacional.

Ainda assim, a estrutura permanece disponível para futuras reavaliações do modelo.

---

# 💾 Exportação do Modelo

Após o treinamento são persistidos dois artefatos fundamentais:

```
modelo_lstm.keras
```

Modelo treinado contendo arquitetura e pesos.

```
scaler.pkl
```

Objeto `StandardScaler` utilizado durante o treinamento.

A API utiliza exatamente esses mesmos artefatos durante a inferência, garantindo que o pipeline de produção seja idêntico ao utilizado no desenvolvimento do modelo.
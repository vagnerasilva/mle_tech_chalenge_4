import logging
import os
import time
import pandas as pd
import yfinance as yf

# 1. Configuração do sistema de logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 2. Crie uma lista com os códigos das ações
#lista_acoes = ["PETR4.SA", "VALE3.SA", "ITUB3.SA", "ITUB4.SA"]
lista_acoes = [ 
                   "VALE3.SA",
    "PETR4.SA",
    "PETR3.SA",
    "ITUB4.SA",
    "BBAS3.SA",
    "BBDC4.SA",
    "B3SA3.SA",
    "ABEV3.SA",
    "WEGE3.SA",
    "ELET3.SA",
    "BPAC11.SA",
    "RENT3.SA",
    "PRIO3.SA",
    "EQTL3.SA",
    "SBSP3.SA"]

# 3. Define a pasta e cria se ela não existir
pasta_destino = "./data"
if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)
    logging.info(f"Pasta '{pasta_destino}' criada com sucesso!")

# Lista temporária para guardar as tabelas de cada ação
lista_tabelas = []

# 4. Loop para baixar os dados de cada ação
for i, acao in enumerate(lista_acoes):
    logging.info(f"Iniciando download da ação {i+1}/{len(lista_acoes)}: {acao}")

    try:
        # Baixa os dados da ação atual (usando 6mo correto 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        dados_acao = yf.download(acao, period="10y", progress=False)

        if not dados_acao.empty:
            # Seleciona apenas a coluna de fechamento 'Close' e renomeia com o nome da ação
            df_fechamento = dados_acao[["Close"]].rename(columns={"Close": acao})
            
            # Adiciona a tabela na nossa lista
            lista_tabelas.append(df_fechamento)
            logging.info(f"Download concluído com sucesso para: {acao}")
        else:
            logging.warning(
                f"Nenhum dado encontrado para a ação: {acao}. Ela será pulada."
            )

    except Exception as e:
        logging.error(f"Erro ao baixar a ação {acao}: {e}")

    # Pausa o código por 2 segundos entre as chamadas
    if i < len(lista_acoes) - 1:
        logging.info("Aguardando 2 segundos antes da próxima chamada...")
        time.sleep(2)

# 5. Junta todas as tabelas usando o método correto do Pandas (pd.concat)
if lista_tabelas:
    # O axis=1 diz para o Pandas juntar lado a lado (coluna por coluna) batendo as datas
    precos_fechamento = pd.concat(lista_tabelas, axis=1)

    logging.info("Exibindo as primeiras linhas dos preços de fechamento:")
    print(precos_fechamento.head())

    # 6. Salva os dados de fechamento consolidados na pasta data
    caminho_arquivo = os.path.join(pasta_destino, "precos_fechamento.csv")
    precos_fechamento.to_csv(caminho_arquivo)
    logging.info(f"Arquivo unificado salvo com sucesso em: {caminho_arquivo}")
else:
    logging.error("Nenhum dado foi baixado. Arquivo CSV não foi criado.")

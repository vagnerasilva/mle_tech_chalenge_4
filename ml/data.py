import datetime

import pandas as pd
import yfinance as yf


class InsufficientDataError(ValueError):
    """Levantado quando o yfinance não retorna pregões suficientes para a janela pedida."""


def fetch_ohlcv(symbol: str, look_back: int, feature_cols: list[str]) -> pd.DataFrame:
    """Busca os últimos `look_back` pregões válidos de `symbol`.

    Pregões ocorrem ~252 dias/ano (~1.45 dias corridos por pregão). Pedimos
    `look_back * 2 + 10` dias corridos de margem para cobrir feriados e finais
    de semana consecutivos, depois recortamos exatamente os últimos `look_back`
    registros válidos.
    """
    end_date = datetime.date.today()
    calendar_days = look_back * 2 + 10
    start_date = end_date - datetime.timedelta(days=calendar_days)

    raw = yf.download(symbol, start=start_date, end=end_date, progress=False)
    if raw.empty:
        raise InsufficientDataError(
            f"yfinance não retornou dados para {symbol!r} entre {start_date} e {end_date}."
        )

    raw.columns = raw.columns.get_level_values(0)
    raw.reset_index(inplace=True)
    raw.dropna(inplace=True)
    raw.reset_index(drop=True, inplace=True)

    if len(raw) < look_back:
        raise InsufficientDataError(
            f"Pregões insuficientes para {symbol!r} após limpeza: obtidos {len(raw)}, "
            f"necessário {look_back}. Verifique o símbolo ou tente novamente mais tarde."
        )

    return raw[["Date", *feature_cols]].iloc[-look_back:].reset_index(drop=True)

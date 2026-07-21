import datetime

from pydantic import BaseModel, ConfigDict, Field


class PredictResponse(BaseModel):
    symbol: str
    predicted_close: float
    last_trading_date: datetime.date
    look_back: int

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "symbol": "BBD",
                    "predicted_close": 3.4482,
                    "last_trading_date": "2026-07-10",
                    "look_back": 30,
                }
            ]
        }
    )

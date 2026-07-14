#!/usr/bin/env python
"""
Script para testar os endpoints de validação/monitoramento da API.

Uso:
    python test_api_monitoring.py
"""

import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import FastAPI
from app.models.base import Base
from app.dependencies import get_db
from app.main import app


def setup_test_db():
    """Cria um banco de testes em memória."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestingSessionLocal()


def test_endpoints():
    """Testa todos os endpoints de validação."""
    client = TestClient(app)
    db = setup_test_db()
    
    print("=" * 60)
    print("TESTANDO ENDPOINTS DE MONITORAMENTO")
    print("=" * 60)
    
    # Teste 1: Salvar uma predição
    print("\n[1] POST /api/v1/predict/next_close")
    response = client.post("/api/v1/predict/next_close")
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Symbol: {data['symbol']}")
        print(f"    Predicted: {data['predicted_close']:.4f}")
        print(f"    Date: {data['last_trading_date']}")
        symbol = data['symbol']
        pred_date = data['last_trading_date']
    else:
        print(f"    ERROR: {response.text}")
        return
    
    # Teste 2: Validar a predição
    print(f"\n[2] GET /api/v1/validation/validate?symbol={symbol}&prediction_date={pred_date}")
    response = client.get(f"/api/v1/validation/validate?symbol={symbol}&prediction_date={pred_date}")
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Status: {data['status']}")
        print(f"    Predicted: {data['predicted_close']:.4f}")
        print(f"    Actual: {data['actual_close']}")
        if data['mape'] is not None:
            print(f"    MAPE: {data['mape']:.2f}%")
    else:
        print(f"    INFO: {response.json()['detail']}")
    
    # Teste 3: Histórico
    print(f"\n[3] GET /api/v1/validation/history?symbol={symbol}&limit=10")
    response = client.get(f"/api/v1/validation/history?symbol={symbol}&limit=10")
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Registros encontrados: {len(data)}")
    else:
        print(f"    INFO: {response.json()['detail']}")
    
    # Teste 4: Resumo de validações
    print(f"\n[4] GET /api/v1/validation/summary?symbol={symbol}")
    response = client.get(f"/api/v1/validation/summary?symbol={symbol}")
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Total predições: {data['total_predictions']}")
        print(f"    Validadas: {data['validated']}")
        print(f"    Pendentes: {data['pending']}")
        if data['avg_mae'] is not None:
            print(f"    MAE médio: {data['avg_mae']:.4f}")
    else:
        print(f"    INFO: {response.json()['detail']}")
    
    # Teste 5: Estatísticas gerais
    print(f"\n[5] GET /api/v1/validation/stats?symbol={symbol}")
    response = client.get(f"/api/v1/validation/stats?symbol={symbol}")
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Total predições: {data['total_predictions']}")
        print(f"    MAPE médio: {data['avg_mape']:.2f}%")
        print(f"    Directional Accuracy: {data['avg_directional_accuracy']:.1%}")
    else:
        print(f"    INFO: {response.json()['detail']}")
    
    print("\n" + "=" * 60)
    print("[OK] Testes concluidos!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        # Importa aqui para não quebrar se FastAPI não estiver instalado
        from fastapi.testclient import TestClient
        
        test_endpoints()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

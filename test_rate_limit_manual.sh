#!/bin/bash

# Script para testar Rate Limiting manualmente
# Faz 15 requisições POST e mostra o status de cada uma

echo "🔐 Teste de Rate Limiting"
echo "======================="
echo ""
echo "Enviando 15 requisições para /api/v1/predict/single"
echo "Limite: 10 requisições em 5 minutos"
echo "Esperado: Primeiras 10 com status 200/422, 11ª+ com status 429"
echo ""

API_URL="http://localhost:8000/api/v1/predict/single"
PAYLOAD='{"symbol":"BBD"}'

for i in {1..15}; do
    echo -n "Requisição $i: "
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")

    # Separar body e status code
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    # Exibir resultado
    if [ "$http_code" = "200" ]; then
        echo "✅ 200 OK (predição bem-sucedida)"
    elif [ "$http_code" = "422" ]; then
        echo "⚠️  422 (dados insuficientes, mas não rate limited)"
    elif [ "$http_code" = "429" ]; then
        # Extrair retry_after do response
        retry=$(echo "$body" | grep -o '"retry_after":[0-9]*' | grep -o '[0-9]*')
        echo "🚫 429 Too Many Requests (aguarde $retry seg)"
        echo "   Response: $body"
    elif [ "$http_code" = "500" ]; then
        echo "❌ 500 (erro interno - modelo pode não estar carregado)"
    else
        echo "❓ $http_code (código desconhecido)"
    fi

    # Pequeno delay entre requisições para evitar timeout
    sleep 0.1
done

echo ""
echo "✅ Teste concluído!"
echo ""
echo "💡 Próximos passos:"
echo "1. Se vir 429 na 11ª requisição: Rate limiting está funcionando! ✅"
echo "2. Se ver todas com 200/422: Verifique se rate_limit_logs está criado"
echo "3. Se ver 500: Verifique se modelo está carregado (/readiness)"

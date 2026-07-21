"""
Rate Limiting Service — Controle de Acesso por IP

Implementa limite de 10 requisições por 5 minutos por IP.
Usa SQLite (rate_limit_logs) para rastreamento de acessos.

Estratégia:
- Janela deslizante de 5 minutos (300 segundos)
- Máximo 10 requisições nessa janela
- Rejeita 11ª requisição com 429 Too Many Requests
- Limpa automaticamente registros antigos
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.logs import RateLimitLog


class RateLimitService:
    """Serviço de rate limiting baseado em SQLite.

    Configurações podem ser customizadas via variáveis de ambiente:
    - APP_RATE_LIMIT_MAX_REQUESTS (padrão: 10)
    - APP_RATE_LIMIT_WINDOW_SECONDS (padrão: 300)
    """

    # Valores padrão (podem ser sobrescritos via Settings)
    MAX_REQUESTS = 10  # Máximo de requisições na janela
    WINDOW_SECONDS = 300  # 5 minutos

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        Extrai IP do cliente da requisição.

        Prioridade:
        1. X-Forwarded-For (reverse proxy como Render.com, Nginx)
        2. X-Real-IP (proxy)
        3. client.host (conexão direta)
        """
        # Header X-Forwarded-For pode ter múltiplos IPs
        # Pegar o primeiro que é o IP real do cliente
        if forwarded := request.headers.get("x-forwarded-for"):
            return forwarded.split(",")[0].strip()

        # Fallback para X-Real-IP (usado por alguns proxies)
        if real_ip := request.headers.get("x-real-ip"):
            return real_ip

        # Última alternativa: IP direto da conexão
        return request.client.host if request.client else "unknown"

    @staticmethod
    def _cleanup_old_entries(db: Session) -> None:
        """Remove registros mais antigos que WINDOW_SECONDS."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=RateLimitService.WINDOW_SECONDS)
        db.query(RateLimitLog).filter(RateLimitLog.requested_at < cutoff_time).delete()
        db.commit()

    @staticmethod
    def check_and_log(ip: str, db: Session) -> tuple[bool, Optional[int]]:
        """
        Verifica se IP pode fazer requisição e registra tentativa.

        Args:
            ip: Endereço IP do cliente
            db: Sessão SQLAlchemy

        Returns:
            (allowed, retry_after_seconds)
            - allowed=True: IP pode fazer requisição
            - allowed=False: IP atingiu limite, retry_after=segundos até reset
        """
        # Limpar registros antigos periodicamente
        RateLimitService._cleanup_old_entries(db)

        # Contar requisições do IP nos últimos WINDOW_SECONDS
        cutoff_time = datetime.utcnow() - timedelta(seconds=RateLimitService.WINDOW_SECONDS)
        recent_requests = db.query(RateLimitLog).filter(
            RateLimitLog.ip_address == ip,
            RateLimitLog.requested_at >= cutoff_time,
        ).all()

        request_count = len(recent_requests)

        if request_count < RateLimitService.MAX_REQUESTS:
            # Permitir e registrar nova tentativa
            new_log = RateLimitLog(ip_address=ip, requested_at=datetime.utcnow())
            db.add(new_log)
            db.commit()
            return True, None
        else:
            # Negar e calcular tempo de espera
            # Pegar a requisição mais antiga na janela
            oldest_request = min(recent_requests, key=lambda r: r.requested_at)
            elapsed = (datetime.utcnow() - oldest_request.requested_at).total_seconds()
            retry_after = int(RateLimitService.WINDOW_SECONDS - elapsed + 1)
            return False, max(1, retry_after)  # Mínimo 1 segundo

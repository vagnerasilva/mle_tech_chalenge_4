"""Shim de compatibilidade: mantém `app.app:app` funcionando para configs de
deploy antigas (ex.: start command já configurado no Render). A aplicação de
verdade vive em app/main.py."""

from app.main import app  # noqa: F401

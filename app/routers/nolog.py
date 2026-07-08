from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.utils.constants import logger

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Rota raiz com instruções básicas de uso da API."""
    logger.info("Acessando rota raiz / para instruções da API")
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stock LSTM Forecast API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                background-color: #000000;
                color: #ffffff;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            header { border-bottom: 1px solid #333333; }
            nav {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                padding: 1rem 2rem;
                gap: 2rem;
            }
            .logo { font-size: 1.25rem; font-weight: 600; color: #ffffff; text-decoration: none; }
            .nav-links { display: flex; gap: 1.5rem; margin-left: auto; }
            .nav-links a {
                text-decoration: none; color: #888888; padding: 0.5rem 1rem;
                border-radius: 6px; transition: all 0.2s ease; font-size: 0.875rem; font-weight: 500;
            }
            .nav-links a:hover { color: #ffffff; background-color: #111111; }
            main {
                flex: 1; max-width: 1200px; margin: 0 auto; padding: 4rem 2rem;
                display: flex; flex-direction: column; align-items: center; text-align: center;
            }
            h1 {
                font-size: 3rem; font-weight: 700; margin-bottom: 1rem;
                background: linear-gradient(to right, #ffffff, #888888);
                background-clip: text; -webkit-background-clip: text;
            }
            .subtitle { font-size: 1.25rem; color: #888888; margin-bottom: 2rem; max-width: 650px; }
            .status-badge {
                display: inline-flex; align-items: center; gap: 0.5rem;
                background-color: #0070f3; color: #ffffff; padding: 0.25rem 0.75rem;
                border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-bottom: 2rem;
            }
            .status-dot { width: 6px; height: 6px; background-color: #00ff88; border-radius: 50%; }
            .cards {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem; width: 100%; max-width: 900px;
            }
            .card {
                background-color: #111111; border: 1px solid #333333; border-radius: 8px;
                padding: 1.5rem; transition: all 0.2s ease; text-align: left;
            }
            .card:hover { border-color: #555555; transform: translateY(-2px); }
            .card h3 { font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem; color: #ffffff; }
            .card p { color: #888888; font-size: 0.875rem; margin-bottom: 1rem; }
            .card a {
                display: inline-flex; align-items: center; color: #ffffff; text-decoration: none;
                font-size: 0.875rem; font-weight: 500; padding: 0.5rem 1rem; background-color: #222222;
                border-radius: 6px; border: 1px solid #333333; transition: all 0.2s ease;
            }
            .card a:hover { background-color: #333333; border-color: #555555; }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">Stock LSTM Forecast API</a>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                    <a href="/api/v1/health">Health</a>
                </div>
            </nav>
        </header>
        <main>
            <div class="status-badge"><span class="status-dot"></span> API online</div>
            <h1>📈 Stock LSTM Forecast API</h1>
            <p class="subtitle">
                API RESTful que serve um modelo LSTM treinado para prever o preço de
                fechamento de ações (ticker padrão: BBD) — Tech Challenge Fase 4, Pós Tech MLET.
            </p>
            <div class="cards">
                <div class="card">
                    <h3>Documentação Interativa</h3>
                    <p>Explore e teste todos os endpoints via Swagger UI.</p>
                    <a href="/docs">Abrir Swagger →</a>
                </div>
                <div class="card">
                    <h3>Health Check</h3>
                    <p>Status da API e se o modelo está carregado.</p>
                    <a href="/api/v1/health">Ver status →</a>
                </div>
                <div class="card">
                    <h3>Prever Fechamento</h3>
                    <p>POST /api/v1/predict — envie um ticker ou uma série histórica.</p>
                    <a href="/docs#/predict">Ver endpoint →</a>
                </div>
            </div>
        </main>
    </body>
    </html>
    """)

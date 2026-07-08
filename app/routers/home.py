from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.utils.constants import logger

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Rota com a listagem de todas as rotas da API disponíveis.
    """
    logger.info("Acessando rota /home para listar rotas disponíveis")
    routes = []
    for route in request.app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                if method not in ["HEAD", "OPTIONS"]:
                    if '/api/' in route.path:
                        routes.append({
                            "path": route.path,
                            "method": method,
                        })

    html = """
    <html>
        <head>
            <title>Stock LSTM Forecast API</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
                    background: #0a0a0a;
                    color: #ffffff;
                    padding: 40px;
                }
                .card {
                    background-color: #111111;
                    border: 1px solid #333333;
                    border-radius: 8px;
                    padding: 1.5rem;
                    transition: all 0.2s ease;
                    text-align: left;
                }
                
                .card:hover {
                    border-color: #555555;
                    transform: translateY(-2px);
                }
                
                .card h3 {
                    font-size: 1.125rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    color: #ffffff;
                }
            
                .card p {
                    color: #888888;
                    font-size: 0.875rem;
                    margin-bottom: 1rem;
                }
                
                .card a {
                    display: inline-flex;
                    align-items: center;
                    color: #ffffff;
                    text-decoration: none;
                    font-size: 0.875rem;
                    font-weight: 500;
                    padding: 0.5rem 1rem;
                    background-color: #222222;
                    border-radius: 6px;
                    border: 1px solid #333333;
                    transition: all 0.2s ease;
                }
                
                .card a:hover {
                    background-color: #333333;
                    border-color: #555555;
                }

                h1 {
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    background: linear-gradient(to right, #ffffff, #888888);
                    -webkit-background-clip: text;
                }
                h1 span {
                    font-size: 2.5rem;
                }
                p {
                    color: #aaaaaa;
                        margin-bottom: 2rem;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    background-color: #111111;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                }
                th, td {
                    text-align: left;
                    padding: 14px 16px;
                }
                th {
                    background: #1f1f1f;
                    color: #06b6d4;
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                tr {
                    border-bottom: 1px solid #333333;
                }
                tr:hover {
                    background: #222222;
                }
                .method {
                    font-weight: bold;
                    color: #22c55e;
                }
                .example {
                    color: #f59e0b;
                    font-family: monospace;
                }
            </style>
        </head>
        <body>
            <h1><span>📈</span> Stock LSTM Forecast API</h1>
            <div class="card">
                <h3>Veja a lista de todas as rotas disponíveis</h3>
                <p> Acesse a documentação para saber mais sobre as rotas <p>
                <a href="/docs">Documentação →</a>
            </div>
            <table>
                <tr>
                    <th>Método</th>
                    <th>Path</th>
                </tr>
    """

    for r in routes:
        html += f"""
            <tr>
                <td class='method'>{r["method"]}</td>
                <td>{r["path"]}</td>
            </tr>
        """

    html += """
            </table>
        </body>
    </html>
    """

    return HTMLResponse(content=html)

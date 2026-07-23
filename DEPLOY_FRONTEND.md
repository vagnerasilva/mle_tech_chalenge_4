# 🚀 Guia de Deploy Frontend + Backend

## 📋 Estrutura do Projeto

```
mle_tech_chalenge_4/
├── app/
│   ├── main.py (FastAPI - serve static files)
│   └── static/ (Frontend compilado aqui)
├── frontend/
│   ├── src/ (Código React)
│   ├── vite.config.js
│   └── package.json
└── render.yaml (Configuração de deploy)
```

## 🏠 Desenvolvimento Local

### Backend

```bash
# Instalar dependências
pip install -r requirements-dev.txt

# Rodar servidor
python -m app.main

# Acesso: http://localhost:8000
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Rodar dev server (com hot reload)
npm run dev

# Acesso: http://localhost:5173
```

## 🔨 Build para Produção

### Opção 1: Build Local (Testa tudo antes de commitar)

```bash
cd frontend
npm install
npm run build
cd ..

# Arquivos estarão em: app/static/
```

### Opção 2: Build no Render (Automático)

O `render.yaml` faz tudo:
1. Build do frontend (`npm run build`)
2. Instala deps Python
3. Roda uvicorn

## 🌐 Testando Localmente

Após fazer build do frontend:

```bash
python -m app.main
```

Acesse: `http://localhost:8000`
- Interface React estará disponível
- API disponível em `/api/v1/*`

## 📦 Deploy no Render

### 1. Commitar mudanças

```bash
git add frontend/ app/static/ render.yaml
git commit -m "feat: add React frontend for LSTM predictions"
git push
```

### 2. No Render.com

Opção A: **Via render.yaml (Automático)**
- Conectar repo GitHub
- Render detecta `render.yaml` automaticamente
- Faz deploy com build frontend + backend

Opção B: **Manual**
- Settings → Build & Deploy
- Build Command:
  ```
  cd frontend && npm install && npm run build && cd ..
  pip install -r requirements-prod.txt
  ```
- Start Command:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

## ✅ Checklist de Deploy

- [ ] Frontend compila sem erros (`npm run build`)
- [ ] Arquivos em `app/static/` criados
- [ ] `index.html` existe em `app/static/`
- [ ] API endpoints funcionam (`/api/v1/predict`)
- [ ] CORS está configurado no FastAPI
- [ ] `.python-version` = 3.13.12
- [ ] `requirements-prod.txt` atualizado
- [ ] `render.yaml` commitado

## 🔍 Troubleshooting

### Frontend não aparece (erro 404)

```bash
# Verificar se build foi feito
ls -la app/static/

# Se vazio, fazer build manual
cd frontend && npm run build
```

### API retorna CORS error

Verificar `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Deve incluir frontend URL
    ...
)
```

### Node/npm não encontrado no Render

Render detecta automaticamente `package.json`. Se não funcionar:
- Verificar se `frontend/package.json` existe
- Verificar se `buildCommand` está correto no `render.yaml`

## 📊 Estrutura de Arquivos Gerada

Após `npm run build`:

```
app/static/
├── index.html (SPA entry point)
├── assets/
│   ├── index-*.js (React app compilado)
│   └── index-*.css (Estilos compilados)
```

FastAPI serve:
- `/` → `index.html`
- `/assets/*` → Arquivos compilados
- `/api/v1/*` → API endpoints

## 🚀 URLs de Produção

Após deploy no Render:
- **Frontend**: `https://seu-app.onrender.com/`
- **API**: `https://seu-app.onrender.com/api/v1/*`
- **Docs**: `https://seu-app.onrender.com/docs`

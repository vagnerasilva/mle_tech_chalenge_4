# LSTM Front-end React

Front-end em React para consumir a API de previsão LSTM.

## 📦 Instalação

```bash
npm install
```

## 🚀 Desenvolvimento

Para rodar o servidor de desenvolvimento com hot reload:

```bash
npm run dev
```

Acesse `http://localhost:5173` (proxy para API em localhost:8000)

## 🔨 Build para Produção

Build gera arquivos em `../app/static`:

```bash
npm run build
```

Arquivos gerados em `app/static`:
- `index.html` - Página principal
- `assets/` - JS, CSS compilados

## 🌐 Integração com FastAPI

O FastAPI serve automaticamente os arquivos estáticos:
- `/` → `app/static/index.html`
- `/assets/*` → Arquivos compilados

## 📝 Estrutura

```
frontend/
├── src/
│   ├── components/
│   │   ├── PredictionForm.jsx
│   │   └── ResultCard.jsx
│   ├── styles/
│   │   ├── form.css
│   │   └── result.css
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── index.html
├── vite.config.js
└── package.json
```

## 🔧 Variáveis de Ambiente

Crie `.env` no diretório frontend se precisar customizar:

```env
VITE_API_URL=http://localhost:8000/api
```

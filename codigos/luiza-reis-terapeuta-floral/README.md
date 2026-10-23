# Luiza Reis - Terapeuta Floral

Site institucional em FastAPI para Luiza Reis, terapeuta floral.

## Rodar localmente

```bash
python -m pip install -r requirements.txt
python app.py
```

Ou, se preferir chamar o Uvicorn direto:

```bash
uvicorn app:app --reload --port 8010
```

Acesse:

```bash
http://127.0.0.1:8010
```

## Deploy na Vercel

```bash
vercel --prod
```

## Pontos para trocar

- WhatsApp e Instagram: `app.py`
- Fotos, videos e textos: `templates/index.html`
- Cores, espacamentos e responsivo: `static/style.css`

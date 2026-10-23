from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI(
    title="Luiza Reis - Terapeuta Floral",
    description="Site institucional de Luiza Reis, terapeuta floral.",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_year": datetime.now().year,
            # Trocar pelo WhatsApp real da Luiza, apenas numeros com DDI e DDD.
            "whatsapp_number": "5545991286029",
            # Trocar pelo link oficial, se o perfil final for outro.
            "instagram_url": "https://www.instagram.com/luizareisterapiafloral/",
        },
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8010, reload=True)

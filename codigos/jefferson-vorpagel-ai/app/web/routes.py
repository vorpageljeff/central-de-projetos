import re
import secrets
import unicodedata
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request, status
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.leads import save_lead, save_record
from app.services.newsbot import run_daily_newsbot
from app.services.notifications import notify_lead
from app.services.portal import (
    ADS,
    EDITORIAL_STATUSES,
    PRODUCTS,
    SERVICES,
    category_slug_from_name,
    get_ad,
    get_article,
    get_articles,
    get_articles_by_category,
    get_categories,
    get_category,
    get_all_editorial_articles,
    get_editorial_article,
    get_featured_article,
    get_related_articles,
    upsert_editable_article,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
security = HTTPBasic()


def template_context(request: Request, **extra):
    return {
        "request": request,
        "settings": settings,
        "categories": get_categories(),
        "whatsapp_phone": settings.whatsapp_phone,
        "top_ad": get_ad("banner-topo"),
        **extra,
    }


def status_message(status: str | None):
    messages = {
        "newsletter-success": ("success", "Cadastro recebido. A newsletter ja esta preparada para integracao futura."),
        "ad-success": ("success", "Interesse registrado. Vou retornar com as possibilidades comerciais."),
        "contact-success": ("success", "Recebi seu interesse. A mensagem ficou registrada para retorno."),
        "error": ("error", "Preencha os campos obrigatorios para eu entender melhor o contexto."),
    }
    if status not in messages:
        return None
    category, text = messages[status]
    return {"category": category, "text": text}


def require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    username_ok = secrets.compare_digest(credentials.username, settings.admin_username)
    password_ok = secrets.compare_digest(credentials.password, settings.admin_password)
    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or f"artigo-{date.today().isoformat()}"


def split_list(value: str) -> list[str]:
    items = re.split(r"[\n,]+", value or "")
    return [item.strip() for item in items if item.strip()]


def article_from_form(
    title: str,
    subtitle: str,
    slug: str,
    category: str,
    tags: str,
    author: str,
    published_at: str,
    reading_time: str,
    image: str,
    image_alt: str,
    source_name: str,
    source_url: str,
    original_language: str,
    ai_summary: str,
    relevance_score: int,
    suggested_category: str,
    impacted_audience: str,
    editorial_status: str,
    human_reviewed: str | None,
    sponsored: str | None,
    affiliate_notice: str | None,
    meta_title: str,
    meta_description: str,
    og_image: str,
    what_happened: str,
    why_matters: str,
    who_impacted: str,
    my_analysis: str,
    how_to_apply: str,
    action: str,
) -> dict:
    parsed_date = date.today()
    if published_at.strip():
        try:
            parsed_date = date.fromisoformat(published_at.strip())
        except ValueError:
            parsed_date = date.today()

    final_status = editorial_status
    final_human_reviewed = human_reviewed == "sim"
    if action == "aprovar":
        final_status = "aprovada"
        final_human_reviewed = True
    elif action == "publicar":
        final_status = "publicada"
        final_human_reviewed = True
    elif action == "arquivar":
        final_status = "arquivada"

    final_slug = slugify(slug or title)
    category_slug = category_slug_from_name(category)
    final_meta_title = meta_title.strip() or title.strip()
    final_meta_description = meta_description.strip() or subtitle.strip()
    final_og_image = og_image.strip() or image.strip()

    return {
        "title": title.strip(),
        "subtitle": subtitle.strip(),
        "slug": final_slug,
        "category": category,
        "category_slug": category_slug,
        "tags": split_list(tags),
        "author": author.strip() or "Jefferson Vorpagel",
        "published_at": parsed_date,
        "reading_time": reading_time.strip() or "5 min",
        "image": image.strip() or "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=82",
        "image_alt": image_alt.strip() or title.strip(),
        "source_name": source_name.strip(),
        "source_url": source_url.strip(),
        "original_language": original_language.strip() or "en",
        "ai_summary": ai_summary.strip(),
        "relevance_score": max(0, min(100, relevance_score)),
        "suggested_category": suggested_category.strip() or category,
        "impacted_audience": split_list(impacted_audience),
        "editorial_status": final_status,
        "human_reviewed": final_human_reviewed,
        "sponsored": sponsored == "sim",
        "affiliate_notice": affiliate_notice == "sim",
        "meta_title": final_meta_title,
        "meta_description": final_meta_description,
        "og_image": final_og_image,
        "what_happened": what_happened.strip(),
        "why_matters": why_matters.strip(),
        "who_impacted": who_impacted.strip(),
        "my_analysis": my_analysis.strip(),
        "how_to_apply": split_list(how_to_apply),
    }


def require_cron(request: Request):
    auth_header = request.headers.get("authorization", "")
    if not settings.cron_secret:
        raise HTTPException(status_code=503, detail="CRON_SECRET nao configurado.")
    if not secrets.compare_digest(auth_header, f"Bearer {settings.cron_secret}"):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/api/cron/daily-news")
async def daily_news_cron(request: Request):
    require_cron(request)
    result = run_daily_newsbot()
    return result


@router.post("/admin/robos/noticias")
async def admin_run_newsbot(_: str = Depends(require_admin)):
    result = run_daily_newsbot()
    return RedirectResponse(
        url=f"/admin/artigos?editorial_status=aguardando-revisao&bot_saved={result['saved']}",
        status_code=303,
    )


@router.get("/admin")
async def admin_home(_: str = Depends(require_admin)):
    return RedirectResponse(url="/admin/artigos", status_code=303)


@router.get("/admin/artigos")
async def admin_articles(request: Request, editorial_status: str = "", _: str = Depends(require_admin)):
    articles = get_all_editorial_articles()
    if editorial_status:
        articles = [article for article in articles if article.get("editorial_status") == editorial_status]

    counters = {
        status_item: len([article for article in get_all_editorial_articles() if article.get("editorial_status") == status_item])
        for status_item in EDITORIAL_STATUSES
    }
    return templates.TemplateResponse(
        "admin_articles.html",
        template_context(
            request,
            articles=articles,
            editorial_statuses=EDITORIAL_STATUSES,
            selected_status=editorial_status,
            counters=counters,
        ),
    )


@router.get("/admin/artigos/novo")
async def admin_new_article(request: Request, _: str = Depends(require_admin)):
    article = {
        "title": "",
        "subtitle": "",
        "slug": "",
        "category": "Noticias de IA",
        "tags": [],
        "author": "Jefferson Vorpagel",
        "published_at": date.today(),
        "reading_time": "5 min",
        "image": "",
        "image_alt": "",
        "source_name": "",
        "source_url": "",
        "original_language": "en",
        "ai_summary": "",
        "relevance_score": 50,
        "suggested_category": "Noticias de IA",
        "impacted_audience": [],
        "editorial_status": "aguardando-revisao",
        "human_reviewed": False,
        "sponsored": False,
        "affiliate_notice": False,
        "meta_title": "",
        "meta_description": "",
        "og_image": "",
        "what_happened": "",
        "why_matters": "",
        "who_impacted": "",
        "my_analysis": "",
        "how_to_apply": [],
    }
    return templates.TemplateResponse(
        "admin_article_form.html",
        template_context(
            request,
            article=article,
            editorial_statuses=EDITORIAL_STATUSES,
            form_action="/admin/artigos/novo",
            mode="new",
        ),
    )


@router.post("/admin/artigos/novo")
async def admin_create_article(
    title: str = Form(""),
    subtitle: str = Form(""),
    new_slug: str = Form(""),
    category: str = Form("Noticias de IA"),
    tags: str = Form(""),
    author: str = Form("Jefferson Vorpagel"),
    published_at: str = Form(""),
    reading_time: str = Form("5 min"),
    image: str = Form(""),
    image_alt: str = Form(""),
    source_name: str = Form(""),
    source_url: str = Form(""),
    original_language: str = Form("en"),
    ai_summary: str = Form(""),
    relevance_score: int = Form(50),
    suggested_category: str = Form(""),
    impacted_audience: str = Form(""),
    editorial_status: str = Form("aguardando-revisao"),
    human_reviewed: str | None = Form(None),
    sponsored: str | None = Form(None),
    affiliate_notice: str | None = Form(None),
    meta_title: str = Form(""),
    meta_description: str = Form(""),
    og_image: str = Form(""),
    what_happened: str = Form(""),
    why_matters: str = Form(""),
    who_impacted: str = Form(""),
    my_analysis: str = Form(""),
    how_to_apply: str = Form(""),
    action: str = Form("salvar"),
    _: str = Depends(require_admin),
):
    article = article_from_form(
        title,
        subtitle,
        new_slug,
        category,
        tags,
        author,
        published_at,
        reading_time,
        image,
        image_alt,
        source_name,
        source_url,
        original_language,
        ai_summary,
        relevance_score,
        suggested_category,
        impacted_audience,
        editorial_status,
        human_reviewed,
        sponsored,
        affiliate_notice,
        meta_title,
        meta_description,
        og_image,
        what_happened,
        why_matters,
        who_impacted,
        my_analysis,
        how_to_apply,
        action,
    )
    if not article["title"]:
        return RedirectResponse(url="/admin/artigos/novo?status=error", status_code=303)

    upsert_editable_article(article)
    return RedirectResponse(url=f"/admin/artigos/{article['slug']}/editar?status=saved", status_code=303)


@router.get("/admin/artigos/{slug}/editar")
async def admin_edit_article(request: Request, slug: str, status: str | None = None, _: str = Depends(require_admin)):
    article = get_editorial_article(slug)
    if not article:
        return templates.TemplateResponse("404.html", template_context(request), status_code=404)

    return templates.TemplateResponse(
        "admin_article_form.html",
        template_context(
            request,
            article=article,
            editorial_statuses=EDITORIAL_STATUSES,
            form_action=f"/admin/artigos/{slug}/editar",
            mode="edit",
            message={"category": "success", "text": "Artigo salvo."} if status == "saved" else None,
        ),
    )


@router.post("/admin/artigos/{slug}/editar")
async def admin_update_article(
    slug: str,
    title: str = Form(""),
    subtitle: str = Form(""),
    new_slug: str = Form(""),
    category: str = Form("Noticias de IA"),
    tags: str = Form(""),
    author: str = Form("Jefferson Vorpagel"),
    published_at: str = Form(""),
    reading_time: str = Form("5 min"),
    image: str = Form(""),
    image_alt: str = Form(""),
    source_name: str = Form(""),
    source_url: str = Form(""),
    original_language: str = Form("en"),
    ai_summary: str = Form(""),
    relevance_score: int = Form(50),
    suggested_category: str = Form(""),
    impacted_audience: str = Form(""),
    editorial_status: str = Form("aguardando-revisao"),
    human_reviewed: str | None = Form(None),
    sponsored: str | None = Form(None),
    affiliate_notice: str | None = Form(None),
    meta_title: str = Form(""),
    meta_description: str = Form(""),
    og_image: str = Form(""),
    what_happened: str = Form(""),
    why_matters: str = Form(""),
    who_impacted: str = Form(""),
    my_analysis: str = Form(""),
    how_to_apply: str = Form(""),
    action: str = Form("salvar"),
    _: str = Depends(require_admin),
):
    article = article_from_form(
        title,
        subtitle,
        new_slug or slug,
        category,
        tags,
        author,
        published_at,
        reading_time,
        image,
        image_alt,
        source_name,
        source_url,
        original_language,
        ai_summary,
        relevance_score,
        suggested_category,
        impacted_audience,
        editorial_status,
        human_reviewed,
        sponsored,
        affiliate_notice,
        meta_title,
        meta_description,
        og_image,
        what_happened,
        why_matters,
        who_impacted,
        my_analysis,
        how_to_apply,
        action,
    )
    upsert_editable_article(article)
    return RedirectResponse(url=f"/admin/artigos/{article['slug']}/editar?status=saved", status_code=303)


@router.get("/")
async def home(request: Request, status: str | None = None):
    articles = get_articles()
    return templates.TemplateResponse(
        "home.html",
        template_context(
            request,
            message=status_message(status),
            featured=get_featured_article(),
            latest=articles[1:5],
            business=get_articles_by_category("ia-nos-negocios") or articles[:3],
            education=get_articles_by_category("ia-na-educacao"),
            agro=get_articles_by_category("ia-no-agro"),
            tools=get_articles_by_category("ferramentas-de-ia"),
            opinion=get_articles_by_category("opiniao") or articles[:2],
            products=PRODUCTS,
            services=SERVICES,
        ),
    )


@router.get("/artigos/{slug}")
async def article_detail(request: Request, slug: str, status: str | None = None):
    article = get_article(slug)
    if not article:
        return templates.TemplateResponse("404.html", template_context(request), status_code=404)

    return templates.TemplateResponse(
        "article.html",
        template_context(
            request,
            article=article,
            related=get_related_articles(article),
            content_ad=get_ad("dentro-materia"),
            final_ad=get_ad("banner-final-materia"),
            message=status_message(status),
        ),
    )


@router.get("/categorias/{slug}")
async def category_page(request: Request, slug: str):
    category = get_category(slug)
    if not category:
        return templates.TemplateResponse("404.html", template_context(request), status_code=404)

    return templates.TemplateResponse(
        "category.html",
        template_context(request, category=category, articles=get_articles_by_category(slug)),
    )


@router.get("/buscar")
async def search(request: Request, q: str = ""):
    term = q.strip().lower()
    articles = []
    if term:
        articles = [
            article
            for article in get_articles()
            if term in article["title"].lower()
            or term in article["subtitle"].lower()
            or term in article["category"].lower()
            or any(term in tag.lower() for tag in article["tags"])
        ]

    return templates.TemplateResponse(
        "search.html",
        template_context(request, query=q.strip(), articles=articles),
    )


@router.get("/anuncie")
async def advertise(request: Request, status: str | None = None):
    return templates.TemplateResponse(
        "advertise.html",
        template_context(request, message=status_message(status), ads=ADS),
    )


@router.post("/anuncie", name="advertise_interest")
async def advertise_interest(
    nome: str = Form(""),
    empresa: str = Form(""),
    email: str = Form(""),
    telefone: str = Form(""),
    interesse: str = Form(""),
    mensagem: str = Form(""),
):
    required = [nome, empresa, email, interesse]
    if not all(value.strip() for value in required):
        return RedirectResponse(url="/anuncie?status=error#formulario", status_code=303)

    save_record(
        settings.advertisers_file,
        {
            "type": "advertiser_interest",
            "name": nome,
            "company": empresa,
            "email": email,
            "phone": telefone,
            "interest": interesse,
            "message": mensagem,
        },
    )
    return RedirectResponse(url="/anuncie?status=ad-success#formulario", status_code=303)


@router.get("/consultoria")
async def consulting(request: Request, status: str | None = None):
    return templates.TemplateResponse(
        "consulting.html",
        template_context(request, services=SERVICES, message=status_message(status)),
    )


@router.get("/sobre")
async def about(request: Request):
    return templates.TemplateResponse("about.html", template_context(request))


@router.post("/newsletter", name="newsletter")
async def newsletter(
    background_tasks: BackgroundTasks,
    nome: str = Form(""),
    email: str = Form(""),
    area_interesse: str = Form(""),
    profissao_segmento: str = Form(""),
    consentimento: str | None = Form(None),
    origem: str = Form("/"),
):
    if not nome.strip() or not email.strip() or consentimento != "sim":
        return RedirectResponse(url=f"{origem}?status=error#newsletter", status_code=303)

    payload = {
        "type": "newsletter",
        "name": nome,
        "email": email,
        "interest_area": area_interesse,
        "profession_segment": profissao_segmento,
        "consent": True,
        "integration_ready_for": ["Mailchimp", "Brevo", "RD Station", "ConvertKit", "database"],
    }
    save_lead(settings.leads_file, payload)
    background_tasks.add_task(
        notify_lead,
        settings.notification_webhook_url,
        {"source": "portal-newsletter", **payload},
    )
    return RedirectResponse(url=f"{origem}?status=newsletter-success#newsletter", status_code=303)


@router.post("/contato", name="contact")
async def contact(
    background_tasks: BackgroundTasks,
    nome: str = Form(""),
    email: str = Form(""),
    mensagem: str = Form(""),
    origem: str = Form("/consultoria"),
):
    if not nome.strip() or not email.strip() or not mensagem.strip():
        return RedirectResponse(url=f"{origem}?status=error#contato", status_code=303)

    payload = {
        "type": "consulting_contact",
        "name": nome,
        "email": email,
        "message": mensagem,
        "whatsapp_to": settings.whatsapp_phone,
    }
    save_lead(settings.leads_file, payload)
    background_tasks.add_task(notify_lead, settings.notification_webhook_url, {"source": "portal-consultoria", **payload})
    return RedirectResponse(url=f"{origem}?status=contact-success#contato", status_code=303)


@router.get("/robots.txt")
async def robots():
    body = f"User-agent: *\nAllow: /\nSitemap: {settings.site_url.rstrip('/')}/sitemap.xml\n"
    return PlainTextResponse(body)


@router.get("/ads.txt")
async def ads_txt():
    if not settings.adsense_client_id.startswith("ca-pub-"):
        return PlainTextResponse("# Configure ADSENSE_CLIENT_ID=ca-pub-xxxxxxxxxxxxxxxx para ativar o ads.txt.\n")

    publisher_id = settings.adsense_client_id.replace("ca-pub-", "")
    return PlainTextResponse(f"google.com, pub-{publisher_id}, DIRECT, f08c47fec0942fa0\n")


@router.get("/sitemap.xml")
async def sitemap():
    base_url = settings.site_url.rstrip("/")
    urls = ["/", "/anuncie", "/consultoria", "/sobre"]
    urls.append("/buscar")
    urls.extend(f"/categorias/{category['slug']}" for category in get_categories())
    urls.extend(f"/artigos/{article['slug']}" for article in get_articles())
    items = "".join(f"<url><loc>{base_url}{url}</loc></url>" for url in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>'
    return Response(content=xml, media_type="application/xml")

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from typing import Any

from app.config import settings
from app.services.portal import category_slug_from_name, get_all_editorial_articles, upsert_editable_article


USER_AGENT = "JeffersonVorpagelAI-Newsbot/1.0 (+https://jefferson-vorpagel-ai.vercel.app)"


@dataclass
class CapturedNews:
    title: str
    url: str
    source_name: str
    summary: str
    published_at: date


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "noscript", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str):
        if not self._ignored_depth:
            text = " ".join(data.split())
            if len(text) > 40:
                self.parts.append(text)

    def text(self) -> str:
        return " ".join(self.parts)


def fetch_url(url: str, timeout: int = 12) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def parse_date(value: str | None) -> date:
    if not value:
        return date.today()
    for token in [value[:10], value]:
        try:
            return date.fromisoformat(token)
        except ValueError:
            continue
    return date.today()


def feed_source_name(source_url: str) -> str:
    host = urllib.parse.urlparse(source_url).netloc.replace("www.", "")
    return host or "Fonte internacional"


def parse_rss(source_url: str, xml_text: str, limit: int = 8) -> list[CapturedNews]:
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    captured: list[CapturedNews] = []
    for item in items[:limit]:
        title = clean_text(item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "")
        link = item.findtext("link") or ""
        atom_link = item.find("{http://www.w3.org/2005/Atom}link")
        if atom_link is not None:
            link = atom_link.attrib.get("href", link)
        summary = clean_text(
            item.findtext("description")
            or item.findtext("summary")
            or item.findtext("{http://www.w3.org/2005/Atom}summary")
            or ""
        )
        published = parse_date(item.findtext("pubDate") or item.findtext("published") or item.findtext("{http://www.w3.org/2005/Atom}published"))
        if title and link:
            captured.append(
                CapturedNews(
                    title=title,
                    url=link,
                    source_name=feed_source_name(source_url),
                    summary=summary,
                    published_at=published,
                )
            )
    return captured


def scrape_article_excerpt(url: str) -> str:
    try:
        page = fetch_url(url)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return ""

    parser = TextExtractor()
    parser.feed(page)
    text = parser.text()
    return text[:1800]


class CollectorAgent:
    def run(self, sources: list[str]) -> list[CapturedNews]:
        captured: list[CapturedNews] = []
        for source in sources:
            try:
                content = fetch_url(source)
                captured.extend(parse_rss(source, content))
            except (ET.ParseError, urllib.error.URLError, TimeoutError, ValueError):
                continue
        return captured


class ClassifierAgent:
    keywords = {
        "IA nos Negocios": ["business", "enterprise", "startup", "productivity", "customer", "sales", "company"],
        "IA na Educacao": ["education", "school", "teacher", "student", "learning", "university"],
        "IA no Agro": ["agriculture", "farm", "crop", "climate", "food", "soil"],
        "Ferramentas de IA": ["tool", "app", "model", "platform", "assistant", "chatbot"],
        "Automacao e Agentes": ["agent", "automation", "workflow", "autonomous", "operator"],
        "Mercado de Trabalho": ["job", "work", "labor", "career", "skills", "profession"],
    }

    def run(self, news: CapturedNews) -> dict[str, Any]:
        text = f"{news.title} {news.summary}".lower()
        score = 58
        category = "Noticias de IA"
        tags = ["inteligencia artificial", "curadoria internacional"]

        for category_name, terms in self.keywords.items():
            matches = [term for term in terms if term in text]
            if matches:
                category = category_name
                score += min(32, len(matches) * 8)
                tags.extend(matches[:3])
                break

        important_terms = ["openai", "google", "microsoft", "anthropic", "nvidia", "regulation", "agents", "education"]
        score += min(10, sum(1 for term in important_terms if term in text) * 3)

        return {
            "category": category,
            "category_slug": category_slug_from_name(category),
            "relevance_score": min(100, score),
            "tags": sorted(set(tags)),
            "impacted_audience": ["Empresas", "Gestores", "Professores", "Analistas", "Times de tecnologia"],
        }


class DraftAgent:
    def run(self, news: CapturedNews, classification: dict[str, Any]) -> dict[str, Any]:
        excerpt = scrape_article_excerpt(news.url) or news.summary
        summary = clean_text(news.summary or excerpt)[:420]
        title = f"O que a noticia sobre {news.title[:72].rstrip()} significa para o Brasil"

        return {
            "title": title,
            "subtitle": "Curadoria internacional de IA transformada em impacto pratico para negocios, educacao, tecnologia e agro.",
            "ai_summary": summary or "Resumo inicial gerado a partir da fonte original para revisao humana.",
            "what_happened": f"A fonte original publicou uma noticia sobre: {news.title}. Este rascunho foi criado para revisao editorial, sem copiar integralmente o conteudo de terceiros.",
            "why_matters": "A noticia pode indicar mudancas relevantes em estrategia, produtividade, educacao, regulacao, ferramentas ou automacao com IA para o contexto brasileiro.",
            "who_impacted": ", ".join(classification["impacted_audience"]),
            "my_analysis": "Inclua aqui sua leitura autoral: o que muda para empresas brasileiras, quais riscos existem e quais decisoes praticas merecem atencao.",
            "how_to_apply": [
                "Validar a fonte original e complementar com contexto brasileiro.",
                "Identificar qual publico sera mais impactado pela mudanca.",
                "Transformar a noticia em recomendacao pratica antes de publicar.",
            ],
            "excerpt_used_for_draft": excerpt[:900],
        }


class QualityAgent:
    def run(self, article: dict[str, Any]) -> dict[str, Any]:
        article["editorial_status"] = "aguardando-revisao"
        article["human_reviewed"] = False
        article["sponsored"] = False
        article["affiliate_notice"] = False
        article["reading_time"] = "5 min"
        article["author"] = "Jefferson Vorpagel"
        article["original_language"] = "en"
        article["image"] = "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=82"
        article["image_alt"] = "Interface digital representando inteligencia artificial e tecnologia"
        article["meta_title"] = article["title"][:70]
        article["meta_description"] = article["subtitle"][:155]
        article["og_image"] = article["image"]
        return article


class PublisherAgent:
    def run(self, articles: list[dict[str, Any]]) -> list[str]:
        existing_slugs = {article["slug"] for article in get_all_editorial_articles()}
        saved: list[str] = []
        for article in articles:
            if article["slug"] in existing_slugs:
                continue
            upsert_editable_article(article)
            saved.append(article["slug"])
            existing_slugs.add(article["slug"])
        return saved


def slug_from_url(url: str, title: str) -> str:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    base = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")[:68]
    return f"{base}-{digest}" if base else f"noticia-ia-{digest}"


def sources_from_settings() -> list[str]:
    return [source.strip() for source in settings.newsbot_sources.split(",") if source.strip()]


def run_daily_newsbot(limit: int | None = None) -> dict[str, Any]:
    daily_limit = limit or settings.newsbot_daily_limit
    collected = CollectorAgent().run(sources_from_settings())
    existing_sources = {article.get("source_url") for article in get_all_editorial_articles()}

    classifier = ClassifierAgent()
    draft_agent = DraftAgent()
    quality_agent = QualityAgent()
    ranked: list[tuple[CapturedNews, dict[str, Any]]] = []
    for item in collected:
        if item.url in existing_sources:
            continue
        classification = classifier.run(item)
        if classification["relevance_score"] >= 60:
            ranked.append((item, classification))

    ranked.sort(key=lambda pair: pair[1]["relevance_score"], reverse=True)
    selected = ranked[: max(1, daily_limit)]
    drafts: list[dict[str, Any]] = []

    for news, classification in selected:
        draft = draft_agent.run(news, classification)
        article = {
            **draft,
            **classification,
            "slug": slug_from_url(news.url, news.title),
            "source_name": news.source_name,
            "source_url": news.url,
            "published_at": date.today(),
            "suggested_category": classification["category"],
        }
        drafts.append(quality_agent.run(article))

    saved = PublisherAgent().run(drafts)
    return {
        "collected": len(collected),
        "selected": len(selected),
        "saved": len(saved),
        "slugs": saved,
        "status": "drafts_created_for_human_review",
    }

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from app.config import settings


EDITORIAL_STATUSES = [
    "capturada",
    "rascunho-gerado",
    "aguardando-revisao",
    "aprovada",
    "publicada",
    "arquivada",
]

CATEGORIES = [
    {"name": "Noticias de IA", "slug": "noticias-de-ia", "description": "Movimentos internacionais de IA traduzidos para impacto pratico no Brasil."},
    {"name": "IA nos Negocios", "slug": "ia-nos-negocios", "description": "Estrategia, produtividade, operacao, atendimento e decisao com IA."},
    {"name": "IA na Educacao", "slug": "ia-na-educacao", "description": "Uso responsavel de IA por professores, instituicoes e estudantes."},
    {"name": "IA no Agro", "slug": "ia-no-agro", "description": "Aplicacoes de IA em gestao rural, produtividade, clima, dados e cadeia agro."},
    {"name": "Ferramentas de IA", "slug": "ferramentas-de-ia", "description": "Curadoria de ferramentas, comparativos e aplicacoes praticas."},
    {"name": "Automacao e Agentes", "slug": "automacao-e-agentes", "description": "Workflows, agentes de IA, integracoes e automacao de processos."},
    {"name": "Mercado de Trabalho", "slug": "mercado-de-trabalho", "description": "Competencias, carreiras e impactos da IA nas profissoes."},
    {"name": "Opiniao", "slug": "opiniao", "description": "Analises autorais sobre tecnologia, negocio, educacao e gestao."},
    {"name": "Guias e Tutoriais", "slug": "guias-e-tutoriais", "description": "Passo a passo para aplicar IA com criterio e seguranca."},
]

ARTICLES = [
    {
        "title": "A nova corrida dos agentes de IA e o que ela muda nas empresas brasileiras",
        "subtitle": "Agentes deixam de ser promessa isolada e comecam a exigir processos, dados e governanca para gerar resultado.",
        "slug": "corrida-agentes-ia-empresas-brasileiras",
        "category": "Automacao e Agentes",
        "category_slug": "automacao-e-agentes",
        "tags": ["agentes de IA", "automacao", "negocios", "governanca"],
        "author": "Jefferson Vorpagel",
        "published_at": date(2026, 5, 20),
        "reading_time": "7 min",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=82",
        "image_alt": "Equipe analisando paineis digitais em ambiente de tecnologia",
        "source_name": "Curadoria internacional de tecnologia",
        "source_url": "https://www.technologyreview.com/",
        "original_language": "en",
        "ai_summary": "Empresas globais estao investindo em agentes capazes de executar tarefas em varias etapas, mas a adocao depende de processos claros e revisao humana.",
        "relevance_score": 94,
        "suggested_category": "Automacao e Agentes",
        "impacted_audience": ["Gestores", "Analistas de negocios", "Times de tecnologia", "Operacoes"],
        "editorial_status": "publicada",
        "human_reviewed": True,
        "sponsored": False,
        "affiliate_notice": False,
        "meta_title": "Agentes de IA: impacto pratico nas empresas brasileiras",
        "meta_description": "Entenda por que a corrida global dos agentes de IA importa para negocios brasileiros e como aplicar com governanca.",
        "og_image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=82",
        "what_happened": "Grandes empresas de tecnologia estao reposicionando seus produtos em torno de agentes capazes de planejar, consultar sistemas, executar tarefas e pedir aprovacao humana quando necessario.",
        "why_matters": "Para empresas brasileiras, a diferenca esta menos no hype e mais na capacidade de redesenhar processos. Sem dados organizados, papeis claros e limites de decisao, o agente vira apenas mais uma interface.",
        "who_impacted": "Gestores que buscam produtividade, times de tecnologia responsaveis por integracoes, analistas que documentam processos e liderancas que precisam controlar risco operacional.",
        "my_analysis": "O ponto central nao e perguntar qual agente comprar, mas quais decisoes podem ser parcialmente automatizadas com seguranca. O ganho real aparece quando a empresa combina fluxo, criterio e supervisao.",
        "how_to_apply": [
            "Mapeie um processo repetitivo com entrada, decisao e saida bem definidas.",
            "Defina quais etapas podem ser sugeridas pela IA e quais exigem aprovacao humana.",
            "Crie metricas simples: tempo economizado, erros evitados e satisfacao do usuario interno.",
        ],
    },
    {
        "title": "IA generativa na sala de aula: de proibicao para criterio de uso",
        "subtitle": "Instituicoes que tratam IA apenas como risco perdem a chance de formar criterio profissional nos estudantes.",
        "slug": "ia-generativa-sala-de-aula-criterio-de-uso",
        "category": "IA na Educacao",
        "category_slug": "ia-na-educacao",
        "tags": ["educacao", "professores", "avaliacao", "letramento em IA"],
        "author": "Jefferson Vorpagel",
        "published_at": date(2026, 5, 16),
        "reading_time": "6 min",
        "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1600&q=82",
        "image_alt": "Estudantes trabalhando em grupo com computadores",
        "source_name": "Relatorios e debates internacionais sobre educacao",
        "source_url": "https://unesdoc.unesco.org/",
        "original_language": "en",
        "ai_summary": "O debate educacional internacional avanca para politicas de uso, transparencia e avaliacao, em vez de proibicao ampla.",
        "relevance_score": 88,
        "suggested_category": "IA na Educacao",
        "impacted_audience": ["Professores", "Coordenadores", "Estudantes", "Instituicoes de ensino"],
        "editorial_status": "publicada",
        "human_reviewed": True,
        "sponsored": False,
        "affiliate_notice": False,
        "meta_title": "IA generativa na educacao: criterio de uso em sala",
        "meta_description": "Como professores e instituicoes podem transformar IA generativa em criterio de aprendizagem, nao em atalho.",
        "og_image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1600&q=82",
        "what_happened": "O debate internacional sobre IA na educacao vem migrando de bloqueios para politicas de uso transparente, citacao de ferramentas e reformulacao de atividades.",
        "why_matters": "No Brasil, professores precisam lidar com uso real de IA pelos alunos. Ignorar isso aumenta desigualdade entre quem sabe usar bem e quem apenas terceiriza pensamento.",
        "who_impacted": "Professores, coordenadores de curso, estudantes, equipes pedagogicas e empresas que contratam profissionais recem-formados.",
        "my_analysis": "A pergunta boa nao e se o aluno usou IA. E se ele sabe explicar decisao, validar resposta, apontar limite e transformar apoio da ferramenta em aprendizagem verificavel.",
        "how_to_apply": [
            "Crie atividades em que o aluno entregue prompt, criterio de avaliacao e revisao propria.",
            "Separe tarefas de treino individual de tarefas onde a IA e permitida com transparencia.",
            "Inclua rubricas que avaliem verificacao, argumentacao e autoria.",
        ],
    },
    {
        "title": "IA no agro depende menos de futurismo e mais de dados confiaveis",
        "subtitle": "Produtores e cooperativas podem capturar valor antes de projetos complexos se organizarem dados operacionais.",
        "slug": "ia-no-agro-dados-confiaveis",
        "category": "IA no Agro",
        "category_slug": "ia-no-agro",
        "tags": ["agro", "dados", "produtividade", "gestao"],
        "author": "Jefferson Vorpagel",
        "published_at": date(2026, 5, 12),
        "reading_time": "5 min",
        "image": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1600&q=82",
        "image_alt": "Plantacao vista ao nascer do sol",
        "source_name": "Curadoria internacional sobre agricultura digital",
        "source_url": "https://www.fao.org/",
        "original_language": "en",
        "ai_summary": "IA no agro cresce com previsao, sensoriamento e recomendacao, mas qualidade dos dados segue como principal gargalo.",
        "relevance_score": 86,
        "suggested_category": "IA no Agro",
        "impacted_audience": ["Produtores", "Cooperativas", "Consultores", "Agtechs"],
        "editorial_status": "publicada",
        "human_reviewed": True,
        "sponsored": False,
        "affiliate_notice": False,
        "meta_title": "IA no agro: valor pratico com dados confiaveis",
        "meta_description": "Por que a adocao de IA no agro brasileiro comeca por dados, processos e decisoes simples.",
        "og_image": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1600&q=82",
        "what_happened": "Solucoes de IA para previsao, monitoramento e recomendacao no campo estao amadurecendo, mas dependem de registros consistentes e contexto local.",
        "why_matters": "Para o agro brasileiro, dados ruins podem gerar recomendacoes caras. O valor aparece quando tecnologia acompanha rotina, clima, solo, maquinario e decisao de manejo.",
        "who_impacted": "Produtores, cooperativas, consultores agronomicos, fornecedores de tecnologia e gestores de propriedades.",
        "my_analysis": "Antes de buscar IA sofisticada, vale organizar um painel simples de decisoes recorrentes: compra, plantio, aplicacao, manutencao e previsao de demanda.",
        "how_to_apply": [
            "Liste os dados ja coletados e quem confia neles.",
            "Escolha uma decisao com alto custo de erro para testar apoio analitico.",
            "Mantenha revisao humana e registro do resultado para comparar safra a safra.",
        ],
    },
    {
        "title": "Ferramentas de IA para analistas: produtividade sem perder criterio",
        "subtitle": "O melhor ganho para analistas vem de acelerar leitura, sintese e documentacao, nao de terceirizar decisao.",
        "slug": "ferramentas-ia-analistas-produtividade-criterio",
        "category": "Ferramentas de IA",
        "category_slug": "ferramentas-de-ia",
        "tags": ["ferramentas", "analise de negocios", "produtividade"],
        "author": "Jefferson Vorpagel",
        "published_at": date(2026, 5, 9),
        "reading_time": "4 min",
        "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1600&q=82",
        "image_alt": "Pessoa analisando graficos e dados em uma tela",
        "source_name": "Curadoria de ferramentas globais de produtividade",
        "source_url": "https://www.gartner.com/",
        "original_language": "en",
        "ai_summary": "Ferramentas de IA ganham espaco em rotinas de analise, mas exigem criterio para evitar documentacao superficial.",
        "relevance_score": 81,
        "suggested_category": "Ferramentas de IA",
        "impacted_audience": ["Analistas", "Product owners", "Gestores de projeto"],
        "editorial_status": "publicada",
        "human_reviewed": True,
        "sponsored": True,
        "affiliate_notice": True,
        "meta_title": "Ferramentas de IA para analistas com criterio",
        "meta_description": "Como usar ferramentas de IA para acelerar analise de negocios, documentacao e sintese sem perder qualidade.",
        "og_image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1600&q=82",
        "what_happened": "Ferramentas de escrita, busca, reunioes e automacao estao se consolidando como apoio diario para analistas e gestores.",
        "why_matters": "A produtividade cresce, mas tambem cresce o risco de requisitos genericos, atas sem decisao e documentos que parecem bons mas nao sustentam execucao.",
        "who_impacted": "Analistas de negocios, gestores de projetos, product owners, consultores e equipes de tecnologia.",
        "my_analysis": "A IA deve reduzir tempo de preparacao e melhorar alternativas. A responsabilidade pelo criterio, pela pergunta e pela decisao continua humana.",
        "how_to_apply": [
            "Use IA para preparar perguntas antes de entrevistas com stakeholders.",
            "Peça sinteses comparativas, mas valide com fontes e contexto do projeto.",
            "Crie checklists de qualidade antes de transformar texto em backlog.",
        ],
    },
]

ADS = [
    {
        "advertiser": "Espaco comercial",
        "title": "Patrocine o Radar de IA Aplicada",
        "image": "",
        "target_url": "/anuncie",
        "position": "banner-topo",
        "starts_at": "2026-05-01",
        "ends_at": "2026-12-31",
        "status": "ativo",
        "impressions": 0,
        "clicks": 0,
    },
    {
        "advertiser": "Consultoria Jefferson Vorpagel",
        "title": "Diagnostico de automacao com IA para empresas",
        "image": "",
        "target_url": "/consultoria",
        "position": "dentro-materia",
        "starts_at": "2026-05-01",
        "ends_at": "2026-12-31",
        "status": "ativo",
        "impressions": 0,
        "clicks": 0,
    },
]

PRODUCTS = [
    "E-books e guias praticos",
    "Cursos e workshops",
    "Templates para diagnostico de IA",
    "Comunidade de IA aplicada",
    "Mentorias e trilhas executivas",
]

SERVICES = [
    "Consultoria em IA para empresas",
    "Palestras e treinamentos corporativos",
    "Diagnostico de automacao com IA",
    "Projetos de agentes de IA",
    "IA aplicada a analise de negocios",
    "IA aplicada a gestao de projetos",
    "IA aplicada ao agro e educacao",
]


def get_categories() -> list[dict]:
    return CATEGORIES


def category_slug_from_name(name: str) -> str:
    category = next((item for item in CATEGORIES if item["name"] == name), None)
    return category["slug"] if category else "noticias-de-ia"


def _article_sort_key(article: dict) -> date:
    published_at = article.get("published_at")
    if isinstance(published_at, date):
        return published_at
    if isinstance(published_at, str):
        try:
            return date.fromisoformat(published_at)
        except ValueError:
            return date.today()
    return date.today()


def _serialize_article(article: dict[str, Any]) -> dict[str, Any]:
    serialized = dict(article)
    if isinstance(serialized.get("published_at"), date):
        serialized["published_at"] = serialized["published_at"].isoformat()
    return serialized


def _hydrate_article(article: dict[str, Any]) -> dict[str, Any]:
    hydrated = dict(article)
    published_at = hydrated.get("published_at")
    if isinstance(published_at, str):
        try:
            hydrated["published_at"] = date.fromisoformat(published_at)
        except ValueError:
            hydrated["published_at"] = date.today()
    hydrated.setdefault("tags", [])
    hydrated.setdefault("how_to_apply", [])
    hydrated.setdefault("impacted_audience", [])
    hydrated.setdefault("editorial_status", "aguardando-revisao")
    hydrated.setdefault("human_reviewed", False)
    hydrated.setdefault("sponsored", False)
    hydrated.setdefault("affiliate_notice", False)
    return hydrated


def load_editable_articles(articles_file: Path | None = None) -> list[dict]:
    file_path = articles_file or settings.articles_file
    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        return []

    return [_hydrate_article(article) for article in data if isinstance(article, dict)]


def save_editable_articles(articles: list[dict], articles_file: Path | None = None) -> None:
    file_path = articles_file or settings.articles_file
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump([_serialize_article(article) for article in articles], file, ensure_ascii=False, indent=2)


def get_all_editorial_articles() -> list[dict]:
    merged = {article["slug"]: _hydrate_article(article) for article in ARTICLES}
    for article in load_editable_articles():
        merged[article["slug"]] = article
    return sorted(merged.values(), key=_article_sort_key, reverse=True)


def upsert_editable_article(article: dict) -> None:
    editable = {item["slug"]: item for item in load_editable_articles()}
    editable[article["slug"]] = _hydrate_article(article)
    save_editable_articles(list(editable.values()))


def get_articles() -> list[dict]:
    return [
        article
        for article in sorted(get_all_editorial_articles(), key=_article_sort_key, reverse=True)
        if article.get("editorial_status") == "publicada"
    ]


def get_article(slug: str) -> dict | None:
    article = next((article for article in get_all_editorial_articles() if article["slug"] == slug), None)
    if not article or article.get("editorial_status") != "publicada":
        return None
    return article


def get_editorial_article(slug: str) -> dict | None:
    return next((article for article in get_all_editorial_articles() if article["slug"] == slug), None)


def get_category(slug: str) -> dict | None:
    return next((category for category in CATEGORIES if category["slug"] == slug), None)


def get_articles_by_category(slug: str) -> list[dict]:
    return [article for article in get_articles() if article["category_slug"] == slug]


def get_featured_article() -> dict:
    return get_articles()[0]


def get_related_articles(article: dict, limit: int = 3) -> list[dict]:
    related = [
        item
        for item in get_articles()
        if item["slug"] != article["slug"]
        and (item["category_slug"] == article["category_slug"] or set(item["tags"]) & set(article["tags"]))
    ]
    return related[:limit]


def get_ad(position: str) -> dict | None:
    return next((ad for ad in ADS if ad["position"] == position and ad["status"] == "ativo"), None)

import os
from pathlib import Path


class Settings:
    app_name = "Jefferson Vorpagel AI"
    default_leads_file = "/tmp/leads.jsonl" if os.getenv("VERCEL") else "instance/leads.jsonl"
    default_articles_file = "/tmp/articles.json" if os.getenv("VERCEL") else "instance/articles.json"
    leads_file = Path(os.getenv("LEADS_FILE", default_leads_file))
    articles_file = Path(os.getenv("ARTICLES_FILE", default_articles_file))
    advertisers_file = Path(os.getenv("ADVERTISERS_FILE", "instance/advertisers.jsonl"))
    whatsapp_phone = os.getenv("WHATSAPP_PHONE", "5545998287556")
    notification_webhook_url = os.getenv("NOTIFICATION_WEBHOOK_URL")
    admin_username = os.getenv("ADMIN_USERNAME", "jefferson")
    admin_password = os.getenv("ADMIN_PASSWORD", "trocar-esta-senha")
    cron_secret = os.getenv("CRON_SECRET", "")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    newsbot_daily_limit = int(os.getenv("NEWSBOT_DAILY_LIMIT", "3"))
    newsbot_sources = os.getenv(
        "NEWSBOT_SOURCES",
        ",".join(
            [
                "https://www.technologyreview.com/feed/",
                "https://venturebeat.com/category/ai/feed/",
                "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            ]
        ),
    )
    site_url = os.getenv("SITE_URL", "http://127.0.0.1:8000")
    ga_measurement_id = os.getenv("GA_MEASUREMENT_ID", "")
    meta_pixel_id = os.getenv("META_PIXEL_ID", "")
    linkedin_partner_id = os.getenv("LINKEDIN_PARTNER_ID", "")
    adsense_client_id = os.getenv("ADSENSE_CLIENT_ID", "")
    adsense_top_slot = os.getenv("ADSENSE_TOP_SLOT", "")
    adsense_feed_slot = os.getenv("ADSENSE_FEED_SLOT", "")
    adsense_article_slot = os.getenv("ADSENSE_ARTICLE_SLOT", "")
    adsense_article_end_slot = os.getenv("ADSENSE_ARTICLE_END_SLOT", "")
    adsense_sidebar_slot = os.getenv("ADSENSE_SIDEBAR_SLOT", "")


settings = Settings()

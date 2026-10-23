"""Publicacao segura de Reels pela API oficial do Instagram."""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    import certifi
except ImportError:  # mensagem clara exibida antes de acessar a API
    certifi = None


class InstagramAPIError(RuntimeError):
    """Erro retornado pela API do Instagram."""


def carregar_env(caminho: Path = Path(".env")) -> None:
    """Carrega um .env simples sem sobrescrever variaveis existentes."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))


class InstagramReels:
    def __init__(self, access_token: str, instagram_user_id: str, api_version: str) -> None:
        self.access_token = access_token
        self.instagram_user_id = instagram_user_id
        self.base_url = f"https://graph.instagram.com/{api_version}"

    def _requisicao(self, metodo: str, endpoint: str, dados: dict | None = None) -> dict:
        if certifi is None:
            raise InstagramAPIError(
                "Dependencia ausente. Execute: python3 -m pip install -r requirements.txt"
            )
        valores = {**(dados or {}), "access_token": self.access_token}
        corpo = urllib.parse.urlencode(valores).encode() if metodo == "POST" else None
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if metodo == "GET":
            url = f"{url}?{urllib.parse.urlencode(valores)}"
        requisicao = urllib.request.Request(url, data=corpo, method=metodo)
        try:
            contexto_ssl = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(
                requisicao, timeout=60, context=contexto_ssl
            ) as resposta:
                return json.loads(resposta.read().decode("utf-8"))
        except urllib.error.HTTPError as erro:
            detalhe = erro.read().decode("utf-8", errors="replace")
            try:
                mensagem = json.loads(detalhe)["error"]["message"]
            except (KeyError, TypeError, json.JSONDecodeError):
                mensagem = detalhe or str(erro)
            raise InstagramAPIError(mensagem) from erro
        except urllib.error.URLError as erro:
            raise InstagramAPIError(f"Falha de conexao: {erro.reason}") from erro

    def criar_container(self, video_url: str, legenda: str) -> str:
        resposta = self._requisicao(
            "POST",
            f"{self.instagram_user_id}/media",
            {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": legenda,
                "share_to_feed": "true",
            },
        )
        return str(resposta["id"])

    def aguardar_processamento(self, container_id: str, limite_segundos: int = 600) -> None:
        inicio = time.monotonic()
        while time.monotonic() - inicio < limite_segundos:
            resposta = self._requisicao(
                "GET", container_id, {"fields": "status_code,status"}
            )
            status = resposta.get("status_code")
            if status == "FINISHED":
                return
            if status in {"ERROR", "EXPIRED"}:
                raise InstagramAPIError(
                    f"Processamento terminou com status {status}: "
                    f"{resposta.get('status', 'sem detalhes')}"
                )
            time.sleep(10)
        raise InstagramAPIError("Tempo limite ao processar o video (10 minutos).")

    def publicar(self, container_id: str) -> str:
        resposta = self._requisicao(
            "POST",
            f"{self.instagram_user_id}/media_publish",
            {"creation_id": container_id},
        )
        return str(resposta["id"])


def cliente_do_ambiente() -> InstagramReels:
    carregar_env()
    token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    usuario = os.getenv("INSTAGRAM_USER_ID", "")
    versao = os.getenv("META_API_VERSION", "v24.0")
    faltando = [
        nome
        for nome, valor in {
            "INSTAGRAM_ACCESS_TOKEN": token,
            "INSTAGRAM_USER_ID": usuario,
        }.items()
        if not valor
    ]
    if faltando:
        raise ValueError(f"Configure no arquivo .env: {', '.join(faltando)}")
    return InstagramReels(token, usuario, versao)

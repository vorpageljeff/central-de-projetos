"""Publicador de Reels para a conta @satirinhas.ia."""

from __future__ import annotations

import argparse
import sys
from instagram_reels import InstagramAPIError, cliente_do_ambiente


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publica um video como Reel.")
    parser.add_argument("video_url", help="URL HTTPS publica e direta do MP4/MOV")
    parser.add_argument("--legenda", default="", help="Legenda e hashtags do Reel")
    parser.add_argument(
        "--publicar",
        action="store_true",
        help="Confirma a publicacao real (sem isso, apenas valida os dados)",
    )
    return parser.parse_args()



def main() -> None:
    args = argumentos()
    if not args.video_url.startswith("https://"):
        raise ValueError("A URL do video precisa comecar com https://")
    if not args.publicar:
        print("Modo de teste: nenhum conteudo foi publicado.")
        print(f"Video: {args.video_url}")
        print(f"Legenda: {args.legenda or '(sem legenda)'}")
        print("Use --publicar quando estiver pronto para enviar o Reel.")
        return

    cliente = cliente_do_ambiente()
    print("Enviando o Reel para processamento...")
    container_id = cliente.criar_container(args.video_url, args.legenda)
    cliente.aguardar_processamento(container_id)
    media_id = cliente.publicar(container_id)
    print(f"Reel publicado com sucesso. ID: {media_id}")


if __name__ == "__main__":
    try:
        main()
    except (InstagramAPIError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        sys.exit(1)

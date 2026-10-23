"""Gera um video vertical dinamico para Shopee Video e redes sociais."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import textwrap
import urllib.parse
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


LARGURA = 720
ALTURA = 1280
FPS = 30
DURACAO = 12


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cria um MP4 9:16 com movimento para divulgar um produto."
    )
    parser.add_argument("--imagem", required=True, type=Path, help="Imagem autorizada do produto")
    parser.add_argument("--produto", required=True, help="Nome curto do produto")
    parser.add_argument("--preco", default="", help="Preco atual, se confirmado")
    parser.add_argument(
        "--beneficio",
        action="append",
        default=[],
        help="Beneficio curto; pode ser repetido ate tres vezes",
    )
    parser.add_argument("--link-afiliado", default="", help="Link que sera anexado no app")
    parser.add_argument(
        "--audio",
        type=Path,
        help="Narração ou trilha para incluir no vídeo (AIFF, WAV, MP3 ou M4A)",
    )
    parser.add_argument("--saida", type=Path, default=Path("outputs/shopee-video.mp4"))
    return parser.parse_args()


def fonte(tamanho: int, negrito: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    nomes = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if negrito else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if negrito else "/Library/Fonts/Arial.ttf",
    ]
    for nome in nomes:
        if Path(nome).exists():
            return ImageFont.truetype(nome, tamanho)
    return ImageFont.load_default()


def conter(imagem: Image.Image, largura: int, altura: int) -> Image.Image:
    copia = imagem.convert("RGBA")
    copia.thumbnail((largura, altura), Image.Resampling.LANCZOS)
    return copia


def centralizar_texto(
    desenho: ImageDraw.ImageDraw,
    texto: str,
    y: int,
    tamanho: int,
    cor: str,
    largura_linha: int,
    negrito: bool = True,
) -> int:
    tipo = fonte(tamanho, negrito)
    linhas = textwrap.wrap(texto, width=largura_linha) or [""]
    altura_linha = int(tamanho * 1.15)
    for linha in linhas:
        caixa = desenho.textbbox((0, 0), linha, font=tipo)
        x = (LARGURA - (caixa[2] - caixa[0])) // 2
        desenho.text((x, y), linha, font=tipo, fill=cor)
        y += altura_linha
    return y


def fundo_gradiente() -> Image.Image:
    quadro = Image.new("RGB", (LARGURA, ALTURA))
    pixels = quadro.load()
    inicio = (255, 111, 20)
    fim = (255, 244, 220)
    for y in range(ALTURA):
        proporcao = y / (ALTURA - 1)
        cor = tuple(int(a + (b - a) * proporcao) for a, b in zip(inicio, fim))
        for x in range(LARGURA):
            pixels[x, y] = cor
    return quadro


def gerar_quadro(
    base: Image.Image,
    produto: Image.Image,
    indice: int,
    nome: str,
    preco: str,
    beneficios: list[str],
    link_afiliado: str,
) -> Image.Image:
    t = indice / FPS
    quadro = base.copy().convert("RGBA")
    desenho = ImageDraw.Draw(quadro)

    # Elementos sempre em movimento para o video nao ser um quadro estatico.
    for n, cor in enumerate(("#20CFC5", "#13213C", "#FFFFFF")):
        x = int(60 + n * 260 + 35 * math.sin(t * 1.7 + n))
        y = int(190 + n * 310 + 28 * math.cos(t * 1.4 + n))
        raio = 34 + n * 7
        desenho.ellipse((x - raio, y - raio, x + raio, y + raio), fill=cor)

    escala = 0.90 + 0.08 * math.sin(t * math.pi / 2)
    produto_animado = produto.resize(
        (int(produto.width * escala), int(produto.height * escala)),
        Image.Resampling.LANCZOS,
    )
    x_produto = (LARGURA - produto_animado.width) // 2
    y_produto = int(315 + 18 * math.sin(t * 2.2))

    sombra = Image.new("RGBA", quadro.size, (0, 0, 0, 0))
    d_sombra = ImageDraw.Draw(sombra)
    d_sombra.rounded_rectangle((68, 270, 652, 900), radius=46, fill=(0, 0, 0, 35))
    quadro.alpha_composite(sombra)
    desenho = ImageDraw.Draw(quadro)
    desenho.rounded_rectangle((56, 258, 640, 888), radius=46, fill="#FFF9EC")
    quadro.alpha_composite(produto_animado, (x_produto, y_produto))
    desenho = ImageDraw.Draw(quadro)

    if t < 2.5:
        centralizar_texto(desenho, "OLHA ESSE ACHADINHO!", 70, 52, "#FFFFFF", 22)
    elif t < 8.5:
        centralizar_texto(desenho, nome.upper(), 70, 44, "#FFFFFF", 25)
    else:
        centralizar_texto(desenho, "TOQUE NO PRODUTO", 70, 50, "#FFFFFF", 22)
        centralizar_texto(desenho, "E CONFIRA A OFERTA", 132, 38, "#13213C", 26)
        if link_afiliado:
            url = urllib.parse.urlsplit(link_afiliado)
            link_visivel = f"{url.netloc}{url.path}"
            centralizar_texto(desenho, link_visivel, 210, 23, "#13213C", 46, False)

    y_texto = 930
    if preco:
        y_texto = centralizar_texto(desenho, preco, y_texto, 58, "#13213C", 18)
    itens = beneficios[:3] or ["Pratico", "Bonito", "Vale conferir"]
    for item in itens:
        y_texto = centralizar_texto(desenho, f"• {item}", y_texto + 8, 30, "#13213C", 32, False)

    assinatura = "@satirinhas.ia"
    tipo = fonte(23, True)
    caixa = desenho.textbbox((0, 0), assinatura, font=tipo)
    desenho.text(((LARGURA - caixa[2]) // 2, 1230), assinatura, font=tipo, fill="#13213C")
    return quadro.convert("RGB")


def main() -> None:
    args = argumentos()
    if not args.imagem.exists():
        raise SystemExit(f"Imagem nao encontrada: {args.imagem}")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    produto = conter(Image.open(args.imagem), 500, 500)
    base = fundo_gradiente()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if args.audio and not args.audio.exists():
        raise SystemExit(f"Audio nao encontrado: {args.audio}")

    saida_video = (
        args.saida.with_name(f"{args.saida.stem}.sem-audio.mp4")
        if args.audio
        else args.saida
    )
    comando = [
        ffmpeg,
        "-y",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{LARGURA}x{ALTURA}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(saida_video),
    ]
    processo = subprocess.Popen(comando, stdin=subprocess.PIPE)
    assert processo.stdin is not None
    try:
        for indice in range(FPS * DURACAO):
            quadro = gerar_quadro(
                base,
                produto,
                indice,
                args.produto,
                args.preco,
                args.beneficio,
                args.link_afiliado,
            )
            processo.stdin.write(quadro.tobytes())
    finally:
        processo.stdin.close()
    retorno = processo.wait()
    if retorno:
        raise SystemExit(f"Falha ao gerar video; ffmpeg retornou {retorno}.")

    if args.audio:
        comando_audio = [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(saida_video),
            "-i",
            str(args.audio),
            "-filter_complex",
            f"[1:a]apad=pad_dur={DURACAO},atrim=0:{DURACAO},"
            f"afade=t=in:st=0:d=0.15,afade=t=out:st={DURACAO - 0.5}:d=0.5[a]",
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-t",
            str(DURACAO),
            "-movflags",
            "+faststart",
            str(args.saida),
        ]
        resultado = subprocess.run(comando_audio, check=False)
        saida_video.unlink(missing_ok=True)
        if resultado.returncode:
            raise SystemExit(
                f"Falha ao incluir audio; ffmpeg retornou {resultado.returncode}."
            )

    manifesto = {
        "video": str(args.saida.resolve()),
        "produto": args.produto,
        "preco": args.preco,
        "beneficios": args.beneficio[:3],
        "link_afiliado": args.link_afiliado,
        "audio": str(args.audio.resolve()) if args.audio else "",
        "publicacao": "No app Shopee: Lives e Videos > criar > Proximo > Adicionar Produto > postar",
    }
    args.saida.with_suffix(".json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Video criado: {args.saida}")
    print(f"Dados da publicacao: {args.saida.with_suffix('.json')}")


if __name__ == "__main__":
    main()

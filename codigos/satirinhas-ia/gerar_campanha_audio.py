"""Gera em lote vídeos verticais narrados a partir das ofertas selecionadas."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
MANIFESTO = BASE / "outputs" / "shopee" / "campanha-4-produtos.json"
PASTA_AUDIO = BASE / "outputs" / "shopee" / "audio"

NARRACOES = {
    "porta-temperos": (
        "Olha esse achadinho para organizar a cozinha. "
        "São dezesseis potes de vidro em uma base giratória, "
        "para deixar os temperos à mão. Toque no produto e confira a oferta."
    ),
    "caneca-mixer": (
        "Chega de colher para misturar café, leite ou chocolate. "
        "Essa caneca mixer tem misturador magnético, é recarregável e vem com tampa. "
        "Toque no produto e confira a oferta."
    ),
    "escova-eletrica": (
        "Quer facilitar a faxina? Essa escova elétrica é sem fio, "
        "tem cinco acessórios e ajuda em diferentes tarefas de limpeza. "
        "Toque no produto e confira a oferta."
    ),
    "kit-21-potes": (
        "Olha esse kit para colocar ordem na cozinha. "
        "São vinte e um potes para guardar mantimentos e organizar os armários. "
        "Toque no produto e confira a oferta."
    ),
}


def main() -> None:
    produtos = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    PASTA_AUDIO.mkdir(parents=True, exist_ok=True)

    for numero, produto in enumerate(produtos, 1):
        slug = produto["slug"]
        audio = PASTA_AUDIO / f"{slug}.aiff"
        video = BASE / "outputs" / "shopee" / f"{slug}-com-audio.mp4"
        narracao = NARRACOES[slug]

        print(f"[{numero}/{len(produtos)}] Gerando narração: {slug}", flush=True)
        subprocess.run(
            ["say", "-v", "Luciana", "-r", "205", "-o", str(audio), narracao],
            check=True,
        )

        comando = [
            sys.executable,
            str(BASE / "shopee_video.py"),
            "--imagem",
            str(BASE / produto["imagem"]),
            "--produto",
            produto["produto"],
            "--preco",
            produto["preco"],
            "--link-afiliado",
            produto["link_afiliado"],
            "--audio",
            str(audio),
            "--saida",
            str(video),
        ]
        for beneficio in produto["beneficios"]:
            comando.extend(["--beneficio", beneficio])
        print(f"[{numero}/{len(produtos)}] Montando vídeo: {slug}", flush=True)
        subprocess.run(comando, check=True, cwd=BASE)
        produto["video_com_audio"] = str(video.relative_to(BASE))
        produto["audio_narracao"] = str(audio.relative_to(BASE))
        produto["narracao"] = narracao

    MANIFESTO.write_text(
        json.dumps(produtos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Campanha com áudio concluída.", flush=True)


if __name__ == "__main__":
    main()

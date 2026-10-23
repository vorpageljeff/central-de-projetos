"""Abre o Portal de Afiliados em um Chrome isolado do navegador pessoal."""

from __future__ import annotations

import subprocess
from pathlib import Path


CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PORTAL = "https://affiliate.shopee.com.br/"
PERFIL = Path(__file__).resolve().parent / ".browser" / "shopee"


def main() -> None:
    if not CHROME.exists():
        raise SystemExit("Google Chrome nao encontrado em /Applications.")

    PERFIL.mkdir(parents=True, exist_ok=True)
    subprocess.Popen(
        [
            str(CHROME),
            f"--user-data-dir={PERFIL}",
            "--profile-directory=Default",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-debugging-address=127.0.0.1",
            "--remote-debugging-port=9225",
            "--remote-allow-origins=http://127.0.0.1:9225",
            f"--app={PORTAL}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print("Portal aberto no Chrome exclusivo da Shopee.")


if __name__ == "__main__":
    main()

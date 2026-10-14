#!/usr/bin/env python3
"""Obtem e valida o MNIST original no formato IDX+gzip, sem pacotes extras.

Uso: python Dia2/Dataset-MNIST/download_mnist.py
Nao implementa leitura para treinamento, redes neurais ou classificacao.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

BASE_URLS = (
    "https://storage.googleapis.com/cvdf-datasets/mnist/",
    "https://raw.githubusercontent.com/fgnt/mnist/master/",
)
# Nomes, tamanhos em bytes e MD5 publicados pelo ecossistema MNIST/torchvision.
FILES = {
    "train-images-idx3-ubyte.gz": (9912422, "f68b3c2dcbeaaa9fbdd348bbdeb94873", (2051, 60000, 28, 28)),
    "train-labels-idx1-ubyte.gz": (28881, "d53e105ee54ea40749a09fcbcd1e9432", (2049, 60000)),
    "t10k-images-idx3-ubyte.gz": (1648877, "9fb629c4189551a2d022fa330f9573f3", (2051, 10000, 28, 28)),
    "t10k-labels-idx1-ubyte.gz": (4542, "ec29112dd5afa0611ce80d1b7f02629c", (2049, 10000)),
}


def verify(path: Path, name: str) -> None:
    size, expected_md5, idx_header = FILES[name]
    if path.stat().st_size != size:
        raise ValueError(f"tamanho inesperado em {name}")
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != expected_md5:
        raise ValueError(f"checksum inesperado em {name}")
    with gzip.open(path, "rb") as stream:
        header = stream.read(4 * len(idx_header))
        if len(header) != 4 * len(idx_header):
            raise ValueError(f"cabecalho IDX incompleto em {name}")
        observed = struct.unpack(">" + "I" * len(idx_header), header)
        if observed != idx_header:
            raise ValueError(f"cabecalho IDX inesperado em {name}: {observed}")


def download_one(name: str, directory: Path) -> None:
    target = directory / name
    if target.is_file():
        try:
            verify(target, name)
            print(f"OK (ja presente): {name}")
            return
        except ValueError:
            target.unlink()
    errors: list[str] = []
    for base in BASE_URLS:
        tmp_name = None
        try:
            with tempfile.NamedTemporaryFile(dir=directory, prefix=".mnist-", delete=False) as temp:
                tmp_name = Path(temp.name)
                with urlopen(base + name, timeout=120) as response:
                    while block := response.read(1024 * 1024):
                        temp.write(block)
            verify(tmp_name, name)
            tmp_name.replace(target)
            print(f"OK (obtido e verificado): {name}")
            return
        except (HTTPError, URLError, OSError, ValueError) as exc:
            errors.append(f"{base} — {exc}")
        finally:
            if tmp_name is not None and tmp_name.exists():
                tmp_name.unlink()
    raise RuntimeError(f"Falha ao obter {name}:\n" + "\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Baixar MNIST IDX+gzip e conferir integridade.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "data",
        help="Diretorio para os quatro arquivos compactados.",
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        for name in FILES:
            download_one(name, args.output)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"MNIST validado: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

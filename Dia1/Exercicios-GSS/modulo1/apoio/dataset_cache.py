"""Download and cache the small public datasets used by the demonstrations."""

from __future__ import annotations

from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

# This module lives in modulo1/apoio. Keep the existing repository
# cache when reorganizing code, so offline lessons reuse downloaded datasets.
CACHE_DIRECTORY = Path(__file__).resolve().parents[2] / ".cache" / "datasets"


def load_dataset_archive(url: str, cache_name: str, user_agent: str) -> bytes:
    """Return a cached archive or download it once into the repository cache."""
    archive_path = CACHE_DIRECTORY / cache_name
    if archive_path.exists():
        return archive_path.read_bytes()

    request = Request(url, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=30) as response:
            archive_bytes = response.read()
    except (OSError, TimeoutError, URLError) as error:
        raise RuntimeError(
            f"Nao foi possivel descarregar {cache_name}; verifica a ligacao a "
            f"internet. O ficheiro tambem nao existe em {archive_path}."
        ) from error

    try:
        CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        archive_path.write_bytes(archive_bytes)
    except OSError as error:
        raise RuntimeError(
            f"O dataset foi descarregado, mas nao pode ser guardado em {archive_path}."
        ) from error
    return archive_bytes

"""
engine/seen.py

Tracks which output_file names have already been generated.
Storage: a single plain-text file, one filename per line, append-only.

Safe across crashes — a video is only marked seen after it has been
fully copied to output_dir, so a re-run never loses or duplicates progress.

To migrate to a database later, replace this module with one that
implements the same three functions: load / add / list_all.
"""

from __future__ import annotations

from pathlib import Path

# In-memory cache keyed by resolved file path string, avoids re-reading the
# file on every contains() check within a single run.
_cache: dict[str, set[str]] = {}


def _key(path: Path) -> str:
    return str(path)


def load(path: Path) -> set[str]:
    """Return the full set of known output_file names. Uses cache."""
    k = _key(path)
    if k not in _cache:
        if not path.exists():
            _cache[k] = set()
        else:
            lines = path.read_text(encoding="utf-8").splitlines()
            _cache[k] = {line.strip() for line in lines if line.strip()}
    return _cache[k]


def contains(path: Path, output_file: str) -> bool:
    return output_file in load(path)


def add(path: Path, output_file: str) -> None:
    """Append output_file to the seen file. Idempotent."""
    existing = load(path)
    if output_file in existing:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    _cache[_key(path)].add(output_file)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{output_file}\n")


def list_all(path: Path) -> list[str]:
    """Return all registered filenames sorted alphabetically."""
    return sorted(load(path))

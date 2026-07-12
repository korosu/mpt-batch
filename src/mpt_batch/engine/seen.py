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

_cache: dict[Path, set[str]] = {}


def load(path: Path) -> set[str]:
    """Return the full set of known output_file names. Cached per path."""
    if path not in _cache:
        if not path.exists():
            _cache[path] = set()
        else:
            lines = path.read_text(encoding="utf-8").splitlines()
            _cache[path] = {line.strip() for line in lines if line.strip()}
    return _cache[path]


def contains(path: Path, output_file: str) -> bool:
    return output_file in load(path)


def add(path: Path, output_file: str) -> None:
    """Append output_file to the seen file. Idempotent."""
    seen_set = load(path)
    if output_file in seen_set:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    seen_set.add(output_file)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{output_file}\n")


def list_all(path: Path) -> list[str]:
    """Return all registered filenames sorted alphabetically."""
    return sorted(load(path))

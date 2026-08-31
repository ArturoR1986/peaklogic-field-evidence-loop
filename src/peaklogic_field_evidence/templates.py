from __future__ import annotations

import json
from pathlib import Path
from .schemas import ProofPoint, ProofTemplate

TEMPLATE_DIR = Path(__file__).parent / "templates"


def load_template(path: Path) -> ProofTemplate:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return ProofTemplate(
        id=raw["id"],
        version=raw["version"],
        task_type=raw["task_type"],
        quality_critical=bool(raw["quality_critical"]),
        keywords=tuple(raw.get("keywords", [])),
        proof_points=tuple(ProofPoint(**pp) for pp in raw["proof_points"]),
    )


def registry() -> tuple[ProofTemplate, ...]:
    return tuple(load_template(p) for p in sorted(TEMPLATE_DIR.glob("*.json")))


def match_template(task_text: str) -> ProofTemplate | None:
    normalized = task_text.casefold()
    scored: list[tuple[int, ProofTemplate]] = []
    for template in registry():
        score = sum(1 for keyword in template.keywords if keyword.casefold() in normalized)
        if score:
            scored.append((score, template))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1].id))
    return scored[0][1]

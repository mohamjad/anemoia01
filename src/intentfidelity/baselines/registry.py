from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BaselineSpec:
    method_id: str
    name: str
    category: str
    status: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {
            "method_id": self.method_id,
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "description": self.description,
        }


BASELINES: tuple[BaselineSpec, ...] = (
    BaselineSpec(
        method_id="identity",
        name="Identity",
        category="alignment",
        status="implemented",
        description="Pass-through reference for already aligned feature spaces.",
    ),
    BaselineSpec(
        method_id="session_centering",
        name="Session centering",
        category="alignment",
        status="implemented",
        description="Subtract session-level feature centroids before evaluation.",
    ),
    BaselineSpec(
        method_id="procrustes",
        name="Procrustes",
        category="alignment",
        status="placeholder",
        description="Rigid alignment baseline for matched feature spaces.",
    ),
    BaselineSpec(
        method_id="cca",
        name="CCA",
        category="alignment",
        status="placeholder",
        description="Canonical-correlation alignment baseline.",
    ),
    BaselineSpec(
        method_id="whitening_coloring",
        name="Whitening-coloring",
        category="alignment",
        status="implemented",
        description="Distribution matching through whitening and recoloring.",
    ),
    BaselineSpec(
        method_id="supervised_fine_tune",
        name="Supervised fine-tune",
        category="adaptive_decoder",
        status="placeholder",
        description="Task-supervised adaptation baseline for later ingestion paths.",
    ),
    BaselineSpec(
        method_id="lm_heavy",
        name="LM-heavy",
        category="language_prior",
        status="placeholder",
        description="High language-prior decoder variant for attribution checks.",
    ),
    BaselineSpec(
        method_id="lm_light",
        name="LM-light",
        category="language_prior",
        status="placeholder",
        description="Lower language-prior decoder variant for attribution checks.",
    ),
)


def list_baselines() -> tuple[BaselineSpec, ...]:
    return BASELINES


def list_implemented_baselines() -> tuple[BaselineSpec, ...]:
    return tuple(baseline for baseline in BASELINES if baseline.status == "implemented")


def get_baseline(method_id: str) -> BaselineSpec:
    for baseline in BASELINES:
        if baseline.method_id == method_id:
            return baseline
    raise KeyError(f"unknown baseline method_id: {method_id}")

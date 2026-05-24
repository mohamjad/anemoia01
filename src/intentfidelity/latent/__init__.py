"""Latent neural-state probe utilities."""

from intentfidelity.latent.backends import LatentBackend, fit_latent_probe
from intentfidelity.latent.cebra_backend import (
    CebraLatentProbeConfig,
    fit_cebra_latent_probe,
)
from intentfidelity.latent.pca import fit_pca_latent_probe
from intentfidelity.latent.reports import (
    LatentDriftReport,
    LatentProbeConfig,
    LatentSample,
    render_latent_drift_markdown,
)

__all__ = [
    "CebraLatentProbeConfig",
    "LatentBackend",
    "LatentDriftReport",
    "LatentProbeConfig",
    "LatentSample",
    "fit_cebra_latent_probe",
    "fit_latent_probe",
    "fit_pca_latent_probe",
    "render_latent_drift_markdown",
]

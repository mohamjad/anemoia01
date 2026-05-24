from intentfidelity.baselines import LabeledExample
from intentfidelity.labels import Prediction, WeakTarget
from intentfidelity.latent import (
    LatentProbeConfig,
    fit_pca_latent_probe,
    render_latent_drift_markdown,
)


def test_fit_pca_latent_probe_reports_neural_feature_state_drift() -> None:
    train = (
        LabeledExample("train-a", "A", (0.0, 0.0, 0.0), "s1"),
        LabeledExample("train-b", "B", (2.0, 0.0, 0.0), "s1"),
        LabeledExample("train-c", "A", (0.0, 2.0, 0.0), "s1"),
    )
    test = (
        LabeledExample("s0", "A", (0.0, 0.0, 0.0), "s1"),
        LabeledExample("s1", "B", (2.0, 0.0, 0.0), "s1"),
        LabeledExample("s2", "A", (0.0, 2.0, 0.0), "s2"),
    )
    targets = (
        WeakTarget("s0", {"A": 1.0, "B": 0.0}, "prompt"),
        WeakTarget("s1", {"A": 0.0, "B": 1.0}, "prompt"),
        WeakTarget("s2", {"A": 1.0, "B": 0.0}, "prompt"),
    )
    predictions = (
        Prediction("s0", {"A": 0.8, "B": 0.2}, "decoder"),
        Prediction("s1", {"A": 0.2, "B": 0.8}, "decoder"),
        Prediction("s2", {"A": 0.5, "B": 0.5}, "decoder"),
    )

    report = fit_pca_latent_probe(
        train,
        test,
        targets,
        predictions,
        config=LatentProbeConfig(n_components=2),
    )

    assert report.config.method_id == "pca_svd_latent_probe"
    assert report.fit_sample_count == 3
    assert report.evaluated_sample_count == 3
    assert report.input_dimension == 3
    assert report.latent_dimension == 2
    assert report.latent_mean_step_size > 0.0
    assert report.latent_centroid_shift > 0.0
    assert len(report.samples) == 3


def test_render_latent_drift_markdown_states_scope() -> None:
    train = (
        LabeledExample("train-a", "A", (0.0, 0.0), "s1"),
        LabeledExample("train-b", "B", (1.0, 0.0), "s1"),
    )
    target = WeakTarget("s0", {"A": 1.0, "B": 0.0}, "prompt")
    prediction = Prediction("s0", {"A": 0.9, "B": 0.1}, "decoder")

    report = fit_pca_latent_probe(
        train,
        (LabeledExample("s0", "A", (0.0, 0.0), "s1"),),
        (target,),
        (prediction,),
    )

    markdown = render_latent_drift_markdown(report)

    assert "Latent Drift Report" in markdown
    assert "neural feature-state probe" in markdown
    assert "direct intent readout" in markdown

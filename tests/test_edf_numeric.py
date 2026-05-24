import pytest

from intentfidelity.ingest.edf import EdfParseError, read_edf_numeric_signals

from edf_fixtures import write_numeric_edf


def test_read_edf_numeric_signals_extracts_requested_labels(tmp_path) -> None:
    path = write_numeric_edf(
        tmp_path / "sample.edf",
        {
            "StimulusBegin": (0, 1, 1),
            "CurrentTarget": (0, 2, 2),
            "Ignored": (9, 9, 9),
        },
    )

    signals = read_edf_numeric_signals(
        path,
        labels=("StimulusBegin", "CurrentTarget"),
    )

    assert signals.path == path
    assert signals.data_record_count == 1
    assert signals.sample_rate("CurrentTarget") == pytest.approx(3.0)
    assert signals.signals == {
        "StimulusBegin": pytest.approx((0.0, 1.0, 1.0)),
        "CurrentTarget": pytest.approx((0.0, 2.0, 2.0)),
    }


def test_read_edf_numeric_signals_reports_missing_requested_label(tmp_path) -> None:
    path = write_numeric_edf(tmp_path / "sample.edf", {"CurrentTarget": (1,)})

    with pytest.raises(EdfParseError, match="missing requested EDF signals"):
        read_edf_numeric_signals(path, labels=("StimulusBegin",))

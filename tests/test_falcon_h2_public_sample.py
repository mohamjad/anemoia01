import os
from pathlib import Path

import pytest

from intentfidelity.protocols import falcon_h2_baseline_eval


@pytest.mark.skipif(
    not os.environ.get("FALCON_H2_SAMPLE_NWB"),
    reason="set FALCON_H2_SAMPLE_NWB to run against a downloaded public H2 NWB file",
)
def test_public_falcon_h2_sample_runs_baseline_eval() -> None:
    result = falcon_h2_baseline_eval(Path(os.environ["FALCON_H2_SAMPLE_NWB"]))

    assert result.dataset_id == "falcon_h2"
    assert len(result.method_scores) == 2


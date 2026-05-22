from intentfidelity.baselines.examples import LabeledExample
from intentfidelity.baselines.io import read_labeled_examples_csv, write_labeled_examples_csv


def test_labeled_examples_csv_round_trip(tmp_path) -> None:
    examples = (
        LabeledExample("s1", "a", [1.0, 2.0], "session-1"),
        LabeledExample("s2", "b", [3.0, 4.0], "session-2"),
    )
    path = tmp_path / "examples.csv"

    write_labeled_examples_csv(examples, path)

    assert read_labeled_examples_csv(path) == examples


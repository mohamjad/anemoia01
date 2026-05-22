from intentfidelity.baselines.synthetic import synthetic_shift_examples


def test_synthetic_shift_examples_return_train_and_test_sets() -> None:
    train, test = synthetic_shift_examples()

    assert len(train) == 4
    assert len(test) == 2
    assert {example.session_id for example in train} == {"session-1"}


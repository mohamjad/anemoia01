from intentfidelity.metrics import MethodScore
from intentfidelity.protocols.schemas import ProtocolType, selection_result


def test_selection_result_uses_selection_protocol_type() -> None:
    result = selection_result(
        "bigp3bci",
        (MethodScore("decoder", 0.1, 0.2),),
        target_type="p300_selection_proxy",
    )

    assert result.protocol == ProtocolType.SELECTION
    assert result.primary_metric == "selection_intent_fidelity_loss"
    assert result.metadata["target_type"] == "p300_selection_proxy"

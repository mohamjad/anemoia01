from __future__ import annotations

from pathlib import Path
import struct


def write_numeric_edf(
    path: Path,
    signals: dict[str, tuple[int, ...]],
    *,
    record_duration: float = 1.0,
) -> Path:
    if not signals:
        raise ValueError("signals cannot be empty")
    sample_counts = {len(values) for values in signals.values()}
    if len(sample_counts) != 1:
        raise ValueError("test EDF signals must have equal sample counts")

    path.parent.mkdir(parents=True, exist_ok=True)
    signal_count = len(signals)
    header_bytes = 256 + signal_count * 256
    samples_per_record = sample_counts.pop()
    fixed_header = b"".join(
        (
            _field("0", 8),
            _field("test patient", 80),
            _field("test recording", 80),
            _field("01.01.26", 8),
            _field("01.01.01", 8),
            _field(str(header_bytes), 8),
            _field("", 44),
            _field("1", 8),
            _field(str(record_duration), 8),
            _field(str(signal_count), 4),
        )
    )

    labels = tuple(signals)
    variable_header = b"".join(
        (
            _fields(labels, 16),
            _fields(["" for _ in labels], 80),
            _fields(["" for _ in labels], 8),
            _fields(["-32768" for _ in labels], 8),
            _fields(["32767" for _ in labels], 8),
            _fields(["-32768" for _ in labels], 8),
            _fields(["32767" for _ in labels], 8),
            _fields(["" for _ in labels], 80),
            _fields([str(samples_per_record) for _ in labels], 8),
            _fields(["" for _ in labels], 32),
        )
    )

    data = b"".join(
        struct.pack(f"<{samples_per_record}h", *signals[label]) for label in labels
    )
    path.write_bytes(fixed_header + variable_header + data)
    return path


def _fields(values, width: int) -> bytes:
    return b"".join(_field(str(value), width) for value in values)


def _field(value: str, width: int) -> bytes:
    encoded = value.encode("ascii")
    if len(encoded) > width:
        encoded = encoded[:width]
    return encoded.ljust(width, b" ")

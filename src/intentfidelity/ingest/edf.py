from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Iterable


class EdfParseError(ValueError):
    """Raised when an EDF file cannot be parsed by the local numeric reader."""


@dataclass(frozen=True)
class EdfSignalInfo:
    label: str
    samples_per_record: int
    physical_min: float
    physical_max: float
    digital_min: int
    digital_max: int

    @property
    def scale(self) -> float:
        digital_span = self.digital_max - self.digital_min
        if digital_span == 0:
            raise EdfParseError(f"digital range is empty for EDF signal: {self.label}")
        return (self.physical_max - self.physical_min) / digital_span


@dataclass(frozen=True)
class EdfNumericSignals:
    path: Path
    data_record_count: int
    data_record_duration: float
    signal_info: tuple[EdfSignalInfo, ...]
    signals: dict[str, tuple[float, ...]]

    def require_signal(self, label: str) -> tuple[float, ...]:
        try:
            return self.signals[label]
        except KeyError as exc:
            raise EdfParseError(f"missing EDF signal: {label}") from exc

    def sample_rate(self, label: str) -> float:
        info = self.signal_info_by_label()[label]
        return info.samples_per_record / self.data_record_duration

    def signal_info_by_label(self) -> dict[str, EdfSignalInfo]:
        return {info.label: info for info in self.signal_info}


def read_edf_numeric_signals(
    path: str | Path,
    *,
    labels: Iterable[str] | None = None,
) -> EdfNumericSignals:
    edf_path = Path(path)
    requested = set(labels) if labels is not None else None
    with edf_path.open("rb") as handle:
        fixed_header = handle.read(256)
        if len(fixed_header) != 256:
            raise EdfParseError("EDF fixed header is incomplete")

        header_bytes = _header_int(fixed_header, 184, 192, "header bytes")
        record_count = _header_int(fixed_header, 236, 244, "data record count")
        record_duration = _header_float(
            fixed_header,
            244,
            252,
            "data record duration",
        )
        signal_count = _header_int(fixed_header, 252, 256, "signal count")
        if signal_count <= 0:
            raise EdfParseError("EDF signal count must be positive")
        if record_count <= 0:
            raise EdfParseError("EDF data record count must be positive")
        if record_duration <= 0.0:
            raise EdfParseError("EDF data record duration must be positive")

        variable_header = handle.read(header_bytes - 256)
        if len(variable_header) != header_bytes - 256:
            raise EdfParseError("EDF signal header is incomplete")
        signal_info = _parse_signal_header(variable_header, signal_count)

        values: dict[str, list[float]] = {
            info.label: []
            for info in signal_info
            if requested is None or info.label in requested
        }

        for _ in range(record_count):
            for info in signal_info:
                byte_count = info.samples_per_record * 2
                raw = handle.read(byte_count)
                if len(raw) != byte_count:
                    raise EdfParseError("EDF data record is truncated")
                if info.label not in values:
                    continue
                values[info.label].extend(_scale_samples(raw, info))

    missing = sorted(requested - values.keys()) if requested is not None else []
    if missing:
        raise EdfParseError(f"missing requested EDF signals: {', '.join(missing)}")

    return EdfNumericSignals(
        path=edf_path,
        data_record_count=record_count,
        data_record_duration=record_duration,
        signal_info=signal_info,
        signals={
            label: tuple(signal_values) for label, signal_values in values.items()
        },
    )


def _parse_signal_header(
    payload: bytes,
    signal_count: int,
) -> tuple[EdfSignalInfo, ...]:
    expected_bytes = 256 * signal_count
    if len(payload) != expected_bytes:
        raise EdfParseError("EDF variable header length does not match signal count")

    offset = 0
    labels = _read_string_field(payload, offset, 16, signal_count)
    offset += 16 * signal_count
    offset += 80 * signal_count
    offset += 8 * signal_count
    physical_min = _read_float_field(payload, offset, 8, signal_count, "physical min")
    offset += 8 * signal_count
    physical_max = _read_float_field(payload, offset, 8, signal_count, "physical max")
    offset += 8 * signal_count
    digital_min = _read_int_field(payload, offset, 8, signal_count, "digital min")
    offset += 8 * signal_count
    digital_max = _read_int_field(payload, offset, 8, signal_count, "digital max")
    offset += 8 * signal_count
    offset += 80 * signal_count
    samples_per_record = _read_int_field(
        payload,
        offset,
        8,
        signal_count,
        "samples per record",
    )

    return tuple(
        EdfSignalInfo(
            label=labels[index],
            samples_per_record=samples_per_record[index],
            physical_min=physical_min[index],
            physical_max=physical_max[index],
            digital_min=digital_min[index],
            digital_max=digital_max[index],
        )
        for index in range(signal_count)
    )


def _scale_samples(raw: bytes, info: EdfSignalInfo) -> tuple[float, ...]:
    count = info.samples_per_record
    digital_values = struct.unpack(f"<{count}h", raw)
    return tuple(
        info.physical_min + (value - info.digital_min) * info.scale
        for value in digital_values
    )


def _header_int(header: bytes, start: int, stop: int, field_name: str) -> int:
    text = header[start:stop].decode("ascii", errors="ignore").strip()
    try:
        return int(text)
    except ValueError as exc:
        raise EdfParseError(f"invalid EDF {field_name}: {text!r}") from exc


def _header_float(header: bytes, start: int, stop: int, field_name: str) -> float:
    text = header[start:stop].decode("ascii", errors="ignore").strip()
    try:
        return float(text)
    except ValueError as exc:
        raise EdfParseError(f"invalid EDF {field_name}: {text!r}") from exc


def _read_string_field(
    payload: bytes,
    start: int,
    width: int,
    count: int,
) -> tuple[str, ...]:
    return tuple(
        payload[start + index * width : start + (index + 1) * width]
        .decode("ascii", errors="ignore")
        .strip()
        for index in range(count)
    )


def _read_int_field(
    payload: bytes,
    start: int,
    width: int,
    count: int,
    field_name: str,
) -> tuple[int, ...]:
    values = _read_string_field(payload, start, width, count)
    try:
        return tuple(int(value) for value in values)
    except ValueError as exc:
        raise EdfParseError(f"invalid EDF {field_name}") from exc


def _read_float_field(
    payload: bytes,
    start: int,
    width: int,
    count: int,
    field_name: str,
) -> tuple[float, ...]:
    values = _read_string_field(payload, start, width, count)
    try:
        return tuple(float(value) for value in values)
    except ValueError as exc:
        raise EdfParseError(f"invalid EDF {field_name}") from exc

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

try:
    from opentelemetry import trace
except Exception:  # pragma: no cover
    trace = None


@contextmanager
def telemetry_span(
    name: str,
    attributes: dict[str, object] | None = None,
) -> Iterator[object | None]:
    if trace is None:
        yield None
        return

    tracer = trace.get_tracer("mental_wellbeing_api")
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                if value is None:
                    continue
                if isinstance(value, (bool, int, float, str)):
                    span.set_attribute(key, value)
                else:
                    span.set_attribute(key, str(value))
        yield span
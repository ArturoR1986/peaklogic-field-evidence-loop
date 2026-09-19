from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import json
from pathlib import Path
from typing import Any, Callable

from .schemas import EvidenceState, MediaObservation, NextAction


class TracePersistenceError(RuntimeError):
    """Raised when an audit event cannot be durably appended."""


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    return value


@dataclass(frozen=True)
class TraceEvent:
    sequence: int
    timestamp_utc: str
    event_type: str
    template_id: str
    stage_before: str
    stage_after: str
    media_id: str | None
    perception: dict[str, Any]
    decision: dict[str, Any]
    state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


class TraceRecorder:
    """Append-only in-memory + optional JSONL audit trace.

    File persistence happens before the event is accepted into the in-memory event
    list. If persistence fails, the caller receives TracePersistenceError and should
    roll back the associated state transition.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.path = Path(path) if path else None
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.events: list[TraceEvent] = []
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        *,
        event_type: str,
        template_id: str,
        stage_before: str,
        stage_after: str,
        state: EvidenceState,
        action: NextAction,
        observation: MediaObservation | None = None,
        perception: dict[str, Any] | None = None,
    ) -> TraceEvent:
        if observation is not None:
            perception_payload = _jsonable(observation)
        else:
            perception_payload = _jsonable(perception or {})

        event = TraceEvent(
            sequence=len(self.events) + 1,
            timestamp_utc=self.clock().astimezone(timezone.utc).isoformat(),
            event_type=event_type,
            template_id=template_id,
            stage_before=stage_before,
            stage_after=stage_after,
            media_id=observation.media_id if observation else None,
            perception=perception_payload,
            decision=_jsonable(action),
            state=_jsonable(state.to_dict()),
        )

        if self.path:
            try:
                with self.path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
                    fh.flush()
            except OSError as exc:
                raise TracePersistenceError("audit trace persistence failed") from exc

        self.events.append(event)
        return event

    def to_list(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self.events]

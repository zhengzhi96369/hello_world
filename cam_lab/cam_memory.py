"""Minimal Continuity-Aware Memory (CAM) prototype.

This module is intentionally lightweight: it captures the core idea used in the
paper draft, namely storing trace-derived experience units with provenance,
applicability boundaries, conflict metadata, runtime hooks, and exponentially
smoothed utility weights.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional


@dataclass
class ExperienceUnit:
    """A structured memory item distilled from an execution trace."""

    id: str
    claim: str
    provenance: List[str] = field(default_factory=list)
    applies_when: List[str] = field(default_factory=list)
    not_applies_when: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    runtime_hook: str = "planning"
    weight: float = 0.5
    helpful_count: int = 0
    harmful_count: int = 0

    def update(self, feedback: float, alpha: float = 0.9) -> None:
        """Update the utility weight with exponential smoothing.

        Args:
            feedback: Numeric reward/signal in [0, 1].
            alpha: Smoothing coefficient. Higher values reduce the effect of a
                single trace.
        """
        if not 0.0 <= feedback <= 1.0:
            raise ValueError("feedback must be in [0, 1]")
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be in [0, 1]")
        self.weight = alpha * self.weight + (1.0 - alpha) * feedback
        if feedback >= 0.5:
            self.helpful_count += 1
        else:
            self.harmful_count += 1


class CAMMemory:
    """Small in-memory store for trace-derived experience units."""

    def __init__(self, alpha: float = 0.9) -> None:
        self.alpha = alpha
        self.units: dict[str, ExperienceUnit] = {}

    def add_or_update(self, unit: ExperienceUnit, feedback: Optional[float] = None) -> None:
        """Insert a new unit or update an existing unit's smoothed weight."""
        if unit.id not in self.units:
            self.units[unit.id] = unit
        if feedback is not None:
            self.units[unit.id].update(feedback=feedback, alpha=self.alpha)

    def retrieve(self, hook: str, context_tags: Iterable[str], top_k: int = 5) -> List[ExperienceUnit]:
        """Retrieve applicable units for a runtime hook and current context tags.

        This is a simple symbolic matcher. In a full system, this can be replaced
        with hybrid semantic retrieval plus predicate checking.
        """
        tags = set(context_tags)
        candidates: list[ExperienceUnit] = []
        for unit in self.units.values():
            if unit.runtime_hook != hook:
                continue
            positive_ok = not unit.applies_when or bool(tags.intersection(unit.applies_when))
            negative_hit = bool(tags.intersection(unit.not_applies_when))
            if positive_ok and not negative_hit:
                candidates.append(unit)
        return sorted(candidates, key=lambda u: u.weight, reverse=True)[:top_k]


def demo() -> None:
    memory = CAMMemory(alpha=0.9)
    unit = ExperienceUnit(
        id="exp_identity_001",
        claim="Resolve cross-app identities before calling transaction APIs.",
        provenance=["task_12", "step_4", "api_error:wrong_identity"],
        applies_when=["cross_app", "transaction"],
        not_applies_when=["explicit_entity_id"],
        runtime_hook="before_tool_call",
    )
    memory.add_or_update(unit, feedback=1.0)
    print(memory.retrieve("before_tool_call", ["cross_app", "transaction"]))


if __name__ == "__main__":
    demo()

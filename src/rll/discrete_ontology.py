"""Typed discrete ontology primitives for the RLL claim-gated research program.

This module deliberately separates:

* typed classes and their cardinalities;
* words (ordered symbol occurrences) and arithmetic values;
* rational values and the provenance of a fraction presentation;
* mathematical invariance and physical relevance.

It does not derive a cosmological coupling from the factor 11. That bridge remains
``TOKEN_VAZIO`` until an explicit, dimensionally defined observable is supplied.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from fractions import Fraction
from math import gcd
from typing import Callable, Generic, Hashable, Iterable, TypeVar


T = TypeVar("T", bound=Hashable)
Y = TypeVar("Y")


class ClaimState(StrEnum):
    """Epistemic states used by the factor-11 work package."""

    PASS_EXACT = "PASS_EXACT"
    CONVENTION = "CONVENTION"
    HYPOTHESIS = "HYPOTHESIS"
    TOKEN_VAZIO = "TOKEN_VAZIO"
    CONTRADICTION = "CONTRADICTION"
    CLAIM_BLOCKED = "CLAIM_BLOCKED"


@dataclass(frozen=True, slots=True)
class TypedClass(Generic[T]):
    """A finite class tagged by logical type.

    Two empty classes of distinct logical types have the same cardinality but are
    not the same typed object. This models the type distinction needed by the
    Whitehead-Russell comparison without claiming to reproduce Principia's full
    ramified type theory.
    """

    type_name: str
    members: frozenset[T]

    def __post_init__(self) -> None:
        if not self.type_name.strip():
            raise ValueError("type_name must be non-empty")

    @classmethod
    def from_members(cls, type_name: str, members: Iterable[T]) -> "TypedClass[T]":
        return cls(type_name=type_name, members=frozenset(members))

    @property
    def cardinality(self) -> int:
        return len(self.members)


@dataclass(frozen=True, slots=True)
class DiscreteWord:
    """An ordered word whose multiplicity and position are preserved."""

    symbols: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(len(symbol) != 1 for symbol in self.symbols):
            raise ValueError("each word symbol must be exactly one Unicode code point")

    @classmethod
    def from_text(cls, text: str) -> "DiscreteWord":
        return cls(tuple(text))

    @property
    def length(self) -> int:
        return len(self.symbols)

    def multiplicity(self, symbol: str) -> int:
        if len(symbol) != 1:
            raise ValueError("symbol must be exactly one Unicode code point")
        return self.symbols.count(symbol)

    def text(self) -> str:
        return "".join(self.symbols)


@dataclass(frozen=True, slots=True)
class FractionPresentation:
    """A rational value together with the provenance of its integer presentation."""

    numerator: int
    denominator: int

    def __post_init__(self) -> None:
        if self.denominator == 0:
            raise ZeroDivisionError("denominator must be non-zero")

    @property
    def common_scale(self) -> int:
        return gcd(abs(self.numerator), abs(self.denominator))

    @property
    def reduced_pair(self) -> tuple[int, int]:
        scale = self.common_scale
        numerator = self.numerator // scale
        denominator = self.denominator // scale
        if denominator < 0:
            numerator *= -1
            denominator *= -1
        return numerator, denominator

    @property
    def value(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def provenance_record(self) -> dict[str, object]:
        reduced_numerator, reduced_denominator = self.reduced_pair
        return {
            "presentation": [self.numerator, self.denominator],
            "reduced_pair": [reduced_numerator, reduced_denominator],
            "rational_value": f"{reduced_numerator}/{reduced_denominator}",
            "common_scale": self.common_scale,
        }


def disjoint_union_cardinality(left: TypedClass[Hashable], right: TypedClass[Hashable]) -> int:
    """Return the cardinality of a tagged disjoint union.

    Tagging prevents equal member values in different operands from collapsing.
    """

    tagged_left = {("left", member) for member in left.members}
    tagged_right = {("right", member) for member in right.members}
    return len(tagged_left | tagged_right)


def same_rational_value(left: FractionPresentation, right: FractionPresentation) -> bool:
    """Check equality in Q, independent of presentation scale."""

    return left.value == right.value


def observable_is_representation_invariant(
    observable: Callable[[FractionPresentation], Y],
    left: FractionPresentation,
    right: FractionPresentation,
) -> bool:
    """Check whether an observable ignores the selected presentation change."""

    return observable(left) == observable(right)


@dataclass(frozen=True, slots=True)
class Factor11GateReport:
    """Claim-gated audit record for the 77/33 -> 7/3 comparison."""

    same_rational_value: bool
    recovered_common_scale: int
    mathematical_state: ClaimState
    physical_coupling_state: ClaimState
    claim_allowed: bool
    reason: str
    next_gate: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["mathematical_state"] = self.mathematical_state.value
        payload["physical_coupling_state"] = self.physical_coupling_state.value
        return payload


def evaluate_factor11_gate(
    *,
    scaled: FractionPresentation | None = None,
    reduced: FractionPresentation | None = None,
    physical_observable: Callable[[FractionPresentation], object] | None = None,
) -> Factor11GateReport:
    """Evaluate the exact arithmetic and the unresolved physical bridge.

    A supplied physical observable is not automatically treated as evidence. It
    only allows the function to detect whether the proposed observable changes
    under the presentation. Scientific promotion still requires units, data,
    uncertainty, a falsifier, and an auditable artifact outside this module.
    """

    scaled = scaled or FractionPresentation(77, 33)
    reduced = reduced or FractionPresentation(7, 3)
    equal_value = same_rational_value(scaled, reduced)
    scale = scaled.common_scale

    if not equal_value or scaled.reduced_pair != reduced.reduced_pair:
        return Factor11GateReport(
            same_rational_value=equal_value,
            recovered_common_scale=scale,
            mathematical_state=ClaimState.CONTRADICTION,
            physical_coupling_state=ClaimState.CLAIM_BLOCKED,
            claim_allowed=False,
            reason="The supplied presentations do not define the same rational value.",
            next_gate="Correct the arithmetic presentation before any physical hypothesis.",
        )

    if scale != 11:
        return Factor11GateReport(
            same_rational_value=True,
            recovered_common_scale=scale,
            mathematical_state=ClaimState.CONTRADICTION,
            physical_coupling_state=ClaimState.CLAIM_BLOCKED,
            claim_allowed=False,
            reason="The selected scaled presentation does not carry common scale 11.",
            next_gate="Supply a presentation whose gcd is exactly 11.",
        )

    if physical_observable is None:
        return Factor11GateReport(
            same_rational_value=True,
            recovered_common_scale=11,
            mathematical_state=ClaimState.PASS_EXACT,
            physical_coupling_state=ClaimState.TOKEN_VAZIO,
            claim_allowed=False,
            reason=(
                "77/33 and 7/3 are equal in Q, while 11 is recoverable as presentation "
                "provenance. No dimensionally defined physical observable was supplied."
            ),
            next_gate=(
                "Define O_11 with units, uncertainty, predicted delta relative to the reduced "
                "baseline, falsifier, dataset, and artifact hash."
            ),
        )

    invariant = observable_is_representation_invariant(physical_observable, scaled, reduced)
    if invariant:
        return Factor11GateReport(
            same_rational_value=True,
            recovered_common_scale=11,
            mathematical_state=ClaimState.PASS_EXACT,
            physical_coupling_state=ClaimState.CLAIM_BLOCKED,
            claim_allowed=False,
            reason="The supplied observable is invariant under removal of the common scale.",
            next_gate="Treat 11 as provenance/gauge for this observable or propose a new testable observable.",
        )

    return Factor11GateReport(
        same_rational_value=True,
        recovered_common_scale=11,
        mathematical_state=ClaimState.PASS_EXACT,
        physical_coupling_state=ClaimState.HYPOTHESIS,
        claim_allowed=False,
        reason=(
            "The supplied observable changes with presentation scale, creating a candidate "
            "hypothesis but not evidence of a cosmological coupling."
        ),
        next_gate=(
            "Document dimensions, calibration, uncertainty, null baseline, falsifier, real dataset, "
            "independent implementation, and reproducible artifact before promotion."
        ),
    )

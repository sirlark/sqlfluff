"""Define RuleContext class."""


import pathlib

from typing import (
    Optional,
    Tuple,
    Any,
)

from dataclasses import dataclass, field

from sqlfluff.core.cached_property import cached_property

from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.dialects import Dialect
from sqlfluff.core.templaters.base import TemplatedFile


@dataclass
class RuleContext:
    """Class for holding the context passed to rule eval functions."""

    # These don't change within a file.
    dialect: Dialect
    fix: bool
    templated_file: Optional[TemplatedFile]
    path: Optional[pathlib.Path]

    # These change within a file.
    # segment: The segment in question
    segment: BaseSegment
    # parent_stack: A tuple of the path from the root to this segment.
    parent_stack: Tuple[BaseSegment, ...] = field(default=tuple())
    # raw_stack: All of the raw segments so far in the file
    raw_stack: Tuple[RawSegment, ...] = field(default=tuple())
    # memory: Arbitrary storage for the rule
    memory: Any = field(default_factory=dict)
    # segment_idx: The index of this segment in the parent
    segment_idx: int = field(default=0)

    @property
    def siblings_pre(self) -> Tuple[BaseSegment, ...]:  # pragma: no cover
        """Return sibling segments prior to self.segment."""
        if self.parent_stack:
            return self.parent_stack[-1].segments[: self.segment_idx]
        else:
            return tuple()

    @property
    def siblings_post(self) -> Tuple[BaseSegment, ...]:
        """Return sibling segments after self.segment."""
        if self.parent_stack:
            return self.parent_stack[-1].segments[self.segment_idx + 1 :]
        else:
            return tuple()  # pragma: no cover

    @cached_property
    def final_segment(self) -> BaseSegment:
        """Returns rightmost & lowest descendant.

        Similar in spirit to BaseRule.is_final_segment(), but:
        - Much faster
        - Does not allow filtering out meta segments
        """
        last_segment: BaseSegment = (
            self.parent_stack[0] if self.parent_stack else self.segment
        )
        while True:
            try:
                last_segment = last_segment.segments[-1]
            except IndexError:
                return last_segment

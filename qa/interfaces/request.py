# coding: utf-8

from dataclasses import dataclass, asdict, field
from typing import List
from ...interfaces import LexicalResult


@dataclass
class Request:
    query: str
    lexical_res: LexicalResult
    history: List[str] = field(default_factory=list)
    debug: bool = False

    def __post_init__(self):
        self.lexical_res = LexicalResult.from_dict(self.lexical_res)

    def to_dict(self):
        return asdict(self)

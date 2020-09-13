# coding: utf-8

from dataclasses import dataclass, asdict
from ...interfaces import LexicalResult


@dataclass
class Request:
    query: str
    lexical_res: LexicalResult
    debug: bool = False

    def __post_init__(self):
        self.lexical_res = LexicalResult.from_dict(self.lexical_res)

    def to_dict(self):
        return asdict(self)

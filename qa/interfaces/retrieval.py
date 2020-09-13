# coding: utf-8

from dataclasses import dataclass
from typing import List, Tuple, Union
from ..enums import EnumRetrievalSource


@dataclass
class Doc:
    query: str
    doc: str
    score: float


@dataclass
class WebPage(Doc):
    url: str


@dataclass
class KBGraph:
    entity_ids: List[str]
    entities: List[str]
    rels: List[Tuple[str, str, str]]

    def __bool__(self):
        return len(self.rels) > 0


@dataclass
class RetrievalData:
    src_type: EnumRetrievalSource
    data: Union[List[Doc], KBGraph]

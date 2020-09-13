# coding: utf-8

from dataclasses import dataclass, field
from typing import Dict
from ..enums import EnumProcessorType


@dataclass
class ProcessorResult:
    processor_type: EnumProcessorType
    model_name: str
    answer: str
    score: float
    data: Dict = field(default_factory=dict)
    debug: Dict = field(default_factory=dict)

    @property
    def detail(self):
        self.data.update({
            'processor_type': self.processor_type.value,
            'model_name': self.model_name,
            'score': self.score,
        })
        return self.data

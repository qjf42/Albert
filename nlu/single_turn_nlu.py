# coding: utf-8
'''单轮NLU'''

from typing import List
from .template_parser import TemplateParser
from ..interfaces import BaseRequest, IntentSlots, SingleTurnNLUResult
from ..utils import log_utils


class BaseIntentSlotParser:
    def __init__(self, conf, log_conf):
        self.parser_name = None
        self.logger = log_utils.get_logger(**log_conf)

    def get_intents(self, utterance: str) -> List[IntentSlots]:
        raise NotImplementedError

    def get_slots(self, utterance: str, intent_slots: List[IntentSlots]) -> List[IntentSlots]:
        raise NotImplementedError

    def parse(self, req: BaseRequest) -> SingleTurnNLUResult:
        ret = SingleTurnNLUResult(self.parser_name)
        utterance = req.utterance
        for intent_res in self.get_intents(utterance):
            ret.add_intent_slots(self.get_slots(utterance, intent_res))
        return ret


class TemplateIntentSlotParser(BaseIntentSlotParser):
    '''基于模板的意图识别和槽位解析'''
    def __init__(self, conf, log_conf):
        super().__init__(conf, log_conf)
        self.parser_name = 'template'

        self.intent_parser_dic = {}
        for intent, intent_conf in conf.items():
            self.logger.info('Template parser loading, intent: %s', intent.value)
            dict_file = intent_conf['dict_file']
            template_file = intent_conf['template_file']
            self.intent_parser_dic[intent] = TemplateParser(dict_file, template_file)
    
    def get_intents(self, utterance: str) -> List[IntentSlots]:
        ret = []
        for intent, parser in self.intent_parser_dic.items():
            # TODO 每个意图暂时只取第一组匹配的槽位
            parse_res = parser.parse(utterance, topk=1)
            if parse_res:
                intent_slots = parse_res[0]
                intent_slots.intent = intent
                ret.append(intent_slots)
        return ret

    def get_slots(self, utterance: str, intent_slots: List[IntentSlots]) -> List[IntentSlots]:
        return intent_slots

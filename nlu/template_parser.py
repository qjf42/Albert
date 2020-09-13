#coding: utf-8
'''基于模板的NLU'''

import re
import json
from typing import List, Dict, Set, Tuple, Optional
from ..enums import EnumIntent
from ..interfaces import Slot, IntentSlots

# 短语词典 {'D:eat': {'吃', '吃饭'}}
pat_dic_t = Dict[str, Set[str]]


class Template:
    def __init__(self, expr: str, extractor_expr: str, score: float, pat_dic: pat_dic_t):
        '''
        Args:
            expr: 模板表达式，是由[D:短语词典名]，[R:正则表达式]，字符串组成的字符串
            extractor_expr: 抽取表达式(json)，key是输出的字段名，value是表达式，变量部分用方括号
            score: 置信度，用于排序
            pat_dic: 短语词典
        '''
        self.expr = expr
        self.extractor_expr = extractor_expr
        self.score = score 
        self._parse_expr(expr, pat_dic)
        self._extractor = self._parse_extractor(extractor_expr)

    def _parse_expr(self, expr: str, pat_dic: pat_dic_t) -> None:
        '''解析模板表达式
        Args:
            expr: 模板表达式，是由[D:短语词典名]，[R:正则表达式]，字符串组成的字符串
            pat_dic: 短语字典
        '''
        reg_expr = ''
        group_names = []
        group_idx_dic = {}

        def _get_group_name(name):
            idx = group_idx_dic.get(name, 0) + 1
            group_idx_dic[name] = idx
            return name if idx == 1 else f'{name}__{idx}'

        for part in self._split(expr):
            # 正则部分
            if part.startswith('[R:'):
                part = part[3:-1]
                assert part and '(' not in part and ')' not in part, 'Empty regex expression'
                group_name = _get_group_name('RE')
                reg_expr += f'(?P<{group_name}>{part})'
                group_names.append(group_name)
            # 短语词典部分
            elif part in pat_dic:
                group_name = _get_group_name(part[3:-1])
                reg_expr += '(?P<%s>%s)' % (group_name, '|'.join(pat_dic[part]))
                group_names.append(group_name)
            # 直接字符串
            else:
                reg_expr += part
        self.reg_expr = reg_expr
        self._pat = re.compile(reg_expr, re.I)
        self.group_names = group_names

    def _parse_extractor(self, extractor_expr: str) -> Dict[str, str]:
        '''
        Args:
            extractor_expr: 抽取表达式(json)，key是输出的字段名，value是表达式，变量部分用方括号
        '''
        if not extractor_expr:
            return {}
        try:
            extractor = json.loads(extractor_expr)
            for k, expr in extractor.items():
                assert '{' not in expr and '}' not in expr
                self._split(expr)
        except Exception as e:
            raise ValueError(f'Invalid extractor expr {extractor_expr}, {e}.')
        return {k: e.replace('[', '{').replace(']', '}') for k,e in extractor.items()}

    def _split(self, expr: str) -> List[str]:
        '''切分模板字符串，每个部分是"[]"包住，或者常量字符串'''
        ret = []
        cur = ''
        left_on = False
        for i, ch in enumerate(expr):
            if ch == '[':
                if left_on:
                    raise ValueError('Invalid pattern expr, double left brackets: %s' % expr[:i+1])
                if cur:
                    ret.append(cur)
                cur = '['
                left_on = True
            elif ch == ']':
                if not left_on:
                    raise ValueError('Invalid pattern expr, unpaired right bracket: %s' % expr[:i+1])
                cur += ']'
                ret.append(cur)
                cur = ''
                left_on = False
            else:
                cur += ch
        if left_on:
            raise ValueError('Invalid pattern expr, unpaired left bracket: %s' % expr)
        if cur:
            ret.append(cur)
        return ret

    def _extract(self, match_values, match_spans) -> List[Slot]:
        ret = []
        match_dic = dict(zip(self.group_names, match_values))
        span_dic = dict(zip(self.group_names, match_spans))
        for k, fmt_str in self._extractor.items():
            val = fmt_str.format(**match_dic)
            span = span_dic.get(fmt_str[1:-1])
            ret.append(Slot(k, val, span[0], span[1]))
        return ret

    def parse(self, utterance: str) -> Tuple[Optional[List[Slot]], float]:
        '''模板匹配'''
        match = self._pat.match(utterance)
        if not match:
            return None, 0
        values = []
        spans = []
        for group_name in self.group_names:
            values.append(match.group(group_name))
            spans.append(match.span(group_name))
        slots = self._extract(values, spans)
        score = self.score if slots is not None else 0
        return slots, score


class TemplateParser:
    def __init__(self, dict_file, template_file):
        self.pat_dic = self._load_pat_dict(dict_file)
        self.templates = self._load_template(template_file, self.pat_dic)

    def _load_pat_dict(self, dict_file) -> pat_dic_t:
        '''加载片段词典，如{[D:stock]: [股票词表]}'''
        with open(dict_file) as f:
            ret = {}
            pat_name = None
            for line in f:
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                if line.startswith('[D:'):
                    pat_name = line
                    ret.setdefault(pat_name, set())
                elif pat_name:
                    ret[pat_name].add(line)
            return ret

    def _load_template(self, template_file: str, pat_dic: pat_dic_t) -> List[Template]:
        '''加载模板'''
        with open(template_file) as f:
            ret = []
            for line in f:
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                expr, extractor, score = line.split('\t')
                ret.append(Template(expr, extractor, float(score), pat_dic))
            ret.sort(key=lambda t: t.score, reverse=True)
            return ret

    def parse(self, utterance: str, topk: int = None) -> List[IntentSlots]:
        '''返回匹配的意图和槽位，取topk'''
        matched = []
        for tpl in self.templates:
            slots, score = tpl.parse(utterance)
            if slots is not None:
                matched.append(IntentSlots(None, slots, score))
            if topk is not None and len(matched) >= topk:
                break
        return matched

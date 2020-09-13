#coding: utf-8
'''机器人服务入口'''

import flask

from .conf import NLU_CONF, BOT_LOG_CONF, NLU_LOG_CONF, SKILL_LOG_CONF
from .nlu import LexicalParser, TemplateIntentSlotParser
from .rank import IntentRank
from .router import Router
from .utils import log_utils
from .enums import EnumRequestSrcType, EnumResponseError
from .interfaces import BaseRequest, RequestFactory, BotResponse


class DumbBot:
    def __init__(self):
        # nlu
        self.lexical_parser = LexicalParser(NLU_CONF['lexical'], NLU_LOG_CONF)
        self.template_parser = TemplateIntentSlotParser(NLU_CONF['template'], NLU_LOG_CONF)
        self.intent_rank = IntentRank()
        # skills
        self.router = Router(SKILL_LOG_CONF)

    def chat(self, req: BaseRequest) -> BotResponse:
        utterance = req.utterance
        resp = BotResponse()
        if req.debug:
            resp.add_debug('request', req.to_dict())
        if not utterance:
            return resp.set_error(EnumResponseError.EMPTY_UTTERANCE)\
                       .set_response('你说什么？')

        # NLU
        lexical_res = self.lexical_parser.parse(req)
        if req.src_type == EnumRequestSrcType.NLU:
            return resp.add_data('nlu', {
                'lexical': lexical_res,
                #'template': template_res,
            })
        template_res = self.template_parser.parse(req)

        if req.debug:
            resp.add_debug('lexical', lexical_res)\
                .add_debug('template_res', template_res)

        # Rank
        self.intent_rank.rank(req, template_res)
        top_intent_slots = None
        if template_res.intent_slots_list:
            top_intent_slots = template_res.intent_slots_list[0]            
        if req.debug:
            resp.add_debug('top_intent_slots', top_intent_slots)

        # Skill
        top_intent = top_intent_slots.intent if top_intent_slots is not None else None
        skill = self.router.route(top_intent_slots.intent)
        skill_resp = skill(req, lexical_res, top_intent_slots)
        if not skill_resp.success:
            return resp.set_error(EnumResponseError.SKILL_ERROR, skill_resp.err_msg)\
                       .set_response('你说的太高端了，我听不懂')
        else:
            return resp.set_response(**skill_resp.response)


'''FLASK'''

BOT = DumbBot()
app = flask.Flask(__name__)
log_utils.set_app_logger(app.logger, **BOT_LOG_CONF)


def parse_req(options):
    ret = {}
    req = flask.request
    data = req.get_json(silent=True) or {}
    for key, required in options.items():
        val = req.args.get(key, data.get(key, req.form.get(key)))
        if val is None and required:
            raise ValueError(f'Parameter [{key}] is missing.')
        ret[key] = val
    return ret


@app.route('/chat_debug', methods=['GET', 'POST'])
def chat_debug():
    param_options = {
        'query': True,
    }
    try:
        query = parse_req(param_options)['query'].strip()
    except:
        resp = BotResponse().set_error(EnumResponseError.INVALID_PARAMS)
        return flask.jsonify(resp)
    try:
        req = RequestFactory.get_request(EnumRequestSrcType.CMD, query, debug=True)
        resp = BOT.chat(req)
    except Exception as e:
        resp = BotResponse().set_error(EnumResponseError.UNKNOWN_ERROR, str(e))
    return flask.jsonify(resp)


@app.route('/nlu', methods=['POST'])
def nlu():
    param_options = {
        'query': True,
        'debug': False,
    }
    try:
        query = parse_req(param_options)['query'].strip()
    except:
        resp = BotResponse().set_error(EnumResponseError.INVALID_PARAMS)
        return flask.jsonify(resp)
    try:
        req = RequestFactory.get_request(EnumRequestSrcType.NLU, query)
        resp = BOT.chat(req)
    except Exception as e:
        resp = BotResponse().set_error(EnumResponseError.NLU_ERROR, str(e))
    return flask.jsonify(resp)


@app.route('/chat_wx', methods=['GET', 'POST'])
def chat_wx():
    param_options = {
        'msg': True,
        'chatroom_id': True,
        'user_id': True,
        'user_name': True,
        'debug': False,
    }
    try:
        params = parse_req(param_options)
    except Exception as e:
        resp = BotResponse().set_error(EnumResponseError.INVALID_PARAMS, str(e))
        return flask.jsonify(resp)
    try:
        req = RequestFactory.get_request(EnumRequestSrcType.WECHAT, **params) 
        resp = BOT.chat(req)
    except Exception as e:
        resp = BotResponse().set_error(EnumResponseError.UNKNOWN_ERROR, str(e))
    return flask.jsonify(resp)


@app.route('/chat_dd', methods=['POST'])
def chat_dingding():
    param_options = {
        'sys.userInput': True,
        'sys.ding.senderId': True,
        'sys.ding.conversationId': True,
        'sys.ding.senderNick': True,
        'debug': False,
    }
    ret = {
        'errorCode': '200',
        'fields': {},
    }
    try:
        ori_params = parse_req(param_options)
    except Exception as e:
        ret['errorCode'] = '500'
        return flask.jsonify(ret)
    try:
        params = {
            'msg': ori_params['sys.userInput'],
            'user_id': ori_params['sys.ding.senderId'],
            'user_name': ori_params['sys.ding.senderNick'],
            'chatgroup_id': ori_params['sys.ding.conversationId'],
            'debug': ori_params['debug'],
        }
        req = RequestFactory.get_request(EnumRequestSrcType.DINGDING, **params) 
        resp = BOT.chat(req)
        assert resp.success
        ret['fields'] = resp.response
    except Exception as e:
        ret['errorCode'] = '500'
    return flask.jsonify(ret)

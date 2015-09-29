__author__ = 'burgosz'
from django import template
from zabbix.api import ZabbixAPI
import json
from django.core.cache import get_cache


register = template.Library()


@register.assignment_tag
def zbx_call(method, args):
    zapi = ZabbixAPI(url='', user='', password='')
    args = args.replace("'", "\"")
    args = json.loads(args)
    cache = get_cache('default')
    if method == "service.get" and args.get('serviceids'):
        key = ""
        for srv_id in args['serviceids']:
            key += srv_id
        cached = cache.get(key)
        if cached:
            return cached
        else:
            result = zapi.do_request(method, args)
            cache.set(key, result, None)
            return result
    result = zapi.do_request(method, args)
    return result

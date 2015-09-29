__author__ = 'burgosz'
from django import template
from zabbix.api import ZabbixAPI
import json
register = template.Library()


@register.assignment_tag
def zbx_stats_get():
    stat = {'count': 0, 'max': 0, 'sum': 0, 'counter': 0, 'MTBF' :0}

    return stat


@register.simple_tag
def zbx_stats_add_service(statobject, key, value):
    if key == "count":
        statobject['count'] += int(value)
    if key == "max":
        if int(value) > statobject['max']:
            statobject['max'] = int(value)
    if key == "sum":
        statobject['sum'] += int(value)
    if key == "MTBF":
        statobject['MTBF'] += int(value)
    if key == "counter":
        statobject['counter'] += 1
    return ""


@register.simple_tag
def zbx_stats_calculate(statobject, interval):
    oktime = interval*statobject['count'] - statobject['sum']
    if statobject['count'] > 0:
        statobject['sla'] = round(oktime/float((interval*statobject['count']))*100, 2)
        statobject['MTBF'] = statobject['MTBF']/statobject['count']
    else:
        statobject['sla'] = 100.00
        statobject['MTBF'] = interval
    return ""

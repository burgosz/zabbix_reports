__author__ = 'burgosz'
from django import template
from zabbix_services import zbx_service_ids_get_deep
# from zabbix.api import ZabbixAPI
import json
from zabbix_reports.templatetags.zabbix_call import zbx_call
from django.core.cache import cache
register = template.Library()

# @register.assignment_tag
# def zbx_periods_deep(service, time_from, time_till):
#
#     triggerid = service['triggerid']
#     if triggerid != 0:
#         periods = zbx_periods_get(triggerid, time_from, time_till)
#     if not service['dependencies']:
#         return None



@register.assignment_tag
def zbx_periods_get(serviceid, time_from, time_till):

    #Caching. If cached return the cached value.
    key = ""+serviceid+time_from+time_till
    cached = cache.get(key)
    if cached:
        return cached

    # Init the stats variable.
    stats = {}
    stats['interval'] = float(time_till)-float(time_from)
    stats['count'] = 0
    stats['max'] = 0
    stats['MTBF'] = stats['interval']
    stats['sla'] = 0
    stats['sum'] = 0
    stats['oktime'] = 0

    periods = []
    sla_result = {}
    sla_result['stats'] = stats

    last_event = []

    # Get the service from Zabbix, to get the triggerid
    args = "{'serviceids': '"+str(serviceid)+"', 'output':'extend', 'selectDependencies':'extend'}"
    service = zbx_call('service.get', args)
    result = service['result'][0]
    triggerid = result['triggerid']

    # Get the last event before the asked time period, to determine the last state of trigger.
    # If the triggerid is 0 and the service has dependencies get all triggerid from deps.
    if triggerid == "0" and result['dependencies']:
        deps = zbx_service_ids_get_deep([result['serviceid']], [])
        triggerid = "["
        args = "{'serviceids': "+deps+", 'output':'extend'}"
        services = zbx_call('service.get', args)
        for srv in services['result']:
            triggerid += "'"+srv['triggerid']+"',"

        triggerid = triggerid[:-1]+"]"
        args = "{'objectids': "+str(triggerid)+", 'time_till':'"+str(time_from)+\
               "', 'output':'extend', 'sortfield':'clock', 'sortorder':'DESC', 'limit':'1'}"
    else:
        args = "{'objectids': '"+str(triggerid)+"', 'time_till':'"+str(time_from)+\
               "', 'output':'extend', 'sortfield':'clock', 'sortorder':'DESC', 'limit':'1'}"
    last_event = zbx_call('event.get', args)
    last_event = last_event['result']


    # Get all events of the asked period.
    if result['triggerid'] == "0":
        args = "{'objectids': "+str(triggerid)+", 'time_till':'"+str(time_till)+\
               "', 'time_from': '"+str(time_from)+"', 'output':'extend', 'sortfield':'clock', 'sortorder':'ASC'}"
    else:
        args = "{'objectids': '"+str(triggerid)+"', 'time_till':'"+str(time_till)+\
               "', 'time_from': '"+str(time_from)+"', 'output':'extend', 'sortfield':'clock', 'sortorder':'ASC'}"
    events = zbx_call('event.get', args)
    events = events['result']

    # If there where no event in the period 2 cases are possible.
    #  1, Last state was 0, so the service has no problem.
    #  2, Last state is 1, so the service had error during the whole period.
    if not events:
        if last_event and last_event[0]['value'] == '1':
            periods.append([time_from, time_till])
        else:
            return sla_result

    # Store the periods while the service was in error.
    else:
        if not last_event:
            last_event.append(events[0])
        eventids = []
        for i in range(1, len(events)-1):
            if events[i-1]['value'] == events[i]['value']:
                eventids.append(events[i-1]['eventid'])
        for event in events:
            if event['eventid'] in eventids:
                events.remove(event)
        result['events'] = events[0]
        if last_event[0]['value'] == '1' and events[0]['value'] == '1' and len(events)>1:
            events.pop(0)
        if last_event[0]['value'] == '1' and events[0]['value'] == '0' and len(events)>1:
            periods.append([time_from, events[0]['clock']])
            events.pop(0)
        if last_event[0]['value'] == '0' and events[0]['value'] == '0' and len(events)>1:
            events.pop(0)
        for i in range(1, len(events)-1, 2):
            periods.append([events[i-1]['clock'], events[i]['clock']])
        if events[-1]['value'] == '1':
            periods.append([events[-1]['clock'], time_till])

    if not periods:
        return sla_result

    sla_result['periods'] = periods

    # Calculate the stats based on periods.
    stats['count'] = len(periods)
    for period in periods:
        if int(period[1])-int(period[0]) > stats['max']:
            stats['max'] = int(period[1])-int(period[0])
        stats['sum'] += int(period[1])-int(period[0])
    stats['oktime'] = stats['interval']-stats['sum']
    stats['avg'] = (str(int(round(stats['sum']/stats['count']))))
    stats['MTBF'] = str(int(round(stats['oktime']/stats['count'])))
    stats['sla'] = str(round(stats['oktime']/stats['interval']*100, 2))
    sla_result['stats'] = stats

    # Cache the results forever. These data should never change.
    cache.set(key, sla_result, None)
    return sla_result



__author__ = 'burgosz'
from django import template
register = template.Library()
from zabbix_reports.templatetags.zabbix_call import zbx_call
from django.core.cache import get_cache

@register.assignment_tag
def zbx_service_container_get():
    services = []
    return services


# Iterate over services and get the service ids in order with there level of deepness.
def _zbx_service_ids_get_deep(topids, service_ids, level=0):
    topidstostring = '["'+'","'.join(str(e) for e in topids)+'"]'
    args = "{'parentids': "+topidstostring+", 'output': 'extend'}"
    services = zbx_call('service.get', args)

    for service in services['result']:
        service_ids.append({'id': str(service['serviceid']), 'level': str(level)})
        pids = []
        pids.append(int(service['serviceid']))
        level += 1
        _zbx_service_ids_get_deep(pids, service_ids, level)
        level -= 1
    return_value = '["'+'","'.join(str(e['id']) for e in service_ids)+'"]'
    return return_value


@register.assignment_tag
def zbx_service_ids_get_deep(topids, service_ids, level=0):
    # Cache the service ids
    cache = get_cache('default')
    key = "deep_"+'["'+'","'.join(str(e) for e in topids)+'"]'
    cached = cache.get(key)
    if cached:
        for cached_srv in cached:
            service_ids.append(cached_srv)
        return '["'+'","'.join(str(e['id']) for e in service_ids)+'"]'
    else:
        return_value = _zbx_service_ids_get_deep(topids, service_ids, level)
        cache.set(key, service_ids, None)
        return return_value

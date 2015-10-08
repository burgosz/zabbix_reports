from django.shortcuts import render
import time
from django.views.decorators.cache import cache_page


#@cache_page(None)
def report(request):

    top_id = []
    top_ids = request.GET['tid'].split('-')
    for top in top_ids:
        top_id.append(int(top))
    date_from = str(time.mktime(time.strptime(request.GET['from'], '%Y%m%d%M%S')))
    date_till = str(time.mktime(time.strptime(request.GET['till'], '%Y%m%d%M%S')))
    date_till = date_till[:-2]
    date_from = date_from[:-2]

    return render(request, 'report.html', {'top_id': top_id,
                                           'time_from': date_from, 'time_till': date_till})

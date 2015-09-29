from django.shortcuts import render
from django_xhtml2pdf.utils import generate_pdf
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
import time


def report(request):
    resp = HttpResponse(content_type='application/pdf')

    top_id = []
    top_ids = request.GET['tid'].split('-')
    for top in top_ids:
        top_id.append(int(top))
    date_from = str(time.mktime(time.strptime(request.GET['from'], '%Y%m%d%M%S')))
    date_till = str(time.mktime(time.strptime(request.GET['till'], '%Y%m%d%M%S')))
    date_till = date_till[:-2]
    date_from = date_from[:-2]

    # result = generate_pdf('report.html', file_object=resp, context={'top_id': top_id,
    #                                      'time_from': date_from, 'time_till': date_till})
    return render(request, 'report.html', {'top_id': top_id,
                                           'time_from': date_from, 'time_till': date_till})
    # return result
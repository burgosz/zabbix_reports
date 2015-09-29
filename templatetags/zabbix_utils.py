__author__ = 'burgosz'
from django import template
import datetime
import time
from dateutil.relativedelta import relativedelta


register = template.Library()


@register.filter('timestamp_to_time')
def convert_timestamp_to_time(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp))


@register.filter('sub')
def subtract(value, arg):
    return int(value) - int(arg)


@register.filter('second_to_readable')
def second_to_readable(second):
    m, s = divmod(int(second), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return "%d nap %d:%02d:%02d" % (d, h, m, s)


@register.assignment_tag
def previous_month(time_from, months):
    date_till =  datetime.datetime.fromtimestamp(int(time_from))
    date_till =  datetime.datetime(date_till.year, date_till.month, 1, 0, 0)
    date_from =  date_till - relativedelta(months=int(months))
    date_from = str(time.mktime(date_from.timetuple()))
    date_till = str(time.mktime(date_till.timetuple()))
    date_till = date_till[:-2]
    date_from = date_from[:-2]

    return [date_from, date_till]


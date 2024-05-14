from django import template
from django.template.defaultfilters import stringfilter

import datetime

register = template.Library()

@register.filter(name='compute_wr')
@stringfilter
def compute_wr(attr):
    if attr == '2':
        return 'H'
    elif attr == '1':
        return 'L'
    elif attr == '0':
        return 'M'
    
@register.filter(name='compute_full_wr')
@stringfilter
def compute_full_wr(attr):
    if attr == '2':
        return 'High'
    elif attr == '1':
        return 'Low'
    elif attr == '0':
        return 'Medium'

@register.filter(name='compute_foot')
@stringfilter
def compute_foot(attr):
    if attr == '1':
        return 'Right'
    elif attr == '2':
        return 'Left'
    
@register.filter(name='compute_age')
@stringfilter
def compute_age(date):
    date_format = "%m/%d/%Y %I:%M:%S %p"
    birth_date = datetime.datetime.strptime(date, date_format)
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

@register.filter(name='page')
@stringfilter
def page(page):
    if page == '0':
        return '10'
    elif page == '1':
        return '11'
    return page
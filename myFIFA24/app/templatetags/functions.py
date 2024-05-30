from django import template
from django.template.defaultfilters import stringfilter

import datetime

register = template.Library()

def compute_wr(attr):
    if attr == '2':
        return 'H'
    elif attr == '1':
        return 'L'
    elif attr == '0':
        return 'M'
    
register.filter(compute_wr)

def compute_full_wr(attr):
    if attr == '2':
        return 'High'
    elif attr == '1':
        return 'Low'
    elif attr == '0':
        return 'Medium'
    
register.filter(compute_wr)

def compute_foot(attr):
    if attr == '1':
        return 'Right'
    elif attr == '2':
        return 'Left'
    
register.filter(compute_foot)

def compute_age(date):
    date_format = "%m/%d/%Y %I:%M:%S %p"
    birth_date = datetime.datetime.strptime(date, date_format)
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

register.filter(compute_age)

def page(page):
    if page == '0':
        return '10'
    elif page == '1':
        return '11'
    return page

register.filter(page)

@register.simple_tag
def position_exists(pos, players):
    for player in players:
        if player["pos"] == pos:
            return player
        
    return None


"""I am writing this module to help me upload repeated reminders to my
Tickler in Evernote.  I want to find the days of the month that follow
certain patterns for the next 30 or 31 days.

It will be slightly tricky to make sure I don't miss things that
should happen on the 31st or something.  I think my basic approach
will be to find the date one month from the day the script is run and
then subtract one day.  I also need to make sure that I run my main
Tickler reminder script on the correct day each month.  It will
probably be best to do this on the first, but I don't want to limit
this module by assuming reminders are always uploaded on the 1st.

This module will be used with approaches that use both email and
geeknote."""

import datetime, time, copy

today = datetime.date.today()

def _get_start_day(start_day=None):
    if start_day is None:
        start_day = today
    return start_day


def find_end_day(start_day=None):
    """Find the day whose day of the month is one less than start_day,
    i.e. if today is the 5th, stop at the 4th of next month."""
    start_day = _get_start_day(start_day)
    end_day = start_day + datetime.timedelta(days=31)
    while end_day.day >= start_day.day:
        end_day -= datetime.timedelta(days=1)#back up one day until my
                                             #day of the month is less
                                             #than start_day's
    return end_day
    

def find_next_weekday(start_day, des_day=0):
    """Find the next Monday or Tuesday or whatever following today.
    des_day is an integer between 0 and 6 where 0 is Monday, 1 is
    Tuesday, ..., and 6 is Sunday."""
    start_day = _get_start_day(start_day)
    day_delta = des_day - start_day.weekday()
    if day_delta < 0:
        day_delta += 7
    delta = datetime.timedelta(days=day_delta)
    return today + delta



def find_all_weekdays(start_day=None, des_day=0, \
                      end_day=None):
    if end_day is None:
        end_day = find_end_day(start_day)
    first_day = find_next_weekday(start_day=start_day, \
                                  des_day=des_day)
    days = [first_day]
    next_day = first_day + datetime.timedelta(days=7)
    while next_day <= end_day:
        days.append(copy.copy(next_day))
        next_day += datetime.timedelta(7)
    return days

    
def find_all_Mondays(**kwargs):
    kwargs['des_day'] = 0
    out = find_all_weekdays(**kwargs)
    return out


def find_all_Tuesdays(**kwargs):
    kwargs['des_day'] = 1
    out = find_all_weekdays(**kwargs)
    return out


def find_all_Wednesdays(**kwargs):
    kwargs['des_day'] = 2
    out = find_all_weekdays(**kwargs)
    return out


def find_all_Thursdays(**kwargs):
    kwargs['des_day'] = 3
    out = find_all_weekdays(**kwargs)
    return out


def find_all_Fridays(**kwargs):
    kwargs['des_day'] = 4
    out = find_all_weekdays(**kwargs)
    return out


def find_all_Saturdays(**kwargs):
    kwargs['des_day'] = 5
    out = find_all_weekdays(**kwargs)
    return out


def find_all_Sundays(**kwargs):
    kwargs['des_day'] = 6
    out = find_all_weekdays(**kwargs)
    return out


def convert_list_of_days_to_tags(listin):
    """Convert a list of datetime.date objects to Tickler tags,
    i.e. D##."""
    tags = []
    for date in listin:
        tag = 'D%0.2i' % date.day
        tags.append(tag)
    return tags


func_dict_str = {'mon':find_all_Mondays, \
                 'tue':find_all_Tuesdays, \
                 'wed':find_all_Wednesdays, \
                 'thu':find_all_Thursdays, \
                 'fri':find_all_Fridays, \
                 'sat':find_all_Saturdays, \
                 'sun':find_all_Sundays, \
                 }


func_dict_int = {0:find_all_Mondays, \
                 1:find_all_Tuesdays, \
                 2:find_all_Wednesdays, \
                 3:find_all_Thursdays, \
                 4:find_all_Fridays, \
                 5:find_all_Saturdays, \
                 6:find_all_Sundays, \
                 }


def get_tags_weekly(day, start_day=None, end_day=None):
    """get a list of tags for something that repeats once per week;
    day is an integer or a string of the day of the week"""
    if type(day) == str:
        key = day[0:3].lower()
        func = func_dict_str[key]
    elif type(day) == int:
        key = day
        func = func_dict_int[key]
    days = func(start_day=start_day, \
                end_day=end_day)
    tags = convert_list_of_days_to_tags(days)
    return tags

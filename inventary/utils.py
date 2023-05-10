import datetime

def get_first_day(year, month):
    first_day = datetime.date(year, month, 1)
    return first_day

def return_month_name(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months[month-1]
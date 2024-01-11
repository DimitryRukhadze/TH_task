import datetime
from dateutil.relativedelta import relativedelta


perform_date = datetime.date(2024, 1, 11)
next_due_date = 5


def cnt_next_due(date, months):
    res_date = date + relativedelta(months=months)
    return res_date


print(cnt_next_due(perform_date, next_due_date))

from dateutil.relativedelta import relativedelta
from datetime import datetime


expected_ndd = datetime.strptime("2019-01-01", "%Y-%m-%d") + relativedelta(months=6) + relativedelta(months=6)
act_ndd = datetime.strptime("2019-06-19", "%Y-%m-%d") + relativedelta(months=6)
print(expected_ndd, act_ndd)

delta = expected_ndd - act_ndd
print(delta)
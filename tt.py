from dateutil.relativedelta import relativedelta
from datetime import datetime


date = datetime.strptime("2019-06-01", "%Y-%m-%d")

print((datetime.strptime("2019-07-01", "%Y-%m-%d") - date))
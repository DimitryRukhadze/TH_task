from dateutil.relativedelta import relativedelta
from datetime import datetime


date = datetime.strptime("2019-08-08", "%Y-%m-%d")

print(date + relativedelta(months=6))
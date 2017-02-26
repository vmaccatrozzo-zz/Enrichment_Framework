from datetime import datetime
from get_BBC_schedule import get_schedule

for day in range(8,10):
	date='2014/06/%s' %day
	date = datetime.strptime(date, "%Y/%m/%d").strftime('%Y/%m/%d')
	get_schedule(date)


from datetime import datetime
date_string = '05:30'
datetime = datetime.strptime(date_string, '%H:%M')

print(datetime)
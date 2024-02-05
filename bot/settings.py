import datetime

from database.settings import DEBUG

if DEBUG:
    ACTION_START_DATE = datetime.date(2024, 1, 1)
else:
    ACTION_START_DATE = datetime.date(2024, 2, 1)
ACTION_END_DATE = datetime.date(2024, 4, 1)

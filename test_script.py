from publics import db
from datetime import datetime

col_task = db()['tasks']

for item in col_task.find({},{'from_date': 1, 'to_date': 1}):
    from_date = datetime.strptime(str(item['from_date'])[:10], "%Y-%m-%d")
    to_date = datetime.strptime(str(item['to_date'])[:10], "%Y-%m-%d")
    col_task.find_one_and_update({'_id':item['_id']},
                             {'$set':{'from_date':from_date, 'to_date':to_date}})
    print(from_date)
    print(to_date)
    # print(item)

import json
from datetime import datetime
from publics import db
from bson import ObjectId
# dddd = {
#     'from_date': '111',
#     'to_date': '222'
# }
# a = '{"$match": {"date": {"$gt": dddd["from_date"],"$lt": dddd["to_date"]}}}'
#
#
# b = json.dumps(a)
# b = re.sub('\\\\', '', b)
# b = b[1:-1]
#
dds = datetime.strptime('2020-06-13', "%Y-%m-%d")

print(dds)
di = []
col = db()['saved_tasks']
col2 = db()['tasks']
# for item in col.find():
#     print(item)
#     item = json.loads(item['query'])
#     item['from_date'] = datetime.now()
#     di.append(item)
# print(di)
# col2.update_one({'_id':ObjectId('5ee4a4b9584c2e8718ef3b39')},{'$set':{'from_date':dds,'to_date':dds,'tags':['asd', 'asdas']}})

col_saved_tasks = db()['save_task_query']
for item in col_saved_tasks.find({'user_id':'5ee5d403ed259e8b76907b13'}):
    if 'tags' in item:
        print('areee')
    print(item)
import sys
sys.path.append('/app/')
from publics import db, PrintException
import requests
from time import sleep
col_sms = db()['sms']
for i in range(5):
    print('Round %s' % i)
    for item in col_sms.find({'sent': False}):
        try:
                item['mobile'] = item['mobile'].replace('+98', '0')
                # item['mobile'] = f'0{item["mobile"]}' if item['mobile'][0] != 0 else item['mobile']
                service_url = "http://87.107.52.205/post/sendsms.ashx?from=1000100059&to=" + item['mobile'] + "&text=" + item['text'] + "&password=9156158310&username=saba-app"
                # service_url = "http://87.107.52.205/post/sendsms.ashx?from=10000130&to=" + item['mobile'] + "&text=" + item['text'] + "&password=9156158310&username=saba-app"
                results = requests.get(url=service_url)
                print(col_sms.update_one({'_id': item['_id']}, {'$set': {'sent': True}}).raw_result)
        except:
            PrintException()
    sleep(10)

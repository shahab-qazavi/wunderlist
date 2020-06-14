from publics import db
from datetime import datetime, timedelta
d = datetime.now()
col = db()['tasks']
col.insert_one(
{
    "user_id":"5ee486091ce8ad11781eff0d",
    "title":"Football",
    "from_date": d,
    "to_date": d + timedelta(days=20),
    "tags":["sport"]
})
col.insert_one(
{
    "user_id":"5ee486091ce8ad11781eff0d",
    "title":"Swim",
    "from_date":d - timedelta(days=20),
    "to_date":d,
    "tags":["sport", "fun"]
})
col.insert_one(
{
    "user_id":"5ee486091ce8ad11781eff0d",
    "title":"Do my work",
    "from_date":d - timedelta(days=2),
    "to_date":d + timedelta(days=10),
    "tags":["business", "fun"]
})
col.insert_one(
{
    "user_id":"5ee486091ce8ad11781eff0d",
    "title":"Running",
    "from_date":d + timedelta(days=5),
    "to_date":d + timedelta(days=40),
    "tags":["fun"]
})

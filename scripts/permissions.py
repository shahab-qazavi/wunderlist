import sys
sys.path.append('/root/dev/wunderlist')
from publics import db, set_db
from bson import ObjectId
set_db('wunderlist')

col_users_roles = db()['users_roles']
col_users_roles.drop()
col_users_roles.insert_many([
    {
        "_id": ObjectId("5e25ab698c90582c5785d291"),
        'name': 'admin',
        'module': 'users',
        'permissions': {
            'allow': ['get'],
        },
    },
    {
        'name': 'user',
        'module': 'profile',
        'permissions': {
            'allow': ['get', 'put'],
            'get': {'user_id': '$uid'},
            'delete': {'user_id': '$uid'},
            'put': {
                'query': {'user_id': '$uid'},
                'set': {}

            },
        },
    },
    {
        'name': 'user',
        'module': 'tasks',
        'permissions': {
            'allow': ['get', 'post', 'put', 'delete'],
            'get': {},
            'post': {'user_id': '$uid'},
            'put': {
                'query': {'user_id': '$uid'},
                'set': {}},
            'delete': {'user_id': '$uid'}
        },
    },
    {
        'name': 'user',
        'module': 'people',
        'permissions': {
            'allow': ['get', 'post', 'put', 'delete'],
            'get': {'user_id': '$uid'},
            'post': {'user_id': '$uid'},
            'put': {
                'query': {'user_id': '$uid'},
                'set': {}

            },
            'delete': {'user_id': '$uid'}

        },
    },
    {
        'name': 'user',
        'module': 'dashboard',
        'permissions': {
            'allow': ['get'],
            'get': {'user_id': '$uid'},
        },
    },
    {
        'name': 'admin',
        'module': 'get_tasks',
        'permissions': {
            'allow': ['get'],
            'get': {},
        },
    },
    {
        'name': 'user',
        'module': 'save_task_query',
        'permissions': {
            'allow': ['get', 'post', 'put', 'delete'],
            'get': {'user_id': '$uid'},
            'post': {'user_id': '$uid'},
            'put': {
                'query': {'user_id': '$uid'},
                'set': {}

            },
            'delete': {'user_id': '$uid'}

        },
    },
    {
        'name': 'user',
        'module': 'resend_activation_code',
        'permissions': {
            'allow': ['get'],
            'get': {},
        },
    },
    {
        'name': 'user',
        'module': 'delete_account',
        'permissions': {
            'allow': ['delete'],
            'delete': {},
        },
    },





])

__author__ = 'Shahab Qazavi'

import inspect
from sms import sms
from base_handler import BaseHandler, Colors
from publics import PrintException, create_md5, encode_token, db, random_digits, send_sms,\
    send_registration_email, consts, send_notification
from datetime import datetime , timedelta
from bson import ObjectId
import json


class Register(BaseHandler):

    def init_method(self):
        self.tokenless = True
        self.required = {
            'post': ['mobile', 'password', 'name', 'family']
        }
        self.inputs = {
            'post': ['mobile', 'password', 'name', 'family', 'email', 'device_info', 'pic', 'tasks_figure']
        }

    def before_post(self):
        try:
            self.method = 'users'
            col_users = db()['users']
            if col_users.count({'mobile': self.params['mobile']}) > 0:
                self.set_output('user', 'mobile_exists')
                return False
            elif self.params.get('email') is not None:
                if col_users.count({'email': self.params['email']}) > 0:
                    self.set_output('user', 'email_exists')
                    return False
            # if col_users.count({'device_info.mac_address': self.params['device_info']['mac_address']}) > 0:
            #     self.set_output('user', 'multiple_registration')
            #     return False

            self.params['activation_code'] = random_digits()
            self.params['confirmed'] = False
            self.params['role'] = 'user'
            self.params['tasks_figure'] = 'line' if 'tasks_figure' not in self.params else self.params['tasks_figure']
            self.params['password_pure'] = self.params['password']
            self.params['password'] = create_md5(self.params['password'])
            # .encode('utf-8')
        except:
            PrintException()
            return False
        return True

    def after_post(self):
        try:
            send_sms(sms['users']['registration_successful'][self.locale] % self.params['activation_code'],
                     self.params['mobile'])

        except:
            PrintException()
        return True

    def post(self, *args, **kwargs):
        self.Print('%s fired' % inspect.stack()[0][3], Colors.GRAY)
        try:
            self.method = 'post'
            if self.pre_post():
                self.params.update(self.added_data)
                col_users = db()['users']
                self.params['create_date'] = datetime.now()
                self.params['last_update'] = datetime.now()
                id = str(col_users.insert(self.params))
                self.id = id
                self.output['data']['item']['id'] = id
                # self.output['token'] = encode_token({'user_id': self.id}).decode()
                self.set_output('public_operations', 'successful')
                self.after_post()
            if consts.LOG_ACTIVE:
                self.log_status(self.output)
        except:
            PrintException()
            self.set_output('public_operations', 'failed')
        self.kmwrite()


class ActiveAccount(BaseHandler):

    def init_method(self):
        self.tokenless = True
        self.casting['ints'] = []
        self.casting['floats'] = []
        self.casting['dics'] = []
        self.casting['lists'] = []
        self.required = {
            'post': ['mobile', 'activation_code']
        }
        self.inputs = {
            'post': ['mobile', 'activation_code'],
        }

    def before_post(self):
        self.Print('%s fired' % inspect.stack()[0][3], Colors.GRAY)
        try:
            col_users = self.db['users']
            update_result = col_users.update({'mobile': self.params['mobile'],
                                              'activation_code': self.params['activation_code']},
                                             {'$set': {'confirmed': True}})
            if update_result['nModified'] == 1:
                user_info = col_users.find_one({
                    'mobile': self.params['mobile'],
                })
                # self.output['token'] = encode_token(
                #     {'user_id': str(user_info['_id'])}).decode()

                # send_notification('welcome', str(user_info['_id']), '',
                #                   consts.NOTIFICATIONS['users']['welcome']['title'][self.locale],
                #                   consts.NOTIFICATIONS['users']['welcome']['description'][self.locale], user=None,
                #                   delayed=False)
                self.set_output('user', 'activate_account')
            else:
                self.set_output('user', 'mobile_not_activated')

            self.allow_action = False
            return True
        except:
            PrintException()
            return False


class Login(BaseHandler):
    def init_method(self):
        self.tokenless = True
        self.required= {
            'post': ['mobile', 'password']
        }
        self.inputs = {
            'post': ['mobile', 'password']
        }

    def before_post(self):
        self.Print('%s fired' % inspect.stack()[0][3], Colors.GRAY)
        try:
            col_users = db()['users']
            col_user_logins = db()['user_logins']
            user_info = col_users.find_one(
                {'mobile': self.params['mobile'],
                 'password': create_md5(self.params['password'])})
            if user_info is None:
                self.set_output('user', 'login_failed')
            else:
                self.user_role = user_info['role']
                user_info = self.after_get_one(user_info)
                self.user_id = user_info['id']
                if user_info['confirmed']:
                    self.user_id = user_info['id']
                    self.set_output('public_operations', 'successful')
                    self.token = encode_token({'user_id': self.user_id, 'role': self.user_role}).decode('ascii')
                    self.output['token'] = self.token
                    last_login = col_user_logins.find({'mobile': self.params['mobile']}).sort('date', -1).limit(1)
                    if last_login.count() > 0:
                        user_info['last_login'] = str(last_login[0]['date'])
                    else:
                        user_info['last_login'] = ''
                        user_info['first_login'] = str(datetime.now())
                    if 'last_update' in user_info: del user_info['last_update']
                    if 'password_pure' in user_info: del user_info['password_pure']
                    if 'password' in user_info: del user_info['password']
                    if '_id' in user_info: del user_info['_id']
                    self.output['data']['item'] = user_info
                else:
                    self.set_output('user', 'inactive')
        except:
            PrintException()
            self.set_output('public_operations', 'failed')

        try:
            col_user_logins = db()['user_logins']
            col_user_logins.insert({
                'user_id': self.user_id,
                'mobile': self.params.get('mobile'),
                'status': self.status,
                'date': datetime.now(),
                'notes': self.note_id
            })
        except:
            PrintException()
        self.allow_action = False


class Profile(BaseHandler):
    def init_method(self):
        self.inputs = {
            'put': ['name', 'family', 'email', 'password', 'pic', 'nav_color', 'background_color']
        }
        self.inputs = {
            'delete': ['id', 'mobile', 'password']
        }
        self.required = {
            'delete': ['id', 'mobile', 'password']
        }

    def before_get(self):
        self.module = 'users'
        return True

    def before_delete(self):
        try:
            self.method = 'users'
            print(self.params['mobile'])
            print(self.user_id)
            col_users = db()['users']
            col_users.delete_one({'_id': ObjectId(self.params['id']), 'mobile': self.params['mobile'],
                                  'password': create_md5(self.params['password'])})
            self.set_output('public_operations', 'successful')
        except:
            PrintException()
        self.allow_action = False

    def get(self, id=None, *args, **kwargs):
        self.Print('%s fired' % inspect.stack()[0][3], Colors.GRAY)
        try:
            self.method = 'get'
            if self.pre_get():
                try:

                    if len(self.fields) > 0:
                        fields = {}
                        for item in self.fields:
                            fields[item] = 1
                    else:
                        fields = {'name': 1, 'family': 1, 'email': 1, 'pic': 1, 'tasks_figure': 1, 'mobile': 1}
                    col_users = db()['users']
                    # print('-----------------------------')
                    # print(self.user_id)
                    # print(self.fields)
                    # print('-----------------------------')
                    user_info = col_users.find_one({'_id': ObjectId(self.user_id)}, fields)
                    user_info['id'] = str(user_info['_id'])
                    del user_info['_id']
                    col_tasks = db()['tasks']
                    user_tasks = []
                    # for item in col_tasks.find({'user_id': {'$in': [self.user_id]}}):
                    #     del item['last_update']
                    #     del item['create_date']
                    #     del item['user_id']
                    #     # item['create_date'] = str(item['create_date'])
                    #     # item['last_update'] = str(item['last_update'])
                    #     if 'from_date' in item:
                    #         item['from_date'] = str(item['from_date'])
                    #     if 'to_date' in item:
                    #         item['to_date'] = str(item['to_date'])
                    #     item['id'] = str(item['_id'])
                    #     del item['_id']
                    #     user_tasks.append(item)
                    user_people = []
                    col_people = db()['people']
                    for item in col_people.find({'user_id': {'$in': [self.user_id]}}):
                        item['id'] = str(item['_id'])
                        del item['_id']
                        del item['create_date']
                        del item['last_update']
                        del item['user_id']
                        user_people.append(item)
                    self.output['data']['item'] = user_info
                    # self.output['data']['item']['tasks'] = user_tasks
                    self.output['data']['item']['people'] = user_people
                    self.set_output('public_operations', 'successful')
                except:
                    PrintException()
                    self.set_output('field_error', 'id_format')
        except:
            PrintException()
            self.set_output('public_operations', 'failed')
        self.kmwrite()

    def put(self, *args, **kwargs):
        try:
            self.method = 'put'
            self.module = 'users'
            if self.pre_put():
                inputs = ['name', 'family', 'email', 'password', 'pic', 'nav_color', 'background_color', 'tasks_figure']
                count = 0
                for item in self.params:
                    if item not in inputs:
                        count += 1
                if count == 0:
                    need_consistency_update = any(x in self.params for x in ['pic', 'name', 'family'])
                    if 'password' in self.params:
                        self.params['password'] = create_md5(self.params['password'])
                        self.params['password_pure'] = self.params['password']
                    col_users = db()['users']
                    col_users.update({'_id': ObjectId(self.user_id)}, {'$set': self.params})
                    if need_consistency_update:
                        col_people = db()['people']
                        col_tasks = db()['tasks']
                        doc = {}
                        if 'name' in self.params: doc['people.name'] = self.params['name']
                        if 'family' in self.params: doc['people.family'] = self.params['family']
                        if 'pic' in self.params: doc['people.pic'] = self.params['pic']
                        col_tasks.update({'people.id': self.user_id}, {'$set': doc}, multi=True)
                        changes = {}

                        if 'name' in self.params and 'pic' not in self.params:
                            changes['$set'] = {'name':self.params['name']}
                        elif 'pic' in self.params and 'name' not in self.params:
                            changes['$set'] = {'pic':self.params['pic']}
                        elif 'pic' in self.params and 'name' in self.params:
                            changes['$set'] = {'name': self.params['name'], 'pic':self.params['pic']}

                        col_people.update({'user_id': self.user_id}, changes, multi=True)
                else:
                    self.set_output('tasks', 'wrong_params')
                    return False
            self.set_output('public_operations', 'successful')
        except:
            PrintException()
            self.set_output('public_operations', 'failed')
        if consts.LOG_ACTIVE:
            self.log_status(self.output)
        self.after_put()
        self.kmwrite()


class ForgotPassword(BaseHandler):
    def init_method(self):
        self.inputs = {
            'post': ['']
        }
        self.tokenless = True

    def post(self, *args, **kwargs):
        self.Print('%s fired' % inspect.stack()[0][3], Colors.GRAY)
        self.method = 'post'
        if self.pre_post():
            try:
                col_users = db()['users']
                activation_code = random_digits()
                if 'mobile' in self.params:
                    user_info = col_users.find_one({'mobile': self.params['mobile']})
                    if user_info is None:
                        self.set_output('user', 'user_not_exists')
                    else:
                        col_users.update_one({'mobile': self.params['mobile']},
                                                         {'$set': {'activation_code': activation_code}})
                        send_sms(sms['users']['forgot_password'][self.locale] % activation_code, self.params['mobile'])
                        self.set_output('public_operations', 'successful')
                else:
                    self.set_output('public_operations', 'successful')
                self.after_post()

            except:
                PrintException()
                self.set_output('public_operations', 'failed')
        self.kmwrite()


class ResetPassword(BaseHandler):
    def init_method(self):
        self.tokenless = True
        self.required = {
            'post': ['mobile', 'activation_code', 'new_password']
        }
        self.inputs = {
            'post': ['mobile', 'activation_code', 'new_password'],
            'put': ['mobile', 'activation_code', 'new_password']
        }

    def before_post(self):
        self.Print('%s fired' % inspect.stack()[0][3], Colors.GRAY)
        try:
            col_users = db()['users']
            result = col_users.find_one_and_update({
                'mobile': self.params['mobile'],
                # 'pure_password': self.params['old_password'],
                'activation_code': self.params['activation_code']
            },
                {'$set': {'password': create_md5(self.params['new_password']),
                 'password_pure': self.params['new_password']}})
            if result is None:
                self.set_output('user', 'password_reset_failed')
            else:
                self.set_output('public_operations', 'successful')
        except:
            PrintException()
            self.set_output('public_operations', 'failed')
            return False
        self.allow_action = False
        return True


class Tasks(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['title']
        }
        self.inputs = {
            'post': ['title', 'from_date', 'to_date', 'tags', 'color', 'description', 'attachment',
                  'location', 'remind', 'people', 'user_id', 'is_done', 'is_favorite','task_figure']
        }
        self.casting['booleans'] = ['remind','is_done', 'favorite']
        self.casting['dates'] = ['from_date', 'to_date']
        self.casting['lists'] = ['tags', 'people', 'attachment']

    def before_post(self):
        count = 0
        for item in self.params:
            if item not in self.inputs['post']:
                count += 1
        print(self.params)
        if count == 0:
            try:
                if 'from_date' in self.params and 'to_date' in self.params:
                    self.params['from_date'] = datetime.strptime(self.params['from_date'], "%Y-%m-%d %H:%M:%S")
                    self.params['to_date'] = datetime.strptime(self.params['to_date'], "%Y-%m-%d %H:%M:%S")

                elif 'from_date' in self.params and 'to_date' not in self.params:
                    self.params['from_date'] = datetime.strptime(self.params['from_date'], "%Y-%m-%d %H:%M:%S")

                elif 'to_date' in self.params and 'from_date' not in self.params:
                    self.params['to_date'] = datetime.strptime(self.params['to_date'], "%Y-%m-%d %H:%M:%S")

                self.params['is_done'] = False
                self.params['is_favorite'] = False

            except:
                PrintException()
                return False
            return True
        else:
            self.set_output('tasks', 'wrong_params')
            return False

    def before_get(self):
        try:
            col_tasks = db()['tasks']
            if 'id' in self.params:
                task = col_tasks.find_one({'_id': ObjectId(self.params['id'])})
                task['id'] = str(task['_id'])
                task['from_date'] = str(task['from_date'])
                task['to_date'] = str(task['to_date'])
                del task['_id']
                del task['create_date']
                del task['last_update']
                del task['user_id']
                self.output['data']['item'] = task
            else:
                tasks = []
                for user_task in col_tasks.find({'user_id': str(self.user_id)}).sort([('create_date', -1)]):
                    user_task['id'] = str(user_task['_id'])
                    del user_task['_id']
                    user_task['from_date'] = str(user_task['from_date'])
                    user_task['to_date'] = str(user_task['to_date'])
                    del user_task['create_date']
                    del user_task['last_update']
                    del user_task['user_id']
                    tasks.append(user_task)
                # tasks = sorted(tasks, reverse=True)
                self.output['data']['list'] = tasks
            self.set_output('public_operations', 'successful')
        except:
            PrintException()
            return False
        self.allow_action = False
        return True

    def before_delete(self):
        try:
            col_tasks = db()['tasks']
            if col_tasks.find_one({'_id': ObjectId(self.params['id'])}):
                col_tasks.delete_one({'_id': ObjectId(self.params['id'])})
                self.set_output('public_operations', 'successful')
            else:
                self.set_output('public_operations', 'record_not_found')
                return False
        except:
            PrintException()
            return False
        self.allow_action = False
        return True

    def before_put(self):
        try:
            inputs = ['title', 'from_date', 'to_date', 'tags', 'color', 'description', 'attachment',
                  'location', 'remind', 'people', 'is_done', 'is_favorite','id']
            print(self.params)
            count = 0
            for item in self.params:
                if item not in inputs:
                    count += 1
            if count == 0:
                if 'from_date' in self.params and 'to_date' in self.params:
                    self.params['from_date'] = datetime.strptime(self.params['from_date'], "%Y-%m-%d %H:%M:%S")
                    self.params['to_date'] = datetime.strptime(self.params['to_date'], "%Y-%m-%d %H:%M:%S")

                elif 'from_date' in self.params and 'to_date' not in self.params:
                    self.params['from_date'] = datetime.strptime(self.params['from_date'], "%Y-%m-%d %H:%M:%S")

                elif 'to_date' in self.params and 'from_date' not in self.params:
                    self.params['to_date'] = datetime.strptime(self.params['to_date'], "%Y-%m-%d %H:%M:%S")
            else:
                self.set_output('tasks', 'wrong_params')
                return False
        except:
            PrintException()
            return False
        return True


class People(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['name', 'pic', 'mobile']
        }
        self.inputs = {
            'post': ['name', 'pic', 'mobile']
        }

    def before_get(self):
        try:
            col_people = db()['people']
            people = []
            for item in col_people.find({'user_id': self.user_id}).sort('create_date', -1):
                print(item)
                item['id'] = str(item['_id'])
                del item['_id']
                del item['create_date']
                del item['last_update']
                del item['user_id']
                people.append(item)
            print('------------------------')
            print(people)
            self.output['data']['list'] = people
            self.set_output('public_operations', 'successful')
        except:
            PrintException()
            return False
        self.allow_action = False
        return True





class SaveTaskQuery(BaseHandler):
    def init_method(self):
        self.required = {
            'post': ['name']
        }
        self.inputs = {
            'post': ['tags', 'amount', 'time', 'from', 'type_date', 'name']
        }


class Dashboard(BaseHandler):
    def before_get(self):
        try:
            date_now = datetime.strptime(str(datetime.now())[:10], "%Y-%m-%d %H:%M:%S")
            queries = {}
            col_saved_tasks = db()['save_task_query']
            for item in col_saved_tasks.find({'user_id': self.user_id}):
                query = {}
                if 'tags' in item:
                    query['tags'] = {'$in': item['tags']}
                if 'from' in item and item['from'] == 'now':
                    print(item)
                    if 'type_date' in item and item['type_date'] == 'to_date':
                        print('injaaaaaa')
                        query[item['type_date']] = date_now + timedelta(
                            days=item['amount'])
                    elif 'type_date' in item and item['type_date'] == 'from_date':
                        query[item['type_date']] = date_now - timedelta(
                            days=item['amount'])
                if 'time' in item and item['time'] != 'now':
                    if 'type_date' in item:
                        if 'from' in item and item['from'] != 'now':
                            if 'amount' in item:
                                if item['time'] == 'pass':
                                    query[item['type_date']] = {
                                        '$lte': datetime.strptime(item['from'], "%Y-%m-%d %H:%M:%S") - timedelta(
                                            days=item['amount'])}
                                elif item['time'] == 'future':
                                    query[item['type_date']] = {
                                        '$gte': datetime.strptime(item['from'], "%Y-%m-%d %H:%M:%S") + timedelta(
                                            days=item['amount'])}
                        elif 'from' not in item:
                            if 'amount' in item and 'time' in item:
                                if item['time'] == 'pass':
                                    query[item['type_date']] = {
                                        '$lte': date_now - timedelta(
                                            days=item['amount'])}
                                elif item['time'] == 'future':
                                    query[item['type_date']] = {
                                        '$gte': date_now + timedelta(
                                            days=item['amount'])}

                elif 'time' in item and item['time'] == 'now':
                    # date = item['type_date'] if 'type_date' in item else 'to_date'
                    query['$and'] = [{'from_date': {'$lte': date_now}}, {'to_date': {'$gte': date_now}}]
                queries[item['name']] = query
            print(queries)
            results = {}
            col_tasks = db()['tasks']
            for items in queries:
                result_list = []
                for item in col_tasks.find(queries[items]):
                    item['id'] = str(item['_id'])
                    del item['_id']
                    if 'create_date' in item:
                        item['create_date'] = str(item['create_date'])
                    if 'last_update' in item:
                        item['last_update'] = str(item['last_update'])
                    if 'from_date' in item:
                        item['from_date'] = str(item['from_date'])
                    if 'to_date' in item:
                        item['to_date'] = str(item['to_date'])
                    result_list.append(item)
                results[items] = result_list
            self.set_output('public_operations', 'successful')
            self.output['data']['list'] = results
        except:
            PrintException()
        self.allow_action = False


class DeleteUser(BaseHandler):
    def init_method(self):
        self.inputs = {
            'delete': ['id','mobile','password']
        }
        self.required = {
            'delete': ['id','mobile','password']
        }

    def before_delete(self):
        try:
            self.method = 'users'
            print(self.params['mobile'])
            print(self.user_id)
            col_users = db()['users']
            col_users.delete_one({'_id': ObjectId(self.params['id']),'mobile':self.params['mobile'],
                                  'password':create_md5(self.params['password'])})
            self.set_output('public_operations', 'successful')
        except:
            PrintException()
        self.allow_action = False

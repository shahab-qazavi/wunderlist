from handlers.handlers import Register, ActiveAccount, Profile, Login, ResetPassword, ForgotPassword,\
    People, Tasks, Dashboard, SaveTaskQuery



url_patterns = [
    ("/v1/active_account", ActiveAccount, None, "active_account_v1"),
    ("/v1/register", Register, None, "register_v1"),
    ("/v1/login", Login, None, "login_v1"),
    ("/v1/profile/?([^/]+)?", Profile, None, "profile_v1"),
    ("/v1/reset_password/?([^/]+)?", ResetPassword, None, "reset_password_v1"),
    ("/v1/forgot_password/?([^/]+)?", ForgotPassword, None, "forgot_password_v1"),
    ("/v1/tasks/?([^/]+)?", Tasks, None, "tasks_v1"),
    ("/v1/people/?([^/]+)?", People, None, "people_v1"),
    ("/v1/dashboard/?([^/]+)?", Dashboard, None, "dashboard_v1"),
    ("/v1/save_task_query/?([^/]+)?", SaveTaskQuery, None, "save_task_query_v1"),

]

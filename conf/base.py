# minsize=1, maxsize=10, echo=False, pool_recycle=-1,
#                 loop=None, **kwargs
db_conf = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'charset': 'utf8',
    'autocommit': True,
    'db': 'sayhello'
}

ERROR_CODE = {
    '0': 'ok',
    '1001': 'request argument incorrect',
    '1002': 'user existed already',
    '1003': 'user had not signed up',
    '1004': 'wrong password'
}

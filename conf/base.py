db_conf = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',
    'charset': 'utf8',
    'autocommit': True,
    'db': 'sayhello'
}
redis_conf = {
    'address': 'redis://localhost',
    'password': 'password',
    'encoding': 'utf-8',
}

ERROR_CODE = {
    '0': 'ok',
    '1001': 'request argument incorrect',
    '1002': 'user existed already',
    '1003': 'user had not signed up',
    '1004': 'wrong password',
    '1005': 'logout already',
    '1006': 'login already',
    '1007': 'had not logged in',
}

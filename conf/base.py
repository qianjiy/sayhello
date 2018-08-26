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
    '1002': 'the name has been used',
    '1003': 'user did not signed up',
    '1004': 'wrong password',
    '1005': 'unknown error',
    '1006': 'valid name format',
    '1007': 'password should contains at least 6 characters'
}

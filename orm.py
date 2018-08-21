import aiomysql
from log.log import get_logger
from conf.base import db_conf

logger = get_logger('db')


async def init_db(loop):
    await create_pool(loop)


async def create_pool(loop):
    logger.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(loop=loop, **db_conf)


async def select(sql, args, size=None):
    global __pool
    async with __pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                res = await cur.fetchmany(size)
            else:
                res = await cur.fetchall()
            return res


async def execute(sql, args):
    # insert update delete
    global __pool
    # print(sql, args)
    async with __pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            except BaseException as e:
                raise
            return affected


class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default


class String(Field):

    def __init__(self, name=None, primary_key=False, default=None, length=50):
        ddl = 'varchar(%d)' % length
        super().__init__(name, ddl, primary_key, default)


class Integer(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class Boolean(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class Float(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


def create_args_str(n):
    return ','.join(['%s'] * n)


class ModelClass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        table_name = attrs.get('__table__', None) or name
        mappings = dict()
        fields = []
        primary_key = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primary_key = k
                else:
                    fields.append(k)
        if not primary_key:
            raise RuntimeError('Primary key not found.')
        escaped_fields = list(map(lambda s: '`%s`' % (mappings.get(s).name or s), fields))
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__mappings__'] = mappings
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primary_key, ','.join(escaped_fields), table_name)
        attrs['__insert__'] = 'insert into `%s` (`%s`, %s)values (%s)' % (
            table_name, primary_key, ','.join(escaped_fields), create_args_str(len(fields) + 1))
        attrs['__update__'] = 'update `%s`' % table_name
        attrs['__delete__'] = 'delete from `%s` where' % (table_name)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelClass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute %s" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if not value:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value

    @classmethod
    async def find(cls, where: dict, size=1):
        # -1 to find all
        if size == -1:
            size = None
        if len(where) == 0:
            res = await select(cls.__select__, [], size)
        else:
            try:
                condition = list(map(lambda s: '`%s` = ?' % (cls.__mappings__.get(s).name or s), where.keys()))
            except AttributeError:
                raise AttributeError('%s does not have exact attributes in %s' % (cls.__name__, list(where.keys())))
            res = await select('%s where %s' % (cls.__select__, ','.join(condition)), list(where.values()), size)
        if len(res) == 0:
            return None
        else:
            return [cls(**d) for d in res]

    @classmethod
    async def find_first(cls, where={}):
        res = await cls.find(where=where, size=1)
        if res:
            return res[0]
        else:
            return None

    @classmethod
    async def find_all(cls, where={}):
        return await cls.find(where=where, size=-1)

    @classmethod
    async def delete(cls, where: dict):
        if len(where) == 0:
            return 0
        try:
            condition = list(map(lambda s: '`%s` = ?' % (cls.__mappings__.get(s).name or s), where.keys()))
        except AttributeError:
            raise AttributeError('%s does not have exact attributes in %s' % (cls.__name__, list(where.keys())))
        res = await execute('%s %s' % (cls.__delete__, ','.join(condition)), list(where.values()))
        return res

    # attrs['__update__'] = 'update `%s` ' % table_name

    @classmethod
    async def change(cls, where: dict, update: dict):
        try:
            up = list(map(lambda s: '`%s`=?' % (cls.__mappings__.get(s).name or s), update.keys()))
            condition = list(map(lambda s: '`%s`=?' % (cls.__mappings__.get(s).name or s), where.keys()))
        except AttributeError:
            raise AttributeError(
                '%s does not have exact attributes in %s' % (cls.__name__, list(where.keys() + list(update.keys()))))
        res = await execute('%s set %s where %s' % (cls.__update__, ','.join(up), ','.join(condition)),
                            list(update.values()) + list(where.values()))
        return res

    async def save(self):
        args = [self.getValueOrDefault(self.__primary_key__)]
        args += list(map(self.getValueOrDefault, self.__fields__))
        res = await execute(self.__insert__, args)
        if res != 1:
            logger.warning('failed to insert record: affected rows: %s' % res)
            return False
        return True

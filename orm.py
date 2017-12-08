#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from macpath import join

__author__ = 'mazhwei'

import aiomysql

import asyncio, logging
logging.basicConfig(level=logging.INFO)


def log(sql,args=()):
    logging.info('SQL: %s'%sql)


async def create_pool(loop, **kw):
    logging.info('create database connect pool..... ')
    global  __pool
    __pool = await aiomysql.create_pool(
        minsize = kw.get('minsize', 1),
        maxsize = kw.get('maxsize', 10),
        loop = loop,
        host = kw.get('host','localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password = kw['password'],
        db = kw['db'],
        charset = kw.get('charset','utf8'),
        autocommit = kw.get('autocommit',True)
    )


async def create_db(name):
    global __pool
    with (await __pool) as conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute('drop database if exists '+name)
            await cursor.execute('create database '+name)
        except BaseException as e:
            await conn.rollback()
            print('create database failed, mysql error:%d:%s'%(e.args[0],e.args[1]))
        finally:
            cursor.close()


async def drop_db(host, user, pw=None, name=None):
    global __pool
    with (await __pool) as conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute('drop database if exists '+name)
        except BaseException as e:
            print('create database failed, mysql error:%d:%s'%(e.args[0],e.args[1]))
        finally:
            cursor.close()
            

async def create_table(sql):
    global __pool                
    with (await __pool) as conn:
        try:
            cursor = await conn.cursor()
            ret = await cursor.execute(sql)
            if ret is not None:
                print('executed succ')
            else:
                print('executed failed')
        except aiomysql.Error as e:
            raise e
        finally:
            await cursor.close()
        
async def isExistDB(name):
    global __pool
    with (await __pool) as conn:
        try:
            cur = await conn.cursor(aiomysql.DictCursor)
            await cur.execute('SELECT * FROM information_schema.SCHEMATA where SCHEMA_NAME="%s"'%name)
            rs = await cur.fetchall()
            cur.close()
            if rs:
                return True
            else:
                return False
        except BaseException as e:
            logging.warning('judge db:%s whether exists is failed!\n error number%s:%s'%(name, e.args[0],e.args[1]))
            return False

async def isExistTBL(db, cls):
    global __pool
    with  (await __pool) as conn:
        try:
            cur = await conn.cursor(aiomysql.DictCursor)
            await cur.execute('SELECT TABLE_NAME FROM information_schema.TABLES where TABLE_SCHEMA="%s" and TABLE_NAME="%s"'%(db,cls.__table__))
            rs = await cur.fetchall()
            cur.close()
            if rs:
                return True
            else:
                return False
        except BaseException as e:
            logging.warning('judge table(%s:%s) whether exists is failed!\n error number %s:%s'%(db, cls.__table__, e.args[0],e.args[1]))
            return False


async def select(sql, args, size=None):
    log(sql,args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?','%s'),args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('row return count:%s'%len(rs))
        return rs


async def execute(sql, args, autocommit=True):
    log(sql)
    global __pool
    with (await __pool) as conn:
        if not autocommit:
            await conn.begin()
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?', '%s'), args)
            affect = cur.rowcount
            await cur.close()
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise e
        return affect


def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

class Field(object):

    def __init__(self, name, column_type, primary_key, default, isNull = None):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
        self.isNull = isNull


    def __str__(self):
        return '<%s,%s:%s>'%(self.__class__.__name__, self.column_type, self.name)


class StringField(Field):

    def __init__(self, name=None, ddl='varchar(100)', primary_key=False, default=None, isNull = ''):
        super().__init__(name,ddl,primary_key,default,isNull)


class BooleanField(Field):

    def __init__(self, name=None, default=False, isNull=''):
        super().__init__(name,'bool',False,default,isNull)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0,isNull = ''):
        super().__init__(name, 'bigint', primary_key, default,isNull)

class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0, isNull = ''):
        super().__init__(name, 'float', primary_key, default, isNull)

class TextField(Field):

    def __init__(self, name=None, default=0, isNull = ''):
        super().__init__(name, 'text', False, default, isNull)

class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        tableName = attrs.get('__table__', None) or name
        logging.info('found Model: %s (table: %s)'%(name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mappings: %s ==> %s'%(k,v))
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise BaseException('Duplicate primary key for Field: %s'%k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise BaseException('primary key is not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`'%f, fields))
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__field__'] = fields
        attrs['__select__'] = 'select `%s`,%s from `%s`'%(primaryKey,','.join(fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s,`%s`) VALUES (%s)'%(tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields)+1))
        attrs['__update__'] = 'update `%s` set %s WHERE `%s`= ?'%(tableName,','.join(map(lambda f: '`%s`=?'%(mappings.get(f).name or f),fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` WHERE `%s`=?'%(tableName,primaryKey)
        return type.__new__(cls, name, bases,attrs)


class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'"%key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self,key,None)

    def getValueOrDefault(self, key):
        value = getattr(self,key,None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.info('using default value for %s: %s'%(key,str(value)))
                setattr(self, key, value)
        return value


    @classmethod
    async def findall(cls, where=None, args=None, **kw):
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy',None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s'%str(limit))
        rs = await select(' '.join(sql),args)
        return [cls(**r) for r in rs]


    @classmethod
    async def findNumer(cls, selectField, where=None, args=None):
        sql = ['select `%s`_num_ from `%s`'%(selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls,prikey):
        sql = '%s where `%s`=?'%(cls.__select__, cls.__primary_key__)
        rs = await select(sql,[prikey],1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])


    async def save(self):
        try:
            args = list(map(self.getValueOrDefault, self.__field__))
            args.append(self.getValueOrDefault(self.__primary_key__))
            print(args)
            print(self.__insert__)
            rows = await execute(self.__insert__, args)
            if rows != 1:
                logging.warning('failed to insert record: affect rows: %s'%rows)
        except BaseException as e:
            raise e


    async def update(self):
        args = list(map(self.getValueOrDefault, self.__field__))
        args.append(self.getValue(self.__primary_key__))
        try:
            rows = await execute(self.__update__, args)
            if rows != 1:
                logging.warning('failed to update record: affect rows:%s'%rows)
        except BaseException as e:
            raise e


    async def remove(self):
        args = self.getValue(self.__primary_key__)
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to remove record by primary key: affect rows:%s'%rows)
            
            
    async def create_self(self):
        try:
            columns = []
            for k, v in self.__mappings__.items():
                columns.append('`%s` %s %s'%(k, v.column_type, v.isNull))
            columns.append('primary key (`%s`)'%self.__primary_key__)
            sql = 'create table %s (%s) engine=innodb default charset=utf8'%(self.__table__, ','.join(columns))    
            await create_table(sql)
        except BaseException as e:
            raise e

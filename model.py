#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'mazhiwei'

import time, uuid, pymysql

from orm import Model, StringField, BooleanField, FloatField, TextField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'user'

    id = StringField(ddl='varchar(50)', primary_key=True, default=next_id(), isNull='not null')
    email = StringField(ddl='varchar(50)', isNull='not null')
    passwd = StringField(ddl='varchar(50)', isNull='not null')
    admin = BooleanField(isNull='not null')
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)', isNull='not null')
    created_at = FloatField(default=time.time, isNull='not null')


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)', isNull='not null')
    user_id = StringField(ddl='varchar(50)', isNull='not null')
    user_name = StringField(ddl='varchar(50)', isNull='not null')
    user_image = StringField(ddl='varchar(500)', isNull='not null')
    name = StringField(ddl='varchar(50)', isNull='not null')
    summary = StringField(ddl='varchar(200)', isNull='not null')
    content = TextField(isNull='not null')
    created_at = FloatField(default=time.time, isNull='not null')


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)', isNull='not null')
    blog_id = StringField(ddl='varchar(50)', isNull='not null')
    user_id = StringField(ddl='varchar(50)', isNull='not null')
    user_name = StringField(ddl='varchar(50)', isNull='not null')
    user_image = StringField(ddl='varchar(500)', isNull='not null')
    content = TextField(isNull='not null')
    created_at = FloatField(default=time.time, isNull='not null')


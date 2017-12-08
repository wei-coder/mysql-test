#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'mazhiwei'

import model
import orm
import aiomysql
import asyncio
import logging; logging.basicConfig(level=logging.INFO)
from config import db

async def init(loop):
    user = model.User(id='00000002', name='ma'.strip(' '), email='hw@email.com', passwd='12345', image='www.baidu.com')
    #blog = model.Blog()
    #comment = model.Comment()
    try:
        await orm.create_pool(loop = loop, **db)
    except aiomysql.Error as e:
        logging.warning('create pool is failed! errno:%s '%e.message)
        return
    try:
        await user.save()
        #await blog.create_self()
        #await comment.create_self()
    except BaseException as e:
        logging.warning('create table is failed! error message:%s'%(e.args[0]))

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop = loop))

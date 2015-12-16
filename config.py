#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

bindPort = 8888

dataDir = "../../../data"
tempDir = "../../../temp"

tasksDir = "tasks"
tasksFilename = "task.json"

jobCheckInterval = 0.5

redisQueuePrefix = "IDEA:"
redisQueueTimeout = 3600

redisCachePrefix = "IDEA:"
redisCacheTimeout = 3600

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

bindPort = 8888

dataDir = "data"
binDir = "bin"
tempDir = "temp"

tasksDir = "tasks"
tasksFilename = "tasks.json"

taskList = ["topic", "topk"]
jobCheckInterval = 0.5

redisQueuePrefix = "gena_miner-service:"
redisQueueTimeout = 3600

redisCachePrefix = "gena_miner-service:"
redisCacheTimeout = 3600

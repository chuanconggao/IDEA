#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json

with open("config.json") as f:
    j = json.load(f)

    bindPort = j["port"]

    tasksDir = j["tasksDir"]

    redisHost = j["redis"]["host"]
    redisPassword = j["redis"]["password"]

tasksFilename = "task.json"

jobCheckInterval = 0.5

redisQueuePrefix = "IDEA:"
redisQueueTimeout = 3600

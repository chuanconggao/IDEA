#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import json

from flask import Flask, jsonify
from flask.ext.api import status
from flask.ext.cors import CORS
from flask.ext.cache import Cache
from flask.ext.compress import Compress

from task import Task
from job import startJob
from config import bindPort, redisCachePrefix, redisCacheTimeout, tasksDir, tasksFilename

app = Flask("gena_miner-service")
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': redisCachePrefix + "service:",
    'CACHE_DEFAULT_TIMEOUT': redisCacheTimeout
})
# cache = Cache(app, config={
    # 'CACHE_TYPE': 'null'
# })
CORS(app)
Compress(app)

sys.path.append(tasksDir)

with open(tasksFilename) as f:
    tasks = {
        x["name"]: Task(x)
        for x in json.load(f)
    }

@app.route('/<task_name>/', methods=['POST'])
def parseTask(task_name):
    if task_name not in tasks:
        return jsonify(error=status.HTTP_404_NOT_FOUND)

    return startJob(tasks[task_name])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=bindPort, threaded=True, debug=True)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path
import json

from flask import Flask, jsonify
from flask.ext.api import status
from flask.ext.cors import CORS
from flask.ext.compress import Compress

from task import getTaskNames, Task
from job import startJob
from config import bindPort, tasksDir, tasksFilename

app = Flask("IDEA")
CORS(app)
Compress(app)

tasks = {}

def _loadTasks():
    tasks.clear()

    for t in getTaskNames():
        d = os.path.join(tasksDir, t)
        with open(os.path.join(d, tasksFilename)) as f:
            j = json.load(f)
            tasks[j["name"]] = Task(j)

_loadTasks()

@app.route('/init/', methods=['GET'])
def loadTasks():
    _loadTasks()

    return jsonify(success=True)

@app.route('/list/', methods=['GET'])
def listTasks():
    return jsonify(result=[
        {
            "name": x.name,
            "args": x.args,
            "description": x.description,
        }
        for x in tasks.itervalues()
    ])

@app.route('/task/<task_name>/', methods=['POST'])
def runTask(task_name):
    if task_name not in tasks:
        return jsonify(error=status.HTTP_404_NOT_FOUND)

    return startJob(tasks[task_name])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=bindPort, threaded=False, debug=True)

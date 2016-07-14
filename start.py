#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage:
    GET (/ | /help)
        Show this help.

    GET /refresh
        Reload tasks.

    GET /list
    GET /tasks
        List tasks.

    GET /tasks/<name>
        Show task <name>.
    POST /tasks/<name>
        Run task <name>, with the arguments posted in JSON.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import os.path
import json
from collections import OrderedDict

from flask import Flask, jsonify, request
from flask_api import status
from flask_cors import CORS
from flask_compress import Compress

from task import getTaskNames, Task
from job import startJob
from config import bindPort, tasksDir, taskFilename

app = Flask("IDEA")
CORS(app)
Compress(app)

tasks = {}

def _loadTasks():
    tasks.clear()

    for t in getTaskNames():
        d = os.path.join(tasksDir, t)
        with open(os.path.join(d, taskFilename)) as f:
            j = json.load(f, object_pairs_hook=OrderedDict)
            tasks[j["name"]] = Task(j)

_loadTasks()

@app.route('/', methods=['GET'])
@app.route('/help', methods=['GET'])
def showHelp():
    return __doc__

@app.route('/refresh', methods=['GET'])
def loadTasks():
    _loadTasks()

    return jsonify(success=True)

def _getDescription(task):
    return {
        "name": task.name,
        "args": task.args,
        "description": task.description,
    }

@app.route('/list', methods=['GET'])
@app.route('/tasks', methods=['GET'])
def listTasks():
    return jsonify(tasks=[
        _getDescription(task) for task in tasks.itervalues()
    ])

@app.route('/tasks/<task_name>', methods=['GET', 'POST'])
def runTask(task_name):
    if task_name not in tasks:
        return jsonify(message="Task does not exist."), status.HTTP_404_NOT_FOUND

    task = tasks[task_name]
    if request.method == 'GET':
        return jsonify(task=_getDescription(task))
    elif request.method == 'POST':
        return startJob(task)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=bindPort, threaded=False, debug=True)

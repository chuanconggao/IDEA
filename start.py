#!/usr/bin/env python3

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

import os
import os.path
import json

from sanic import response
from sanic import Sanic
from flask_api import status
from sanic_cors import CORS
from sanic_compress import Compress

from task import getTaskNames, Task
from job import startJob
from config import bindPort, tasksDir, taskFilename

app = Sanic("IDEA")
app.config.LOGO = ""
CORS(app)
Compress(app)

tasks = {}

def __loadTasks():
    tasks.clear()

    for t in getTaskNames():
        d = os.path.join(tasksDir, t)
        with open(os.path.join(d, taskFilename)) as f:
            j = json.load(f)
            tasks[j["name"]] = Task(j)


__loadTasks()

@app.route('/')
@app.route('/help')
async def showHelp(request):
    return response.text(__doc__)


@app.route('/refresh')
async def loadTasks(request):
    __loadTasks()

    return response.json({
        "success": True
    })


def __getDescription(task):
    return {
        "name": task.name,
        "args": task.args,
        "description": task.description,
    }


@app.route('/list')
@app.route('/tasks')
async def listTasks(request):
    return response.json({
        "tasks": [
            __getDescription(task) for task in tasks.values()
        ]
    })


@app.route('/tasks/<task_name>', methods=['GET', 'POST'])
async def runTask(request, task_name):
    if task_name not in tasks:
        return response.json({
            "message": "Task does not exist."
        }, status=status.HTTP_404_NOT_FOUND)

    task = tasks[task_name]
    if request.method == 'GET':
        return response.json({
            "task": __getDescription(task)
        })
    elif request.method == 'POST':
        return await startJob(request, task)

    return response.json({
        "message": "Unsupported method."
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=bindPort, debug=True)

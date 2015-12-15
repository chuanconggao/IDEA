#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from time import sleep

from rq import Queue
from redis import Redis
from flask import jsonify, request
from flask.ext.api import status

from config import taskList, redisQueuePrefix, redisQueueTimeout

connection = Redis()
queues = {
    task: Queue(
        redisQueuePrefix + task,
        connection=connection,
        default_timeout=redisQueueTimeout
    )
    for task in taskList
}

def verifyRequest(method, contentType):
    if request.method != method:
        return (False, status.HTTP_405_METHOD_NOT_ALLOWED)

    if contentType is not None and request.headers['Content-Type'] != contentType:
        return (False, status.HTTP_406_NOT_ACCEPTABLE)

    return (True, None)

def startJob(task, func, argStrs):
    def parseArgs(j, argStrs):
        return [j[s] for s in argStrs]

    (verified, error) = verifyRequest('POST', 'application/json')
    if not verified:
        return jsonify(error=error)

    job = queues[task].enqueue(func, *parseArgs(request.json, argStrs))

    while not job.is_failed and job.result is None:
        sleep(1)

    if job.is_failed:
        return jsonify(error=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return jsonify(result=job.result)

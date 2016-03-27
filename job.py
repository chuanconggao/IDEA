#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from time import sleep
import zlib

from rq import Queue
from redis import Redis
from flask import jsonify, request
from flask.ext.api import status
import msgpack

from task import getTaskNames
from config import jobCheckInterval, redisHost, redisPassword, redisQueuePrefix, redisQueueTimeout

connection = Redis(host=redisHost, password=redisPassword)
queues = {
    task: Queue(
        redisQueuePrefix + task,
        connection=connection,
        default_timeout=redisQueueTimeout
    )
    for task in getTaskNames()
}

def verifyRequest(method, contentType):
    if request.method != method:
        return status.HTTP_405_METHOD_NOT_ALLOWED

    if contentType is not None and request.headers['Content-Type'] != contentType:
        return status.HTTP_406_NOT_ACCEPTABLE

    return None

def startJob(task):
    def parseArgs(j, argStrs):
        return [j[s] for s in argStrs]

    compress = request.args.get('compress') == 'true'
    error = verifyRequest('POST', 'application/octet-stream' if compress else 'application/json')
    if error is not None:
        return jsonify(error=True), error

    job = queues[task.name].enqueue(
        task.func,
        *parseArgs(
            msgpack.unpackb(zlib.decompress(request.get_data())) if compress else request.json,
            task.args
        )
    )

    runtime = 0
    while not job.is_failed and job.result is None:
        sleep(jobCheckInterval)
        runtime += jobCheckInterval

    return (
        jsonify(error=True), status.HTTP_500_INTERNAL_SERVER_ERROR if job.is_failed
        else jsonify(result=job.result, runtime=runtime)
    )

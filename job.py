#!/usr/bin/env python3

import asyncio
import zlib

from rq import Queue
from redis import Redis
from sanic import response
from flask_api import status
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

def verifyRequest(request, method, contentType):
    if request.method != method:
        return status.HTTP_405_METHOD_NOT_ALLOWED

    if contentType is not None and request.headers['Content-Type'] != contentType:
        return status.HTTP_406_NOT_ACCEPTABLE

    return None


def decompress(d):
    return msgpack.unpackb(zlib.decompress(d), encoding='utf-8')


async def startJob(request, task):
    compress = request.args.get('compress') == 'true'

    error = verifyRequest(request, 'POST', 'application/octet-stream' if compress else 'application/json')
    if error is not None:
        return response.json({
            "message": "Invalid request parameters."
        }, status=error)

    try:
        job = queues[task.name].enqueue(
            task.func,
            **{
                s: (decompress(request.body) if compress else request.json)[s]
                for s in task.args
            }
        )
    except Exception as e:
        return response.json({
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    runtime = 0
    while not job.is_failed and job.result is None:
        await asyncio.sleep(jobCheckInterval)
        runtime += jobCheckInterval

    if job.is_failed:
        return response.json({
            "message": "Fail to execute the task."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response.json({
        "result": job.result,
        "runtime": runtime
    })

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask, jsonify, request
from flask.ext.api import status
from flask.ext.cors import CORS
from flask.ext.cache import Cache
from flask.ext.compress import Compress

from config import bindPort, redisCachePrefix, redisCacheTimeout
from topic import getTopicTable
from topk import getTopKTable

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

def startJob(func, argStrs, method='POST', contentType='application/json'):
    def parseArgs(j, argStrs):
        return [j[s] for s in argStrs]

    if request.method == method:
        if request.headers['Content-Type'] == contentType:
            result = func(*parseArgs(request.json, argStrs))

            if result is None:
                return jsonify(error=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return jsonify(result=result)
        else:
            return jsonify(error=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return jsonify(error=status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route('/topic/', methods=['POST'])
def topic():
    return startJob(
        getTopicTable,
        ["idStr", "content", "k", "wordNum"]
    )

@app.route('/topk/', methods=['POST'])
def topk():
    return startJob(
        getTopKTable,
        ["idStr", "content", "k", "minLen", "maxLen"]
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=bindPort, threaded=False, debug=True)

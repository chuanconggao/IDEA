#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Flask
from flask.ext.cors import CORS
from flask.ext.cache import Cache
from flask.ext.compress import Compress

from job import startJob
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

@app.route('/topic/', methods=['POST'])
def topic():
    return startJob(
        "topic", getTopicTable,
        ["idStr", "content", "k", "wordNum"]
    )

@app.route('/topk/', methods=['POST'])
def topk():
    return startJob(
        "topk", getTopKTable,
        ["idStr", "content", "k", "minLen", "maxLen"]
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=bindPort, threaded=False, debug=True)

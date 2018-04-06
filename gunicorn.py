#!/usr/bin/env python3

import json

with open("config.json") as f:
    j = json.load(f)

    bindPort = j["port"]

bind = "0.0.0.0:{}".format(bindPort)
workers = 1
worker_class = "sanic.worker.GunicornWorker"
timeout = 600

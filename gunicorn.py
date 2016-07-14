#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

with open("config.json") as f:
    j = json.load(f)

    bindPort = j["port"]

bind = "0.0.0.0:{}".format(bindPort)
workers = 4
loglevel = "debug"
timeout = 60 * 10

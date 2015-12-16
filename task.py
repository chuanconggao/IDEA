#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import os.path

from config import tasksDir

def getTaskNames():
    return [
        d for d in os.listdir(tasksDir)
        if os.path.isdir(os.path.join(tasksDir, d))
    ]

class Task(object):
    def __init__(self, template):
        self.name = template["name"]
        self.args = template["args"]
        sys.path.append(os.path.join(tasksDir, template["name"]))
        self.func = getattr(__import__(template["name"]), template["func"])
        self.description = template["description"]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

class Task(object):
    def __init__(self, template):
        self.name = template["name"]
        self.args = template["args"]
        self.func = getattr(__import__(template["import"]), template["func"])
        self.description = template["description"]

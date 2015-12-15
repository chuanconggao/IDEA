#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re
import subprocess
import codecs
from time import sleep

from rq import Queue
from redis import Redis

from config import dataDir, redisQueuePrefix, redisQueueTimeout
from aux import print2

q = Queue(
    redisQueuePrefix + "topic",
    connection=Redis(),
    default_timeout=redisQueueTimeout
)

def getTopicTable(idStr, content, k, wordNum):
    job = q.enqueue(getTopicTable_worker, idStr, content, k, wordNum)

    while not job.is_failed and job.result is None:
        sleep(1)

    return job.result

def getTopicTable_worker(idStr, content, k, wordNum):
    topicDir = os.path.join(dataDir, "topic")
    if not os.path.isdir(topicDir):
        os.mkdir(topicDir)

    baseName = "_".join([
        idStr,
        "k=" + str(k),
        "wordnum=" + str(wordNum)
    ])

    fileName = os.path.join(topicDir, baseName)
    inputFileName = fileName + ".in"
    malletFileName = fileName + ".mallet"
    outputFileName = fileName + ".out"

    if not os.path.isfile(outputFileName):
        print2("Modeling \"{}\" with: k={}, wordnum={}...".format(
            idStr, k, wordNum
        ))

        with codecs.open(inputFileName, 'w', 'utf-8', errors="ignore") as f:
            for i in content:
                f.write(i)
                f.write('\n')

        args = [
            "mallet import-file",
            "--input \"{}\"".format(inputFileName),
            "--output \"{}\"".format(malletFileName),
            "--keep-sequence", "--remove-stopwords"
        ]
        subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        args = [
            "mallet train-topics",
            "--input \"{}\"".format(malletFileName),
            "--num-topics " + str(k),
            "--num-top-words " + str(wordNum + 1),
            "--show-topics-interval 1000",
            "--output-topic-keys \"{}\"".format(outputFileName)
        ]
        subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    reFilter = re.compile(r"^\d+\t\d+(?:\.\d+)?\t", re.I | re.U)

    results = []
    with codecs.open(outputFileName, 'r', 'utf-8', errors="ignore") as f:
        for i in f:
            results.append(reFilter.sub("", i.rstrip()).split(' '))

    return results

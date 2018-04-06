#!/usr/bin/env python3

import sys
from functools import partial

print2 = partial(print, file=sys.stderr)

def str2bool(s):
    return s.lower() in ["1", "true", "yes"]


def bool2str(s):
    return "true" if s else "false"

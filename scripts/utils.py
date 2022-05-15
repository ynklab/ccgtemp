#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time

def time_count(fn):
  # Funtion wrapper used to measure time consumption
  def _wrapper(*args, **kwargs):
    start = time.clock()
    returns = fn(*args, **kwargs)
    logging.debug("[time_count]: %s took %fs" % (fn.__name__, time.clock() - start))
    return returns
  return _wrapper


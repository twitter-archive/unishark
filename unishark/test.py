__author__ = 'yni'

import concurrent.futures
from time import sleep


# def worker(s):
#     sleep(s)
#     return s
# with concurrent.futures.ThreadPoolExecutor(5) as e:
#     futures = [e.submit(worker, i) for i in range(5)]
#     done = concurrent.futures.as_completed(futures)
#     for f in done:
#         print(f.result())

from unishark.runner import BufferedTestResult
from unittest.runner import TextTestResult
import sys
r = TextTestResult(sys.stdout, True, 0)
print(r.__module__)

import os
import sys

import webtensor

__author__ = "jlthm"
__maintainer__ = "jlthm""
__status__ = "Production"

'''
This console-based application allows recursive web-crawling with level 3 tensors.
The datatype tensor acts like a multidimensional dictionary.
Requests are an iteration of the third axis. For detailed information see github @jlthm/webtensor

'''

if not sys.argv[-1].endswith(".py"):
    print("This script takes no arguments.")
    exit()

console = webtensor.Console("webtensor")
console.run()

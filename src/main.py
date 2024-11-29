import os
import sys

import webtensor

__author__ = "jlthm"
__maintainer__ = "jlthm"
__status__ = "Production"

'''
This console-based application allows specific and automated recursive webcrawling
with tensor-datatypes level 3. For detailed information see github @jlthm/webtensor

'''

if not sys.argv[-1].endswith(".py"):
    print("This module takes no arguments.")
    exit()

console = webtensor.Console("webtensor")
console.run()

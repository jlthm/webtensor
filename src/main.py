import os
import sys

import webtensor

__author__ = "Julian Bauer"
__maintainer__ = "Julian Bauer"
__email__ = "julian.bauer@n.roteskreuz.at"
__status__ = "Production"

'''
This console-based application allows specific and automated access to
parts of the data provided by ems-services in lower austria.

The application uses 3 submodules:
    - ac144_console.py to provide a program interface
    - ac144_session.py is used to create network connections to the 
        relevant services
    - ac144_set.py is used to convert the gathered data into readable
        formats

'''

if not sys.argv[-1].endswith(".py"):
    print("This module takes no arguments.")
    exit()

console = webtensor.Console("afc144")
console.run()

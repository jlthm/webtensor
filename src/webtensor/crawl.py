import os
import sys
import time
import json
import copy
import itertools
import datetime
import re
import requests


__author__ = "jlthm"
__maintainer__ = "jlthm"
__status__ = "Production"
__version__ = "1.0.1"

'''
This file is part of the module webtensor.

'''
class NetworkReq:
    def __init__(self):

        self.req_type = 'GET'
        self.req_url = ''
        self.req_contype = 'application/x-www-form-urlencoded'
        self.req_redirect = 1
        self.req_args = {}
        self.req_cookies = {}
        
        self.resp = None
        self.resp_text = ""
        self.resp_cookies = {}
        self.resp_url = ""
        self.resp_status = 0

    def request(self):

        if not self.req_url:
            return []
        
        headers = {'Content-type': self.req_contype}

        if self.req_type == "GET":
            self.resp = requests.get(self.req_url, headers=headers, params=self.req_args, allow_redirects=self.req_redirect, cookies=self.req_cookies)

        elif self.req_type == "POST":
            self.resp = requests.post(self.req_url, headers=headers, data=self.req_args, allow_redirects=self.req_redirect, cookies=self.req_cookies)
        
        self.resp_status = self.resp.status_code
        self.resp_text = self.resp.text
        self.resp_cookies = self.resp.cookies
        self.resp_url = self.resp.url

class Crawler:
    def __init__(self, dataset=None):
        self.dataset = copy.deepcopy(dataset) # in case of failure
    
    def execute(self):
        # --- CHECKING DATASET REQUIREMENTS ---

        if not self.dataset:
            return False

        for j in range(self.dataset.length()[2]):

            if not self._parseParams(j):
                return False 

            req = NetworkReq()
            req.req_type =      self.dataset[0][0][j]
            req.req_url =       self.dataset[0][1][j]
            req.req_contype =   self.dataset[0][2][j]
            req.req_redirect =  self.dataset[0][3][j]

            arg_labels = self.dataset[1][None][-1]
            arg_data = self.dataset[1][None][j]

            for a in range(len(arg_labels)):
                if arg_labels[a]: # check if not NULL, None or 0
                    req.req_args.update({arg_labels[a]: arg_data[a]})
            
            cookie_labels = self.dataset[2][None][-1]
            cookie_data = self.dataset[2][None][j]
            for c in range(len(cookie_labels)):
                if cookie_labels[c]: # check if not NULL, None or 0
                    req.req_cookies.update({cookie_labels[c]: cookie_data[c]})
        
            req.request()

            self.dataset[3][0][j] = req.resp_status
            self.dataset[3][1][j] = req.resp_text
            self.dataset[3][2][j] = req.resp_url

            for c in req.resp_cookies:
                self.dataset[3][[c]][j] = req.resp_cookies[c]

        return self.dataset
    
    def _parseParams(self, z):
        for i, j in itertools.product(range(self.dataset.length()[0]), range(self.dataset.length()[1])):
            if -1 in [i, j, z]:
                continue
            if not [i, j, z] in self.dataset:
                continue
            prevalue = self.dataset[i][j][z]
            if type(prevalue) != str:
                raise ValueError("Value with index: {0}{1}{2} has an invalid value.".format(str(i), str(j), str(z)))
            operator = prevalue[0:prevalue.find(":")]
            postvalue = ''

            if operator == "s":
                postvalue = prevalue[prevalue.find(":")+1:]
            elif operator == "i":
                sys.stdout.write("\033[F")
                postvalue = input("Input for {0}".format(prevalue[prevalue.find(":")+1:]) + ">> ")
            elif operator == "d":
                postvalue = datetime.today().strftime(prevalue[prevalue.find(":")+1:])
            elif operator == "r":
                suboperator = prevalue[prevalue.replace(':', '-', 0).find(":")+1:prevalue.replace(':', '-', 1).find(":")]
                indices = prevalue[prevalue.replace(':', '-', 1).find(":")+1:prevalue.replace(':', '-', 2).find(":")][1:-1].split(",")
                try:
                    indices = [int(i) for i in indices]
                except KeyError:
                    return False
                rx = prevalue[prevalue.replace(':', '-', 2).find(":")+1:]

                if suboperator == "r":
                    absindex = [i-indices[0], j-indices[1], z-indices[2]]
                elif suboperator == "a":
                    absindex = indices
                else:
                    continue
                
                cellToRegex = self.dataset[absindex[0]][absindex[1]][absindex[2]]
                rematch = re.search(rx, cellToRegex)
                rematch = (rematch.group(1) if rematch is not None else False)
                if rematch:
                    postvalue = rematch

            self.dataset[i][j][z] = postvalue
        
        return True
import os
import sys
import time
import json
import copy
import itertools
import datetime
import re
import requests
from lxml import html, etree


__author__ = "jlthm"
__maintainer__ = "jlthm"
__status__ = "Production"
__version__ = "1.0.1"

'''
This file is part of the module webtensor.

'''
class NetworkReq:
    def __init__(self, s, d):

        self.debug = d

        self.session=s
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

        if self.debug:
            print("---------------------------------")
            print("PERFORMING NETWORK REQUEST WITH: ")
            print("REQ_TYPE: ", self.req_type.encode())
            print("REQ_URL: ", self.req_url.encode())
            print("REQ_CONTYPE: ", self.req_contype.encode())
            print("REQ_REDIRECT: ", self.req_redirect.encode())
            print("REQ_ARGS: ", str(self.req_args).encode())
            print("REQ_COOKIES: ", str(self.session.cookies.get_dict()).encode())
        
        self.session.headers.update({'Content-Type': self.req_contype})
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'})


        if self.req_type == "GET":
            self.resp = self.session.get(self.req_url, params=self.req_args, allow_redirects=self.req_redirect)

        elif self.req_type == "POST":
            self.resp = self.session.post(self.req_url, data=self.req_args, allow_redirects=self.req_redirect)
        
        self.resp_status = self.resp.status_code
        self.resp_text = self.resp.text
        self.resp_cookies = self.session.cookies.get_dict()
        self.resp_url = self.resp.url

        if self.debug:
            print("RESP_STATUS: ", self.resp_status)
            print("RESP_URL: ", self.resp_url)
            print("RESP COOKIES: ", self.resp_cookies)
            # print("RESP_TEXT: ", self.resp_text)

class Crawler:
    def __init__(self, dataset=None):
        self.dataset = copy.deepcopy(dataset) # in case of failure
        self.session = requests.Session()
    
    def execute(self, debug=False):
        # --- CHECKING DATASET REQUIREMENTS ---

        if not self.dataset:
            return False

        for j in range(self.dataset.length()[2]):

            while True:
                if not self._parseParams(j):
                    return False 

                req = NetworkReq(s=self.session, d=debug)
                try:
                    req.req_type =      self.dataset[0][0][j]
                    req.req_url =       self.dataset[0][1][j]
                    req.req_contype =   self.dataset[0][2][j]
                    req.req_redirect =  self.dataset[0][3][j]

                    arg_labels = self.dataset[1][None][-1]
                    arg_data = self.dataset[1][None][j]

                    for a in range(len(arg_labels)):
                        if not arg_data[a]:
                            continue
                        if arg_labels[a]: # check if not NULL, None or 0
                            req.req_args.update({arg_labels[a]: arg_data[a]})
                    
                    # cookie_labels = self.dataset[2][None][-1]
                    # cookie_data = self.dataset[2][None][j]
                    # for c in range(len(cookie_labels)):
                    #     if cookie_labels[c]: # check if not NULL, None or 0
                    #         req.req_cookies.update({cookie_labels[c]: cookie_data[c]})
                
                    req.request()
                    if req.resp_status != 200:
                        return False

                    self.dataset[3][0][j] = req.resp_status
                    self.dataset[3][1][j] = req.resp_text
                    self.dataset[3][2][j] = req.resp_url

                    # for c in req.resp_cookies:
                    #     self.dataset[3][[c]][j+1] = req.resp_cookies[c]

                    if (not self.dataset[0][4][j]) or self.dataset[0][4][j] == '0':
                        break

                    time.sleep(0.2)
                except IndexError:
                    break
                except KeyError:
                    break
                
        return self.dataset
    
    def _parseParams(self, z):
        for i, j in itertools.product(range(self.dataset.length()[0]), range(self.dataset.length()[1])):
            if -1 in [i, j, z]:
                continue
            if not [i, j, z] in self.dataset:
                continue
            prevalue = self.dataset[i][j][z]
            if type(prevalue) != str:
                continue
            operator = prevalue[:1]
            postvalue = ''

            if operator == "s":
                postvalue = prevalue[prevalue.find(":")+1:]
            elif operator == "i":
                try:
                    postvalue = input("Input for {0}".format(prevalue[prevalue.find(":")+1:]) + ">> ")
                except KeyboardInterrupt:
                    return False
            elif operator == "d":
                postvalue = datetime.datetime.today().strftime(prevalue[prevalue.find(":")+1:])
            elif operator in ["r", "o"]:
                suboperator = prevalue[prevalue.replace(':', '-', 0).find(":")+1:prevalue.replace(':', '-', 1).find(":")]
                indices = prevalue[prevalue.replace(':', '-', 1).find(":")+1:prevalue.replace(':', '-', 2).find(":")][1:-1].split(",")
                rx = prevalue[prevalue.replace(':', '-', 2).find(":")+1:]

                try:
                    indices = [int(i) for i in indices]
                except KeyError:
                    return False

                if suboperator == "r":
                    absindex = [i+indices[0], j+indices[1], z+indices[2]]
                elif suboperator == "a":
                    absindex = indices
                else:
                    continue

                cellToRegex = self.dataset[absindex[0]][absindex[1]][absindex[2]]

                rematch = re.search(rx, cellToRegex)
                rematch = (rematch.group(1) if rematch is not None else False)

                if rematch:
                    postvalue = rematch

                if operator == "o":
                    try:
                        input("Crawler prints: " + str(postvalue))
                    except KeyboardInterrupt:
                        return False
            
            elif operator == "p":
                suboperator = prevalue[prevalue.replace(':', '-', 0).find(":")+1:prevalue.replace(':', '-', 1).find(":")]
                indices1 = prevalue[prevalue.replace(':', '-', 1).find(":")+1:prevalue.replace(':', '-', 2).find(":")][1:-1].split(",")
                indices2 = prevalue[prevalue.replace(':', '-', 2).find(":")+1:prevalue.replace(':', '-', 3).find(":")][1:-1].split(",")
                rx = prevalue[prevalue.replace(':', '-', 3).find(":")+1:]

                try:
                    indices1 = [int(i) for i in indices1]
                except KeyError:
                    return False
                
                try:
                    indices2 = [int(i) for i in indices2]
                except KeyError:
                    return False

                if suboperator == "r":
                    absindex1 = [i+indices1[0], j+indices1[1], z+indices1[2]]
                    absindex2 = [i+indices2[0], j+indices2[1], z+indices2[2]]
                elif suboperator == "a":
                    absindex1 = indices1
                    absindex2 = indices2
                
                cellToRegex = self.dataset[absindex1[0]][absindex1[1]][absindex1[2]]

                rematch = re.search(rx, cellToRegex)
                rematch = (rematch.group(1) if rematch is not None else False)

                if rematch:
                    self.dataset[absindex2[0]][absindex2[1]][absindex2[2]] = rematch
                else:
                    self.dataset[absindex2[0]][absindex2[1]][absindex2[2]] = ''
                
                postvalue = prevalue

            elif operator == "x":
                suboperator = prevalue[prevalue.replace(':', '-', 0).find(":")+1:prevalue.replace(':', '-', 1).find(":")]
                indices1 = prevalue[prevalue.replace(':', '-', 1).find(":")+1:prevalue.replace(':', '-', 2).find(":")][1:-1].split(",")
                xp = prevalue[prevalue.replace(':', '-', 2).find(":")+1:prevalue.replace(':', '-', 3).find(":")]
                attr = prevalue[prevalue.replace(':', '-', 3).find(":")+1:]

                try:
                    indices1 = [int(i) for i in indices1]
                except KeyError:
                    return False
                
                if suboperator == "r":
                    absindex1 = [i+indices1[0], j+indices1[1], z+indices1[2]]
                elif suboperator == "a":
                    absindex1 = indices1

                cellToXPath = " ".join(self.dataset[absindex1[0]][absindex1[1]][absindex1[2]].replace('\/', '/').replace('\n', '').replace('\\n', '').strip().split())
                xpathTree = html.fromstring(cellToXPath)
                r = xpathTree.xpath(xp)

                if r:
                    if attr:
                        postvalue = r[0].attrib[attr]
                    else:
                        postvalue = (r[0].text + ''.join([str(etree.tostring(e).decode()) for e in r[0]])).strip()
                else:
                    postvalue = ''

            else:
                postvalue = prevalue

            self.dataset[i][j][z] = postvalue
        
        return True
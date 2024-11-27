import os
import sys
import time
import json
import inspect
import itertools
import time

from .dataset import Dataset
from .crawl import Crawler

__author__ = "jlthm"
__maintainer__ = "jlthm"
__status__ = "Production"
__version__ = "1.0.1"

'''
This file is part of the module webtensor.

'''

class CMgr:
    def __init__(self):
        self._datasets = {}

        self.dataset_ = lambda: 2

    def _as_color(self, st, color='') -> str:
        c_end = '\033[0m'
        c_color = '\033[0m'
        if color == '':
            c_color = '\033[0m'
        if color == 'red':
            c_color = '\033[91m'
        if color == 'orange':
            c_color = '\033[33m'
        if color == 'violett':
            c_color = '\033[94m'
        if color == 'green':
            c_color = '\033[32m'
        return c_color + str(st) + c_end
    
    def _get_pargs(self, args, takein=0):
        args_dict = {}
        for a in args[takein:]:
            if not a.startswith("--"):
                args_dict["oc"] = a
                continue
            if not "=" in a:
                return False
            args_dict[a.split("=")[0].replace("--", "")] = a.split("=")[1]
        return args_dict
    
    def help(self, args) -> list:
        return [
            [self._as_color("Note: For a detailed description, control instructions and examples see github.com/jlthm.", "orange")],
            [],
            ["All possible commands (to be extended):"],
            ["> help"],
            ["> dataset create mydataset"],
            ["> dataset remove mydataset"],
            ["> dataset set mydataset --index=0,0,0 --value=example"],
            ["> dataset read mydataset --index=0,0,0"],
            ["> dataset load mydataset --in=mydata.tensor.json"],
            ["> dataset export mydataset --out=newdata.tensor.json"],
            ["> dataset extract mydataset[1][][] --out=myextracteddata.json"],
            ["> dataset visualedit mydataset (TBD)"],
            ["> crawlwith mydataset"],
            ["> exit"]
        ]

    def dataset_create(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]

        # create new object

        d = Dataset()
        if pargs["oc"] in self._datasets:
            return [
                [self._as_color("Object already created.", color="red")]
            ]
        self._datasets[pargs["oc"]] = d

        return [
            [self._as_color("Object successfully created.", color="green")]
            ]
    
    def dataset_remove(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]

        # create new object
        try:
            del self._datasets[pargs["oc"]]
            return [
                [self._as_color("Object successfully removed.", color="green")]
            ]
        except KeyError:
            return [
                [self._as_color("Object not found.", color="red")]
            ]

    def dataset_set(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc", "index", "value"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]
        
        if not pargs["oc"] in self._datasets:
            return [[self._as_color("No such dataset.", color="red")]]

        if not len(pargs["index"].split(",")) == 3:
            return [[self._as_color("Invalid index", color="red")]]
        
        index = [int(i) for i in pargs["index"].split(",")]

        self._datasets[pargs["oc"]][index[0]][index[1]][index[2]] = pargs["value"]

        return [[self._as_color("Value set", color="green")]]

    def dataset_read(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc", "index"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]
        
        if not pargs["oc"] in self._datasets:
            return [[self._as_color("No such dataset.", color="red")]]

        if not len(pargs["index"].split(",")) == 3:
            return [[self._as_color("Invalid index", color="red")]]
        
        index = [int(i) for i in pargs["index"].split(",")]
        try:
            val = self._datasets[pargs["oc"]][index[0]][index[1]][index[2]]
        except KeyError:
            return [[self._as_color("No value set for this index", color="green")]]

        return [[self._as_color("The value of cell ({0}) is: {1}".format(", ".join(pargs["index"].split(",")), str(val)), color="green")]]

    def dataset_load(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc", "in"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]

        if not os.path.isfile(pargs["in"]):
            return [[self._as_color("No such file.", color="red")]]

        if not pargs["oc"] in self._datasets:
            return [[self._as_color("No such dataset.", color="red")]]

        inset = json.load(open(pargs["in"], "r"))

        self._datasets[pargs["oc"]].clear()

        for val in inset:
            self._datasets[pargs["oc"]][val[0]][val[1]][val[2]] = val[3]
            
        return [[self._as_color("Dataset loaded successfully.", color="green")]]
    
    def dataset_export(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc", "out"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]
        
        if not pargs["oc"] in self._datasets:
            return [[self._as_color("No such dataset.", color="red")]]
        
        outset = []
        for i, j, k in self._datasets[pargs["oc"]]:
            if [i, j, k] in self._datasets[pargs["oc"]]:
                outset += [[i, j, k, self._datasets[pargs["oc"]][i][j][k]]]
        
        json.dump(outset, open(pargs["out"], "w"))
            
        return [[self._as_color("Dataset exported successfully.", color="green")]]

    def dataset_extract(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc", "out"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]

        dataset_name = pargs["oc"][0:pargs["oc"].find("[")]
        if not dataset_name in self._datasets:
            return [[self._as_color("No such dataset {0}.".format(str(dataset_name)), color="red")]]

        dataset_inds = pargs["oc"].replace(dataset_name, "")
        di = [0, 0, 0]
        for k in range(3):
            di[k] = dataset_inds[dataset_inds.find("[")+1:dataset_inds.find("]")]
            if di[k] in ["none", "None", "NULL", "null", '']:
                di[k] = None
            dataset_inds = dataset_inds[dataset_inds.find("]")+1:]
        for k in range(3):
            try:
                di[k] = int(di[k])
            except TypeError:
                continue
            except ValueError:
                continue

        subdataset = self._datasets[dataset_name][di[0]][di[1]][di[2]]

        try:
            pass
        except KeyError:
            return [[self._as_color("Faulty index.", color="red")]]
        
        json.dump(subdataset, open(pargs["out"], "w"))
            
        return [[self._as_color("Subset exported successfully.", color="violett")]]

    def dataset_visualedit(self, args):
        # Parse arguments and check requirements
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]
        
        if not pargs["oc"] in self._datasets:
            return [[self._as_color("No such dataset.", color="red")]]

        return [[self._as_color("Command in development", color="violett")]]

    def crawlwith(self, args):
        pargs = self._get_pargs(args, inspect.stack()[0][3].count("_"))
        if pargs == False:
            return [
                [self._as_color("Command failed: Could not interpret input:", color="red")],
                [],
                ["> " + " ".join(args)],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
            ]

        _min_reqs = ["oc"]

        for r in _min_reqs:
            if r not in pargs:
                return [
                    [self._as_color("Command failed: This command is missing an argument:", color="red")],
                    [],
                    ["> " + " ".join(args)],
                    [],
                    [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]
        
        if not pargs["oc"] in self._datasets:
            return [[self._as_color("No such dataset.", color="red")]]

        crawler = Crawler(dataset=self._datasets[pargs["oc"]])
        resp = crawler.execute()
        if not resp:
            return [[self._as_color("Crawling failed.", color="red")]]
        else:

            self._datasets[pargs["oc"]] = resp
            return [[self._as_color("Crawling done. Dataset datatransfer successful.", "green")]]

class Console:
    '''
    Console Interface

    '''
    def __init__(self, label):
        self._output_queue = []
        self._output = [[]]
        self._output_lines = 1
        self._output_columns = 1
        self._ml_status = True
        self._commands_mgr = CMgr()

        self._output_header = [["WebWatchConsole v{0}".format(__version__)], []]

        self.label = label
    
    def clear(self):
        self._output_queue = [[]]
    
    def _as_color(self, st, color=''):
        c_end = '\033[0m'
        c_color = '\033[0m'
        if color == '':
            c_color = '\033[0m'
        if color == 'red':
            c_color = '\033[91m'
        if color == 'orange':
            c_color = '\033[33m'
        if color == 'violett':
            c_color = '\033[94m'
        if color == 'green':
            c_color = '\033[32m'

        return c_color + str(st) + c_end
    
    def _display(self):
        self._output_lines = os.get_terminal_size().lines
        self._output_columns = os.get_terminal_size().columns

        for l in range(len(self._output_queue)):
            if l > self._output_lines+1:
                break
            self._output += [[]]
            for c in range(len(self._output_queue[l])):
                if c > self._output_columns:
                    break
                self._output[l] += [self._output_queue[l][c]]
        
        sys.stdout.write("\033[H\033[J") # [H: Top left corner [J: Clear console
        for l in range(len(self._output)):
            for c in range(len(self._output[l])):
                sys.stdout.write(self._output[l][c])
            sys.stdout.write("\033[E")
        
        self._output = [[]]
        
    def _cmdinput(self):
        self._output_lines = os.get_terminal_size().lines
        self._output_columns = os.get_terminal_size().columns

        sys.stdout.write("\033[{0};1H".format(str(self._output_lines-1)))
        sys.stdout.write("{0}> ".format(self.label))
        try:
            c = input("")
        except KeyboardInterrupt:
            sys.exit()
        return c
    
    def _cmdinterpreter(self, cmd):
        cmd_struc = cmd.strip().split(" ")

        # Quick access to avoid script failure
        if cmd_struc[0] == "exit":
            return False

        # Output header
        self._output_queue = []
        self._output_queue += self._output_header

        cn = 1

        if str(cmd_struc[0] + "_") in dir(self._commands_mgr) and not str(cmd_struc[0]).startswith("_"):
            cn = getattr(self._commands_mgr, cmd_struc[0] + "_")()

        cmd_setcm = "_".join([c for c in cmd_struc if (not c.startswith("--") and cmd_struc.index(c) < cn)])

        if cmd_setcm in dir(self._commands_mgr) and not cmd_setcm.startswith("_"):
            self._output_queue += getattr(self._commands_mgr, cmd_setcm)(args=cmd_struc)
        else:
            self._output_queue += [
                [self._as_color("Command failed: Command not found. Please use help to see all commands.", color="red")],
                [],
                [self._as_color("Please check required arguments or call 'help'.", color="orange")]
                ]
        return True

    def run(self):
        self._output_queue = [
            ["You started WebWatchConsole v{0}".format(__version__)],
            [],
            ["This project is maintained by @jlthm on github. See github page for more information."],
            ["Type 'help' for more information."]
        ]
        sys.stdout.write('\033[2J')

        self._ml()
        self.end()
    
    def _ml(self):
        while self._ml_status:
            self._display()
            self._ml_status = self._cmdinterpreter(self._cmdinput())

    def end(self):
        sys.stdout.write("\033[H\033[J")
        exit()
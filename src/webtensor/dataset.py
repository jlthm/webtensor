import os
import sys
import itertools
import copy

__author__ = "jlthm"
__maintainer__ = "jlthm"
__status__ = "Production"
__version__ = "1.0.1"

'''
This file is part of the module webtensor.

'''

class DatasetSub1:
    def __init__(self, parent, coordinates):
        self.parent = parent
        self.coordinates = coordinates
    
    def __getitem__(self, a):
        self.coordinates.append(a)
        d2 = DatasetSub2(self.parent, self.coordinates)
        return d2

    def __setitem__(self, a, v):
        raise SyntaxError("Tensor values need three coordinates")
    
    def __repr__(self):
        raise SyntaxError("Tensor values need three coordinates")
    
    def __call__(self):
        raise SyntaxError("Tensor values need three coordinates")

class DatasetSub2:
    def __init__(self, parent, coordinates):
        self.parent = parent
        self.coordinates = coordinates

    def __getitem__(self, a):
        self.coordinates.append(a)
        return self.parent.getItemTensor(self.coordinates)

    def __setitem__(self, a, v):
        self.coordinates.append(a)
        return self.parent.setItemTensor(self.coordinates, v)
    
    def __repr__(self):
        raise SyntaxError("Tensor values need three coordinates")
    
    def __call__(self):
        raise SyntaxError("Tensor values need three coordinates")

class Dataset:
    # -- (Important) Special operation methods --
    def __init__(self):
        self.data = [
            [-1, -1, -1, "Tensor"]
        ]
    
    def setItemTensor(self, coordinates=[], value=None):

        orientation = [(True if (co != None) else False) for co in coordinates]

        if orientation != [True, True, True]:
            raise NotImplementedError("Method not allowed")

        self._set(c=self._exactC(coordinates), v=value)
        return
    
    def getItemTensor(self, coordinates=[]):
        return self._extract(c=self._exactC(c=coordinates))
    
    def _exactC(self, c=[]):

        c_in = c
        c_out = []
        
        # -- Checking type, translating edge labels
        for ci in range(3):
            nci = [0, 1, 2]
            nci.remove(ci)
            if type(c_in[ci]) in [int, type(None)]:
                c_out.append(c_in[ci])
                continue
            
            elif type(c_in[ci]) in [str]:
                f = False
                for i in range(len(self.data)):
                    if self.data[i][nci[0]] == -1 and self.data[i][nci[1]] == -1 and self.data[i][ci] != -1:
                        c_out.append(self.data[i][ci])
                        f = True
                        break
                if f:
                    continue
                raise KeyError("No Edge label with name: {0}".format(c_in[ci]))
            
            elif type(c_in[ci]) in [list]:
                pl = c_in[ci][0]
                if type(pl) not in [str]:
                    raise IndexError("Tensor indices must be of type: int, str, [str].")
                else:
                    c_out.append([pl])
                
            else:
                raise IndexError("Tensor indices must be of type: int, str, [str].")

        # -- Translate plane labels

        # Check for enough information
        if not int in [type(i) for i in c_out]:
            raise KeyError("Tensor must contain at least one edge index or label.")

        '''
        The algorithm for finding a plane label goes the following:
        - Go through the plane-label-indices
        - Fix one of the numeric indices.
        - Go through the plane labels in this column/row. Return index.
        - If no index is found, try another numeric index.
        '''


        for p in range(3):
            if [type(k) for k in c_out][p] == list:
                pi = None
                for j in range(3):
                    if pi == None:
                        if [type(k) for k in c_out][j] == int:
                            # One index is fixed, the other one is what we are looking for, so the third one (t) must be -1.
                            t = [0, 1, 2]
                            t.remove(p)
                            t.remove(j)
                            t = t[0]
                            for i in range(len(self.data)):
                                if self.data[i][j] == c_out[j] and self.data[i][t] == -1 and self.data[i][3] == c_out[p][0]:
                                    pi = self.data[i][p]
                                    break
                if pi != None:
                    c_out[p] = pi
                else:
                    raise KeyError("No such plane-label.")

        return c_out

    def _matrix(self, zero=True) -> list:
        m = []
        '''
        Convert Tensor to a list-in-list-in-list object
        '''
        if not zero:
            for i in range(len(self.data)):
                if (self.data[i][0] == -1) or (self.data[i][1] == -1) or (self.data[i][2] == -1):
                    continue

                c = self.data[i]
                
                if c[0] >= len(m):
                    m += [[] for _ in range(c[0] - len(m) + 1)]

                if c[1] >= len(m[c[0]]):
                    m[c[0]] += [[] for _ in range(c[1] - len(m[c[0]]) + 1)]

                if c[2] >= len(m[c[0]][c[1]]):
                    m[c[0]][c[1]] += [0 for _ in range(c[2] - len(m[c[0]][c[1]]) + 1)]

                m[c[0]][c[1]][c[2]] = c[3]
        else:

            m = [[[0 for _ in range(self.__len__()[2]+1)]  
                 for _ in range(self.__len__()[1]+1)]  
                 for _ in range(self.__len__()[0]+1)]

            for i in range(len(self.data)):
                if (self.data[i][0] == -1) or (self.data[i][1] == -1) or (self.data[i][2] == -1):
                    continue
                c = self.data[i]
                m[c[0]][c[1]][c[2]] = c[3]

        return m
    
    def _extract(self, c: list) -> list:
        '''
        Convert Tensor to a lower-dimensional list-in-list object
        '''

        orientation = [(True if ((co != None and co != False) or type(co) == int) else False) for co in c]
        # THREE FALSE

        if orientation == [True, True, True]:
            for i in self.data:
                if i[:3] == c:
                    return i[3]
            raise KeyError("Index not in Tensor")

        elif orientation == [False, False, False]:
            return self._matrix()

        #  ---------------------------------------------------------------
        #  -- TWO False, ONE True = one fixed = Tensor level 2 - matrix -- 

        m = []

        f = 0 # fixed coordinate index
        nf = (0, 0) # variable coordinate indices

        if orientation == [True, False, False]:
            f = 0
            nf = (1, 2)
        elif orientation == [False, True, False]:
            f = 1
            nf = (0, 2)
        elif orientation == [False, False, True]:
            f = 2
            nf = (0, 1)

        if (f, nf) != (0, (0, 0)):
            # expand matrix with zeros
            for j in range(self.__len__()[nf[0]]+1):
                m += [[0]*(self.__len__()[nf[1]]+1)]

            for i in range(len(self.data)):
                if self.data[i][f] != c[f]:
                    continue
                k, l = nf
                
                m[self.data[i][k]][self.data[i][l]] = self.data[i][3]
                
            return m
        
        #  ---------------------------------------------------------------
        #  -- ONE False, TWO True = two fixed = tensor level 1 - vector -- 

        m = []

        f = (0, 0) # fixed coordinate index
        nf = 0 # variable coordinate indices

        if orientation == [True, True, False]:
            f = (0, 1)
            nf = 2
        elif orientation == [True, False, True]:
            f = (0, 2)
            nf = 1
        elif orientation == [False, True, True]:
            f = (1, 2)
            nf = 0

        m += [0 for _ in range(self.__len__()[nf])]
        
        for i in range(len(self.data)):
            if (self.data[i][f[0]] == c[f[0]]) and (self.data[i][f[1]] == c[f[1]]):
                if self.data[i][nf] != -1:
                    m[self.data[i][nf]] = self.data[i][3]

        return m

    def _set(self, c: list, v):

        for i in range(len(self.data)):
            if self.data[i][:3] == c:
                self.data[i][3] = v
                return
        self.data.append([*c, v])

    def __getitem__(self, a):
        d1 = DatasetSub1(self, coordinates=[a])
        return d1
    
    def __setitem__(self, a, v):
        raise SyntaxError("Tensor values need three coordinates")
    
    def __call__(self):
        raise SyntaxError("Tensor object cannot be called")

    def __len__(self):
        m1, m2, m3 = 0, 0, 0

        for i in range(len(self.data)):
            if self.data[i][0]+1 > m1:
                m1 = self.data[i][0]+1
            if self.data[i][1]+1 > m2:
                m2 = self.data[i][1]+1
            if self.data[i][2]+1 > m3:
                m3 = self.data[i][2]+1
        return [m1, m2, m3]
    
    def length(self):
        m1, m2, m3 = 0, 0, 0

        for i in range(len(self.data)):
            if self.data[i][0]+1 > m1:
                m1 = self.data[i][0]+1
            if self.data[i][1]+1 > m2:
                m2 = self.data[i][1]+1
            if self.data[i][2]+1 > m3:
                m3 = self.data[i][2]+1
        return [m1, m2, m3]

    def clear(self):
        self.data = []

    # -- Other (not so important) special operation methods --

    def __repr__(self):
        return '<Tensor Object>'

    def __str__(self):
        return str(self._matrix())

    def __format__(self, format_spec):
        if isinstance(format_spec, int):
            raise TypeError("Tensor Object cannot be converted to int")
        if isinstance(format_spec, list):
            return self._matrix()
        elif isinstance(format_spec, dict):
            return {"tensor": self._matrix()}
        elif isinstance(format_spec, float):
            raise TypeError("Tensor Object cannot be converted to float")
        else:
            raise TypeError("Tensor Object cannot be converted to the specified datatype.")

    def __lt__(self, other):
        if isinstance(other, Dataset):
            return self.size() < other.size()
        else:
            raise TypeError("Comparison not supported for Tensors and {0}".format(str(type(other))))
    
    def __le__(self, other):
        if isinstance(other, Dataset):
            return self.size() <= other.size()
        else:
            raise TypeError("Comparison not supported for Tensors and {0}".format(str(type(other))))
    
    def __gt__(self, other):
        if isinstance(other, Dataset):
            return self.size() > other.size()
        else:
            raise TypeError("Comparison not supported for Tensors and {0}".format(str(type(other))))
    
    def __ge__(self, other):
        if isinstance(other, Dataset):
            return self.size() >= other.size()
        else:
            raise TypeError("Comparison not supported for Tensors and {0}".format(str(type(other))))

    def __eq__(self, other):
        if isinstance(other, Dataset):
            return self.data == other.data
        else:
            raise TypeError("Comparison not supported for Tensors and {0}".format(str(type(other))))
    
    def __ne__(self, other):
        if isinstance(other, Dataset):
            return self.data != other.data
        else:
            raise TypeError("Comparison not supported for Tensors and {0}".format(str(type(other))))
    
    def __hash__(self):
        raise TypeError("Unhashable Type: Tensor.")

    def __bool__(self):
        x = False
        for i in range(len(self.data)):
            if (self.data[i][0] != -1) and (self.data[i][1] != -1) and (self.data[i][2] != -1):
                x = True
        return x
    
    def __iter__(self):
        return itertools.product(*[range(v) for v in self.__len__()])
    
    def __contains__(self, item):
        if type(item) == list:
            for i in range(len(self.data)):
                if self.data[i][:3] == item:
                    return True
            return False
        else:
            for i in range(len(self.data)):
                if self.data[i][3] == item:
                    return True
        return False

    def __add__(self, other):
        if not isinstance(other, Dataset):
            raise TypeError("Cannot add Tensor and {0}".format(str(type(other))))
        
        la = copy.deepcopy(self)
        ra = copy.deepcopy(other)

        for i in ra.data:
            for j in la.data:
                if j[:3] == i[:3]:
                    j[3] = i[3]
                else:
                    la.append(i)
        
        return la
    
    def __sub__(self, other):
        raise TypeError("Subtraction not supported.")
    
    def __mul__(self, other):
        raise TypeError("Multiplication not supported.")
    
    def __truediv__(self, other):
        raise TypeError("Division not supported.")
    
    def __floordiv__(self, other):
        raise TypeError("Division not supported.")
    
    def __mod__(self, other):
        raise TypeError("Modulo not supported.")
    
    def __divmod__(self, other):
        raise TypeError("Modulo not supported.")
    
    def __pow__(self, other):
        raise TypeError("Power function not supported.")
    
    def __and__(self, other):
        return self.__bool__() and bool(other)
    
    def __xor__(self, other):
        return self.__bool__() and bool(other)
    
    def __or__(self, other):
        return self.__bool__() and bool(other)
    
    def __neg__(self):
        raise TypeError("Tensor object cannot be negative.")
    
    def __pos__(self):
        raise TypeError("Tensor object cannot be positive.")
    
    def __pos__(self):
        raise TypeError("Tensor object cannot be positive.")
    
    def __int__(self):
        raise TypeError("Tensor object cannot be converted to int.")
    
    def __float__(self):
        raise TypeError("Tensor object cannot be converted to float.")

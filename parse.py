import re
from enum import Enum

class exprType(Enum):
    FUNC=1,
    NUM=2,
    VAR=3,
    OP=4

class parseNode:
    def __init__(self,type,leftChild=None,rightChild=None):
        self.type = type
        self.leftChild = leftChild
        self.rightChild = rightChild


#Function names compiled into a regex expression. I'll probably create a separate file to put these in later.
funcNames = ["arcsin","arccos","arctan","log","sqrt","ln","sin","cos","tan"]

funcNames.sort(key=lambda x:len(x),reverse=True)

funcPatternStr = "(" + funcNames[0] + ")"
for func in funcNames[1:]: 
    funcPatternStr += "|(" + func + ")"

funcPattern = re.compile(funcPatternStr)
numPattern = re.compile("[0-9]*\.[0-9]+|[0-9]+")
varPattern = re.compile("[a-zA-Z]\_.|[a-zA-Z]")
opPattern = re.compile("\+|\-|\*|\/|\^")

patterns = [(funcPattern,exprType.FUNC),(numPattern,exprType.NUM),(varPattern,exprType.NUM),(opPattern,exprType.OP)]


def tokenize(str):

    
    print(m)
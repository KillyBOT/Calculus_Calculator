import re
from enum import Enum
from copy import deepcopy

class ParseError(Exception):
    pass

class exprType(Enum):
    PAR=1
    FUNC=2,
    CONST=3,
    NUM=4,
    VAR=5,
    OP=6

def exprStr(expr):
    if expr==exprType.FUNC :
        return "Function"
    elif expr==exprType.NUM:
        return "Number"
    elif expr==exprType.VAR:
        return "Variable"
    elif expr==exprType.OP:
        return "Operation"
    
    return "You should never see this"

class parseNode:
    def __init__(self,type,data=None,leftChild=None,rightChild=None):
        self.type = type
        self.data = data
        self.leftChild = leftChild
        self.rightChild = rightChild

    def __str__(self):
        retVal =  str(self.data)
        if self.leftChild:
            retVal += " [" + str(self.leftChild) + "]"
        if self.rightChild:
            retVal += " [" + str(self.rightChild) + "]"
        return retVal

    def __repr__(self):
        return str(self)

#Function names compiled into a regex expression. I'll probably create a separate file to put these in later.
funcNames = ["arcsin","arccos","arctan","log","sqrt","ln","sin","cos","tan"]
funcNames.sort(key=lambda x:len(x),reverse=True)

funcPatternStr = "|".join(funcNames)

#Constant names compiled into a regex expression. This will probably get grouped with the function name file I mentioned earlier.
constNames = ["e","pi"]
constNames.sort(key=lambda x:len(x),reverse=True)

constPatternStr = "|".join(constNames)

patternStrDict = {
    exprType.PAR: "\(|\)",
    exprType.FUNC: funcPatternStr,
    exprType.CONST: constPatternStr,
    exprType.VAR: "[a-zA-Z][0-9]+|[a-df-zA-Z]\_.|[a-zA-Z]",
    exprType.NUM: "[0-9]*\.[0-9]+|[0-9]+",
    exprType.OP: "\+|\-|\*|\/|\^"
}

#The order here matters a lot, as functions > variable names > numbers
groupPatternStr = "(" + "|".join(patternStrDict.values()) + ")"

#Tokenize an input string into a bunch of parseNode objects.
def tokenize(st):
    tokens = []

    groups = re.findall(groupPatternStr,st)

    for group in groups:
        for expr, pattern in patternStrDict.items():
            if re.match(pattern,group):
                tokens.append(parseNode(expr,int(group) if expr == exprType.NUM else group))
                break

    print(tokens)
    return tokens

#Build a tree based on the tokens given. Again, parentheses are not used here!
def buildTree(tokens):

    #Follow this order of operations: functions, exponents, multiplication, division, addition, subtraction
    opOrder = ["*","/","+","-"] #I left out exponents because of a special multiplication rule. I do deal with them later though

    hasPars = True
    hasFuncs = True
    hasExp = True
    hasMultCase = True
    hasOps = True

    #Parentheses
    while hasPars:
        hasPars = False
        for ind in range(len(tokens)-1):
            if tokens[ind].type == exprType.PAR and tokens[ind].data == "(":
                hasPars = True
                p = 1
                end = ind + 1
                while p > 0:
                    try:
                        if tokens[end].type == exprType.PAR and tokens[end].data == ")":
                            p -= 1
                        elif tokens[end].type == exprType.PAR and tokens[end].data == "(":
                            p += 1
                        end += 1
                    except IndexError:
                        raise ParseError

                print(tokens[0:ind],tokens[ind+1:end-1],tokens[end:])
                tokens = tokens[0:ind] + buildTree(tokens[ind+1:end-1]) + tokens[end:]
                print(tokens)
                break

    #Functions
    while hasFuncs:
        hasFuncs = False
        for ind in range(len(tokens)-1):
            if tokens[ind].type == exprType.FUNC and not tokens[ind].rightChild:
                hasFuncs = True
                try:
                    tokens[ind].rightChild = deepcopy(tokens[ind+1])
                    tokens.pop(ind+1)
                    break
                except IndexError:
                    raise ParseError

    #Operations
    #Annoyingly, I need to make a special case for multiplication when a number if followed by a variable, meaning there will be some redundancies. 
    while hasExp:
        hasExp = False
        for ind in range(len(tokens)-1):
            if tokens[ind].type == exprType.OP and tokens[ind].data == "^" and not tokens[ind].rightChild:
                hasExp = True
                try:
                    tokens[ind].leftChild = deepcopy(tokens[ind-1])
                    tokens[ind].rightChild = deepcopy(tokens[ind+1])
                    tokens.pop(ind+1)
                    tokens.pop(ind-1)
                    break
                except IndexError:
                    raise ParseError
        
    #Special multiplication case: when two objects that are not unassigned operators (i.e. have no left or right children) are next to each other, multiply them together
    while hasMultCase:
        hasMultCase = False
        for ind in range(len(tokens)-1):
            if not ((tokens[ind].type == exprType.OP and not tokens[ind].rightChild) or (tokens[ind+1].type == exprType.OP and not tokens[ind+1].rightChild)):
                hasMultCase = True
                newNode = parseNode(exprType.OP,"*",deepcopy(tokens[ind]),deepcopy(tokens[ind+1]))
                tokens[ind] = newNode
                tokens.pop(ind+1)
                break
    
    while hasOps:
        hasOps = False
        for ind in range(len(tokens)-1):
            if tokens[ind].type == exprType.OP and not tokens[ind].rightChild:
                hasOps = True
                for op in opOrder:
                    if tokens[ind].data == op:
                        try:
                            #Special case when the minus is at the front of the expression, since that indicates a negative number
                            tokens[ind].leftChild = parseNode(exprType.NUM,0) if (op == "-" and ind == 0) else deepcopy(tokens[ind-1])
                            tokens[ind].rightChild = deepcopy(tokens[ind+1])
                            tokens.pop(ind+1)
                            if ind > 0:
                                tokens.pop(ind-1)
                            break
                        except IndexError:
                            raise ParseError

                break

    return tokens
                
#The actual parsing function. Takes in a string and returns an operation tree.
def parse(st):
    st = st.replace(" ","") #Get rid off any spaces
    return buildTree(tokenize(st))
import re
from enum import Enum
from copy import deepcopy
from typing import final

class ParseError(Exception):
    pass

class exprType(Enum):
    PAR=1
    FUNC=2,
    CONST=3,
    NUM=4,
    VAR=5,
    OP=6

opPrecedenceDict = {
    "(":7,
    ")":6,
    "^":5,
    "*":4,
    "/":3,
    "+":2,
    "-":1
}

def exprStr(expr):
    if expr==exprType.FUNC:
        return "Function"
    elif expr==exprType.NUM:
        return "Number"
    elif expr==exprType.VAR:
        return "Variable"
    elif expr==exprType.OP:
        return "Operation"
    elif expr==exprType.CONST:
        return "Constant"
    
    return "You should never see this"

class exprNode:
    def __init__(self,type,data=None,leftChild=None,rightChild=None):
        self.type = type
        self.data = data
        self.leftChild = leftChild
        self.rightChild = rightChild

    def __str__(self):
        #retVal =  exprStr(self.type) + " "+str(self.data)
        retVal = str(self.data)
        if self.leftChild:
            retVal += " [" + str(self.leftChild) + "]"
        if self.rightChild:
            retVal += " [" + str(self.rightChild) + "]"
        return retVal

    def __repr__(self):
        return str(self)

#Function names compiled into a regex expression. I'll probably create a separate file to put these in later.
funcNames = ["arcsin","arccos","arctan","log","sqrt","ln","sin","cos","tan","abs"]
funcNames.sort(key=lambda x:len(x),reverse=True)

funcPatternStr = "|".join(funcNames)

#Constant names compiled into a regex expression. This will probably get grouped with the function name file I mentioned earlier.
constNames = ["e","pi"]
constNames.sort(key=lambda x:len(x),reverse=True)

constPatternStr = "|".join(constNames)

patternStrDict = {
    exprType.PAR: "\(|\)|\|",
    exprType.FUNC: funcPatternStr,
    exprType.CONST: constPatternStr,
    exprType.VAR: "[a-zA-Z][0-9]+|[a-df-zA-Z]\_.|[a-zA-Z]",
    exprType.NUM: "[0-9]*\.[0-9]+|[0-9]+",
    exprType.OP: "\+|\-|\*|\/|\^"
}

#The order here matters a lot, as functions > variable names > numbers
groupPatternStr = "(" + "|".join(patternStrDict.values()) + ")"

#Tokenize an input string into a bunch of exprNode objects. Also adds in a multiplication signs in some instances (5x -> 5*x, for example)
def tokenize(st):
    tokens = []

    groups = re.findall(groupPatternStr,st)

    seenAbs = False

    for group in groups:
        for expr, pattern in patternStrDict.items():
            if re.match(pattern,group):

                #Parsing error where there are two 
                if expr == exprType.PAR and group == ")" and tokens and tokens[-1].type == exprType.PAR and tokens[-1].data == "(":
                    raise ParseError("Empty set of parentheses")

                #Multiplication case. Very messy, and probably can be done better, but there are so many edge cases to consider that I don't think there's a better way of doing this
                if (expr in [exprType.CONST,exprType.VAR,exprType.FUNC] or (expr == exprType.PAR and (group == "(" or (group == "|" and not seenAbs)))) and tokens and (tokens[-1].type in [exprType.CONST,exprType.VAR,exprType.NUM] or tokens[-1].data == ")"):
                    tokens.append(exprNode(exprType.OP,"*"))

                #Vertical bar absolute value case
                if expr == exprType.PAR and group == "|":
                    if seenAbs:
                        tokens.append(exprNode(exprType.PAR,")"))
                    else:
                        tokens.append(exprNode(exprType.FUNC,"abs"))
                        tokens.append(exprNode(exprType.PAR,"("))
                    seenAbs = not seenAbs
                else:
                    tokens.append(exprNode(expr,int(group) if expr == exprType.NUM else group))

                break

    #print(tokens)
    return tokens

#Build a tree based on the tokens given. Again, parentheses are not used here!
"""def buildTree(tokens):

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
                newNode = exprNode(exprType.OP,"*",deepcopy(tokens[ind]),deepcopy(tokens[ind+1]))
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
                            tokens[ind].leftChild = exprNode(exprType.NUM,0) if (op == "-" and ind == 0) else deepcopy(tokens[ind-1])
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
"""

#Turns out there's an algorithm called the shunting-yard algorithm that is even better at building a parsing tree, so I'll implement that and see if it works better
def shunting_yard(st):
    tokens = tokenize(st)
    outStack = []
    opStack = []

    #Create a postfix notation string that will later turn into an abstract syntax tree
    for token in tokens:
        if token.type in [exprType.NUM, exprType.CONST, exprType.VAR]:
            outStack.append(token)
        elif token.type == exprType.FUNC or (token.type == exprType.PAR and token.data == "("):
            opStack.append(token)
        elif token.type == exprType.OP:
            while opStack and (opStack[-1].type == exprType.OP or opStack[-1].data == ")") and (opPrecedenceDict[opStack[-1].data] > opPrecedenceDict[token.data] or (opPrecedenceDict[opStack[-1].data] == opPrecedenceDict[token.data] and token.data != "^")):
                outStack.append(opStack.pop())
            opStack.append(token)
        elif token.type == exprType.PAR and token.data == ")":

            while opStack and opStack[-1].data != "(":
                outStack.append(opStack.pop())

            if not opStack:
                raise ParseError("No corresponding left parenthsis found for right parenthesis")

            opStack.pop()

            if opStack and opStack[-1].type == exprType.FUNC:
                outStack.append(opStack.pop())
            
    for op in range(len(opStack)):
        if opStack[-1].data == "(":
            raise ParseError("No corresponding left parenthesis found for right parenthesis")
        outStack.append(opStack.pop())

    #print(outStack)

    #Turn the output stack into an abstract syntax tree

    s = []

    while outStack:
        #print(outStack,s)
        l = outStack.pop(0)
        if (l.type == exprType.FUNC or l.type == exprType.OP) and (l.rightChild == None):
            l.rightChild = s.pop()
            if s and l.type == exprType.OP:
                l.leftChild = s.pop()

            outStack.insert(0,l)
            if len(outStack) == 1:
                #print(outStack[0])
                return outStack[0]

        else:
            s.append(l)

    #This should never happen
    raise ParseError("Error converting from postfix tree to abstract syntax tree. This should never happen, so if it happens I don't know what to say...")
    return None

#Simplifies the abstract syntax tree given to it.
#TODO: Work on this later
def simplify(ast):
    pass
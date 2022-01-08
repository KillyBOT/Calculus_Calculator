from copy import deepcopy
from parse import exprNode, exprType
from copy import deepcopy

#All of the following functions will, when given a node, give the derivative of that node

def der_add(ast):
    return exprNode(exprType.OP, "+", der(ast.leftChild),der(ast.rightChild))

def der_sub(ast):
    return exprNode(exprType.OP, "-", der(ast.leftChild),der(ast.rightChild))

def der_mult(ast): #d/dx xy = x'y + xy'
    lDer = der(ast.leftChild)
    rDer = der(ast.rightChild)

    lNode = exprNode(exprType.OP, "*" , deepcopy(lDer),deepcopy(ast.rightChild))
    rNode = exprNode(exprType.OP, "*", deepcopy(ast.leftChild),deepcopy(rDer))

    return exprNode(exprType.OP, "+", lNode, rNode)

def der_div(ast): #d/dx f/g = (f'g-fg')/g^2
    lDer = der(ast.leftChild)
    rDer = der(ast.rightChild)
    
    lNode = exprNode(exprType.OP, "*", deepcopy(lDer),deepcopy(ast.rightChild))
    rNode = exprNode(exprType.OP, "*", deepcopy(ast.leftChild),deepcopy(rDer))
    nDer = exprNode(exprType.OP,"-", lNode, rNode)

    dDer = exprNode(exprType.OP, "^", deepcopy(ast.rightChild),exprNode(exprType.NUM,2))

    return exprNode(exprNode.OP, "/", nDer, dDer)

def der(ast):
    if ast.type == exprType.CONST or ast.type == exprType.NUM:
        return exprNode(exprType.NUM,0)
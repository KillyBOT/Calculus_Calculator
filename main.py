import parse

def main():
    tokens = parse.tokenize("37x^54+4x+sinx")
    tree = parse.buildTree(tokens)

    print(tree)

    print(parse.parse("(74x+(7x^5))sin(4x)"))
    print(parse.parse("sin(sqrt(e^x+a)/2)"))


if __name__ == "__main__":
    main()
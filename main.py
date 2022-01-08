import parse

def main():
    tokens = parse.tokenize("37x^54+4x+5xsinx")

    """print(parse.parse("(74x+(7x^5))sin(4x)"))
    print(parse.parse("sin(sqrt(e^x+a)/2)"))
    print(parse.parse("sin3x+5"))"""

    print(parse.shunting_yard("sin(sqrt(e^x+a)/2)"))
    print(parse.shunting_yard("x^4+3x^2+12x+cos(3pi/4)"))


if __name__ == "__main__":
    main()
import parse #Parsing functions
import der #Derivative functions

def main():
    tokens = parse.tokenize("37x^54+4x+5xsinx")

    """print(parse.parse("(74x+(7x^5))sin(4x)"))
    print(parse.parse("sin(sqrt(e^x+a)/2)"))
    print(parse.parse("sin3x+5"))"""

    print(parse.shunting_yard("sin(sqrt(e^x+a)/2)"))
    print(parse.shunting_yard("x^4+3x^2+12x+cos(3pi/4)"))
    print(parse.shunting_yard("(-3x)^2"))
    print(parse.shunting_yard("(3x+5)(4x+6)"))
    print(parse.shunting_yard("|4x+6||5x+7|"))
    print(parse.shunting_yard("sin(4x)/cos(5x)tan(12pix)"))
    print(parse.shunting_yard("ln(ln(x))+(x+10)^10"))


if __name__ == "__main__":
    main()
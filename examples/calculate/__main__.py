import sys
sys.path.insert(0, "..")

import jclp


class Calc:
    def __init__(self):
        self._history = ""

    def calc(self, arg):
        self._history += arg + "\n"
        return eval(arg)

    def history(self):
        if self._history == "":
            return "history is empty..."
        return self._history


def main():
    calc = Calc()

    parser = jclp.Parser(
        open("calculate/commands.json"),
        {"calc": calc},
        version="jclp: calculate [0.1.0]"
    )

    print(parser.process(sys.argv[1:]))


if __name__ == "__main__":
    main()

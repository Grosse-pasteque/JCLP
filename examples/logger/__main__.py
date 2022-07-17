import sys
sys.path.insert(0, "..")

import jclp


class Logger:
    def __init__(self):
        self.user = "Brian"
        self.password = 1234
        self.logged = False

    def logging(self, user: str, password: int):
        if not self.logged:
            if user == self.user and password == self.password:
                self.logged = True
                return f"You are logged in as {user} !"
            return f"Failed to login. . ."
        return f"Already logged !"

    def disconnect(self):
        if self.logged:
            self.logged = False
            return f"Disconnected from user " + self.user
        return f"Already disconnected !"

    def interact(self, arg):
        if self.logged:
            return arg
        return "You need to be logged to be able to do that :/"


def main():
    logger = Logger()

    parser = jclp.Parser(
        open("logger/commands.json"),
        {"logger": logger},
        version="jclp: logger [0.1.0]"
    )

    print(parser.process(sys.argv[1:]))


if __name__ == "__main__":
    main()

import sys
sys.path.insert(0, "..")

import jclp


def main():
	parser = jclp.Parser(open("basic/commands.json"))

	print(parser.process(sys.argv[1:]))


if __name__ == "__main__":
	main()

from typing import Optional, Union, List
import json
from _io import TextIOWrapper


class Parser:
    def __init__(
        self,
        files:           Union[str, List[str]],
        _globals:        dict = {},
        version:         Optional[str] = None,
        alliases:        bool = True,
        help_command:    str = "help",
        version_command: str = "version"
    ):
        # files: Union[json-file, [json-file, ...]]
        if not isinstance(files, list):
            files = [files]

        self.commands_files = files
        self.commands = {}

        for file in files:
            if isinstance(file, TextIOWrapper):
                commands = json.loads(file.read())
            if isinstance(file, str):
                commands = json.loads(file)

            for name, command in commands.items():
                self.commands[name] = command

        self.alliases = alliases
        self.version = version
        self._globals = _globals

        self.help_command = "--" + help_command
        self.version_command = "--" + version_command

        self.last_entry = None

        if version_command is not None:
            self.commands[version_command] = { "return": repr(self.version) }

        if help_command is not None:
            self.commands[help_command] = { "return": "self.help()" }

        self.defaults = {
            "type":    None,
            "default": None,
            "reduct":  True,
            "check":   None,
            "repr":    False
        }

    def call(self, command: List[str]):
        if isinstance(command, list) and all(isinstance(a, str) for a in command):
            return self.process(command)
        raise TypeError(
            "arg: 'command' must be a list of strings !")

    def usage(self, command: List[str], args: List[Union[str, dict]]):
        argsuse = ""
        for arg in args:
            if isinstance(arg, str):
                arg = {"name": arg}
            arguse = "-{0} <{0}> | <{0}>".format(arg["name"])
            if arg.get("reduct", True):
                arguse += f" | -{arg['name'][0]} <{arg['name']}>"
            if arg.get("default", None):
                arguse = "[" + arguse + "]"
            argsuse += " " + arguse
        if self.alliases:
            cmduse = " ".join(f"{cmd} ({cmd[0]})" for cmd in command)
        else:
            cmduse = " ".join(command)
        return cmduse + argsuse

    def help(self, command: Optional[dict] = None) -> str:
        if command is None:
            return self.full_help()

        cmd = self.last_entry[:self.last_entry.index(self.help_command)]
        base = f"\n\tHelp for {'.'.join(cmd) if cmd else self.version!r} :"

        if self.is_runable(command):
            args = command.get("args", None)
            if args is not None:
                args = ", ".join(
                    arg if isinstance(arg, str) else arg["name"]
                    for arg in args
                )
            return f"""{base}
 | Description  : {command.get("description", None)}
 | Arguments    : {args}
 | Returns      : {command["return"]!r}

 Usage: {self.usage(cmd, command.get("args", []))}"""

        return "{}\n | Description : {}\n | Commands : {}".format(
            base,
            command.get("description", None),
            ", ".join(repr(n) for n in command["commands"])
        )

    def full_help(self) -> str:
        def _gen(commands, message, level=0):
            for name, command in commands.items():
                message += "\t" * level + name.lstrip("-") + "\n"

                if not self.is_runable(command):
                    message = _gen(command["commands"], message, level=level + 1)
            return message

        return "\nList of all commands {}\n\n{}\n{}".format(
            '~' * 49,
            _gen(self.commands, ''),
            '~' * 70
        )

    def is_runable(self, command: dict) -> bool:
        return "return" in command

    def get_allias(self, name: str, command: Union[dict, list]) -> Union[str, None]:
        if isinstance(command, list):
            for arg in command:
                if arg.get("reduct", True) and arg["name"][0] == name[0]:
                    return arg["name"]
        else:
            for command_name in command:
                if command_name[0] == name[0]:
                    return command_name

    @staticmethod
    def clean(val: str) -> str:
        return str(val).replace("<class '", "").replace("'>", "")

    def run(self, args: dict, seq: str):
        for name, value in args.items():
            seq = seq.replace("<" + name + ">", str(value))

        # raise error if fails
        try:
            return eval(seq, self._globals, locals())
        except Exception:
            return seq

    def check_arg(self, name: str, value: str, params: dict):
        if params["type"] is not None:
            try:
                rtype = eval(
                    params["type"],
                    self._globals
                )
            except Exception:
                raise TypeError(
                    f"Can't get argument type for arg {name!r}") from None
            try:
                if not isinstance(value, rtype):
                    if rtype == bool:
                        value = eval(value)
                    else:
                        value = rtype(value)
            except Exception:
                return "Got type {!r} instead of {!r} for arg: {!r}".format(
                    self.clean(type(value)),
                    self.clean(rtype),
                    name
                )
        if params["check"] is not None:
            try:
                result = eval(
                    params["check"].replace("%a", repr(value)),
                    self._globals
                )
            except Exception:
                raise Exception(
                    f"Can't execute check {params['check']!r}")
            if isinstance(result, str):
                return result
            if result not in [None, True]:
                return f"Argument: {name!r} has not valid value !"
        if params["repr"] == True:
            value = repr(value)
        return (value, )

    def parse_args(self, eargs: List[str], ekwargs: dict, rawargs: List[dict]) -> dict:
        allargs = {}
        for carg in rawargs.copy():
            if isinstance(carg, str):
                allargs[carg] = self.defaults.copy()
            else:
                allargs[carg.pop("name")] = {
                    **self.defaults,
                    **carg
                }

        args = {}
        for name, value in ekwargs.items():
            if name in allargs or (name := self.get_allias(name, allargs)):
                ret = self.check_arg(name, value, allargs[name])
                if isinstance(ret, str):
                    return ret
                args[name] = ret[0]
                allargs.pop(name)
            else:
                return f"Invalid argument {name!r} !"

        for value in eargs:
            name = list(allargs)[0]
            ret = self.check_arg(name, value, allargs[name])
            if isinstance(ret, str):
                return ret
            args[name] = ret[0]
            allargs.pop(name)

        missing = []
        for name, params in allargs.items():
            if params["default"] is not None:
                try:
                    args[name] = eval(params["default"], self._globals)
                except:
                    raise AttributeError(
                        f"Default argument {params['default']!r} "
                        f"for command {name!r} can't be executed.")

            else:
                missing.append(repr(name))

        if missing:
            return "Missing argument{}: {} !".format(
                "s" if len(missing) > 1 else "",
                ", ".join(missing)
            )

        return args

    def sorted_entry(self, entry: List[str]):
        args, kwargs = [], {}
        i  = 0
        while i != len(entry):
            if entry[i].startswith(self.help_command) or entry[i].startswith(self.version_command):
                return "You can't use version command or help command like this"
            if entry[i].startswith("-"):
                try:
                    kwargs[entry[i][1:]] = entry[i + 1]
                except IndexError:
                    return f"Missing value for argument {entry[i][1:]!r} !"
                i += 2
            else:
                args.append(entry[i])
                i += 1
        return args, kwargs

    def process(self, entry: List[str]):
        """ Function used to process and run a sequence (already parsed)
        with recursivity to find the path to the command you want to execute
        """
        self.last_entry = entry

        def _process(current, com, bentry, index=0):
            if self.alliases and \
            current not in com and \
            (allias := self.get_allias(current, com)):
                bentry[index] = allias
                current = allias

            nexte = bentry[index + 1] if len(bentry) > index + 1 else None

            if index == 0 and current.startswith("--"):
                if len(bentry) > 1:
                    return "Can't process arguments after '--' commands"

                if current == self.help_command:
                    return self.full_help()

                elif current == self.version_command:
                    return self.version

            if current not in com:
                return "Command doesn't exist !"

            if nexte is not None:
                if "--description".startswith(nexte):
                    return com[current].get(
                        "description",
                        "This command hasn't any description..."
                    )

                if self.help_command.startswith(nexte):
                    return self.help(com[current])

            if self.is_runable(com[current]):
                ret = self.sorted_entry(bentry[index + 1:]) # sorted entry (args, kwargs)
                if isinstance(ret, str):
                    return ret

                ret = self.parse_args(*ret, com[current].get("args", []))
                if isinstance(ret, str):
                    return ret

                return self.run(ret, com[current]["return"])

            elif "commands" not in com[current]:
                raise NotImplementedError(
                    f"command: {current!r} is not runable and has no commands in it.")

            return _process(
                bentry[index + 1],
                com[current]["commands"],
                bentry,
                index + 1
            )

        # start recursive function
        return _process(entry[0], self.commands, entry)

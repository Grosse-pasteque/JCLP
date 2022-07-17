# Json Command Line Parser

##### By Big watermelon#6705


------------


### Setup:

Import the jclp module.
```py
import jclp
```

Initialize the Parser with:
- file(s) which contains your commands
- then the globals() of your script

```py
parser = jclp.Parser(open('commands.json'), globals())
```

Finally process the command line that you want to run for example `sys.argv`:
```py
parser.process(sys.argv[1:])
# the first value is the file name so we ignore it
```

- **Full code**:

```python
import sys
import jclp

parser = jclp.Parser(open('commands.json'), globals())

print(parser.process(sys.argv[1:]))
```

### Commands:

Commands blocks.

| key  | type  | contains  |
| ------------ | ------------ | ------------ |
| description | *Optional\[str\]* | The command description |
| commands | *dict* | Other commands |

Runable commands are the one with a **return** key (**and not a commands key**).

| key  | type  | contains  |
| ------------ | ------------ | ------------ |
| description | *Optional\[str\]* | The command description |
| args | *Optional\[List\[Union\[str, dict\]\]\]* | Arguments of the command |
| return | *str* | The returned value |


- **Examples**:

```json
{
    "multiply": {
        "args": [
            {"name": "a", "type": "int"},
            {"name": "b", "type": "int"}
        ],
        "return": "<a> * <b>"
    }
}
```

```bash
>>> multiply 4 8
32
```


------------


```json
{
    "say-hello-to": {
        "description": "say hello to someone !",
        "commands": {
            "James": {"return": "hello James !"},
            "Brian": {"return": "hello Brian !"},
            "Anna": {"return": "hello Anna !"}
        }
    }
}
```

```bash
>>> say-hello-to James
hello James !

>>> say-hello-to Brian
hello Brian !
```

**But this is not optimized !**

We can use an arg has the person name.

```json
{
    "say-hello-to": {
        "description": "say hello to someone !",
        "args": ["name"],
        "return": "hello <name> !"
    }
}
```
And now we just have to do:
```bash
>>> say-hello-to Brian
hello Brian !

>>> say-hello-to "Mary Popins"
hello Mary Popins !
```


------------


##### Arguments:

All the other ones are optionnal.
**There is no default for opyionnal arguments !**

| key | type(s) | explaination |
| ------------ | ------------ | ------------ |
| type | *str* | Argument type (automaticly converted) |
| default | *str* | The argument default value |
| reduct | *bool* | If the argument can be reducted `-arg` -> `-a` |
| check | *evaluable sequence* | Check the argument (ex: `%a > 10`) |
| repr | *bool* | If the argument is passed as repr or not in the return sequence |


------------


### Special args:

Special args are optionnal and can give you some information on a command, for example:
```bash
>>> say-hello-to --description
say hello to someone !

>>> say-hello-to --help

        Help for 'say-hello-to' :
 | Description  : say hello to someone !
 | Arguments    : name
 | Returns      : 'hello <name> !'

 Usage: say-hello-to (s) -name <name> | <name> | -n <name>
```


------------


### More examples:

You can find more examples of how to use this module [here](./examples/).


------------


## Questions or issues ?

**Contact me on discord: ``Big watermelon#6705`**
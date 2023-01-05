from string import ascii_lowercase,ascii_uppercase,digits
# fucking lexer
# currently realization is broken
# upd: +- working
def lexer(c):
  comment = False
  tokens = []
  tokens2 = []
  words = [False, []]
  for i,e in enumerate(c):
    if e == "#": comment = not comment
    elif comment or e == "\n": continue
    elif e in [*ascii_lowercase,*ascii_uppercase,*digits,"_"]:
      words[0] = True
      words[1].append(e)
    else:
      if words[0]:
        tokens.append("".join(words[1]))
        tokens.append(e)
        words[1] = []
        words[0] = False
      else:
        tokens.append(e)
  quote = [False,[]]
  for _,e in enumerate(tokens):
    if e == "\"":
      if quote[0]:
        tokens2.append("".join(quote[1]))
        quote[1] = []
      tokens2.append("\"")
      quote[0] = not quote[0]
    elif quote[0]:
      quote[1].append(e)
    elif e == "-" and tokens[tokens.index(e)+1] == ">":
      tokens2.append("->")
    elif e == ">" and tokens[tokens.index(e)-1] == "-": continue
    elif e == " ": continue
    else: tokens2.append(e)
  for i in tokens2:
    if i == "\"": tokens2.remove(i)
  return tokens2

def run(code,*args):
  variables = {}
  for i in range(len(args)):
    variables[f"arg{i+1}"] = args[i]
  modules = {
    "core": {
      "print": lambda *args: print(*args),
      "update_var": lambda name,value: variables.update({name:value})
     },
     "custom": {}
  }
  bracket = [False,[]]
  function = [False,"main",[]]
  current = modules
  if type(code) == str: code = lexer(code)
  print(code)
  for i,c in enumerate(code):
    if c == "func":
      function[0] = True
      function[1] = code[i+1]
    elif c == "}":
      function[2] = function[2][1:]
      function_block = function[2]
      modules["custom"][function[1]] = lambda *args: run(" ".join(function_block),*args)
      function[0] = False
      function[1] = "main"
      function[2] = []
    elif function[0]:
      function[2].append(c)
    elif c == "->":
      child = code[i+1]
      parent = code[i-1]
      if parent in modules:
        current = modules[parent]
      if type(current) == function:
        print("Current is function")
      elif child in current:
        current = current[child]
      else:
        raise Exception(f"Cannot find property {child} of {parent}")
    elif c == "(": bracket[0] = True
    elif c == ")":
      bracket[0] = False
      current(*bracket[1])
      bracket[1] = []
    elif bracket[0]:
      if c == "$":
        vname = code[code.index(c)+1]
        if not vname in variables: raise Exception(f"{vname} is not defined")
        bracket[1].append(variables[vname])
      elif c.isdigit():
       c = int(c)
      bracket[1].append(c)


example = """
# комментарий #
core->print("Hello World")
core->update_var("pasha" 115)
core->print($pasha)
func hello {
core->print("Im in function" $arg1)
}
custom->hello("hello")
"""
run(example,"Hello")
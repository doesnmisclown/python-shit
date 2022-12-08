def lexer(c):
  return c.split()

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
  quote = [False,[]]
  function = [False,"main",[]]
  current = modules
  if type(code) == str: code = lexer(code)
  comment = False
  for i,c in enumerate(code):
    if c == "func":
      function[0] = True
      function[1] = code[i+1]
    elif c == "endfunc":
      function[2] = function[2][1:]
      function_block = function[2]
      modules["custom"][function[1]] = lambda *args: run(" ".join(function_block),*args)
      function[0] = False
      function[1] = "main"
      function[2] = []
    elif function[0]:
      function[2].append(c)
    elif c == "#": comment = not comment
    elif comment: continue
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
      if c == '"':
        quote[0] = not quote[0]
        if not quote[0]:
          bracket[1].append(" ".join(quote[1]))
          quote[1] = []
      elif quote[0]:
        quote[1].append(c)
      elif c.startswith("$"):
        vname = c[1:]
        if not vname in variables: raise Exception(f"{vname} is not defined")
        bracket[1].append(variables[vname])
      elif c.isdigit():
       c = int(c)
       bracket[1].append(c)


example = """
# комментарий #
core -> print ( " Hello World " )
core -> update_var ( " pasha " 115 )
core -> print ( $pasha )
func hello
core -> print ( " I'm in function " )
endfunc
custom -> hello ( )
core -> print ( " It's working? " )
"""
run(example,"Hello")
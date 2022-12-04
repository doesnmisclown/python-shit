code = """
# комментарий #

import ./some.link as some
modules -> core -> print ( " Hello World " )
modules -> some -> sub -> run ( " Lorem ipsum dolor sit omlet " )
modules -> core -> update_var ( " pasha " 115 )
modules -> core -> print ( $pasha )
modules -> core -> print_sum ( 1 1 )
func hello argument1 argument2
begin 

end
"""
variables = {}
modules = {
  "core": {
    "print": lambda *args: print(*args),
    "update_var": lambda name,value: variables.update({name:value}),
    "print_sum": lambda a,b: print(a+b)
  }
}
current = None
code = code.split()
print(code)
is_comment = False
is_bracket = False
in_bracket = []
is_quote = False
in_quote = []

for i,c in enumerate(code):
  if c == "#":
    is_comment = not is_comment
  elif is_comment:
    continue
  elif c == "import":
    module = code[i+1]
    name = None
    if code[i+2] == "as":
      name = code[i+3]
    else:
      name = code[i+1].split(".link")[0]
    modules[name] = dict(sub=dict(run=lambda x: print(x)))
  elif c == "->":
    child = code[ i+1 ]
    parent = code[ i-1 ]
    if parent == "modules":
      current = modules
    current = current[child]
  elif c == "(":
    is_bracket = True
  elif c == ")":
    is_bracket = False
    current(*in_bracket)
    in_bracket = []
  elif is_bracket:
    if c == '"':
      is_quote = not is_quote
      if not is_quote:
        in_bracket.append(" ".join(in_quote))
        in_quote = []
    elif is_quote:
      in_quote.append(c)
    elif c.startswith("$"):
      vname = c[1:]
      if not vname in variables: raise Exception(f"{vname} is not defined")
      in_bracket.append(variables[vname])
    else:
      if c.isdigit(): c = int(c)
      in_bracket.append(c)
print(variables)
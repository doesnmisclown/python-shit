import os
packages = []
def parse_history(hstr):
  _packages = []
  hstr = ":".join(hstr.split(":")[1:])
  r = hstr.split("),")
  for rr in r:
    rr = rr.strip()
    if "automatic" in rr: continue
    rr = rr.split(":")[0]
    _packages.append(rr)
  return _packages
with open(f"{os.getenv('PREFIX') or ''}/var/log/apt/history.log") as f:
  f = f.read()
  f = f.split("\n")
  for p in f:
    if p.startswith("Install"):
      p = parse_history(p)
      for pp in p:
        packages.append(pp)
    elif p.startswith("Remove") or p.startswith("Purge"):
       p = parse_history(p)
       for pp in p:
         if pp in packages:
           packages.remove(pp)
print("\n".join(["Installed packages:",*packages]))
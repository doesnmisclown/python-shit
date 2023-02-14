"""
history.py - script for debian which count manual installed packages using apt history log
"""
import os
packages = []
def parse_history(hstr):
    """
    This function parse history line and return non-automatic packages
    """
    _packages = []
    hstr = ":".join(hstr.split(":")[1:])
    package_names = hstr.split("),")
    for name in package_names:
        name = name.strip()
        if "automatic" in name:
            continue
        name = name.split(":")[0]
        _packages.append(name)
    return _packages
with open(f"{os.getenv('PREFIX') or ''}/var/log/apt/history.log","r",encoding="utf8") as f:
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

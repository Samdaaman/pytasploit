# Readme
## TODO
- AED module which can revive pyterpreter from a separate process


### Compiling pyterpreter into single file:  
`pinliner pyterpreter -o pyterpreter.py`


pip install git+https://github.com/calebstewart/pwncat.git@v0.3.1
pip install git+https://github.com/calebstewart/paramiko


### Pwncat mods
/remote/victim.py
line 356
```
self.shell = self.which("bash")
if self.shell is None:
    self.shell = self.which("sh")
progress.log(
    f"[yellow]warning[/yellow]: could not detect shell; assuming [blue]{self.shell}[/blue]"
)
```

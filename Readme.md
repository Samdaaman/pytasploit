# Readme
### Compiling pyterpreter into single file:  
`pinliner pyterpreter -o pyterpreter.py`


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
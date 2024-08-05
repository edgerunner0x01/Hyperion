from zProbe.Lib.zProbe import Target
from zProbe.Lib import zProbe
from Shell import fshell
zProbe.logger=zProbe.Log("DEBUG").logger
fshell.Shell.logger = fshell.Log(log_method="DEBUG").logger
def main():
    shell=fshell.Shell()
    shell.Banner()
    shell.Menu()
    shell.Run()
if __name__ == "__main__":
    main()


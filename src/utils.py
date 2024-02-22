import os
class Utilities:
    def MkdirIfNotExists(dirv: str) -> None:
        if (not os.path.exists(dirv)):
            os.mkdir(dirv)    

    def CheckDir(dirv: str) -> bool:
        if (not os.path.exists(dirv) or not os.path.isdir(dirv)):
            return False
        return True
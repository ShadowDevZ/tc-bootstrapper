from defs import *
import os
import shutil

class Stamp:
    def _WriteStamp(self, path:str, ptype: str) -> bool:
        if (not self._CheckStamp()):
            return False
        f = open(self.stampPath + "/.notice", "a")
    
    
    
    
        if (ptype != 'A' and ptype != 'D'):
            return False;
    
   
    
        f.write(ptype + ' ' + path + '\n')
    
        f.close()
        return True
    
    def _ClenupStamp(self) -> bool:
        
        if (not self.IsInitialized()):
            return False
        
        if (not self._CheckStamp()):
          #  print("Cleanup failed, stamp doesnt exist")
            #err already set by called function
            return False
        f = open(self.stampPath+"/.notice", 'r+')
    

    
        for ln in f:
    
        

            if ln.startswith('A'):
                a = ln.rstrip().split()
           
                if (os.path.exists(a[-1])):
                   # print(f"Cleaning {a[-1]}")
                    os.remove(a[-1])


            elif ln.startswith('D'):
                a = ln.rstrip().split()
                if (os.path.exists(a[-1])):
                 #   print(f"Cleaning tree {a[-1]}")
                    shutil.rmtree(a[-1])
       

    
        f.close()
        return True
    
    def _CheckStamp(self) -> bool:
       
        if (not self.IsInitialized()):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return False
        
        if (not os.path.exists(self.stampPath + "/.notice")):
            self.SetLastError(BSOE.BSOE_NOFILE)
            return False
        
        f = open(self.stampPath + "/.notice", "r")
        msg = "#!!!This file has been autogenerated and is used as stamp\n"
        if (f.readline() != msg):
            
            f.close()
            self.SetLastError(BSOE.BSOE_IO_FAIL)
            return False
        f.close()
        self.SetLastError(BSOE.BSOE_SUCCESS)
        return True
        
    def _DeleteStamp(self) -> bool:
        if (not self.IsInitialized()):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return False
        if (not self._CheckStamp()):
            return False
        
        os.remove(self.stampPath + "/.notice")
        self.SetLastError(BSOE.BSOE_SUCCESS)
        return True
    def _CreateStamp(self) -> bool:
        if (not self.IsInitialized()):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return False
        if (not os.path.exists(self.stampPath) and not os.path.exists(self.stampPath + "/.notice")):
            self.SetLastError(BSOE.BSOE_NOFILE)
            return False
        
        f = open(f"{self.stampPath}/.notice", "w")
        f.write("#!!!This file has been autogenerated and is used as stamp\n#DO NOT EDIT MANUALLY\n")
        f.close()
        self.SetLastError(BSOE.BSOE_SUCCESS)
        return True
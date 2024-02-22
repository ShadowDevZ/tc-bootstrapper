import os
import subprocess
from defs import *
import utils
class Build:
    def _CompileTargetBU(self) -> BSOE:
        if (not self.IsInitialized()):
            return BSOE.BSOE_LIB_NOT_INIT
        
        
        
    
    #check stamp
        target = self.ConfigGetEntry("BINUTILS_ARCH")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
      
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
        bv = self.ConfigGetEntry("BU_VERSION")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
        cf = self.ConfigGetEntry("CFLAGS_BINUTILS")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
        nproc = self.ConfigGetEntry("NPROC")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
    
        bucmd = f"../{bv}/configure --target={target} --prefix={self.installPath} {cf}"
     
       # print(bucmd, self.workDir + bv)
       # print(f"make -j{nproc}", self.workDir + bv)
       # print("make install", self.workDir + bv)
        utils.Utilities.MkdirIfNotExists(self.workDir + "binutils_build")
        self._WriteStamp(self.workDir + "binutils_build", 'D')
        self._xcall(bucmd, self.workDir + "binutils_build")
        self._xcall(f"make -j{nproc}", self.workDir +"binutils_build")
        self._xcall("make install",self.workDir+ "binutils_build")
        
        return BSOE.BSOE_SUCCESS
    
    
    def _xcall(self, cmd: str, wd: str) -> int:
        if (not self.IsInitialized()):
            return -1
        envi = os.environ.copy()
        envi["PATH"] = f"{self.installPath}/bin:{envi['PATH']}"
        ret = subprocess.Popen(cmd,env=envi, shell=True,cwd=wd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8', universal_newlines=True)
        if (ret == None):
            self.SetLastError(BSOE.BSOE_XCALL_FAIL)
            return -1
        if (not (self.options & BootStrapperOptions.BSOE_SUPPRESS)):
            while True:
                ln = ret.stdout.readline()
            
                if not ln:
                    break
                print(ln, end='')
            
        exitCode = ret.wait()
        
        if (exitCode != 0):
            self.SetLastError(BSOE.BSOE_XCALL_FAIL)
            return exitCode
        
        self.SetLastError(BSOE.BSOE_SUCCESS)
        return 0
    
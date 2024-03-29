from re import sub
import utils
from defs import *
import subprocess
import os

def _ApplyRedZonePatch(self) -> bool:
    if (not self.IsInitialized()):
            return False
    if (not self.options & BootStrapperOptions.BSOE_X64_ELF_NORED):
        self.SetLastError(BSOE.BSOE_INV_OPT)
        return False
    
    rpatch = os.path.dirname(os.path.realpath(__file__)) + '/patches/x86_64-elf-noredzone.patch'
 
    txt="""
#Autogenerated by TC-Bootstrapper\n
MULTILIB_OPTIONS += mno-red-zone\n
MULTILIB_DIRNAMES += no-red-zone

    """
    gcc_src = self.ConfigGetEntry("GCC_DEST_FILE_DOWNLOAD")
    if (gcc_src == -1):
        self.SetLastError(BSOE.BSOE_INV_OPT)
        return False
    
    idx = gcc_src.find(".tar.")
    if (idx != -1):
            gcc_src = gcc_src[:idx]
    else:
            self.SetLastError(BSOE.BSOE_NOFILE)
            return False
    
    #compatible with gcc 10, 12 and 13 release
    #todo in future make the patch process automated
    versionsCompat = ["10","12", "13"]
    
    f = open(f"{gcc_src}/gcc/config/i386/x86_64-elf-nored", "w")
    f.write(txt)
    f.close()
    
    gccVersion = self.ConfigGetEntry("GCC_VERSION")
    if (gccVersion == -1):
        self.SetLastError(BSOE.BSOE_INV_OPT)
        return False
    #strip gcc- prefix
    gccVersion = gccVersion[4:]
    #find first dot separator
    idx = gccVersion.find('.')
    print(gccVersion)
    print(idx)
    if (idx == -1):
        self.SetLastError(BSOE.BSOE_INTERNAL)
        return False
    
    gccMajor = gccVersion[:idx]
    print(gcc_src)
    if (gccMajor in versionsCompat):
        rpatch += gccMajor
    else:
        
        self.SetLastError(BSOE.BSOE_NOFILE)
        return False
    
    if (not os.path.exists(rpatch) or not os.path.isfile):
        self.SetLastError(BSOE.BSOE_NOFILE)
        return False
    
    
    rv = subprocess.Popen(f"/bin/patch {gcc_src}/gcc/config.gcc {rpatch}", shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8', universal_newlines=True)
    if (rv == None):
        self.SetLastError(BSOE.BSOE_XCALL_FAIL)
        return False
    
    while (True):
        ln = rv.stdout.readline()
        if not ln:
            break
        if 'FAILED' in ln:
            self.SetLastError(BSOE.BSOE_XCALL_FAIL)
            return False
        if (not self.options & BootStrapperOptions.BSOE_SUPPRESS):
            print(ln)
    
    
    
    self.SetLastError(BSOE.BSOE_SUCCESS)
    return True

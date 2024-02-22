import pathlib
import os
from defs import *
import tarfile
import redzone
class Unpack:
     def UnpackBinutils(self) -> BSOE:
        if (not self.IsInitialized()):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return BSOE.BSOE_LIB_NOT_INIT
        buver = self.ConfigGetEntry("BU_VERSION")
        dst = self.ConfigGetEntry("BU_DEST_FILE_DOWNLOAD")
        if (dst == -1 or buver == -1):
            self.SetLastError(BSOE.BSOE_INTERNAL)
            
            return BSOE.BSOE_INTERNAL
       
      
        ret = self._UnpackSource(dst, overwrite=True)
        self._WriteStamp(self.extractPath + '/'+buver, 'D')
        self.SetLastError(ret)
        return ret
    
     def UnpackGcc(self) -> BSOE:
        if (not self.IsInitialized()):
            return BSOE.BSOE_LIB_NOT_INIT
        
        dst = self.ConfigGetEntry("GCC_DEST_FILE_DOWNLOAD")
        gccver = self.ConfigGetEntry("GCC_VERSION")
        if (dst == -1 or gccver == -1):
            return BSOE.BSOE_INTERNAL
        
        ret = self._UnpackSource(dst)
        self._WriteStamp(self.extractPath + '/'+gccver, 'D')
        if (ret != BSOE.BSOE_SUCCESS):
            return ret
        
        if (self.options & BootStrapperOptions.BSOE_X64_ELF_NORED):
            rv = redzone._ApplyRedZonePatch(self)
            if (rv != True):
                return BSOE.BSOE_IO_FAIL
        
        
        
        return ret
    
     def _UnpackSource(self, src: str, overwrite=False) -> BSOE:
        if (not self.IsInitialized()):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return BSOE.BSOE_LIB_NOT_INIT
        
        if (not os.path.exists(self.extractPath)):
            self.SetLastError(BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
        if (not os.path.exists(src)):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return BSOE.BSOE_NOFILE
        
        perms = "r:"
        rpath = src.split('/')[-1]
        
        #strip extension from path
        idx = rpath.find(".tar.")
        if (idx != -1):
            rpath = rpath[:idx]
        else:
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return BSOE.BSOE_NOFILE
        
        if (overwrite == False and (not self.options & BootStrapperOptions.BSOE_OVERWRITE_ALL)):
            if (os.path.exists(self.extractPath + rpath)):
                self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
                return BSOE.BSOE_SRC_ALR_EXISTS
        
        for ext in self._filter:
            _ext = ext.split('.')[-1]
            if '.' + _ext == pathlib.Path(src).suffix.lower():
                perms += ext.split('.')[-1]
                break
       
        tar = tarfile.open(src, perms)
        tar.extractall(self.extractPath, filter=tarfile.tar_filter)
        
        tar.close()
        
        #timestamp
        
        
        return BSOE.BSOE_SUCCESS
        
    
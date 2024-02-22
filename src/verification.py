from defs import *
import os
import gnupg
class Verify:
    def _VerifySignature(self, sig: str, file: str) -> BSOE:
        if (not self.IsInitialized()):
            return BSOE.BSOE_LIB_NOT_INIT
        
        if (not os.path.exists(sig) or not os.path.isfile(sig)):
            return BSOE.BSOE_NOFILE
        
        ghome = self.keyChainPath + "/gpghome"
        if (not os.path.exists(ghome)):
            os.makedirs(ghome, mode=0o700)
        
        if (not os.path.isdir(ghome)):
            return BSOE.BSOE_NOFILE
        
        gpg = gnupg.GPG(gnupghome=ghome)
        gpg.import_keys_file(self.keyChainPath + "/gnu-keyring.gpg")
        
        f = open(sig, 'rb')
        ires = gpg.verify_file(f, file, close_file=True)
        
        if (not self._WriteStamp(ghome, 'D')):
            return BSOE.BSOE_STAMP_FAIL
        
        if (ires.valid):
            return BSOE.BSOE_SUCCESS
        else:
            return BSOE.BSOE_SIGNATURE
            
    def VerifySignature(self, bd: BootStrapperObject) ->bool:
        if (not self.IsInitialized()):
            return False
        vals = []
        if (bd == BootStrapperObject.BSOBJ_BINUTILS):
            vals = ["BU_SIGNATURE", "BU_DEST_FILE_DOWNLOAD"]
        elif (bd == BootStrapperObject.BSOBJ_GCC):
            vals = ["GCC_SIGNATURE", "GCC_DEST_FILE_DOWNLOAD"]
        else:
            return False
        
        if (self.ConfigGetEntry(vals[0]) != -1 and self.ConfigGetEntry(vals[1]) != -1):
                rv = self._VerifySignature(str(self.ConfigGetEntry(vals[0])), str(self.ConfigGetEntry(vals[1])))
                if (rv != BSOE.BSOE_SUCCESS):
                    self.SetLastError(BSOE.BSOE_SIGNATURE)
                    return False
        
        
        
        return True

 #Downloadds detached signature for the specified object
    #uri -> url to the source
    #downloadPath -> local save path
    def _DownloadSignature(self, uri: str, downloadPath: str) -> BSOE:
        if (not self.IsInitialized()):
            return BSOE.BSOE_LIB_NOT_INIT
        sig = uri + ".sig"
        
        rv = self._DownloadSource(sig, downloadPath)
        if (rv != BSOE.BSOE_SUCCESS):
            return self.GetLastError()
        
        return BSOE.BSOE_SUCCESS

    
    def _DownloadKeychainGNU(self) -> BSOE:
        if (not self.IsInitialized()):
            return BSOE.BSOE_LIB_NOT_INIT
        rv = self._DownloadSource(GNU_GPG_KEYRING, self.keyChainPath + "/gnu-keyring.gpg", overwrite=True)
        if (rv != BSOE.BSOE_SUCCESS):
            return rv
        
        
        
        return BSOE.BSOE_SUCCESS
   
        
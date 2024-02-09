import subprocess
from build import GetBinUtilsUrl, get_files, mkdir_if_not_exists
import menu
import os
import requests
from bs4 import BeautifulSoup
import pathlib
import urllib.request
import urllib.parse
import urllib.error
import sys
import tarfile
import shutil
from subprocess import call

from enum import IntEnum

class BootStrapperOptions(IntEnum):
    BSO_VERIFY_PGP = 1 << 1
    BSO_CLEANUP = 1 << 2
    BSO_MAXCORE = 1 << 3
    BSO_OUTPUT_VERBOSE = 1 << 4
    #if not set, provides TUI menu
    BSO_SCRIPTABLE = 1 << 5
    BSO_OVERWRITE = 1 << 6
    BSO_FILE_LOG = 1 << 7
    BSOE_INIT_LIB = 1 << 8
    BSOE_OVERWRITE_DOWNLOAD = 1 << 9
class BootStrapperDownloadOpts(IntEnum):
    BSDO_NONE = 0
    BSDO_GCC = 1 << 1
    BSDO_BINUTILS = 1 << 2

class BSOE(IntEnum):
    BSOE_SUCCESS = 0
    BSOE_BAD_PARAM = 1
    BSOE_IO_FAIL = 2
    BSOE_ACCESS_DENIED = 3
    BSOE_PGP_FAIL = 4
    BSOE_NODISK = 5
    BSOE_UNR_SRC = 6
    BSOE_NOFILE = 7
    BSOE_RMT_INVALID = 8
    BSOE_INTERNAL = 9
    BSOE_INV_OPT = 10
    BSOE_INST_PATH = 11
    BSOE_XCALL_FAIL = 12
    BSOE_STAMPLOCK = 13
    BSOE_RMT_URL = 14
    BSOE_FILE_CORRUPTED = 15
    BSOE_BAD_PRIVIL = 16
    BSOE_LIB_NOT_INIT = 17
    BSOE_OVERFLOW = 18
    BSOE_LIB_ALR_INIT = 19
    BSOE_NOT_IMPLEMENTED = 20
    BSOE_SRC_ALR_EXISTS = 21
    
def CheckDir(dir) -> bool:
    if (not os.path.exists(dir) or not os.path.isdir(dir)):
        return False
    return True
import multiprocessing


CONFIG_URL_BINUTILS="https://ftp.gnu.org/gnu/binutils"
CONFIG_URL_TOOLCHAIN="https://ftp.gnu.org/gnu/gcc/"

GNU_GPG_KEYRING="https://ftp.gnu.org/gnu/gnu-keyring.gpg"



g_config = []
class BootStrapper:
   
    
    def __init__(self, workDir, installPath, extractPath=None, stampPath=None, options=0, keychainPath=None) -> None:
        #todo make it more flexible using config so it can be changed later
        self.workDir = workDir
        self.installPath = installPath
        self.extractPath = extractPath
        self.stampPath = stampPath
        self.options = options
        self._lastErrorCode = 0
        self.nproc = 0
      #  self._config = [None]
        self.keyChainPath = keychainPath
        
        
    
    def Inititialize(self) -> BSOE:
        
       
        
        
        if (self.options & BootStrapperOptions.BSOE_INIT_LIB):
            return BSOE.BSOE_LIB_ALR_INIT
        
        if (not CheckDir(self.workDir) or not CheckDir(self.installPath)):
            return BSOE.BSOE_NOFILE
            
        if (self.nproc <= 0 or self.nproc > multiprocessing.cpu_count()):
            return BSOE.BSOE_OVERFLOW
        
        
        if (self.stampPath == None):
            self.stampPath = self.workDir
        elif (not CheckDir(self.stampPath)):
            return BSOE.BSOE_NOFILE
        
        if (self.extractPath == None):
            self.extractPath = self.workDir
        elif (not CheckDir(self.extractPath)):
            return BSOE.BSOE_NOFILE
        
        if (self.keyChainPath == None):
            self.keyChainPath = self.workDir + "/keychain"
            mkdir_if_not_exists(self.keyChainPath)
        
        elif (not CheckDir(self.keyChainPath)):
            return BSOE.BSOE_NOFILE
                
        
        
        self.options |= BootStrapperOptions.BSOE_INIT_LIB
        
        #temporary, todo later
      #  if (self.options != BootStrapperOptions.BSOE_INIT_LIB):
      #      return BSOE.BSOE_NOT_IMPLEMENTED
        
        
        return BSOE.BSOE_SUCCESS
    
    
            
    def Finalize(self) -> BSOE:
        if (not (self.options & BootStrapperOptions.BSOE_INIT_LIB)):
            return BSOE.BSOE_LIB_NOT_INIT
        
        self.options &= ~(BootStrapperOptions.BSOE_INIT_LIB)
        return BSOE.BSOE_SUCCESS
        
        
        
    
    def IsInitialized(self) -> bool:
        if (not (self.options & BootStrapperOptions.BSOE_INIT_LIB)):
            return False
        return True
    
    def SetLastError(self, err: BSOE) -> None:
        if (err <= len(BSOE)):
            self._lastErrorCode = err
    
    def GetLastError(self):
        return self._lastErrorCode
    
    def GetLastErrorAsString(self) -> str:
        _errs = ["Success",
                 "Bad parameter",
                 "I/O fail",
                 "Access denied",
                 "PGP verification failed",
                 "No diskspace left",
                 "Source is unreachable",
                 "No such file or directory",
                 "Failed to retrieve remote file",
                 "Internal error",
                 "Invalid options passed to compiler",
                 "Install path does not exist",
                 "Failed to call remote process",
                 "Timestamp is not locked",
                 "Remote url does not exist",
                 "Corrupted file",
                 "Bad privileges",
                 "Library not initialized",
                 "Parameter overflown",
                 "Library has been already intialized",
                 "Function/Feature is not currently supported",
                 "Source file already exists"]
        
        return _errs[self._lastErrorCode]
    
    
    def _GetRemoteFileList(self, url: str, allowedExtension: list=[]) -> list:
        if (not BootStrapper.IsInitialized):
            BootStrapper.SetLastError(self, BSOE.BSOE_LIB_NOT_INIT)
            return []
        
        response = requests.get(url)
        if (url[-1] == "/"):
            url = url[::1]
            
        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, "html.parser")
            files = []
            
            for atag in soup.find_all('a', href=True):
                href = atag['href']
                
                fullUrl = url + '/' + href
                
                if allowedExtension is not []:
                    
                    for ext in allowedExtension:
                      if fullUrl.lower().endswith(ext):
                          files.append(fullUrl)
                else:
                    files.append(fullUrl) 
            BootStrapper.SetLastError(self, BSOE.BSOE_SUCCESS)
            return files
        else:
            BootStrapper.SetLastError(self, BSOE.BSOE_UNR_SRC)
            return [response.status_code] 
        
    
    def _GetRemoteDirList(self, url: str) -> list:
        
        if (not BootStrapper.IsInitialized):
            BootStrapper.SetLastError(self, BSOE.BSOE_LIB_NOT_INIT)
            return []
        
        
        response = requests.get(url)
        
        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, "html.parser")
            dirs = []
            
            for atag in soup.find_all('a', href=True):
                href = atag['href']
                
                fullUrl = urllib.parse.urljoin(url, href)
                
                if (fullUrl.endswith('/')):
                    dirs.append(fullUrl)
            BootStrapper.SetLastError(self, BSOE.BSOE_SUCCESS)
            return dirs
        else:
            BootStrapper.SetLastError(self, BSOE.BSOE_UNR_SRC)
            return [response.status_code]
    """
    def MenuGetBinUtils(self):
        
        files = get_files(CONFIG_URL_BINUTILS, [".tar.xz"])
        if (BootStrapper.GetLastError(self) != BSOE.BSOE_SUCCESS):
            #todo show on menu
            print("dbg url fail:", str(files))
            pass
        #show menu here
        
       """ 
    
    def _DownloadSource(self, url: str, dst: str):
        if (not self.options & BootStrapperOptions.BSOE_OVERWRITE_DOWNLOAD):
            BootStrapper.SetLastError(self, BSOE.BSOE_SRC_ALR_EXISTS)
            return False
        
        try:
            urllib.request.urlopen(url, timeout=5)
        except urllib.error.URLError as e:
            BootStrapper.SetLastError(self, BSOE.BSOE_RMT_URL)
            return False
        
        try:
            #add report
            urllib.request.urlretrieve(url, dst)
        except urllib.error.URLError as e:
            BootStrapper.SetLastError(self, BSOE.BSOE_RMT_URL)
            return False
        
        #todo stamp here
    
    def _DownloadSourceGCC(self):
        pass
    
    
    
    def CompileTarget(self, arch, ccOptions) -> BSOE:
        return BSOE.BSOE_ACCESS_DENIED
        pass
    
    def _CompileTargetGcc():
        pass
    def _CompileTargetBU()):
        pass
    
    def _ExtractSources():
        pass
    
    
    def VerifyPGP():
        pass
    def _xcall():
        pass
    
    def UnpackSource():
        pass
    
    def _WriteStamp():
        pass
    def _ClenupStamp():
        pass
    def _DeleteStamp():
        pass
    def CreateStamp():
        pass
    
    def DownloadMenu():
        pass
    def OptionsMenu():
        pass
    def WorkProgress():
        pass
    # global config instead of locally passed vars
    #example usage: ConfigWrite(CONFIG_CC, "gcc")
    #               ConfigWrite(CONFIG_NPROC, 8)
    #       compile_options = ["-Werror", "-mno-red-zone"]...
    #       ..
    #       ConfigWrite(CONFIG_COPTS, compile_options)
    
    #todo use more efficient approach, eg. binary search
    def ConfigGetEntry(self, var: str):
        for e in g_config:
            for x in e:
                if g_config[x][0] == var:
                    return g_config[x][1]
        
        return None
            
        
    def ConfigWriteEntry(self, var:str, key):
        global g_config
        found = False
        val = -1
        for e in g_config:
            for x in e:
                if g_config[x][0] == var:
                    found = True
                    val = x
                    
        if (not found):
            g_config += [[var, key]]
        else:
            g_config[val][1] = key

    
    
    
    
    
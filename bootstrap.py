import subprocess
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

from enum import Enum

class BootStrapperOptions(Enum):
    BSO_VERIFY_PGP = 1 << 1
    BSO_CLEANUP = 1 << 2
    BSO_MAXCORE = 1 << 3
    BSO_OUTPUT_VERBOSE = 1 << 4
    #if not set, provides TUI menu
    BSO_SCRIPTABLE = 1 << 5
    BSO_OVERWRITE = 1 << 6
    BSO_FILE_LOG = 1 << 7
    

class BSOE(Enum):
    BSOE_SUCCESS = 0
    BSOE_BAD_PARAM = 1,
    BSOE_IO_FAIL = 2,
    BSOE_ACCESS_DENIED = 3,
    BSOE_PGP_FAIL = 4,
    BSOE_NODISK = 5,
    BSOE_UNR_SRC = 6,
    BSOE_NOFILE = 7,
    BSOE_RMT_INVALID = 8,
    BSOE_INTERNAL = 9,
    BSOE_INV_OPT = 10,
    BSOE_INST_PATH = 11,
    BSOE_XCALL_FAIL = 12,
    BSOE_STAMPLOCK = 13,
    BSOE_RMT_URL = 14,
    BSOE_FILE_CORRUPTED = 15,
    BSOE_BAD_PRIVIL = 16
    

class BootStrapper:
   
    
    def __init__(self, workDir, installPath, extractPath=None, stampPath=None, options=0, argv=[None]) -> None:
        
        self.workDir = workDir
        self.installPath = installPath
        self.extractPath = extractPath
        self.stampPath = stampPath
        self.options = options
        self._lastErrorCode = 0
        self.nproc = 0
        self._config = [None]
        
        pass
    
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
                 "Bad privileges"]
        
        return _errs[self._lastErrorCode]
    
    def CompileTarget(self, arch, ccOptions) -> BSOE:
        return BSOE.BSOE_ACCESS_DENIED
        pass
    
    def _CompileTargetGcc():
        pass
    def _CompileTargetBU()):
        pass
    
    def _ExtractSources():
        pass
    
    def DownloadSource():
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
    
    def ConfigGetEntry(self, var: str):
        pass
    def ConfigWriteEntry(self, var:str, key):
        pass

    
    
    
    
    
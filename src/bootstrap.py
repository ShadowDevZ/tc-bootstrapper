import subprocess

#import menu
import os
from threading import local
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
import gnupg

from defs import *
import utils

import multiprocessing
import stamp
import verification
import download
import extract
import compile
import utils

class BootStrapper(stamp.Stamp, verification.Verify, download.Download, extract.Unpack, compile.Build):
   
    
    def __init__(self, workDir, installPath, extractPath="", stampPath="", options=0, keychainPath="", downloadCallback=None) -> None:
        #todo make it more flexible using config so it can be changed later
        
         #ranked by priority
        self._filter = [".tar.xz", ".tar.lz", ".tar.gz", ".tar.bz2"]
        self._config = []
        self._lastErrorCode = BSOE.BSOE_SUCCESS
        self.options = options
        self._lastUriDownloaded = ""
        self._lastUriPathLocal = ""
        if (downloadCallback != None):
            self._downloadCallback = downloadCallback
        else:
            self._downloadCallback = None
        self.nproc = 0
       
        
        
        if (options & BootStrapperOptions.BSOE_QUERY_ONLY):
            
            return
        
        
        self.workDir = workDir
        
        if (self.workDir[-1] != '/'):
            self.workDir += '/'
        
        self.installPath = installPath
        if (self.installPath[-1] != '/'):
            self.installPath += '/'
            
        if (extractPath != None):
            self.extractPath = extractPath
        else:
            self.extractPath = workDir
        
        if (self.extractPath[-1] != '/'):
            self.extractPath += '/'
        
        
        if (stampPath == None):
            self.stampPath = self.workDir
        else:
            self.stampPath = stampPath
            
        
            
        
        
        self.keyChainPath = keychainPath
        
        
        
       #causes problems with build
   # def __del__(self):
   #     self.Finalize()
        
    
    def Inititialize(self) -> BSOE:
        if (self.options & BootStrapperOptions.BSOE_QUERY_ONLY):
            return BSOE.BSOE_SUCCESS
        
        utils.Utilities.MkdirIfNotExists(self.extractPath)
        utils.Utilities.MkdirIfNotExists(self.workDir)
        utils.Utilities.MkdirIfNotExists(self.installPath)
        
        
        
        if (self.options & BootStrapperOptions.BSOE_INIT_LIB):
            BootStrapper.SetLastError(self, BSOE.BSOE_LIB_ALR_INIT)
            return BSOE.BSOE_LIB_ALR_INIT
        
        if (not utils.Utilities.CheckDir(self.workDir) or not utils.Utilities.CheckDir(self.installPath)):
            BootStrapper.SetLastError(self, BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
           
        _nproc = int(self.ConfigGetEntry("NPROC")) 
        
        if (_nproc > multiprocessing.cpu_count()):
            BootStrapper.SetLastError(self, BSOE.BSOE_OVERFLOW)
            return BSOE.BSOE_OVERFLOW
        elif (_nproc == -1):
            self.nproc = 1
        
        else:
            self.nproc = _nproc
            
        
        
        if (self.stampPath == ""):
            self.stampPath = self.workDir
        elif (not utils.Utilities.CheckDir(self.stampPath)):
            BootStrapper.SetLastError(self, BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
        
        if (self.extractPath == ""):
            self.extractPath = self.workDir
        elif (not utils.Utilities.CheckDir(self.extractPath)):
            BootStrapper.SetLastError(self, BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
        
        if (self.keyChainPath == ""):
            self.keyChainPath = self.workDir + "/keychain"
            utils.Utilities.MkdirIfNotExists(self.keyChainPath)
        
        elif (not utils.Utilities.CheckDir(self.keyChainPath)):
            BootStrapper.SetLastError(self, BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
                
        
        
        self.options |= BootStrapperOptions.BSOE_INIT_LIB
        
        #temporary, todo later
      #  if (self.options != BootStrapperOptions.BSOE_INIT_LIB):
      #      return BSOE.BSOE_NOT_IMPLEMENTED
        
        BootStrapper.SetLastError(self, BSOE.BSOE_SUCCESS)
        if(not self._CreateStamp()):
            return BSOE.BSOE_STAMP_FAIL
        
        self._WriteStamp(self.workDir, 'D')
        er = self._DownloadKeychainGNU()
        
        
        return er
    
    
            
    def Finalize(self) -> BSOE:
        if (not (self.options & BootStrapperOptions.BSOE_INIT_LIB)):
            return BSOE.BSOE_LIB_NOT_INIT
        
        
        #call cleanup routine here
        if (self.options & BootStrapperOptions.BSO_CLEANUP):
            self._ClenupStamp()
            self._DeleteStamp()
        
        self.options &= ~(BootStrapperOptions.BSOE_INIT_LIB)
        return BSOE.BSOE_SUCCESS
        
        
        
    
    def IsInitialized(self) -> bool:
        if (not (self.options & BootStrapperOptions.BSOE_INIT_LIB)):
            return False
        return True
    
    def SetLastError(self, err: BSOE) -> None:
        if (err <= len(BSOE)):
            self._lastErrorCode = err
    
    def GetLastError(self) -> BSOE:
        return self._lastErrorCode
    
    def GetLastErrorAsString(self) -> str:
        
        return self.GetErrorAsString(self.GetLastError())
    
    def GetErrorAsString(self, err: BSOE) -> str:
        if (err > len(BSOE)):
            return "<NULL>"
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
                 "Source file already exists",
                 "Failed to initialize timestamp",
                 "Failed to check remote or local signature",
                 "Invalid version"]
        
        return _errs[err]
    
    
    
    
   
    
    
   
    # global config instead of locally passed vars
    #example usage: ConfigWrite(CONFIG_CC, "gcc")
    #               ConfigWrite(CONFIG_NPROC, 8)
    #       compile_options = ["-Werror", "-mno-red-zone"]...
    #       ..
    #       ConfigWrite(CONFIG_COPTS, compile_options)
    
    #todo use more efficient approach, eg. binary search
    def ConfigGetEntry(self, var: str):

        for i in range(len(self._config)):
            for j in range(i+1):
                if self._config[j][0] == var:
                    return self._config[j][1]
        
        return -1
            
        
    def ConfigWriteEntry(self, var:str, key):
        
        found = False
        val = -1
        for i in range(len(self._config)):
            for j in range(i+1):
                if self._config[j][0] == var:
                    found = True
                    val = j
                    
        if (not found):
            self._config += [[var, key]]
        else:
            self._config[val][1] = key



    
    
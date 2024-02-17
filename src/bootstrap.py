import subprocess

#import menu
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
    BSOE_PULL_LATEST = 1 << 10
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
    BSOE_STAMP_FAIL = 22
    

def MkdirIfNotExists(dir: str) -> None:
    if (not os.path.exists(dir)):
        os.mkdir(dir)    

def CheckDir(dir) -> bool:
    if (not os.path.exists(dir) or not os.path.isdir(dir)):
        return False
    return True
import multiprocessing


CONFIG_URL_BINUTILS="https://ftp.gnu.org/gnu/binutils"
CONFIG_URL_TOOLCHAIN="https://ftp.gnu.org/gnu/gcc/"

GNU_GPG_KEYRING="https://ftp.gnu.org/gnu/gnu-keyring.gpg"




class BootStrapper:
   
    
    def __init__(self, workDir, installPath, extractPath=None, stampPath=None, options=0, keychainPath=None) -> None:
        #todo make it more flexible using config so it can be changed later
        self.workDir = workDir
        self.installPath = installPath
        if (extractPath != None):
            self.extractPath = extractPath
        else:
            self.extractPath = workDir
        
        if (stampPath == None):
            self.stampPath = self.workDir
        else:
            self.stampPath = stampPath
        self.options = options
        self._lastErrorCode = BSOE.BSOE_SUCCESS
        self.nproc = 0
        self._config = []
        self.keyChainPath = keychainPath
        #ranked by priority
        self._filter = [".tar.xz", ".tar.lz", ".tar.gz", ".tar.bz2"]
       
        
        
    
    def Inititialize(self) -> BSOE:
        
        MkdirIfNotExists(self.extractPath)
        MkdirIfNotExists(self.workDir)
        MkdirIfNotExists(self.installPath)
        
        
        
        if (self.options & BootStrapperOptions.BSOE_INIT_LIB):
            BootStrapper.SetLastError(self, BSOE.BSOE_LIB_ALR_INIT)
            return BSOE.BSOE_LIB_ALR_INIT
        
        if (not CheckDir(self.workDir) or not CheckDir(self.installPath)):
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
            
        
        
        if (self.stampPath == None):
            self.stampPath = self.workDir
        elif (not CheckDir(self.stampPath)):
            BootStrapper.SetLastError(self, BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
        
        if (self.extractPath == None):
            self.extractPath = self.workDir
        elif (not CheckDir(self.extractPath)):
            BootStrapper.SetLastError(self, BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
        
        if (self.keyChainPath == None):
            self.keyChainPath = self.workDir + "/keychain"
            MkdirIfNotExists(self.keyChainPath)
        
        elif (not CheckDir(self.keyChainPath)):
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
        return BSOE.BSOE_SUCCESS
    
    
            
    def Finalize(self) -> BSOE:
        if (not (self.options & BootStrapperOptions.BSOE_INIT_LIB)):
            return BSOE.BSOE_LIB_NOT_INIT
        
        self.options &= ~(BootStrapperOptions.BSOE_INIT_LIB)
        #call cleanup routine here
        
        self._ClenupStamp()
        self._DeleteStamp()
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
                 "Failed to initialize timestamp"]
        
        return _errs[err]
    
    def _GetRemoteFileList(self, url: str) -> list:
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
                
                if self._filter is not []:
                    
                    for ext in self._filter:
                      if fullUrl.lower().endswith(ext):
                          files.append(fullUrl)
                else:
                    files.append(fullUrl) 
            BootStrapper.SetLastError(self, BSOE.BSOE_SUCCESS)
            return files
        else:
            BootStrapper.SetLastError(self, BSOE.BSOE_UNR_SRC)
            return [response.status_code] 
    
    def _print_params(self):
        print("\n\n")
        print("ext", self.extractPath)
        print("wrk", self.workDir)
        print("inst", self.installPath)
        print("opt", self.options)
        print("cfg", self._config)
        print("err", self._lastErrorCode)
        print("estr", self.GetLastErrorAsString())
        print("\n\n")
    
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

    
    def _DownloadSource(self, url: str, dst: str) -> BSOE:
        if (os.path.exists(dst) and (not self.options & BootStrapperOptions.BSOE_OVERWRITE_DOWNLOAD)):
            BootStrapper.SetLastError(self, BSOE.BSOE_SRC_ALR_EXISTS)
            return BSOE.BSOE_SUCCESS
        
       
        try:
            urllib.request.urlopen(url, timeout=5)
        except urllib.error.URLError as e:
            BootStrapper.SetLastError(self, BSOE.BSOE_RMT_URL)
           
            return BSOE.BSOE_RMT_URL
        
        try:
            #add report
            urllib.request.urlretrieve(url, dst)
        except urllib.error.URLError as e:
            BootStrapper.SetLastError(self, BSOE.BSOE_RMT_URL)
           
            return BSOE.BSOE_RMT_URL
        
        BootStrapper.SetLastError(self, BSOE.BSOE_SUCCESS)
        self._WriteStamp(self.extractPath + '/'+dst, 'A')
        return BSOE.BSOE_SUCCESS
        #todo stamp here
    
   
    #vesion is in format 13.2.0 and is catted to the CONFIG_URL_TOOLCHAIN
    def _DownloadSourceGCC(self, version) -> BSOE:
       
        if (not self.IsInitialized()):
            return BSOE.BSOE_LIB_NOT_INIT
          
        dirs = self._GetRemoteDirList(CONFIG_URL_TOOLCHAIN)
        ret = self.GetLastError()
        
        if (ret != BSOE.BSOE_SUCCESS):
            return BSOE.BSOE_RMT_URL
        if (dirs == []):
            return BSOE.BSOE_RMT_URL
        
        url = ""
        for i in range(len(dirs)):
            if (dirs[i][-1] == '/'):
                dirs[i] = dirs[i][:-1]
            ve = dirs[i].rsplit('-')
            if (version == ve[-1]):

                url = dirs[i]
                
        
        gccVersion = url.split('/')[-1]
        url = url + '/' + gccVersion + self._filter[0]
    
        ret = self._DownloadSource(url, self.workDir + gccVersion + self._filter[0])
      
    #todo stamp
        if (ret != BSOE.BSOE_SUCCESS):
            return ret
        else:
            self.ConfigWriteEntry("GCC_DEST_FILE_DOWNLOAD", self.workDir + gccVersion + self._filter[0])
            self.ConfigWriteEntry("GCC_VERSION", gccVersion)
            return BSOE.BSOE_SUCCESS
        
    def _DownloadSourceBinutils(self, version) -> BSOE:
       
        if (not self.IsInitialized()):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return BSOE.BSOE_LIB_NOT_INIT
          
        files = self._GetRemoteFileList(CONFIG_URL_BINUTILS)
    
        ret = self.GetLastError()
         
        if (ret != BSOE.BSOE_SUCCESS):
            self.SetLastError(BSOE.BSOE_RMT_URL)
            return BSOE.BSOE_RMT_URL
        if (files == []):
            self.SetLastError(BSOE.BSOE_RMT_URL)
            return BSOE.BSOE_RMT_URL
        
        url = CONFIG_URL_BINUTILS + '/' + 'binutils-' + version + self._filter[0]
        if (not url in files):
            self.SetLastError(BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
        
        buVersion = url.split('/')[-1]
         
        #strip extension from path
        idx = buVersion.find(".tar.")
        if (idx != -1):
            buVersion = buVersion[:idx]
        else:
            self.SetLastError(BSOE.BSOE_NOFILE)
            return BSOE.BSOE_NOFILE
        
        
        ret = self._DownloadSource(url, self.workDir + buVersion + self._filter[0])
        
        
        
    
        
    #todo stamp
        if (ret != BSOE.BSOE_SUCCESS):
            return ret
        else:
            self.ConfigWriteEntry("BU_DEST_FILE_DOWNLOAD",self.workDir + buVersion + self._filter[0])
            self.ConfigWriteEntry("BU_VERSION", buVersion)
            self.SetLastError(BSOE.BSOE_SUCCESS)
            return BSOE.BSOE_SUCCESS
    
    def CompileTarget(self, arch, ccOptions) -> BSOE:
        return BSOE.BSOE_ACCESS_DENIED
        pass
    
    def _CompileTargetGcc(self) -> BSOE:
        if (not self.IsInitialized()):
            return BSOE.BSOE_LIB_NOT_INIT
    
    #check stamp
        target = self.ConfigGetEntry("GCC_ARCH")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
      
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
        bv = self.ConfigGetEntry("GCC_VERSION")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
        cf = self.ConfigGetEntry("CFLAGS_GCC")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
        nproc = self.ConfigGetEntry("NPROC")
        if (target == -1):
            return BSOE.BSOE_BAD_PARAM
    
        gcccmd = f"../{bv}/configure --target={target} --prefix={self.installPath} {cf}"
        print(gcccmd)
       # print(bucmd, self.workDir + bv)
       # print(f"make -j{nproc}", self.workDir + bv)
       # print("make install", self.workDir + bv)
        MkdirIfNotExists(self.workDir + "gcc_build")
        self._xcall(gcccmd, self.workDir + "gcc_build")
        self._xcall(f"make all-gcc -j{nproc} && make all-target-libgcc -j{nproc}", self.workDir +"gcc_build")
        self._xcall("make install-gcc && make install-target-libgcc",self.workDir+ "gcc_build")
        
        return BSOE.BSOE_SUCCESS
    
    
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
        MkdirIfNotExists(self.workDir + "binutils_build")
        self._WriteStamp(self.workDir + "binutils_build", 'D')
        self._xcall(bucmd, self.workDir + "binutils_build")
        self._xcall(f"make -j{nproc}", self.workDir +"binutils_build")
        self._xcall("make install",self.workDir+ "binutils_build")
        
        return BSOE.BSOE_SUCCESS
    
    def VerifyPGP():
        pass
    def _xcall(self, cmd: str, wd: str) -> int:
        if (not self.IsInitialized()):
            return -1
        envi = os.environ.copy()
        envi["PATH"] = f"{self.installPath}/bin:{envi['PATH']}"
        ret = subprocess.Popen(cmd,env=envi, shell=True,cwd=wd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8', universal_newlines=True)

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
    
    def UnpackBinutils(self) -> BSOE:
        if (not self.IsInitialized()):
            self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
            return BSOE.BSOE_LIB_NOT_INIT
        buver = self.ConfigGetEntry("BU_VERSION")
        dst = self.ConfigGetEntry("BU_DEST_FILE_DOWNLOAD")
        if (dst == -1 or buver == -1):
            self.SetLastError(BSOE.BSOE_INTERNAL)
            
            return BSOE.BSOE_INTERNAL
       
      
        ret = self._UnpackSource(dst)
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
        self.SetLastError(ret)
        return ret
    
    def _UnpackSource(self, src: str) -> BSOE:
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
        
        if (not self.options & BootStrapperOptions.BSO_OVERWRITE):
            if (os.path.exists(self.extractPath + rpath)):
                self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
                return BSOE.BSOE_SRC_ALR_EXISTS
        
        for ext in self._filter:
            _ext = ext.split('.')[-1]
            if '.' + _ext == pathlib.Path(src).suffix.lower():
                perms += ext.split('.')[-1]
                break
       
        tar = tarfile.open(src, perms)
        tar.extractall(self.extractPath)
        
        tar.close()
        
        #timestamp
        
        
        return BSOE.BSOE_SUCCESS
        
    
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
        if (not self._CheckStamp()):
            print("Cleanup failed, stamp doesnt exist")
            return False
        f = open(self.stampPath+"/.notice", 'r+')
    

    
        for ln in f:
    
        

            if ln.startswith('A'):
                a = ln.rstrip().split()
           
                if (os.path.exists(a[-1])):
                    print(f"Cleaning {a[-1]}")
                    os.remove(a[-1])


            elif ln.startswith('D'):
                a = ln.rstrip().split()
                if (os.path.exists(a[-1])):
                    print(f"Cleaning tree {a[-1]}")
                    shutil.rmtree(a[-1])
       

    
        f.close()
        return True
    
    def _CheckStamp(self) -> bool:
        if (not os.path.exists(self.stampPath + "/.notice")):
            return False
        
        f= open(self.stampPath + "/.notice", "r")
        msg = "#!!!This file has been autogenerated and is used as stamp\n"
        if (f.readline() != msg):
            print("Not a valid timestamp")
            f.close()
            return False
        f.close()
        return True
        
    def _DeleteStamp(self) -> bool:
        if (not self._CheckStamp()):
            return False
        
        os.remove(self.stampPath + "/.notice")
        return True
    def _CreateStamp(self) -> bool:
        if (not os.path.exists(self.stampPath) and not os.path.exists(self.stampPath + "/.notice")):
            return False
        f = open(f"{self.stampPath}/.notice", "w")
        f.write("#!!!This file has been autogenerated and is used as stamp\n#DO NOT EDIT MANUALLY\n")
        f.close()
        return True
    
    def DownloadMenu():
        pass
    def OptionsMenu():
        pass
    def WorkReportProgress():
        pass
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



    
    
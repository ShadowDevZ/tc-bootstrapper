import requests
import os
from bs4 import BeautifulSoup
import bootstrap
import urllib.request
import urllib.parse
import urllib.error
from defs import *
import utils
import sys
class Download:
    def _GetRemoteFileList(self, url: str) -> list:
        #if (not self.IsInitialized):
          #  self.SetLastError(self, BSOE.BSOE_LIB_NOT_INIT)
           # return []
        
        response = requests.get(url)
        if (url[-1] == "/"):
            url = url[::1]
            
        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, "html.parser")
            files = []
            
            for atag in soup.find_all('a', href=True):
                href = atag['href']
                
                fullUrl = url + '/' + href
                
                if (self != None):
                    if self._filter is not []:
                    
                        for ext in self._filter:
                            if fullUrl.lower().endswith(ext):
                                files.append(fullUrl)
                    else:
                        files.append(fullUrl) 
                else:
                    files.append(fullUrl)
                        
            if (self != None):        
                self.SetLastError(BSOE.BSOE_SUCCESS)
            return files
        else:
            if (self != None):
                self.SetLastError(BSOE.BSOE_UNR_SRC)
            return [response.status_code] 
    
    
    
    def _GetRemoteDirList(self, url: str) -> list:
        
       # if (not self.IsInitialized):
        #    self.SetLastError(BSOE.BSOE_LIB_NOT_INIT)
        #    return []
        
        
        response = requests.get(url)
        
        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, "html.parser")
            dirs = []
            
            for atag in soup.find_all('a', href=True):
                href = atag['href']
                
                fullUrl = urllib.parse.urljoin(url, href)
                
                if (fullUrl.endswith('/')):
                    dirs.append(fullUrl)
            #if function is called outside of the class
            if (self != None):
                self.SetLastError(BSOE.BSOE_SUCCESS)
            return dirs
        else:
            if (self != None):
                self.SetLastError(BSOE.BSOE_UNR_SRC)
            return [response.status_code]

    
    def _DownloadSource(self, url: str, dst: str, autoStamp=True, overwrite=False) -> BSOE:
        if (os.path.exists(dst) and overwrite == False and (not self.options & BootStrapperOptions.BSOE_OVERWRITE_ALL)):
            self.SetLastError(BSOE.BSOE_SRC_ALR_EXISTS)
            return BSOE.BSOE_SRC_ALR_EXISTS
        
       
        try:
            urllib.request.urlopen(url, timeout=5)
        except urllib.error.URLError as e:
            self.SetLastError(BSOE.BSOE_RMT_URL)
           
            return BSOE.BSOE_RMT_URL
        
        try:
            #add report
            self._lastUriDownloaded = url
            self._lastUriPathLocal = dst
            urllib.request.urlretrieve(url, dst, reporthook=self._urllib_cb)
        except urllib.error.URLError as e:
            self.SetLastError(BSOE.BSOE_RMT_URL)
           
            return BSOE.BSOE_RMT_URL
        
        
        if (autoStamp):
            self._WriteStamp(self.extractPath + '/'+dst, 'A')

        
        
        self.SetLastError(BSOE.BSOE_SUCCESS)
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
        found = False
        for i in range(len(dirs)):
            if (dirs[i][-1] == '/'):
                dirs[i] = dirs[i][:-1]
            ve = dirs[i].rsplit('-')
            if (version == ve[-1]):

                url = dirs[i]
                found = True
                
        if (not found):
            self.SetLastError(BSOE.BSOE_BADVER)
            return BSOE.BSOE_BADVER
                
        
        gccVersion = url.split('/')[-1]
        url = url + '/' + gccVersion + self._filter[0]
    
        localPath = self.workDir + gccVersion + self._filter[0]
        ret = self._DownloadSource(url, localPath)
      
    #todo stamp
        if (ret != BSOE.BSOE_SUCCESS):
            return ret
        else:
            ret = self._DownloadSignature(url, localPath + ".sig")
            if (ret != BSOE.BSOE_SUCCESS):
                return ret 
            
            self.ConfigWriteEntry("GCC_DEST_FILE_DOWNLOAD", localPath)
            self.ConfigWriteEntry("GCC_VERSION", gccVersion)
            self.ConfigWriteEntry("GCC_SIGNATURE", localPath + ".sig")
       
         #   sys.exit(0)
            return BSOE.BSOE_SUCCESS
    
    
    
    def _urllib_cb(self, block_num: int, block_size: int, total_size: int):
        if (self._downloadCallback != None):
            self._downloadCallback(self._lastUriDownloaded, self._lastUriPathLocal, block_num, block_size, total_size)
    
    
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
        
        try:
            urllib.request.urlopen(url)
        except urllib.error.URLError as e:
            self.SetLastError(BSOE.BSOE_BADVER)
            return BSOE.BSOE_BADVER
        
        
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
        
        localPath = self.workDir + buVersion + self._filter[0]
        ret = self._DownloadSource(url, localPath)
        
        
        
    
        
    #todo stamp
        if (ret != BSOE.BSOE_SUCCESS):
            return ret
        else:
            ret = self._DownloadSignature(url, localPath + ".sig")
            if (ret != BSOE.BSOE_SUCCESS):
                return ret 
            
            self.ConfigWriteEntry("BU_DEST_FILE_DOWNLOAD",localPath)
            self.ConfigWriteEntry("BU_VERSION", buVersion)
            self.ConfigWriteEntry("BU_SIGNATURE", localPath + ".sig")
            
            
            self.SetLastError(BSOE.BSOE_SUCCESS)
            return BSOE.BSOE_SUCCESS
    
  
    def DownloadBinUtils(self, ver: str) -> bool:
   
        if (not self._DownloadSourceBinutils(ver) == BSOE.BSOE_SUCCESS):
            return False
        if (self.options & BootStrapperOptions.BSO_VERIFY_PGP):
           
            if (self.VerifySignature(BootStrapperObject.BSOBJ_BINUTILS) != True):
                return False
       
        if (self.UnpackBinutils() != BSOE.BSOE_SUCCESS):
            return False
      
        
        if (self._CompileTargetBU() != BSOE.BSOE_SUCCESS):
            return False
        
        return True
        
    def DownloadGCC(self, ver: str) -> bool:
   
        if (not self._DownloadSourceGCC(ver) == BSOE.BSOE_SUCCESS):
            return False
        if (self.options & BootStrapperOptions.BSO_VERIFY_PGP):
           
            if (self.VerifySignature(BootStrapperObject.BSOBJ_GCC) != True):
                return False
       
        if (self.UnpackGcc() != BSOE.BSOE_SUCCESS):
            return False
      
        
        if (self._CompileTargetGcc() != BSOE.BSOE_SUCCESS):
            return False
        
        return True
            
    
 
   
    
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
        
       # print(bucmd, self.workDir + bv)
       # print(f"make -j{nproc}", self.workDir + bv)
       # print("make install", self.workDir + bv)
        utils.Utilities.MkdirIfNotExists(self.workDir + "gcc_build")
        self._xcall(gcccmd, self.workDir + "gcc_build")
        self._xcall(f"make all-gcc -j{nproc} && make all-target-libgcc -j{nproc}", self.workDir +"gcc_build")
        self._xcall("make install-gcc && make install-target-libgcc",self.workDir+ "gcc_build")
        
        return BSOE.BSOE_SUCCESS
    
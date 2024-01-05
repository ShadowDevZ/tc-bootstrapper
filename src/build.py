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
CONFIG_URL_BINUTILS="https://ftp.gnu.org/gnu/binutils"
CONFIG_URL_TOOLCHAIN="https://ftp.gnu.org/gnu/gcc/"

GNU_GPG_KEYRING="https://ftp.gnu.org/gnu/gnu-keyring.gpg"


        



def get_files(url: str, allowed_extensions: list=[]) -> list:
    response = requests.get(url)
    if (url[-1] == '/'):
        url = url[:-1]
    
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        files = []
        
        # Extract href attributes from anchor tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Join the URL to handle relative paths
           
         
            full_url = url + "/" + href
            
            # Check if the link points to a file based on its extension
            if allowed_extensions is not []:
                # or any(full_url.lower().endswith(ext) for ext in allowed_extensions):
                
                for ext in allowed_extensions:
                    if full_url.lower().endswith(ext):
                        files.append(full_url)
            else:
                files.append(full_url)

        return files
    else:
        print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
        return []



def get_directories(url: str):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        directories = []

        # Extract href attributes from anchor tags that point to directories
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Join the URL to handle relative paths
            full_url = urllib.parse.urljoin(url, href)
            
            # Check if it ends with a '/' to identify directories
            if full_url.endswith('/'):
                directories.append(full_url)

        return directories
    else:
        print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
        return []


g_FilterGlob = [".tar.xz", ".tar.lz", ".tar.gz", ".tar.bz2"]

def GetOutDir():
    inpl = ".te.mp/"
    
    while not os.path.isdir(inpl) or (inpl[-1] == '/'):
        inpl = input("Out Directory: ")
    return inpl

 
def GetBinUtilsUrl(mflags: int= 0,Filter: list=[]):
    if (Filter == []):
        Filter = g_FilterGlob
    
    files = get_files(CONFIG_URL_BINUTILS, [".tar.xz"])
    v = menu.DisplayMenu("binutils",files, mflags)
    
    
    return v

def splitpath(stri: str, index: int=-1):
    if stri[-1] == '/':
        stri = stri[:-1]
    
    return '.' + stri.split('.')[index]

def GetGccUrl(mflags: int=0, Filter: list=[]):
    directories = get_directories(CONFIG_URL_TOOLCHAIN)
    ch = menu.DisplayMenu("gcc",directories, mflags)
   # print(ch)
    
    if (Filter == []):
        Filter = g_FilterGlob
   
    files = get_files(ch, Filter)
    if (files == []):
        print("Failed to obtain GCC url list")
        return ''
    
    
    for file in files:
        
        for ext in Filter:
            
            
            if (splitpath(ext, -2) in file):
               
                if (splitpath(ext, -1) == pathlib.Path(file).suffix):
                    return file
    
    return ''


def urllib_progress_report(block_num: int, block_size: int, total_size: int):
    download_size = (block_num * block_size) / 1024
    
     
    print("Downloaded [{0}KiB/{1}KiB]".format(round(download_size,2), round(total_size / 1024, 2)))
  #  sys.stdout.flush()
    print('\033[F\033[K', end='')
    
    
DOWNLOAD_SOURCE_OVERWRITE = 1 << 1
DOWNLOAD_SOURCE_RET_SRC_EXISTS = 2
DOWNLOAD_SOURCE_RET_SRC_FAIL = 1
DOWNLOAD_SOURCE_RET_SUCCESS = 0
DOWNLOAD_SOURCE_RET_STAMP_FAIL = 3

def CreateNoticeStamp(dir: str) -> bool:
    if (not os.path.exists(dir) and not os.path.exists(dir + "/.notice")):
        return False
    f = open(f"{dir}/.notice", "w")
    f.write("#!!!This file has been autogenerated and is used as stamp\n#DO NOT EDIT MANUALLY\n")
    f.close()
    return True


def CheckStamp(stamp: str) -> bool:
    if (not os.path.exists(stamp)):
        return False
    
    
    f = open(stamp, "r")
    msg = "#!!!This file has been autogenerated and is used as stamp\n"
    
 
 
    if (f.readline() != msg):
        print("Not a valid timestamp")
        f.close()
        return False
    f.close()
    return True

def WriteToNoticeStampDir(stamp: str, path: str, ptype: str) -> bool:
    
    if (not CheckStamp(stamp)):
        return False
    
    f = open(stamp, "a")
    
    
    
    
    if (ptype != 'A' and ptype != 'D'):
        return False;
    
   
    
    f.write(ptype + ' ' + path + '\n')
    
    f.close()
    return True


def DeleteNoticeStamp(stamp: str) -> bool:
    if (not CheckStamp(stamp)):
        return False
    
    os.remove(stamp)
    return True

def DownloadSource(uri: str, dest: str, stamp: str, dflags: int=0) -> int:
#automatically appends compression type as extension
  
   # dest += splitpath(uri)
    
    
    
    if (not (dflags & DOWNLOAD_SOURCE_OVERWRITE)): 
        if (os.path.exists(dest)):
            print(f"{dest} already exists, not overwriting")
            return DOWNLOAD_SOURCE_RET_SRC_EXISTS
        
    
    try:
        urllib.request.urlopen(uri, timeout=5)
        print(f"{uri} - [OK] (0)")
    except urllib.error.URLError as e:
        print(f"{uri} - [FAIL] ({e})")
        return DOWNLOAD_SOURCE_RET_SRC_FAIL
    except Exception as e:
        print(f"An error occurred while checking remote source: {e}")
        return DOWNLOAD_SOURCE_RET_SRC_FAIL
    
    try:
        print(f"Downloading {uri.split('/')[-1]} to {dest}")
        
        urllib.request.urlretrieve(uri, dest, urllib_progress_report)
        print("Download complete")
    except urllib.error.URLError as e:
        print("URLLIB Error while downloading file: " + str(e))
        return DOWNLOAD_SOURCE_RET_SRC_FAIL
    except Exception as e:
        print(f"An error occurred while downloading remote source: {e}")
        return DOWNLOAD_SOURCE_RET_SRC_FAIL

    
    if (not CheckStamp(stamp+ ".notice")):
        if (not CreateNoticeStamp(stamp)):
            return DOWNLOAD_SOURCE_RET_STAMP_FAIL
    
    if (not WriteToNoticeStampDir(stamp+ ".notice", dest, 'A')):
            return DOWNLOAD_SOURCE_RET_STAMP_FAIL

    return DOWNLOAD_SOURCE_RET_SUCCESS
        
UNPACK_SOURCE_OVERWRITE = 1 << 1
def UnpackSource(src: str, dst: str, uflags: int=0) -> bool:
    perms = "r:"
    if (not os.path.exists(dst)):
        os.mkdir(dst)

    
    
    
    
    rpath = src.split('/')[-1]
    
    idx = rpath.find(".tar.")
    if (idx != -1):
        rpath = rpath[:idx]
    
    
    #print(dst +'/'+ rpath)
    if (not (uflags & UNPACK_SOURCE_OVERWRITE)):
        if (os.path.exists(dst+ '/' + rpath)):
            print(f"{rpath} already exists, skipping")
            return False
    
    for ext in g_FilterGlob:
        _ext = ext.split('.')[-1]
        
        
        if '.' + _ext == pathlib.Path(src).suffix.lower():
            perms += _ext
            break
    
    tar = tarfile.open(src, perms)
    tar.extractall(dst)
    tar.close()
    
    
    if (not CheckStamp(dst+ ".notice")):
        print("No valid stamp found")
        return False
    
    
    if (not WriteToNoticeStampDir(dst+ "/.notice", dst + rpath, 'D')):
            print("Failed to write to the stamp")
            return False
    
    return True

AT_BINUTILS_CONFIG="../$AUTOBUVER/configure --target=$AUTO_TARGET --prefix=$AUTO_PREFIX --with-sysroot --disable-nls -disable-werror"
AT_BINUTILS_MAKE="make -j$AUTO_CORE"
AT_BINUTILS_INSTALL="make install"


AT_GCC_CONFIG="../$AUTOGCCVER/configure --target=$AUTO_TARGET --prefix=$AUTO_PREFIX --disable-nls --enable-languages=c,c++ --without-headers"
AT_GCC_MAKE="make all-gcc -j$AUTO_CORE && make all-target-libgcc -j$AUTO_CORE"
AT_GCC_INSTALL="make install-gcc && make install-target-libgcc"


#prefix=install path
#target=architecture



def xcall(cmd: str, cwd: str) -> None:
    envi = os.environ.copy()
    envi["PATH"] = f"/home/shadow/Projects/TcBootstrapper/downloaded/install/bin:{envi['PATH']}" 
  #  print(cmd)
    ret = subprocess.Popen(cmd, env=envi, shell=True, cwd=cwd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,encoding='utf-8',universal_newlines=True)
  #  stdout, stderr = ret.communicate()
    
    while True:
        ln = ret.stdout.readline()
      
     
        if not ln:
            break

        print(ln, end='')
    
    exitcode = ret.wait()
 #   ret = call(cmd, cwd=cwd,shell=True)
    
    
    if (exitcode != 0):
        print("Failed to execute build command!, command returned " + str(exitcode))
        sys.exit(1)

def CompileTargetBinutils(src: str,prefix: str,target: str, nproc: int,tree: str, stamp: str) -> bool:
    
    if (not os.path.exists(src)):
        os.mkdir(src)
        
    if (not CheckStamp(stamp)):
        print("Failed to check stamp signature")
        return False
    
    if (not WriteToNoticeStampDir(stamp, src, 'D')):
        print("Failed to write a stamp")
        return False

    
    #bad approach however we have only 2 options and there wont be more so we do not need a parser
    #todo do it once then substring so i dont need to call this also from the gcc target
    binutilsConfig = AT_BINUTILS_CONFIG.replace("--target=$AUTO_TARGET", f"--target={target}")
    binutilsConfig = binutilsConfig.replace("--prefix=$AUTO_PREFIX", f"--prefix={prefix}")
    binutilsConfig = binutilsConfig.replace("../$AUTOBUVER/configure", f"../{tree}/configure")
   # print(binutilsConfig)
    xcall(binutilsConfig, src)
    
    binutilsMake  = AT_BINUTILS_MAKE.replace("$AUTO_CORE", f"{nproc}")
    xcall(binutilsMake, src)
    xcall(AT_BINUTILS_INSTALL, src)
    return True
    


def CompileTargetGcc(src: str,prefix: str,target: str, nproc: int, tree: str, stamp: str) -> bool:
    if (not os.path.exists(src)):
        os.mkdir(src)
        
    if (not CheckStamp(stamp)):
        print("Failed to check stamp signature while building GCC")
        return False
    
    if (not WriteToNoticeStampDir(stamp, src, 'D')):
        print("Failed to write a stamp while building GCC")
        return False
    
    #bad approach however we have only 2 options and there wont be more so we do not need a parser
    gccConfig = AT_GCC_CONFIG.replace("--target=$AUTO_TARGET", f"--target={target}")
    gccConfig = gccConfig.replace("--prefix=$AUTO_PREFIX", f"--prefix={prefix}")
    
    
    gccConfig = gccConfig.replace("../$AUTOGCCVER/configure", f"../{tree}/configure")
    

    xcall(gccConfig, src)
    
    gccMake  = AT_GCC_MAKE.replace("$AUTO_CORE", f"{nproc}")
  
   
    
    xcall(gccMake, src)
    xcall(AT_GCC_INSTALL, src)
    
    return True
    
def CleanupTree(src: str) -> bool:
    if (not CheckStamp(src + "/.notice")):
        print("Cleanup failed, stamp doesnt exist")
        return False
    f = open(src+"/.notice", 'r+')
    

    
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
       
        if (not ln.startswith('#')):
            a = ln.rstrip().split()
            if (not os.path.exists(a[-1])):
                f.write(ln)
    
    f.close()
    return True
        
        
                
                
        
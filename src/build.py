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
from subprocess import call
CONFIG_URL_BINUTILS="https://ftp.gnu.org/gnu/binutils"
CONFIG_URL_TOOLCHAIN="https://ftp.gnu.org/gnu/gcc/"

GNU_GPG_KEYRING="https://ftp.gnu.org/gnu/gnu-keyring.gpg"


        



def get_files(url, allowed_extensions=None):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        files = []

        # Extract href attributes from anchor tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Join the URL to handle relative paths
           
         
            full_url = url + "/" + href
           
            # Check if the link points to a file based on its extension
            if allowed_extensions is None or any(full_url.lower().endswith(ext) for ext in allowed_extensions):
                files.append(full_url)

        return files
    else:
        print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
        return []



def get_directories(url):
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

 
def GetBinUtilsUrl(mflags = 0,Filter=None):
    if (Filter == None):
        Filter = g_FilterGlob
    
    files = get_files(CONFIG_URL_BINUTILS, Filter)
    
    v = menu.DisplayMenu("binutils",files, mflags)
    return v

def splitpath(stri, index=-1):
    return '.' + stri.split('.')[index]

def GetGccUrl(mflags=0, Filter=None):
    directories = get_directories(CONFIG_URL_TOOLCHAIN)
    ch = menu.DisplayMenu("gcc",directories, mflags)
    files = get_files(ch)
    if (Filter == None):
        Filter = g_FilterGlob
    
    for file in files:
        for ext in Filter:

            if (splitpath(ext, -2) in file):
             if (splitpath(ext, -1) == pathlib.Path(file).suffix):
                    return file
    
    return None


def urllib_progress_report(block_num, block_size, total_size):
    download_size = (block_num * block_size) / 1024
    
     
    print("Downloaded [{0}KiB/{1}KiB]".format(round(download_size,2), round(total_size / 1024, 2)))
  #  sys.stdout.flush()
    print('\033[F\033[K', end='')
    
    
DOWNLOAD_SOURCE_OVERWRITE = 1 << 1
DOWNLOAD_SOURCE_RET_SRC_EXISTS = 2
DOWNLOAD_SOURCE_RET_SRC_FAIL = 1
DOWNLOAD_SOURCE_RET_SUCCESS = 0


def DownloadSource(uri, dest, dflags=0):
#automatically appends compression type as extension
  
   # dest += splitpath(uri)
    
   
    
    if (not (dflags & DOWNLOAD_SOURCE_OVERWRITE)): 
        if (os.path.exists(dest)):
            print("{0} already exists, not overwriting".format(dest))
            return DOWNLOAD_SOURCE_RET_SRC_EXISTS
        
    
    try:
        urllib.request.urlopen(uri, timeout=5)
        print("{0} - [OK] (0)".format(uri))
    except urllib.error.URLError as e:
        print("{0} - [FAIL] ({1})".format(uri, e))
        return DOWNLOAD_SOURCE_RET_SRC_FAIL
    except Exception as e:
        print(f"An error occurred while checking remote source: {e}")
        return DOWNLOAD_SOURCE_RET_SRC_FAIL
    
    try:
        print("Downloading {0} to {1}".format(uri.split('/')[-1], dest))
        
        urllib.request.urlretrieve(uri, dest, urllib_progress_report)
        print("Download complete")
    except urllib.error.URLError as e:
        print("URLLIB Error while downloading file: " + str(e))
        return DOWNLOAD_SOURCE_RET_SRC_FAIL
    except Exception as e:
        print(f"An error occurred while downloading remote source: {e}")
        return DOWNLOAD_SOURCE_RET_SRC_FAIL

    return DOWNLOAD_SOURCE_RET_SUCCESS
        

def UnpackSource(src, dst):
    perms = "r:"
    
    
    
    
    rpath = src.split('/')[-1]
    
    idx = rpath.find(".tar.")
    if (idx != -1):
        rpath = rpath[:idx]
    
    
    print(dst +'/'+ rpath)
    if (os.path.exists(dst+ '/' + rpath)):
        print(f"{rpath} already exists, skipping")
        return
    
    for ext in g_FilterGlob:
        _ext = ext.split('.')[-1]
        
        
        if '.' + _ext == pathlib.Path(src).suffix.lower():
            perms += _ext
            break
    
    tar = tarfile.open(src, perms)
    tar.extractall(dst)
    tar.close()

AT_BINUTILS_CONFIG="./configure --target=$AUTO_TARGET --prefix=$AUTO_PREFIX --with-sysroot --disable-nls -disable-werror"
AT_BINUTILS_MAKE="make -j$AUTO_CORE"
AT_BINUTILS_INSTALL="make install"


AT_GCC_CONFIG="./configure --target=$AUTO_TARGET --prefix=$AUTO_PREFIX --disable-nls --enable-languages=c,c++ --without-headers"
AT_GCC_MAKE="make all-gcc -j$AUTO_CORE && make all-target-libgcc -j$AUTO_CORE"
AT_GCC_INSTALL="make install-gcc && make install-target-libgcc"


#prefix=install path
#target=architecture
COMPILE_TARGET_X86="i686-elf"
COMPILE_TARGET_AMD64="x86_64-elf"


def xcall(cmd, cwd):
    ret = call(cmd, cwd=cwd,shell=True)
    if (ret != 0):
        print("Failed to execute build command!, command returned " + str(ret))
        os.abort()

def CompileTargetBinutils(src,prefix,target):
    
    #bad approach however we have only 2 options and there wont be more so we do not need a parser
    binutilsConfig = AT_BINUTILS_CONFIG.replace("--target=$AUTO_TARGET", f"--target={target}")
    binutilsConfig = AT_BINUTILS_CONFIG.replace("--prefix=$AUTO_PREFIX", f"--target={prefix}")
    
    xcall(binutilsConfig, src)
    
    
    
    
    pass


def CompileTargetsGcc(src,target, njobs):
    pass
import menu
import os
import requests
from bs4 import BeautifulSoup
import pathlib
import urllib.request
import urllib.parse
import urllib.error
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



def GetOutDir():
    inpl = ".te.mp/"
    
    while not os.path.isdir(inpl) or (inpl[-1] == '/'):
        inpl = input("Out Directory: ")
    return inpl


def GetBinUtilsUrl(mflags = 0,Filter=None):
    if (Filter == None):
        Filter = [".tar.xz", ".tar.lz", ".tar.gz", ".tar.bz2"]
    
    files = get_files(CONFIG_URL_BINUTILS, Filter)
    
    v = menu.DisplayMenu("binutils",files, mflags)
    return v

def splitpath(stri, index):
    return '.' + stri.split('.')[index]

def GetGccUrl(mflags=0, Filter=None):
    directories = get_directories(CONFIG_URL_TOOLCHAIN)
    ch = menu.DisplayMenu("gcc",directories, mflags)
    files = get_files(ch)
    if (Filter == None):
        Filter = [".tar.xz", ".tar.lz", ".tar.gz", ".tar.bz2"]
    
    for file in files:
        for ext in Filter:

            if (splitpath(ext, -2) in file):
             if (splitpath(ext, -1) == pathlib.Path(file).suffix):
                    return file
    
    return None

def DownloadSource(uri, dest, VerifyPGP=True):
    try:
        urllib.request.urlopen(uri, timeout=5)
        print(f"{0} - [OK] (0)", uri)
    except urllib.error.URLError as e:
        print(f"{0} - [FAIL] ({1})", uri, e)
        return False
    except Exception as e:
        print(f"An error occurred while checking remote source: {e}")
        return False
    
    try:
        print("Downloading {0} to {1}", uri.split('/')[-1], dest)
        urllib.request.urlretrieve(uri, dest)
        print("Download complete")
    except urllib.error.URLError as e:
        print("URLLIB Error while downloading file: " + str(e))
        return False
    except Exception as e:
        print(f"An error occurred while downloading remote source: {e}")
        return False

    return True
        
        
        
TC_DEBUG_DOWNLOAD_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/"
#DownloadSource(GetBinUtilsUrl(menu.DISP_MENU_LATEST), TC_DEBUG_DOWNLOAD_PATH+"binutils.tar")
#DownloadSource(GetGccUrl(menu.DISP_MENU_LATEST), TC_DEBUG_DOWNLOAD_PATH+"gcc.tar")
print(GetBinUtilsUrl())
#print(GetGccUrl(menu.DISP_MENU_LATEST))

#print(menu.DisplayMenu("gcc",directories))

#outDir = GetOutDir() + "/work"
#print(outDir)


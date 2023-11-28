import menu
import os
import requests
from bs4 import BeautifulSoup
import pathlib
from urllib.parse import urljoin
CONFIG_URL_BINUTILS="https://ftp.gnu.org/gnu/binutils"
CONFIG_URL_TOOLCHAIN="https://ftp.gnu.org/gnu/gcc/"

def get_files(url, allowed_extensions=None):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        files = []

        # Extract href attributes from anchor tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Join the URL to handle relative paths
            full_url = urljoin(url, href)

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
            full_url = urljoin(url, href)
            
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


def GetBinUtilsUrl():
    files = get_files(CONFIG_URL_BINUTILS, [".xz", ".lz", ".gz", ".bz2"])
    v = menu.DisplayMenu("binutils",files)
    return v

def GetGccUrl():
    directories = get_directories(CONFIG_URL_TOOLCHAIN)
    ch = menu.DisplayMenu("gcc",directories)
    print(ch)
    files = get_files(ch)
    
    tmp = ""
    for i in range(len(files)):
        if ".tar.xz" in files[i]:
            tmp = files[i]
            break
        elif ".tar.gz" in files[i]:
            tmp = files[i]
            break
    return tmp
            


print(GetBinUtilsUrl())
print(GetGccUrl())

#print(menu.DisplayMenu("gcc",directories))

#outDir = GetOutDir() + "/work"
#print(outDir)


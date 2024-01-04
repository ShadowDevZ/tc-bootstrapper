import menu
import sys
import build
import multiprocessing
TC_DEBUG_DOWNLOAD_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/"
TC_DEBUG_EXTRACT_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work"


def GetCoreCount():
    while (True):
             try:
                 inp = int(input(f"Number of jobs (1-{multiprocessing.cpu_count()}): "))
                 if (inp >= 0 and inp <= multiprocessing.cpu_count()):
                     break
             except ValueError:
                 continue
    
    return inp
g_CpuCount = GetCoreCount()


print(">>Setting up binutils")
binutils_build = build.GetBinUtilsUrl(menu.DISP_MENU_LATEST)
binutils_version = binutils_build.split('/')[-1]

build.DownloadSource(binutils_build, TC_DEBUG_DOWNLOAD_PATH + binutils_version)


print(">>Unpacking Binutils")
build.UnpackSource(TC_DEBUG_DOWNLOAD_PATH + binutils_version, TC_DEBUG_EXTRACT_PATH)

#build.CompileTargetBinutils()


'''
gcc_build = build.GetGccUrl(menu.DISP_MENU_LATEST)
gcc_version = gcc_build.split('/')[-1]
print(">>Setting up GCC")
build.DownloadSource(gcc_build, TC_DEBUG_DOWNLOAD_PATH+gcc_version)

'''


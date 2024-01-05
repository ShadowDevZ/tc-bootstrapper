import menu
import sys
import os
import build
import multiprocessing
TC_DEBUG_DOWNLOAD_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/"
TC_DEBUG_EXTRACT_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
TC_DEBUG_INSTALL_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/install/"
TC_DEBUG_STAMP_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
COMPILE_TARGET_X86="i686-elf"
COMPILE_TARGET_AMD64="x86_64-elf"
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

def CutString(stri, substr):
    
    idx = stri.find(substr)
    if (idx != -1):
        stri = stri[:idx]
    
    return stri




print(">>Setting up binutils")
binutils_build = build.GetBinUtilsUrl(menu.DISP_MENU_LATEST)
binutils_version = binutils_build.split('/')[-1]


build.DownloadSource(binutils_build, TC_DEBUG_DOWNLOAD_PATH + binutils_version,TC_DEBUG_STAMP_PATH)


#print(">>Unpacking Binutils")
build.UnpackSource(TC_DEBUG_DOWNLOAD_PATH + binutils_version, TC_DEBUG_EXTRACT_PATH)

if (not os.path.exists(TC_DEBUG_INSTALL_PATH)):
    os.mkdir(TC_DEBUG_INSTALL_PATH)

binutils_dir = CutString(binutils_version ,".tar.")

build_stamp = TC_DEBUG_EXTRACT_PATH + ".notice"

#build.CompileTargetBinutils(TC_DEBUG_EXTRACT_PATH + "/binutils_build",  TC_DEBUG_INSTALL_PATH, COMPILE_TARGET_AMD64, g_CpuCount, binutils_dir, build_stamp)
#print(">>Binutils compiled")



gcc_build = build.GetGccUrl(menu.DISP_MENU_LATEST)
gcc_version = gcc_build.split('/')[-1]
#print(">>Setting up GCC")
print(gcc_build)
#build.DownloadSource(gcc_build, TC_DEBUG_DOWNLOAD_PATH+gcc_version, TC_DEBUG_STAMP_PATH)

gcc_dir = CutString(gcc_version, ".tar.")
print(">>Unpacking GCC")
#build.UnpackSource(TC_DEBUG_DOWNLOAD_PATH + gcc_version, TC_DEBUG_EXTRACT_PATH)

#build.CompileTargetGcc(TC_DEBUG_EXTRACT_PATH + "/gcc_build",  TC_DEBUG_INSTALL_PATH, COMPILE_TARGET_AMD64, g_CpuCount, gcc_dir, build_stamp)
print(">>GCC compiled")


build.CleanupTree(TC_DEBUG_STAMP_PATH)
build.DeleteNoticeStamp(build_stamp)
import menu
import sys
import os
import build
import multiprocessing
TC_DEBUG_DOWNLOAD_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/"
TC_DEBUG_KEYCHAAIN_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/keychain"
TC_DEBUG_EXTRACT_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
TC_DEBUG_INSTALL_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/install/"
TC_DEBUG_STAMP_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
COMPILE_TARGET_X86="i686-elf"
COMPILE_TARGET_AMD64="x86_64-elf"
TC_DEBUG_BUILD_STAMP = TC_DEBUG_EXTRACT_PATH + ".notice"
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

def CutString(stri, substr) -> str:
    
    idx = stri.find(substr)
    if (idx != -1):
        stri = stri[:idx]
    
    return stri


build.mkdir_if_not_exists(TC_DEBUG_STAMP_PATH)
build.CreateNoticeStamp(TC_DEBUG_STAMP_PATH)
print(">>Downloading keychain")
build.DownloadGPGKeychain(build.GNU_GPG_KEYRING, TC_DEBUG_DOWNLOAD_PATH + "/gnu-keyring.gpg", TC_DEBUG_BUILD_STAMP)


print(">>Setting up binutils")
binutils_build = build.GetBinUtilsUrl(menu.DISP_MENU_LATEST)
binutils_version = binutils_build.split('/')[-1]








build.DownloadSource(binutils_build, TC_DEBUG_DOWNLOAD_PATH + binutils_version,TC_DEBUG_STAMP_PATH)



build.DownloadDetachedSignature(binutils_build, TC_DEBUG_DOWNLOAD_PATH + binutils_version + ".sig", TC_DEBUG_BUILD_STAMP)


sig,errmsg = build.VerifyPGP(TC_DEBUG_DOWNLOAD_PATH + binutils_version + ".sig",TC_DEBUG_DOWNLOAD_PATH + binutils_version, TC_DEBUG_KEYCHAAIN_PATH, TC_DEBUG_DOWNLOAD_PATH + "gnu-keyring.gpg", TC_DEBUG_BUILD_STAMP)
if (not sig):
    print("GPG verification failed for binutils")
    print("message: ", errmsg)
    sys.exit(3)
else:
    print(">>[PGP] BINUTILS OK")

print(">>Unpacking Binutils")



build.UnpackSource(TC_DEBUG_DOWNLOAD_PATH + binutils_version, TC_DEBUG_EXTRACT_PATH)

build.mkdir_if_not_exists(TC_DEBUG_INSTALL_PATH)

binutils_dir = CutString(binutils_version ,".tar.")






build.CompileTargetBinutils(TC_DEBUG_EXTRACT_PATH + "/binutils_build",  TC_DEBUG_INSTALL_PATH, COMPILE_TARGET_AMD64, g_CpuCount, binutils_dir, TC_DEBUG_BUILD_STAMP)
print(">>Binutils compiled")


"""


gcc_build = build.GetGccUrl(menu.DISP_MENU_LATEST)
gcc_version = gcc_build.split('/')[-1]
print(">>Setting up GCC")
print(gcc_build)
build.DownloadSource(gcc_build, TC_DEBUG_DOWNLOAD_PATH+gcc_version, TC_DEBUG_STAMP_PATH)

build.DownloadDetachedSignature(gcc_build, TC_DEBUG_DOWNLOAD_PATH + gcc_version + ".sig")


sig,errmsg = build.VerifyPGP(TC_DEBUG_DOWNLOAD_PATH + gcc_version + ".sig",TC_DEBUG_DOWNLOAD_PATH + gcc_version, TC_DEBUG_KEYCHAAIN_PATH, TC_DEBUG_DOWNLOAD_PATH + "gnu-keyring.gpg")
if (not sig):
    print("GPG verification failed for GCC")
    print("message: ", errmsg)
    sys.exit(3)
else:
    print(">>[PGP] GPG OK")


gcc_dir = CutString(gcc_version, ".tar.")
print(">>Unpacking GCC")
build.UnpackSource(TC_DEBUG_DOWNLOAD_PATH + gcc_version, TC_DEBUG_EXTRACT_PATH)





build.CompileTargetGcc(TC_DEBUG_EXTRACT_PATH + "/gcc_build",  TC_DEBUG_INSTALL_PATH, COMPILE_TARGET_AMD64, g_CpuCount, gcc_dir, TC_DEBUG_BUILD_STAMP)
print(">>GCC compiled")


"""




build.CleanupTree(TC_DEBUG_STAMP_PATH)
build.DeleteNoticeStamp(TC_DEBUG_BUILD_STAMP)


#

#print(build.VerifyPGP(TC_DEBUG_DOWNLOAD_PATH + "gcc-13.2.0.tar.gz.sig", TC_DEBUG_DOWNLOAD_PATH + "gcc-13.2.0.tar.gz",TC_DEBUG_KEYCHAAIN_PATH, "/home/shadow/Projects/TcBootstrapper/downloaded/gnu-keyring.gpg"))
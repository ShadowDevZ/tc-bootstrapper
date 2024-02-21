from urllib import parse
import bootstrap
"""
TC_DEBUG_DOWNLOAD_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/"
TC_DEBUG_KEYCHAAIN_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/keychain"
TC_DEBUG_EXTRACT_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
TC_DEBUG_INSTALL_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/install/"
TC_DEBUG_STAMP_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
COMPILE_TARGET_X86="i686-elf"
COMPILE_TARGET_AMD64="x86_64-elf"
TC_DEBUG_BUILD_STAMP = TC_DEBUG_EXTRACT_PATH + ".notice"


def vcb(url: str, localPath: str, block_num: int, block_size: int, total_size: int):
    download_size = (block_num * block_size) / 1024
    uri = url.split('/')[-1]
    
     
    print("Downloaded {0} to {1} [{2}KiB/{3}KiB]".format(uri, localPath, round(download_size,2), round(total_size / 1024, 2)))
  #  sys.stdout.flush()
    print('\033[F\033[K', end='')
    

bp = bootstrap.BootStrapper(TC_DEBUG_EXTRACT_PATH, TC_DEBUG_INSTALL_PATH, TC_DEBUG_EXTRACT_PATH, options=bootstrap.BootStrapperOptions.BSO_CLEANUP | bootstrap.BootStrapperOptions.BSO_VERIFY_PGP, downloadCallback=vcb)
bp.Inititialize()


if (bp.GetLastError() != bootstrap.BSOE.BSOE_SUCCESS):
    print(bp.GetLastError())
else:
    print("init success")    




bp.ConfigWriteEntry("NPROC", 8)
bp.ConfigWriteEntry("CFLAGS_BINUTILS", "--with-sysroot --disable-nls -disable-werror")
bp.ConfigWriteEntry("CFLAGS_GCC", "--disable-nls --enable-languages=c,c++ --without-headers")
bp.ConfigWriteEntry("BINUTILS_ARCH", "x86_64-elf")
bp.ConfigWriteEntry("GCC_ARCH", "x86_64-elf")

#assert(bp._DownloadSourceBinutils("2.42") == bootstrap.BSOE.BSOE_SUCCESS)
#assert(bp.VerifySignature(bootstrap.BootStrapperObject.BSOBJ_BINUTILS) == True)
#assert(bp.UnpackBinutils() == bootstrap.BSOE.BSOE_SUCCESS)
#print("unpack error", str(bp.GetLastError()))

#assert(bp._CompileTargetBU() == bootstrap.BSOE.BSOE_SUCCESS)



if (bp.DownloadBinUtils("2.42") != True):
    print("bu_err: ", bp.GetLastError(), bp.GetLastErrorAsString())

#if (bp.DownloadGCC("13.2.0") != True):
 #   print("gcc_err: ", bp.GetLastError(), bp.GetLastErrorAsString())


# 
# ._DownloadSourceGCC("13.2.0") == bootstrap.BSOE.BSOE_SUCCESS)
#assert(bp.UnpackGcc() == bootstrap.BSOE.BSOE_SUCCESS)
#assert(bp._CompileTargetGcc() == bootstrap.BSOE.BSOE_SUCCESS)
#bp._print_params()
#if (bp.GetLastError() != bootstrap.BSOE.BSOE_SUCCESS):
#    print("err: ")

bp.Finalize()

"""

TC_VERSION = "0.0.1"
import argparse
import bootstrap
import pathlib
import os
import sys
verbosity = -1
workDir = ''
installDir = ''
nproc = 1
options = 0
def vprint(*args, **kwargs) -> None:
    if (verbosity == 0):
        return
    print(*args, **kwargs)

def CheckDir(dir: str) -> bool:
    if (os.path.exists(dir) and os.path.isdir(dir)):
        return True
    
    return False

def lst2str(lst: list) -> str:
    ap = ""
    
    for w in lst:
        ap += w
        
    return ap
    




def vcb(url: str, localPath: str, block_num: int, block_size: int, total_size: int):
    download_size = (block_num * block_size) / 1024
    uri = url.split('/')[-1]
    
     
    print("Downloaded {0} to {1} [{2}KiB/{3}KiB]".format(uri, localPath, round(download_size,2), round(total_size / 1024, 2)))
  #  sys.stdout.flush()
    print('\033[F\033[K', end='')
    
callbackDownload = vcb

parser = argparse.ArgumentParser()
parser.add_argument('-q', "--quiet", help="Supress output", action="store_true")
parser.add_argument('-s', "--suppress", help="Supress compiler output", action="store_true")
parser.add_argument('-w', "--workdir", help="Directory where the toolchian is built")
parser.add_argument('-i', "--instdir", help="Directory where toolchain is installed")
parser.add_argument('-t', "--targets", help="Which targets to build, available options are and 'gcc' 'binutils' (options are combinable) ", nargs='+')
parser.add_argument('-a', "--arch", help="Global architecture used by all targets in compilation")
parser.add_argument("--arch_gcc", help="GCC specific architecture")
parser.add_argument("--arch_binutils", help="Binutils specific architecture")
parser.add_argument('-n', "--nproc", help="Number of parallel jobs", type=int)
parser.add_argument("-o", "--overwrite", help="Overwrites all existing files instead of throwing error if same files are present", action="store_true")
parser.add_argument('-c', "--autoclean", help="Automatically clean all files inside workdir which were used in the process of compilation", action="store_true")
parser.add_argument("--gcc_flags", help="GCC specific autoconfig flags", nargs='+')
parser.add_argument("--binutils_flags", help="Binutils specific autoconfig flags", nargs='+')
parser.add_argument("--gcc_version", help="Version of GCC to build, if not specified the latest release is pulled")
parser.add_argument("--binutils_version", help="Version of Binutils to build, if not specified the latest release is pulled")
parser.add_argument("--list_gcc", help="Lists all available gcc versions", action="store_true")
parser.add_argument("--list_binutils", help="Lists all available binutils versions", action="store_true")
parser.add_argument("-g", "--verify_pgp", help="Verifies PGP signature before installation", action="store_true")
parser.add_argument('-v', "--version", help="Prints version information", action="store_true")
args = parser.parse_args()




if (args.version):
    print("tc-bootstrapper v" + TC_VERSION)
    print("Developed by ShadowDevZ - 2024")
    sys.exit(0)

if (args.quiet):
    verbosity = 0
    callbackDownload = None

if (args.list_binutils):
    bx = bootstrap.BootStrapper(None, None, None, None,bootstrap.BootStrapperOptions.BSOE_NO_INIT, "None", None)
    v = bx._GetRemoteFileList("https://ftp.gnu.org/gnu/binutils")
    for e in v:
        idx = e.find(".tar.")
        if (idx != -1):
            
            if (e.endswith(".tar.xz")):
                e = e[:idx]
                e = e.split('/')[-1]
                print(e)
    
    sys.exit(0)
    
if (args.list_gcc):
    bx = bootstrap.BootStrapper(None, None, None, None,bootstrap.BootStrapperOptions.BSOE_NO_INIT, "None", None)
    v = bx._GetRemoteDirList("https://ftp.gnu.org/gnu/gcc/")
    for e in v:
        print(e.split('/')[-2])
 
    
    sys.exit(0)

if (not args.workdir or not args.instdir or not args.targets):
    print("Not all arguments were supplied")
    sys.exit(1)



if (args.nproc):
    nproc = args.nproc

if (args.workdir):
    if (not CheckDir(args.workdir)):
        vprint("Work directory does not exists")
        sys.exit(1)

if (args.instdir):
    if (not CheckDir(args.instdir)):
        vprint("Installation directory does not exists")
        sys.exit(2)

workDir = os.path.abspath(args.workdir)
installDir = os.path.abspath(args.instdir)

if (args.verify_pgp):
    options |= bootstrap.BootStrapperOptions.BSO_VERIFY_PGP

if (args.overwrite):
    options |= bootstrap.BootStrapperOptions.BSOE_OVERWRITE_ALL
    
if (args.autoclean):
    options |= bootstrap.BootStrapperOptions.BSO_CLEANUP

if (args.suppress):
    options |= bootstrap.BootStrapperOptions.BSOE_SUPPRESS

if (args.arch):
    args.arch_gcc = args.arch
    args.arch_binutils = args.arch

if (args.targets):
    if ("gcc" in args.targets):
        if (args.arch_gcc == None or args.gcc_flags == None or args.gcc_version == None):
            vprint("GCC specific arguments missing")
            sys.exit(3)
            
    if ("binutils" in args.targets):
        if (args.arch_binutils == None or args.binutils_flags == None or args.binutils_version == None):
            vprint("Binutils specific arguments missing")
            sys.exit(4)
  
#print(lst2str(args.gcc_flags), nproc, workDir, installDir)


bp = bootstrap.BootStrapper(workDir, installDir,workDir, options=options, downloadCallback=callbackDownload)
bp.Inititialize()


if (bp.GetLastError() != bootstrap.BSOE.BSOE_SUCCESS):
    vprint("Failed to initialize library with error {0}[{1}]", bp.GetLastError(), bp.GetLastErrorAsString())
    sys.exit(1)
if "binutils" in args.targets:
    bp.ConfigWriteEntry("NPROC", nproc)
    bp.ConfigWriteEntry("CFLAGS_BINUTILS", lst2str(args.binutils_flags))
    
    bp.ConfigWriteEntry("BINUTILS_ARCH", args.arch_binutils)
    
    vprint(">> Downloading Binutils")
    if (not bp._DownloadSourceBinutils(args.binutils_version) == bootstrap.BSOE.BSOE_SUCCESS):
        vprint("[!] Failed to download binutils, error: {0}", bp.GetLastErrorAsString())
        sys.exit(6)
    
    if (args.verify_pgp):
        vprint(">> Verifying Binutils signature")
        if (bp.VerifySignature(bootstrap.BootStrapperObject.BSOBJ_BINUTILS) != True):
            vprint("[!] Failed to verify signature for binutils {0}", bp.GetLastErrorAsString())
            sys.exit(7)
    vprint(">> Unpacking Binutils")
    if (bp.UnpackBinutils() != bootstrap.BSOE.BSOE_SUCCESS):
        vprint("[!] Failed to unpack binutils tarball, error: {0}", bp.GetLastErrorAsString())
        sys.exit(8)
    vprint(">> Compiling Binutils source")    
    if (bp._CompileTargetBU() != bootstrap.BSOE.BSOE_SUCCESS):
        vprint("[!] Compilation of Binutils failed, error: {0}", bp.GetLastErrorAsString())
        sys.exit(9)

vprint(">> Binutils compiled")
if "gcc" in args.targets:
    bp.ConfigWriteEntry("CFLAGS_GCC", lst2str(args.gcc_flags))
    bp.ConfigWriteEntry("GCC_ARCH", args.arch_gcc)
    vprint(">> Downloading gcc")
    if (not bp._DownloadSourceGCC(args.gcc_version) == bootstrap.BSOE.BSOE_SUCCESS):
        vprint("[!] Failed to download gcc, error: {0}", bp.GetLastErrorAsString())
        sys.exit(6)
    
    if (args.verify_pgp):
        vprint(">> Verifying GCC signature")
        if (bp.VerifySignature(bootstrap.BootStrapperObject.BSOBJ_GCC) != True):
            vprint("[!] Failed to verify signature for gcc {0}", bp.GetLastErrorAsString())
            sys.exit(7)
    vprint(">> Unpacking GCC")
    if (bp.UnpackGcc() != bootstrap.BSOE.BSOE_SUCCESS):
        vprint("[!] Failed to unpack gcc tarball, error: {0}", bp.GetLastErrorAsString())
        sys.exit(8)
    vprint(">> Compiling Binutils source")    
    if (bp._CompileTargetGcc() != bootstrap.BSOE.BSOE_SUCCESS):
        vprint("[!] Compilation of gcc failed, error: {0}", bp.GetLastErrorAsString())
        sys.exit(9)
    vprint(">> GCC compiled")
    
    
    
    



bp.Finalize()
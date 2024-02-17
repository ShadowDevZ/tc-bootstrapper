import bootstrap
TC_DEBUG_DOWNLOAD_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/"
TC_DEBUG_KEYCHAAIN_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/keychain"
TC_DEBUG_EXTRACT_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
TC_DEBUG_INSTALL_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/install/"
TC_DEBUG_STAMP_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
COMPILE_TARGET_X86="i686-elf"
COMPILE_TARGET_AMD64="x86_64-elf"
TC_DEBUG_BUILD_STAMP = TC_DEBUG_EXTRACT_PATH + ".notice"




bp = bootstrap.BootStrapper(TC_DEBUG_DOWNLOAD_PATH, TC_DEBUG_INSTALL_PATH, TC_DEBUG_EXTRACT_PATH)
bp.Inititialize()


if (bp.GetLastError() != bootstrap.BSOE.BSOE_SUCCESS):
    print(bp.GetLastError())
else:
    print("init success")    


bootstrap.MkdirIfNotExists(TC_DEBUG_DOWNLOAD_PATH)
bootstrap.MkdirIfNotExists(TC_DEBUG_EXTRACT_PATH)
bootstrap.MkdirIfNotExists(TC_DEBUG_INSTALL_PATH)

bp.ConfigWriteEntry("NPROC", 4)
bp._DownloadSourceGCC("13.2.0")
bp.UnpackGcc()
#bp._print_params()
if (bp.GetLastError() != bootstrap.BSOE.BSOE_SUCCESS):
    print("err: ")
    

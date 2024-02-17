import bootstrap
TC_DEBUG_DOWNLOAD_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/"
TC_DEBUG_KEYCHAAIN_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/keychain"
TC_DEBUG_EXTRACT_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
TC_DEBUG_INSTALL_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/install/"
TC_DEBUG_STAMP_PATH="/home/shadow/Projects/TcBootstrapper/downloaded/work/"
COMPILE_TARGET_X86="i686-elf"
COMPILE_TARGET_AMD64="x86_64-elf"
TC_DEBUG_BUILD_STAMP = TC_DEBUG_EXTRACT_PATH + ".notice"




bp = bootstrap.BootStrapper(TC_DEBUG_EXTRACT_PATH, TC_DEBUG_INSTALL_PATH, TC_DEBUG_EXTRACT_PATH)
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
#assert(bp.UnpackBinutils() == bootstrap.BSOE.BSOE_SUCCESS)
print("unpack error", str(bp.GetLastError()))

#assert(bp._CompileTargetBU() == bootstrap.BSOE.BSOE_SUCCESS)


assert(bp._DownloadSourceGCC("13.2.0") == bootstrap.BSOE.BSOE_SUCCESS)
assert(bp.UnpackGcc() == bootstrap.BSOE.BSOE_SUCCESS)
assert(bp._CompileTargetGcc() == bootstrap.BSOE.BSOE_SUCCESS)
#bp._print_params()
if (bp.GetLastError() != bootstrap.BSOE.BSOE_SUCCESS):
    print("err: ")
    

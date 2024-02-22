from enum import IntEnum


class BootStrapperOptions(IntEnum):
    BSO_VERIFY_PGP = 1 << 1
    BSO_CLEANUP = 1 << 2
   # BSO_MAXCORE = 1 << 3
    BSO_OUTPUT_VERBOSE = 1 << 5
   # BSO_FILE_LOG = 1 << 6
    #internal flag
    BSOE_INIT_LIB = 1 << 7
    BSOE_OVERWRITE_ALL = 1 << 9
    #BSOE_PULL_LATEST = 1 << 10
    BSOE_SUPPRESS = 1 << 11
    BSOE_QUERY_ONLY = 1 << 12
    #patch availabel only for x86_64-elf target
    BSOE_X64_ELF_NORED = 1 << 13
class BootStrapperDownloadOpts(IntEnum):
    BSDO_NONE = 0
    BSDO_GCC = 1 << 1
    BSDO_BINUTILS = 1 << 2

class BSOE(IntEnum):
    BSOE_SUCCESS = 0
    BSOE_BAD_PARAM = 1
    BSOE_IO_FAIL = 2
    BSOE_ACCESS_DENIED = 3
    BSOE_PGP_FAIL = 4
    BSOE_NODISK = 5
    BSOE_UNR_SRC = 6
    BSOE_NOFILE = 7
    BSOE_RMT_INVALID = 8
    BSOE_INTERNAL = 9
    BSOE_INV_OPT = 10
    BSOE_INST_PATH = 11
    BSOE_XCALL_FAIL = 12
    BSOE_STAMPLOCK = 13
    BSOE_RMT_URL = 14
    BSOE_FILE_CORRUPTED = 15
    BSOE_BAD_PRIVIL = 16
    BSOE_LIB_NOT_INIT = 17
    BSOE_OVERFLOW = 18
    BSOE_LIB_ALR_INIT = 19
    BSOE_NOT_IMPLEMENTED = 20
    BSOE_SRC_ALR_EXISTS = 21
    BSOE_STAMP_FAIL = 22
    BSOE_SIGNATURE = 23
    BSOE_BADVER = 24

class BootStrapperObject(IntEnum):
    BSOBJ_BINUTILS = 1 << 1
    BSOBJ_GCC = 1 << 2
    BSOBJ_LIBGCCs = 1 << 3 
    
CONFIG_URL_BINUTILS="https://ftp.gnu.org/gnu/binutils"
CONFIG_URL_TOOLCHAIN="https://ftp.gnu.org/gnu/gcc/"

GNU_GPG_KEYRING="https://ftp.gnu.org/gnu/gnu-keyring.gpg"

TC_VERSION = "0.0.1"
LTS_GCC = "13.2.0"
LTS_BINUTILS = "2.42"
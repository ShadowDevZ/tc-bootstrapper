# tc-bootsrapper
! Warning some changes pushed to the main branch may not work as expected or not at all resulting in broken build.
In the future there will be automated unit tests and checks before commit.
For now please use releases marked as usable or the `stable` branch.
The code is also in very early stage. DO NOT USE IT IN PRODUCTION or any critical tasks. 

Easily create a toolchain for os development or cross compiling.
Support for libgcc without redzone is supported for versions `10`, `12`, `13`
Stable and tested LTS versions are `GCC 13.2.0` and `Binutils 2.42`
# Progress
Works pretty well now (with code editing), fixing some bugs then i will refacctor
some things and add argument parsing, prettier output and configuration so multiple
parts dont need to be rerun multiple times
# Dependencies
- Linux system (for now)
- urllib (py3)
- patch
- BeautifulSoup4 (py3)
- tarfile (py3)
- shutil (py3)
- gnupg (py3)

also add things like clean that delete the tarballs and work folder

# Usage 
## Options and help menu
`python3 main.py --help`

## Build full toolchain
`python3 main.py -t gcc binutils -w ../downloaded/work -i ../downloaded/install -g -n 8 --arch="x86_64-elf" --gcc_flags="-disable-nls --enable-languages=c,c++ --without-headers" --gcc_version="LTS" -c -r -m --binutils_version="LTS" --binutils_flags="--with-sysroot --disable-nls --disable-werror"`


# Major todo
- Effective way to use timestamp to prevent multiple verifications
- Fix path bugs when calling function eg. path is /path//file instead od /path/file
- More user friendly output
- Make this work on non POSIX compliant systems
- add `requirements.txt` for the pip
- Create `man` page
- Create wheel package

# tc-bootsrapper
Easily create a toolchain for os development

# Progress
Works pretty well now (with code editing), fixing some bugs then i will refacctor
some things and add argument parsing, prettier output and configuration so multiple
parts dont need to be rerun multiple times

also add things like clean that delete the tarballs and work folder

all of the TC_DEBUG* macros are here just for the development rest are going to be taken
either from STDIN or the ARGV

# Major todo
- Add PGP key verification
- Fix path bugs when calling function eg. path is /path//file instead od /path/file
- Better output
- Refactor code
- Make this work on non POSIX compliant systems
- add `requirements.txt` for the pip
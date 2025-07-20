#!/usr/bin/python3
import sys
import os
import errno
import shutil

script_absolute_path = os.path.abspath(sys.argv[0])
ip_path = os.path.join(os.path.dirname(os.path.dirname(script_absolute_path)), 'ip')
sys.path.append(ip_path)

from branch import Branch
from repo   import Repo

# Constants used by script
GIT_CLONE_PATH = 'ssh://git@bitbucket.org'
CURRENT_DIR = os.getcwd()
DEPS_STRING = 'DEP_BUILD_LIST'
DEPS_DIRECTORY = '.deps'


# Finds the latesttag and modifies the Makefile entry
def processDep(dep):
    dep_split = dep.split("!")
    library_path = os.path.dirname(dep_split[-1])
    library_name = os.path.basename(dep_split[-1]).rstrip("\r\n")

    clone_url = os.path.join(GIT_CLONE_PATH,
                         library_path,
                         library_name)

    clone_location = os.path.join(DEPS_DIRECTORY,
                                  library_path)
    print(clone_url, 'test  ', clone_location)
    repo = Repo(clone_url, clone_location)

    req_branch_name_split = dep_split[0].split("^")
    if len(req_branch_name_split) > 1:
        major_version = req_branch_name_split[1]
        if not major_version.isdigit():
            print('Invalid major version')
            sys.exit(errno.EINVAL)
        req_branch = Branch(Branch.version_to_string(repo.get_latest_tag(int(major_version)).version))
    else:
        req_branch = Branch(Branch.version_to_string(repo.get_latest_tag().version))

    dep_split[0] = req_branch.name + "!";
    return "".join(str(x) for x in dep_split)

# Check number of Arguments provided by caller
if len(sys.argv) == 1:
    source_makefile  = "Makefile.tags"
    release_makefile = "Makefile.release"
elif len(sys.argv) == 3:
    source_makefile  = sys.argv[1];
    release_makefile = sys.argv[2];
else:
    print('Invalid number of arguments. Use case: ', sys.argv[0], '[sourceMakefile] [releaseMakefile]');
    sys.exit(errno.EINVAL)

# Open source makefile
try:
    source_makefile_file = open(source_makefile, "r")
except IOError:
    print('Unable to open ', source_makefile)
    sys.exit(errno.ENOENT)

# Delete release makefile if it exists
if os.path.exists(release_makefile):
    os.remove(release_makefile)

# Open release makefile
try:
    release_makefile_file = open(release_makefile, "w")
except IOError:
    print('Unable to open ', release_makefile)
    sys.exit(errno.ENOENT)

# Delete temporary deps folder if exists
if os.path.exists(DEPS_DIRECTORY):
    shutil.rmtree(DEPS_DIRECTORY)

# Traverse input file line by line
# Will need some cleaning when we figure out what we want to do with our tools
for line in source_makefile_file:
    if DEPS_STRING in line:
        line_split = line.split(" ")
        if line_split[0] == DEPS_STRING:
            modified_line = []
            for element in line_split:
                if 'latestTag' in element:
                    modified_line.append(processDep(element))
                else:
                    modified_line.append(element)
            release_makefile_file.write(" ".join(str(x) for x in modified_line)
)
        else:
            release_makefile_file.write(line)
    else:
        release_makefile_file.write(line)

# Clean Up
if os.path.exists(DEPS_DIRECTORY):
    shutil.rmtree(DEPS_DIRECTORY)
source_makefile_file.close();
release_makefile_file.close();

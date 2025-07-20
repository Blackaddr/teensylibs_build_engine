#!/usr/bin/python3
import sys
import os
import errno

script_absolute_path = os.path.abspath(sys.argv[0])
ip_path = os.path.join(os.path.dirname(os.path.dirname(script_absolute_path)), 'ip')
sys.path.append(ip_path)

from branch import Branch
from   repo import Repo

# Constants used by script
GIT_CLONE_PATH = os.environ.get('GIT_CLONE_PATH') or 'ssh://git@github.com'
CURRENT_DIR = os.getcwd()

# Check number of Arguments provided by caller
if not (len(sys.argv) == 3 or len(sys.argv) == 4):
    print('Invalid number of arguments. Use case: ', sys.argv[0], 'depsDir library [version]')
    print('Ex:', sys.argv[0], './deps el-lib/libsysutil 1')
    sys.exit(errno.EINVAL)

# Parse arguments provided by caller
deps_directory = sys.argv[1]
library_path = os.path.dirname(sys.argv[2])
library_name = os.path.basename(sys.argv[2])
major_version = None
if len(sys.argv) == 4:
    major_version = sys.argv[3]
    if not major_version.isdigit():
        print('Invalid major version')
        sys.exit(errno.EINVAL)

clone_url = os.path.join(GIT_CLONE_PATH,
                         library_path,
                         library_name)

clone_location = os.path.join(deps_directory,
                              library_path)

# Create instance to manage the repo
repo = Repo(clone_url, clone_location)

# Print the latest tag with the specified major_version if any
if major_version == None:
    latest_tag = Branch.version_to_string(repo.get_latest_tag().version)
else:
    latest_tag = Branch.version_to_string(repo.get_latest_tag(int(major_version)).version)

repo.checkout_branch(latest_tag)

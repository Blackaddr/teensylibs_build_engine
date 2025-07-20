#!/usr/bin/python3
import sys
import os
import errno

script_absolute_path = os.path.abspath(sys.argv[0])
ip_path = os.path.join(os.path.dirname(os.path.dirname(script_absolute_path)), 'ip')
sys.path.append(ip_path)

from branch import Branch
from repo   import Repo

# Constants used by script
GIT_CLONE_PATH = os.environ.get('GIT_CLONE_PATH') or 'ssh://git@github.com'
CURRENT_DIR = os.getcwd()
if "\\:" in CURRENT_DIR:
    CURRENT_DIR = CURRENT_DIR.replace(":\\", "/")
    CURRENT_DIR = "/" + CURRENT_DIR.replace("\\", "/")

# Check number of Arguments provided by caller
if not len(sys.argv) == 4:
    print('Invalid number of arguments. Use case: ', sys.argv[0], 'depsDir library branch')
    print('Ex:', sys.argv[0], './deps el-lib/libsysutil master')
    sys.exit(errno.EINVAL)

# Parse arguments provided by caller
deps_directory = sys.argv[1]

if ":" in deps_directory:
    deps_directory = deps_directory.split(":")[1]
    deps_directory = deps_directory.replace("\\", "/")

library_path = os.path.dirname(sys.argv[2])
library_name = os.path.basename(sys.argv[2])
req_branch = Branch(sys.argv[3])

clone_url = os.path.join(GIT_CLONE_PATH,
                         library_path,
                         library_name)

clone_url = clone_url.replace("\\", "/")

clone_location = os.path.join(deps_directory,
                              library_path)

clone_location = clone_location.replace(":\\", "/")
clone_location = clone_location.replace(":/", "/")

# Create instance to manage the repo
repo = Repo(clone_url, clone_location)

# latestTag is a code word to be interpreted has the latest tagged version and
# not a branch called latestTag. If a : is provided following by a digit then it
# specifies the latest release of that specific major version
req_branch_name_split = req_branch.name.split("^")
if req_branch_name_split[0] == 'latestTag':
    if len(req_branch_name_split) > 1:
        major_version = req_branch_name_split[1]
        if not major_version.isdigit():
            print('Invalid major version')
            sys.exit(errno.EINVAL)
        req_branch = Branch(Branch.version_to_string(repo.get_latest_tag(int(major_version)).version))
    else:
        req_branch = Branch(Branch.version_to_string(repo.get_latest_tag().version))
if not repo.initialized :
    repo.checkout_branch(req_branch.name)

# These rules are imposed by us so they reside on this top level script
# If the requested branch matches the current branch then do nothing
if req_branch.name != repo.curBranch.name:
    # If both the current branch and the requested branch are tags than they most
    # be compatible. If they are, checkout the new branch, if not, issue an error
    if req_branch.is_tag and repo.curBranch.is_tag:
        if not req_branch.versions_are_compatible(repo.curBranch.version):
            print('Incompatible versions requested. Current is',
                  repo.curBranch.version,
                  'while requested is',
                  req_branch.version)
            sys.exit(errno.EPERM)
        else:
            # If the tags are compatible then checkout the new branch if its a
            # newer version
            if req_branch > repo.curBranch:
                repo.checkout_branch(req_branch.name)
    # If the requested branch is master and the current branch is a tag then
    # checkout the requested branch
    elif req_branch.is_master and repo.curBranch.is_tag:
        repo.checkout_branch(req_branch.name)
    elif not req_branch.is_tag and not req_branch.is_master:
        # If the current branch is already a branch then issue an error
        if not repo.curBranch.is_tag and not repo.curBranch.is_master:
            if req_branch.name != repo.curBranch.name:
                print('Incompatible branches requested. Current is',
                      repo.curBranch.name,
                      'while requested is',
                      req_branch.name)
                sys.exit(errno.EPERM)
        # Requested is a branch and current is either master or tag so checkout
        # request
        repo.checkout_branch(req_branch.name)

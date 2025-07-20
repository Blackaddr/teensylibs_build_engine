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
if not len(sys.argv) == 2:
    print('Invalid number of arguments. Use case: ', sys.argv[0], 'depsDir')
    print('Ex:', sys.argv[0], './deps')
    sys.exit(errno.EINVAL)

# Parse arguments provided by caller
deps_directory = sys.argv[1]


# Check if dependencies directory exists
if not os.path.exists(deps_directory) :
    print('ERROR: Deps directory does not exist')
    sys.exit(errno.ENOENT)

os.chdir(deps_directory)

print('\n')
print('{0:30}{1:40}{2:20}{3:20}'.format('Library Name',
                               'Current Branch',
                               'Latest Minor/Patch',
                               'Latest Release'))
print('-' * 120)

for lib_type in os.listdir('.'):
    for lib in os.listdir(lib_type):
        clone_url = os.path.join(GIT_CLONE_PATH,
                                 lib_type,
                                 lib)
        repo = Repo(clone_url, lib_type)
        cur_branch = repo.curBranch.name
        if (repo.curBranch.is_tag):
            latest_minor_patch = repo.get_latest_tag(repo.curBranch.version[0]).name;
            if latest_minor_patch != cur_branch:
                latest_minor_patch  += '*';
        else:
            latest_minor_patch = 'N/A'
        latest_release = repo.get_latest_tag().name
        if not latest_release:
            latest_release = 'N/A'
        else:
            if latest_release != cur_branch:
                latest_release += '*'
        print('{0:30}{1:40}{2:20}{3:20}'.format(lib,
                                                cur_branch[0:36],
                                                latest_minor_patch,
                                                latest_release))


# Return to original directory
os.chdir(CURRENT_DIR)

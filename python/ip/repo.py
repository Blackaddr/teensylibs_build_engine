#!/usr/bin/python3
import sys
import os
import os.path
import subprocess
import errno

from branch import Branch

class Repo:
    # This class provides methods to clone and manage a git repo

    # Constructor takes the url of a repo and the location where the user wants
    # it cloned to. The clone_location is expected to be a relative path.
    def __init__(self, repo_url, clone_location):
        """
        Class constructor.

        Constructor takes the url of a repo and the location where the user wants
        it cloned to. The clone_location is expected to be a relative path.

        :param repo_url: Repository url
        :type repo_url: string
        :param clone_location: Clone path
        :type clone_location: string
        """

        # get current directory
        original_dir = os.getcwd()

        # get name of repo
        self._repo_name = os.path.split(repo_url)[-1]

        # Create the directory to clone into
        os.makedirs(os.path.join(original_dir, clone_location), exist_ok=True)

        # Switch to the desired clone location
        os.chdir(os.path.join(original_dir, clone_location))

        # Check if the repo already exists, if not clone it'
        if os.path.exists(self._repo_name) :
            os.chdir(self._repo_name)

            # keep track of the clone location
            ### Super confusing! You have an input parameter by the same name
            ### (semantically) but you are setting this instance variable to
            ### have a different meaning
            self._clone_location = os.getcwd()

            # Exists so we just need to query the current branch name
            try:
                command = ['git',
                           'rev-parse',
                           '--abbrev-ref',
                           'HEAD']
                cur_branch_name = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')
                cur_branch_name = cur_branch_name.strip('\n')
                # A bit of a kludge. Need to look into a git command that works for both
                # tags and branches
                if cur_branch_name == "HEAD" :
                    command = ['git',
                               'describe',
                               '--tags',
                               '--exact-match']
                    cur_branch_name = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')
                    cur_branch_name = cur_branch_name.strip('\n')
                self._cur_branch = Branch(cur_branch_name)
            except subprocess.CalledProcessError as e:
                print('ERROR: Unexpected error. Failed while retrieving branch name of repo', self._repo_name)
                print('ERROR: Check if you are connected to the network')
                sys.exit(errno.EIO)

            # Repo had already been cloned
            self._initialized = True

        else :
            # Doesn't exist so it needs to be cloned
            try:
                command = ['git',
                           'clone',
                           repo_url,
                           os.path.basename(repo_url)]
                subprocess.call(command, stdout=open(os.devnull, 'wb'))
            except subprocess.CalledProcessError as e:
                print('ERROR: Unable to clone repo', repo_url)
                print('ERROR: Check if repo / branch exists and if you are connected to the network')
                sys.exit(errno.EIO)
            # Keep track of what is the current branch and location of the clone
            # directory
            self._cur_branch = Branch('master')
            os.chdir(self._repo_name)
            self._clone_location = os.getcwd()

            # Repo required to be cloned, the current branch is master but it is
            # considered unitialized until a checkout is issue
            self._initialized = False

        # Go back to the directory we were initially
        os.chdir(original_dir);

    # This function checkout the desired branch of a git repo clone
    def checkout_branch(self, branch_name):
        """
        This function checked out the desired branch.

        :param branch_name: Branch name to be checked out
        :type branch_name: string
        """
        # get current directory
        original_dir = os.getcwd()

        # Check if clone location actually exists
        if not os.path.exists(self._clone_location):
            print('ERROR: Clone location does not exist. Unable to checkout branch',
                  branch_name,
                  'of repo',
                  self._repo_name)
            sys.exit(errno.ENOENT)

        # cd to clone directory
        os.chdir(self._clone_location)

        # checkout desired branch
        try:
            subprocess.call(['git', 'checkout', branch_name])
        except subprocess.CalledProcessError as e:
            print('ERROR: Unable to checkout branch',
                  branch_name,
                  'of repo',
                  self._repo_name)
            print('ERROR: Check if branch exists and if you are connected to the network')
            sys.exit(errno.EIO)

        # Update internal branch reference
        self._cur_branch = Branch(branch_name)

        # Repo is now initialized after the checkout of a branch
        self._initialized = True

        # cd to original directory
        os.chdir(original_dir)

    # This function looks for the latest tag of a specific major version or of
    # the latest version
    def get_latest_tag(self, *args):
        """
        This function get the latest tag of a specific major version or of the latest major
        version if none is specified full tag with the format [Major Minor Patch]. If the major
        version does not exist, it will return [None None None]

        :return: latest tag
        :rtype: List containing three integers (Major, Minor, Patch)
        """
        # Check if a major version is specified
        major_version = None
        if len(args) == 1:
            major_version = args[0]

        # get current directory
        original_dir = os.getcwd()

        # Check if clone location actually exists
        if not os.path.exists(self._clone_location):
            print('ERROR: Clone location does not exist. Unable to get latest tag of major version',
                  major_version,
                  'of repo',
                  self._repo_name)
            sys.exit(errno.ENOENT)

        # cd to clone directory
        os.chdir(self._clone_location)

        # checkout desired branch
        try:
            list_of_tags = subprocess.run(['git', 'tag'], stdout=subprocess.PIPE).stdout.decode('utf-8').split("\n")
        except subprocess.CalledProcessError as e:
            print('ERROR: Unable to get list of tags for major version',
                  major_version,
                  'of repo',
                  self._repo_name)
            print('ERROR: Check if repo exists and if you are connected to the network')
            sys.exit(errno.EIO)
        ret_val = Branch("")
        latest_branch = Branch("0.0.0")
        for tags in list_of_tags:
            branch = Branch(tags)
            # Only compare major versions if one was provided as an input and
            # only use branches that contain a proper version
            if ((branch.version[0] == major_version) or (major_version == None)) and branch.version[0] != None:
                if branch > latest_branch:
                    latest_branch = branch;
                    ret_val = latest_branch

        # cd to original directory
        os.chdir(original_dir)

        return ret_val

    # This function returns the current branch instant
    @property
    def curBranch(self):
        """
        This function returns the current branch instant.

        :return: current branch in repo
        :rtype: string
        """
        return self._cur_branch

    # This function returns if the repo has been initialized
    @property
    def initialized(self):
        """
        Is initialized.

        :return: True if initialized, false otherwise
        :rtype: boolean
        """
        return self._initialized


#!/usr/bin/python3
class Branch:
    """This class provides methods to manage a branch of a repo, compare versions and
    parse versions from strings

    Add additional info about class and its usage here...
    """

    def __init__(self, branch_name):
        """Constructor takes a branch name of format string and populates the version
           fields if the branch is a tag of format major.minor.patch

        :param branch_name: Describe the branchName variable
        :type branch_name: Describe the type(s) of data you expect
        """
        ret_val = Branch.getVersion(branch_name)
        if ret_val[0] is not None:
            self._major = ret_val[0]
            self._minor = ret_val[1]
            self._patch = ret_val[2]
            self._is_tag = True
            self._is_master = False
        else:
            self._major = None
            self._minor = None
            self._patch = None
            self._is_tag = False
            if branch_name.lower() == 'master':
                self._is_master = True
            else:
                self._is_master = False

        self._name = branch_name

    def versions_are_compatible(self, other_version):
        """
        Check if provided version is compatible. As long as the major number matches, two
        versions will be considered compatible. Version format is Major, Minor, Patch

        :param other_version: List containing three integers (Major, Minor, Patch)
        :type other_version: List containing three integers (Major, Minor, Patch)

        :return: True if versions are compatible, false otherwise
        :rtype: boolean
        """
        ret_val = False
        if self._major == other_version[0] and self._is_tag:
            ret_val = True
        return ret_val

    def __gt__(self, other):
        """
        Check if branch version is greater than other branch's version

        :param other: The other branch to compare against
        :type other: An instance of the Branch class
        :return: True if it version characteristics are greater, otherwise false.
        :rtype: boolean
        """

        # Ensure other is an instance of Branch
        if not isinstance(other, Branch):
            print('ERROR: Cannot compare a Branch instance with an instance of', type(other))
            sys.exit(errno.ENOENT)

        ret_val = False
        if self._major > other._major:
            ret_val = True
        elif self._major == other._major:
            if self._minor > other._minor:
                ret_val = True
            elif self._minor == other._minor:
                if self._patch > other._patch:
                    ret_val = True
        return ret_val

    @property
    def is_tag(self):
        """
        Check if branch is a tag.

        :return: True if branch is a tag, false otherwise
        :rtype: boolean
        """
        return self._is_tag

    @property
    def is_master(self):
        """
        Check if branch is master.

        :return: True if branch is a master, false otherwise
        :rtype: boolean
        """
        return self._is_master

    @property
    def name(self):
        """
        Get branch name.

        :return: Name of branch
        :rtype: string
        """
        return self._name

    @property
    def version(self):
        """
        Get branch's version.
        :return: Version of branch
        :rtype: List containing three integers (Major, Minor, Patch)
        """
        return [self._major, self._minor, self._patch]


    @staticmethod
    def getVersion(branch_name):
        """
        Check if this branch name is a tag or a regular branch

        It will be consider a tag if it has 3 numbers delimited by a '.'
        It may have a 'd' as the last character that gets ignored for the purposes of
        versioning

        Return [None, None, None] if it is not a valid tag

        :param branch_name: Name of branch
        :type branch_name: string
        :return: Branch version
        :rtype: List containing three integers (Major, Minor, Patch)
        """
        ret_val = [None, None, None]
        branch_name_split = branch_name.split('.')

        if len(branch_name_split) == 3:
            branch_name_split[2].rstrip('d')
            if branch_name_split[0].isdigit() and \
               branch_name_split[1].isdigit() and \
               branch_name_split[2].isdigit():
                ret_val = [int(item) for item in branch_name_split]
        return ret_val

    @staticmethod
    def version_to_string(version):
        """
        Converts version into a string following the format Major.Minor.Patch

        :return: Version
        :rtype: string
        """

        return ".".join(str(elem) for elem in version)

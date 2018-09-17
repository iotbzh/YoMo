#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess
import shlex
import re
import xml.etree.ElementTree as ET
import gzip
import tempfile

global VERBOSE
VERBOSE = False


def checkDir(aPath):
    '''
    Check a directory, exit((1) if not exist
    '''
    if not os.path.isdir(aPath):
        print("path ", aPath, " is not a valid directory")
        exit(1)


def get_src_name(rpm_name):
    '''
    Get the rpm name from the rpm file name
    '''
    pattern_rpm = re.compile(
        r'^([\w\.\-\+]*)\-([\w\.\-\+]*)\-([\w\.]*)\.(\w*).rpm')
    searchRes = pattern_rpm.search(rpm_name)
    if searchRes is None:
        print("ERROR: The file %s is not a rpm format file" % rpm_name)
    else:
        result = searchRes.groups()
        return result[0]
    return None


class Package:
    def __init__(self, name, version, location, sourcerpm):
        self.__name = name
        self.__version = version["ver"]
        self.__epoch = version["epoch"]
        self.__revision = version["rel"]
        self.__location = location
        self.__srcpkg = get_src_name(sourcerpm)

    def get_name(self):
        '''
        Return the package name
        '''
        return self.__name

    def get_location(self):
        '''
        Return the location of the file in the repository
        '''
        return self.__location

    def get_version(self):
        '''
        Return the "${version}-${revision}" of the package
        '''
        return "%s-%s" % (self.__version, self.__revision)

    def get_src_name(self):
        '''
        Return the rpm source name
        '''
        return self.__srcpkg

    def publish(self, repo_srcdir, repo_destdir):
        '''
        Publish rpm file from repository source
        '''
        dstFile = os.path.join(repo_destdir, self.__location)
        dstFile_dir = os.path.dirname(dstFile)
        if not os.path.exists(dstFile_dir):
            os.makedirs(dstFile_dir)
        shutil.copyfile(os.path.join(repo_srcdir, self.__location), dstFile)

    def remove_rpm(self, repo_dir):
        '''
        Remove rpm file from repository source
        '''
        rpm_file = os.path.join(repo_dir, self.__location)
        if not os.path.exists(rpm_file):
            print("ERROR: the file %s do not exist" % rpm_file)
        os.remove(rpm_file)

    def check_if_update_is_needed(self, repo_srcdir, dstFile):
        '''
        Compare two rpm file and find if some real binary difference exist
        '''
        cmd_check_diff = "pkg-diff.sh %s %s" % (
            os.path.join(repo_srcdir, self.__location), dstFile)
        args = shlex.split(cmd_check_diff)
        res = subprocess.run(args, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if res.returncode == 0:
            return False
        else:
            return True


class PackageSource:
    def __init__(self, name, repository_path):
        self.__binPackage = []
        self.__repository_path = repository_path
        self.__name = name
        self.__version = None

    def get_name(self):
        '''
        Return package source name
        '''
        return self.__name

    def get_repository_path(self):
        '''
        Return repository path
        '''
        return self.__repository_path

    def append_pkg(self, package):
        '''
        Add a new package
        '''
        self.__binPackage.append(package)

    def get_version(self):
        '''
        Return the version "${version}-${revision}" of the package
        '''
        if self.__version is None:
            for pkg in self.__binPackage:
                ver = pkg.get_version()
                if self.__version is None:
                    self.__version = ver
                else:
                    if self.__version != ver:
                        print("ERROR source package %s have different rpm version %s and %s. Can't update repository" % (
                            self.__name, self.__version, ver))
                        exit(1)

        return self.__version

    def get_packages(self):
        '''
        Return the list of package
        '''
        return self.__binPackage

    def get_package(self, name):
        '''
        return the package with the given rpm name
        '''
        for pkg in self.__binPackage:
            if pkg.get_name() == name:
                return pkg
        return None

    def publish(self, repo_destdir):
        '''
        Publish the rpm files from repository source
        '''
        for pkg in self.__binPackage:
            pkg.publish(self.__repository_path, repo_destdir)

    def remove(self):
        '''
        Clean repository
        Should only be used for destination
        '''
        for pkg in self.__binPackage:
            pkg.remove_rpm(self.__repository_path)


class RepositoriesSynchronizer:
    def __init__(self, inputdir, outputdir, remove_unused=False):
        self.__inputdir = inputdir
        self.__outputdir = outputdir
        self.__remove_unused = remove_unused

        checkDir(self.__inputdir)

        self.__dico_repo_type = {}
        self.__dico_repo_type["nativesdk"] = "nativesdk"
        self.__dico_repo_type["runtime"] = "runtime"

        self.__repo_destdir = {}
        self.__repo_destdir["nativesdk"] = os.path.join(
            self.__outputdir, self.__dico_repo_type["nativesdk"])
        self.__repo_destdir["runtime"] = os.path.join(
            self.__outputdir, self.__dico_repo_type["runtime"])

        self.__dest_rpm_pkg = {}
        self.__src_rpm_pkg = {}

    def __direct_copy_repo(self, repo_type, repo_destdir):
        '''
        Make a direct copy of the repository
        '''
        listArchDir = os.listdir(self.__inputdir)
        # The rpm files are store two level after the input dir directory
        for archDir in listArchDir:
            # We need to separate cross compile packages and SDK packages
            if "sdk" in archDir:
                dir_type = self.__dico_repo_type["nativesdk"]
            else:
                dir_type = self.__dico_repo_type["runtime"]

            if repo_type == dir_type:
                if not os.path.isdir(repo_destdir):
                    os.makedirs(repo_destdir, exist_ok=True)

                dest_repo = os.path.join(repo_destdir, archDir)

                if os.path.isdir(dest_repo):
                    print("path ", dest_repo, " already exist")
                    exit(1)

                shutil.copytree(os.path.join(
                    self.__inputdir, archDir), dest_repo)

    def check_if_update_is_needed(self, src_rpm, dest_rpm):
        '''
        Check if a package of the repository need an update
        '''
        for src_pkg in src_rpm.get_packages():
            dst_pkg = dest_rpm.get_package(src_pkg.get_name())
            if dst_pkg is None:
                return True
            dst_rpm = os.path.join(dest_rpm.get_repository_path(), dst_pkg.get_location())
            if src_pkg.check_if_update_is_needed(src_rpm.get_repository_path(), dst_rpm):
                return True
        return False

    def check_package(self, src_rpm, dest_rpm, repo_destdir):
        '''
        Check package for an update
        '''
        if src_rpm.get_version() > dest_rpm.get_version() and self.check_if_update_is_needed(src_rpm, dest_rpm):
            dest_rpm.remove()
            src_rpm.publish(repo_destdir)
        elif src_rpm.get_version() < dest_rpm.get_version():
            print("WARNING the %s version %s is older than %s and not be update." % (
                dest_rpm.get_name(), src_rpm.get_version(), dest_rpm.get_version()))

    def __check_rpm_2_update(self, src_rpm_pkg, dest_rpm_pkg, repo_destdir):
        '''
        Check all package for an update
        '''
        src_rpm = src_rpm_pkg.keys()
        dest_rpm = dest_rpm_pkg.keys()
        if self.__remove_unused:
            unused_pkg = set(dest_rpm) - set(src_rpm)
            for pkg in unused_pkg:
                dest_rpm_pkg[pkg].remove()

        new_pkg = set(src_rpm) - set(dest_rpm)
        for pkg in new_pkg:
            src_rpm_pkg[pkg].publish(repo_destdir)

        common_pkg = set(src_rpm) & set(dest_rpm)
        total_pkg = len(common_pkg)
        number_check = 0
        ERASE_LINE = '\x1b[2K'
        if VERBOSE:
            print("check rpm to update %s/%s " % (number_check, total_pkg), end="\r")
        for pkg in common_pkg:
            number_check += 1
            if VERBOSE:
                print("check rpm %s to update %s/%s " % (pkg, number_check, total_pkg), end="\r")
            self.check_package(src_rpm_pkg[pkg], dest_rpm_pkg[pkg], repo_destdir)
            if VERBOSE:
                print(ERASE_LINE, end="\r")

    def __get_primary_path(self, repository_path):
        '''
        Return the path of the primary.xml.gz file of the repository
        '''
        repomd = os.path.join(repository_path, "repodata", "repomd.xml")

        tree = ET.parse(repomd)
        root = tree.getroot()
        for child in root:
            if 'type' in child.attrib and 'primary' == child.attrib['type']:
                for g_child in child:
                    if 'href' in g_child.attrib:
                        return g_child.attrib['href']
        return None

    def __get_namespace(self, xml_path):
        '''
        Return the namespace of the xml file
        '''
        xml = None
        rpm_namespaces = {}

        from xml.etree import ElementTree
        with gzip.open(xml_path, 'rb') as xml_file:
            for event, elem in ElementTree.iterparse(xml_file, ('start', 'start-ns')):
                if event == 'start-ns':
                    if elem[0] in rpm_namespaces and rpm_namespaces[elem[0]] != elem[1]:
                        raise KeyError(
                            "Duplicate prefix with different URI found.")
                    rpm_namespaces[str(elem[0])] = elem[1]
                elif event == 'start':
                    if xml is None:
                        xml = elem
                        break
        return rpm_namespaces

    def __get_rpm_from_primary(self, rpm_element, rpm_namespace):
        '''
        Get a package from a xml element
        '''
        rpm_name = rpm_element.find('{%s}name' % rpm_namespace['']).text
        rpm_version = rpm_element.find(
            '{%s}version' % rpm_namespace['']).attrib
        location = rpm_element.find(
            '{%s}location' % rpm_namespace['']).attrib['href']
        format = rpm_element.find('{%s}format' % rpm_namespace[''])
        sourcerpm = format.find('{%s}sourcerpm' % rpm_namespace['rpm']).text

        return Package(rpm_name, rpm_version, location, sourcerpm)

    def __get_primary(self, repository_path, primary_gz_path):
        '''
        Get the dico of rpm package from the primary.xml.gz file
        '''
        primary_gz = os.path.join(repository_path, primary_gz_path)
        dico_src_package = {}
        if not os.path.isfile(primary_gz):
            print("ERROR no primary file %s" % primary_gz)
            return None

        rpm_namespace = self.__get_namespace(primary_gz)
        xmlin = gzip.open(primary_gz, 'rb')

        root = ET.fromstring(xmlin.read())
        for child in root:
            if 'type' in child.attrib and 'rpm' in child.attrib['type']:
                package = self.__get_rpm_from_primary(child, rpm_namespace)
                if not package.get_src_name() in dico_src_package:
                    dico_src_package[package.get_src_name()] = PackageSource(package.get_src_name(), repository_path)
                dico_src_package[package.get_src_name()].append_pkg(package)
        return dico_src_package

    def __scan_repository(self, repository_path):
        '''
        Get the dico of rpm package from the repository
        '''
        primary_gz_path = self.__get_primary_path(repository_path)
        if primary_gz_path is None:
            print("ERROR no primary find in %s " % repository_path)
        package_src = self.__get_primary(repository_path, primary_gz_path)
        return package_src

    def sync_repositories(self):
        '''
        Synchronize all repositories
        '''
        if VERBOSE:
            print("Start repositories synchronisation")

        for repo in self.__dico_repo_type:
            self.sync_repository(repo)

        if VERBOSE:
            print("Create output repositories done")

    def sync_repository(self, repo):
        '''
        Synchronize a repository
        '''
        is_repo_new = not os.path.isdir(self.__repo_destdir[repo])
        if is_repo_new:
            if VERBOSE:
                print("The repository %s do not exit. Create it, if necessary." % self.__repo_destdir[repo])
            self.__direct_copy_repo(repo, self.__repo_destdir[repo])
        else:
            if not os.path.isfile(os.path.join(self.__repo_destdir[repo], "repodata", "repomd.xml")):
                print("The directory %s is not a rpm repository" %
                      self.__repo_destdir[repo])
            else:
                if VERBOSE:
                    print("Scan output repositories")
                self.__dest_rpm_pkg[repo] = self.__scan_repository(
                    self.__repo_destdir[repo])
                tmpdirname = tempfile.mkdtemp()
                self.__direct_copy_repo(repo, tmpdirname)
                self.__create_repo(tmpdirname)
                if VERBOSE:
                    print("Scan input repository")
                self.__src_rpm_pkg[repo] = self.__scan_repository(tmpdirname)
                if VERBOSE:
                    print("Check for update needed")
                self.__check_rpm_2_update(
                    self.__src_rpm_pkg[repo], self.__dest_rpm_pkg[repo], self.__repo_destdir[repo])
                shutil.rmtree(tmpdirname)
        if os.path.isdir(self.__repo_destdir[repo]):
            if VERBOSE:
                print("Create repository config file in %s" %
                        self.__repo_destdir[repo])
            self.__create_repo(self.__repo_destdir[repo])

    def __create_repo(self, destDir):
        '''
        Create or update rpm a repository
        '''
        cmd_createrepo = "createrepo_c"
        if shutil.which(cmd_createrepo) is None:
            cmd_createrepo = "createrepo"
        if shutil.which(cmd_createrepo) is None:
            print("Can't find tool %s, please install it." % cmd_createrepo)
            exit(1)

        cmd_repo = "%s %s" % (cmd_createrepo, destDir)
        args = shlex.split(cmd_repo)
        subprocess.check_output(args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity", action="store_true")
    parser.add_argument("-i", "--input", help="yocto rpm sources")
    parser.add_argument("-o", "--output", help="RPM repository destination")
    parser.add_argument("-m", "--remove-unused",
                        help="remove unsed rpm during update", action='store_true')

    args = parser.parse_args()
    if args.input is None:
        print("input file is empty")
        exit(1)
    if args.output is None:
        print("output dir is empty")
        exit(1)
    if args.verbose:
        global VERBOSE
        VERBOSE = True

    syr = RepositoriesSynchronizer(args.input, args.output, args.remove_unused)

    syr.sync_repositories()


if __name__ == '__main__':
    main()

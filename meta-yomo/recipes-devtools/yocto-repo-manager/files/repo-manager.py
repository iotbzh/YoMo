#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess
import shlex
import re

global VERBOSE
VERBOSE=False

global ERASE_LINE
ERASE_LINE = '\x1b[2K'

global pattern_rpm
#Regular expression for parsing a RPM file name.
pattern_rpm = re.compile(r'^([\w\.\-\+]*)\-([\w\.\-\+]*)\-([\w\.]*)\.(\w*).rpm')

def checkDir(aPath):
    if not os.path.isdir(aPath):
        print("path ",aPath," is not a valid directory")
        exit(1)

class Package:
    def __init__(self, fullname, directory=None, repoName=None, archDir=None):
        searchRes=pattern_rpm.search(fullname)

        if searchRes is None:
            print("ERROR: The file %s is not a rpm format file" % fullname)
        else:
            result=searchRes.groups()
            self.__name=result[0]
            self.__version=result[1]
            self.__revision=result[2]
            self.__arch=result[3]

            self.__repoName=repoName
            self.__archDir=archDir

            self.__fullpath=None
            self.__srcpkg=None

            if directory is not None:
                self.__fullpath=os.path.join(directory, fullname)
                srcName=self.__find_package_source()
                if srcName is None:
                    print("ERROR: can't find src package for %s" % fullname)
                else:
                    self.__srcpkg=Package(srcName)

    #We need to find source package name of a rpm file
    def __find_package_source(self):
        #Use a subprocess is not the most efficiant, need to be optimized
        cmd_findsrc="rpm -q -p --queryformat %%{SOURCERPM} %s" % (self.__fullpath)
        args = shlex.split(cmd_findsrc)
        res=subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if res.returncode == 0 :
            return res.stdout.decode('utf8')
        else:
            return None

    def getName(self):
        return self.__name

    def getRpmPath(self):
        return self.__fullpath

    def getVersion(self):
        return self.__version

    def getSrcName(self):
        return self.__srcpkg.getName()

    def copyRPM(self, destDir):
        dstFileDir=os.path.join(destDir, self.__repoName, self.__archDir)
        if not os.path.exists(dstFileDir):
            os.makedirs(dstFileDir)

        fullname="%s-%s-%s.%s.rpm" %(self.__name, self.__version, self.__revision, self.__arch)
        dstFile=os.path.join(dstFileDir, fullname)

        shutil.copyfile( self.__fullpath, dstFile)

    def removeRPM(self):
        os.remove(self.__fullpath)

    #Compare two rpm file and find if some real binary difference exist (like rpm-check.sh)
    def checkIfUpdateIsNeeded(self, dstFile):
        cmd_check_diff="pkg-diff.sh %s %s" % (self.__fullpath, dstFile)
        args = shlex.split(cmd_check_diff)
        res=subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0 :
            return False
        else:
            return True

    def updateRevision(self):
        if self.__revision.startswith("r"):
            rawRev=self.__revision[1:].split(".")
            try:
                rawRev[-1]=str(int(rawRev[-1])+1)
            except:
                print("ERROR: revision %s can't be incremented" % ( self.__revision))
                exit(1)
            self.__revision="r"+".".join(rawRev)
        else:
            #Only yocto package revision start with a "r"
            print("ERROR: Unknow format for revision" % self.__revision)
            exit(1)

    def getRevision(self):
        return self.__revision

    def setRevision(self, revision):
        self.__revision=revision

class PackageSource:
    def __init__(self):
        #All the binaries rpm comming from this source
        self.__binPackage=[]
        self.needUpdateRevision=False
        self.newPkg=False

    def appendPkg(self,package):
        self.__binPackage.append(package)

    def copyRPM(self, destDir):
        for pkg in self.__binPackage:
            pkg.copyRPM(destDir)

    def getPackages(self):
        return self.__binPackage

    def getPackage(self, name):
        for pkg in self.__binPackage:
            if pkg.getName() == name:
                return pkg
        return None

    def getListPackages(self):
        listPkg=[]
        for pkg in self.__binPackage:
            listPkg.append(pkg.getName())
        return listPkg

    def updateRevision(self):
        for pkg in self.__binPackage:
            pkg.updateRevision()

    def setRevision(self,revision):
        for pkg in self.__binPackage:
            pkg.setRevision(revision)

    def getRevision(self):
        revision=None
        #All binaries package should have the same revision
        #Need to be improve, with a cache may be
        for pkg in self.__binPackage:
            r=pkg.getRevision()

            if revision is  None:
                revision=r
            elif revision != r:
                print("WARNING: package %s have a revision %s." % (pkg.getName(),revision))

        return revision

    def removeRPM(self):
        #Clean repository
        #Should only be used for destination
        for pkg in self.__binPackage:
            pkg.removeRPM()

class RepositoriesSynchronizer:
    def __init__(self, inputdir, outputdir, reponame, outputAuxilaire=[], lockOutputAuxilaire=True, removeUnused=False):
        self.__inputdir=inputdir
        self.__outputdir=outputdir
        self.__reponame=reponame
        self.__destdir=reponame

        checkDir(self.__inputdir)
        checkDir(self.__outputdir)
        self.__destdir=os.path.join(self.__outputdir, self.__reponame)

        self.__dicoNewPackageSource={}
        self.__dicoRepoPackageSource={}

    def __scanInputRPM(self):
        listArchDir=os.listdir( self.__inputdir)
        #The rpm files are store two level after the input dir directory
        for archDir in listArchDir:
            #We need to separate cross compile packages and SDK packages
            if "sdk" in archDir:
                repoName="nativesdk"
            else:
                repoName="runtime"
            fullPathDir=os.path.join(self.__inputdir, archDir)
            listNewRpm=os.listdir( fullPathDir)
            scnPkg=1
            totalPkg=len(listNewRpm)
            for newRpm in listNewRpm:
                if VERBOSE:
                    b = "Scan Input RPM in %s: %s/%s" % (archDir, scnPkg, totalPkg)
                    print (ERASE_LINE, end="\r")
                    print (b, end="\r")
                    scnPkg+=1
                newPackage=Package(newRpm, fullPathDir, repoName, archDir)
                if newPackage.getSrcName() not in self.__dicoNewPackageSource:
                    self.__dicoNewPackageSource[newPackage.getSrcName()]=PackageSource()
                #Store binary rpm file by rpm src
                self.__dicoNewPackageSource[newPackage.getSrcName()].appendPkg(newPackage)
            if VERBOSE:
                print (ERASE_LINE, end="\r")
        if VERBOSE:
            print (ERASE_LINE, end="\r")
            print ("Scan Input RPM done.", end="\n")

    def __scanOutputRPM(self):
        #The rpm files are store two level after the input dir directory
        for repoName in ["nativesdk", "runtime"]:
            #We need to separate cross compile packages and SDK packages
            repoPath=os.path.join(self.__destdir, repoName)
            if os.path.exists(repoPath):
                listArchDir=os.listdir( repoPath )
                for archDir in listArchDir:
                    #Black list repodata directory
                    if archDir != "repodata":
                        archDirPath=os.path.join(repoPath, archDir)
                        if os.path.exists(archDirPath):
                            listreporpm=os.listdir( archDirPath)
                            scnPkg=0
                            totalPkg=len(listreporpm)
                            for rpmfile in listreporpm:
                                if VERBOSE:
                                    b = "Scan Output RPM in %s/%s: %s/%s" % (repoName, archDir, scnPkg, totalPkg)
                                    print (ERASE_LINE, end="\r")
                                    print (b, end="\r")
                                    scnPkg+=1
                                aPackage=Package(rpmfile, archDirPath, repoName, archDir)
                                if aPackage.getSrcName() not in self.__dicoRepoPackageSource:
                                    self.__dicoRepoPackageSource[aPackage.getSrcName()]=PackageSource()
                                self.__dicoRepoPackageSource[aPackage.getSrcName()].appendPkg(aPackage)
                            if VERBOSE:
                                print (ERASE_LINE, end="\r")
        if VERBOSE:
            print (ERASE_LINE, end="\r")
            print ("Scan Input RPM done.", end="\n")

    def __checkRPM2Update(self):
        scnPkg=1
        totalPkg=len( self.__dicoNewPackageSource)
        listUpdatedPkg=[]
        for newpkg in self.__dicoNewPackageSource:
            if VERBOSE:
                b = "Check update RPM %s %s/%s" % ( newpkg, scnPkg, totalPkg)
                print (ERASE_LINE, end="\r")
                print (b, end="\r")
                scnPkg+=1
            #If the package source is not in the soutput reposutory, it's a new package
            if newpkg in self.__dicoRepoPackageSource:
                #Compare all the binaries files of the package source
                self.__comparePackages(self.__dicoNewPackageSource[newpkg], self.__dicoRepoPackageSource[newpkg], self.__destdir)
                if self.__dicoNewPackageSource[newpkg].needUpdateRevision:
                    #Update all binaries files revision
                    self.__dicoRepoPackageSource[newpkg].updateRevision()
                    self.__dicoNewPackageSource[newpkg].setRevision(self.__dicoRepoPackageSource[newpkg].getRevision())
                    self.__dicoRepoPackageSource[newpkg].removeRPM()
            else:
                self.__dicoNewPackageSource[newpkg].newPkg = True

            if  self.__dicoNewPackageSource[newpkg].newPkg or self.__dicoNewPackageSource[newpkg].needUpdateRevision:
                self.__dicoNewPackageSource[newpkg].copyRPM(self.__destdir)

                listUpdatedPkg.append(newpkg)
        if VERBOSE:
            print (ERASE_LINE, end="\r")
        if VERBOSE and len(listUpdatedPkg) > 0:
            if len(listUpdatedPkg) < 50:
                print ("Updated packages:")
                for Updatedpkg in listUpdatedPkg:
                    print ("\t%s" % Updatedpkg)
            else:
                print ("Updated %s packages" % len(listUpdatedPkg))


    def __comparePackages(self, newPackageSource, repoPackageSource, destDir):
        for newPackage in newPackageSource.getPackages():
            if newPackage.getName() not in repoPackageSource.getListPackages():
                newPackageSource.needUpdateRevision=True
                break
            repoPackage=repoPackageSource.getPackage(newPackage.getName())
            if newPackage.getVersion() != repoPackage.getVersion() or newPackage.checkIfUpdateIsNeeded(repoPackage.getRpmPath()):
                newPackageSource.needUpdateRevision=True
                break

    def __checkDeprecatedRPM(self):
        newPkg=set(self.__dicoNewPackageSource)
        oldPkg=set(self.__dicoRepoPackageSource)
        deprecatedPkg=oldPkg.difference(newPkg)
        if VERBOSE and len(deprecatedPkg) > 0:
            if len(deprecatedPkg) < 50:
                print ("Deprecated packages:")
                for pkg in deprecatedPkg:
                    print ("\t%s" % pkg)
            else:
                print ("%s Deprecated packages" % len(deprecatedPkg))

    def syncRepository(self):
        if VERBOSE:
            print("Start repositories synchronisation")
        self.__scanInputRPM()
        if VERBOSE:
            print("Scan input repository done")
        self.__scanOutputRPM()
        if VERBOSE:
            print("Scan output repositories done")
        self.__checkRPM2Update()
        if VERBOSE:
            print("Check for update needed done")
        self.__checkDeprecatedRPM()
        if VERBOSE:
            print("Check Deprecated done")
        self.createRepos(self.__destdir)
        if VERBOSE:
            print("Create output repositories done")

    def syncRpmFile(self, srcArchDir, destArchDir):
        listNewRpm=os.listdir( srcArchDir)

        dicoNewPackage={}

        if VERBOSE:
            print("Update rpm")

        for newRpm in listNewRpm:
            srcFile=os.path.join(srcArchDir, newRpm)
            dstFile=os.path.join(destArchDir, newRpm)
            if newRpm not in listOldRpm:
                shutil.copyfile( srcFile, dstFile)
            else:
                updateRpmFile(srcFile,dstFile)

    def createRepos(self, destDir):
        listDirRepo = os.listdir( destDir)
        for dirRepo in listDirRepo:
            self.__createRepo( os.path.join( destDir, dirRepo))

    def __createRepo(self, destDir):
        cmd_repo="createrepo_c %s" % (destDir)
        args = shlex.split(cmd_repo)
        subRes=subprocess.check_output(args)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-i", "--input", help="yocto rpm sources")
    parser.add_argument("-o", "--output", help="RPM repository destination")
    parser.add_argument("-a", "--output-auxilaire", help="yocto repository auxiliary destination", action='append')
    parser.add_argument("-l", "--lock-output-auxilaire", help="Do not publish rpm to auxilaire Repositories", action='store_true')
    parser.add_argument("-m", "--remove-unused", help="remove unsed rpm during update", action='store_false')
    parser.add_argument("-r", "--reponame", help="repository destination")

    args = parser.parse_args()

    if args.input is None:
        print("input file is empty")
        exit(1)
    if args.output is None:
        print("output dir is empty")
        exit(1)
    if args.reponame is None:
        print("reponame dir is empty")
        exit(1)
    if args.verbose:
        global VERBOSE
        VERBOSE=True

    sr=RepositoriesSynchronizer(args.input, args.output, args.reponame, args.output_auxilaire, args.lock_output_auxilaire, args.remove_unused)
    sr.syncRepository()

if __name__ == '__main__':
    main()


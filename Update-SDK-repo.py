#!/usr/bin/python
from __future__ import print_function
import argparse
import os
import shutil
import subprocess
import shlex

global VERBOSE
VERBOSE=False

def checkDir(aPath):
    if not os.path.isdir(aPath):
        print("path ",aPath," is not a valid directory")
        exit(1)

def updateRpmFile( srcFile, dstFile):
    if VERBOSE:
        print("The file %s need to be update." % (dstFile))
    shutil.copyfile( srcFile, dstFile)

def syncRpmFile(srcArchDir, destArchDir):
    listOldRpm=os.listdir( destArchDir)
    listNewRpm=os.listdir( srcArchDir)
    for oldRpm in listOldRpm:
        if oldRpm not in listNewRpm:
            rmFile=os.path.join(destArchDir, oldRpm)
            print("The file %s is a old rpm, need to be remove." % (rmFile))
            os.unlink(rmFile)
            
    for newRpm in listNewRpm:
        srcFile=os.path.join(srcArchDir, newRpm)
        dstFile=os.path.join(destArchDir, newRpm)
        if newRpm not in listOldRpm:
            shutil.copyfile( srcFile, dstFile)
        else:
            updateRpmFile(srcFile,dstFile)

def syncRepositoryByArch(inputDir, outputDir, dirToSync):
    #TODO: repo name need to be gene
    if "nativesdk" in dirToSync:
        repoName="x86_64-aglsdk-linux"
    else:
        repoName="aarch64-agl-linux"
        
    destArchDir=os.path.join(outputDir, repoName, dirToSync)
    if not os.path.exists(destArchDir):
        os.makedirs(destArchDir)
    syncRpmFile(os.path.join(inputDir, dirToSync), destArchDir)


def createAglRepo( destDir):
    cmd_repo="createrepo %s" % (destDir)
    args = shlex.split(cmd_repo)
    subRes=subprocess.check_output(args)

def createAglRepos(destDir):
    listDirRepo = os.listdir( destDir)
    for dirRepo in listDirRepo:
        createAglRepo( os.path.join( destDir, dirRepo))

def syncRepository(inputDir, outputDir, reponame):
    checkDir(inputDir)
    checkDir(outputDir)
    destDir=os.path.join(outputDir, reponame)
    if not os.path.exists(destDir):
        os.makedirs(destDir)
    
    listDirToSync=os.listdir( inputDir)
    for dirToSync in listDirToSync:
        syncRepositoryByArch(inputDir, destDir,dirToSync)
        
    createAglRepos(destDir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    parser.add_argument("-i", "--input", help="yocto repository sources")
    parser.add_argument("-o", "--output", help="AGL repository destination")
    parser.add_argument("-r", "--reponame", help="AGL repository destination")
    
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
    syncRepository(args.input, args.output, args.reponame)

if __name__ == '__main__':
    main()
    

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright  2016  Miguel Tremblay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not see  <http://www.gnu.org/licenses/>.
############################################################################

"""
Name:        exif_rename_files.py
Description: Rename or copy jpg files according to the information included in
 the EXIF information of the picture. File format is YYYY-MM-DD_HHmm[_NN].jpg

Notes: 

Author: Miguel Tremblay (http://ptaff.ca/miguel/)
Date: January 24th 2016
"""

import sys
import os
import re
import stat
import shutil

import exifread

VERSION = "1.0"
FILETYPE= [".jpg", ".JPG"]
# Verbose level:
## 0 Silent mode
## 1 Normal mode
## 2 Full debug
SILENT = 0
NORMAL = 1
VERBOSE = 2

nGlobalVerbosity = 1
lLog = ["Output log of exif_rename_files.py"]

def my_print(sMessage, nMessageVerbosity=NORMAL):
   """
   Use this method to write the message in the standart output and the log file, if requested.
   """

   # Add the message in the log
   global lLog
   lLog.append(sMessage)
 
   if nGlobalVerbosity != SILENT:
      if nMessageVerbosity == NORMAL:
         print sMessage
      elif nMessageVerbosity == VERBOSE and nGlobalVerbosity == VERBOSE:
         print sMessage
   

def get_images_path(sDirectory, bRecursive):
   """
   Get the images path in directory and stores it into a list.
   """
   lPathImages = []

   # Check if the directory exists
   if not os.path.exists(sDirectory):
      my_print("Directory '" + sDirectory + "' does not exists! Exiting")
      exit(2)

   # If the recursivity is not asked, simply list the files in the directory
   # Took the recipe here: http://ur1.ca/ogdez
   my_print("Looking for image files with extension in: " + str(FILETYPE), VERBOSE)
   if not bRecursive:
      for file in os.listdir(sDirectory):
         sExtension = os.path.splitext(file)[1]
         if sExtension in FILETYPE:
            lPathImages.append(os.path.join(sDirectory, file))
   else: # Walk the directories
      for root, dirs, files in os.walk(sDirectory):
         for file in files:
            sExtension = os.path.splitext(file)[1]
            if sExtension in FILETYPE:
               lPathImages.append(os.path.join(root, file))

   return lPathImages

def get_images_with_exif(lPathImages):
   """
   Inspect the images in list and return a dictionnary including:
   * key: image path
   * value: EXIF DateTimeOriginal
   """

   # Check if the image contain exif information
   nNbrImages = len(lPathImages)
   my_print("%s images found" % (nNbrImages),  VERBOSE)
   my_print("----",  nMessageVerbosity=VERBOSE)
   my_print("Getting EXIF information from files", VERBOSE)
   lPathImages.sort()
   dExif = {}
   i = 1
   for sImagePath in lPathImages:
      my_print ('Processing image %s/%s: %s\r' % \
                (i,nNbrImages, os.path.basename(sImagePath)))
      i = i + 1
      f = open(sImagePath, 'r')
      try:
         tags = exifread.process_file(f, strict=True)
         sExifDate = str(tags["EXIF DateTimeOriginal"])
         dExif[sImagePath] = sExifDate
      except (KeyError), inst:
         my_print ("No EXIF information found in file '" + sImagePath + "'")
         my_print ("Skipping.")
      my_print("----")

   return dExif

def create_path_with_exif(sPath, sExif):
   """
   Create a file name with the exif date.
   """
   sExtension = os.path.splitext(sPath)[1]
   sNewFileName = sExif.replace(':',"-").replace(" ", "_")+ sExtension   
   sPathNew = os.path.join(os.path.dirname(sPath),sNewFileName)

   # Check if the file are not already been renamed correctly
   if sPathNew == sPath:
      my_print ("Warning: File is already in the right format. Skipping '%s'" % (sPath))
      return None

   return sPathNew
   
def create_new_image_path(dExif, sInputDirectory, sOuputDirectory, bCopyTree):
   """
   Based on the input path, the Exif information and the options, create the new path for the images.
   """

   lPathOld = dExif.keys()
   lPathOld.sort()
   dNewPathRaw = {}
   # If there is no destination, the images are copy/overwritten in the same directory than the input
   if sOuputDirectory is None:
      for sPathOld in lPathOld:
         sPathNew = create_path_with_exif(sPathOld,  dExif[sPathOld])
         if sPathNew is not None:
            dNewPathRaw[sPathOld] = sPathNew
   else: # Recreate the same tree in the output
      sDirToRemove = os.path.dirname(sInputDirectory)
      for sPathOld in lPathOld:
         # "1" in "[1:]" is used to remove the first "/", so the path can be merged (see http://ur1.ca/ogdev)
         sSubDirectory = os.path.dirname(sPathOld).replace(sDirToRemove,"")[1:]
         sNewDirectory = os.path.join(sOuputDirectory, sSubDirectory)
         sPathNew =  create_path_with_exif(os.path.join(sNewDirectory,os.path.basename(sPathOld)),\
                                           dExif[sPathOld])
         if sPathNew is not None:
            dNewPathRaw[sPathOld] = sPathNew

   return dNewPathRaw
         
def get_unique_path_for_images(dNewPathRawWithPossibleCollision):
   """
   Identifying the collision for new path being the same in the dictionnary dNewPathRawWithPossibleCollision
   To avoid the collision, add "_N" before the extension.
   """
   
   my_print ("Checking uniqueness of output file name", VERBOSE)
   dNewPathUnique = {}
   dNewOldPath = {}
   for k, v in dNewPathRawWithPossibleCollision.iteritems():
    dNewOldPath.setdefault(v, []).append(k)
    
   for sNewPath in dNewOldPath.keys():
      nNbrImageWithThisExif =  len(dNewOldPath[sNewPath])
      if nNbrImageWithThisExif == 1:
         # Ignore if origin and destination are the same
         if dNewOldPath[sNewPath][0] == sNewPath:
            my_print ("File already has the right name and is in the destination directory.\n Ignoring '%s'" \
                      % (sNewPath))
            my_print ("----")
         else: 
            dNewPathUnique[dNewOldPath[sNewPath][0]] = sNewPath
            my_print ("EXIF date is unique, renaming\n %s --> %s" % (dNewOldPath[sNewPath], sNewPath), VERBOSE)
            my_print ("----", VERBOSE)
      else:
         my_print ("File %s is not unique! There is %s occurences" % (sNewPath, nNbrImageWithThisExif))
         nNumberDigit = len(str(nNbrImageWithThisExif))
         # Update each image path by adding a numbe of digit before the extension.
         i = 0
         lNewPath =  dNewOldPath[sNewPath]
         lNewPath.sort()
         for sOldImagePathWithSameExif in lNewPath:
            sNewImagePathSame = sNewPath
            sExtension = os.path.splitext(sNewImagePathSame)[1]
            j = "_" + str(i).zfill(nNumberDigit)
            sNewImagePathUnique = re.sub(sExtension + '$', j + sExtension, sNewImagePathSame)
            if sOldImagePathWithSameExif == sNewImagePathUnique:
               my_print ("File already has the right name and is in the destination directory.\n Ignoring '%s'" %\
                         (sNewImagePathUnique))
               my_print ("----")
            else:
               dNewPathUnique[sOldImagePathWithSameExif] = sNewImagePathUnique
            i = i + 1
            my_print ("Renaming\n %s --> %s" % (sOldImagePathWithSameExif,sNewImagePathUnique))
         my_print ("----")

   return dNewPathUnique

def ignore_files(dir, files):
   """
   Function to be called by shutil.copytree to only copy the directory, not the files.
   Recipe comes from here: http://ur1.ca/ogemo
   """
   return [f for f in files if os.path.isfile(os.path.join(dir, f))]

def copytree(src, dst, symlinks = False, ignore = None):
   """
   Local copytree that permits to copy a directory to another one, even if the source already exists.
   Source of the function is here: http://ur1.ca/ogen8
   """

   if not os.path.exists(dst):
      os.makedirs(dst)
      shutil.copystat(src, dst)
   lst = os.listdir(src)
   if ignore:
      excl = ignore(src, lst)
      lst = [x for x in lst if x not in excl]
   for item in lst:
      s = os.path.join(src, item)
      d = os.path.join(dst, item)
      if symlinks and os.path.islink(s):
         if os.path.lexists(d):
            os.remove(d)
         os.symlink(os.readlink(s), d)
         try:
            st = os.lstat(s)
            mode = stat.S_IMODE(st.st_mode)
            os.lchmod(d, mode)
         except:
            pass # lchmod not available
      elif os.path.isdir(s):
         copytree(s, d, symlinks, ignore)
      else:
         shutil.copy2(s, d)

      
def write_log(sPath):
   """
   Write the log written in the global list lLog in the provided path.
   """

   f = open(sPath, 'w')
   f.writelines([sString+os.linesep for sString in lLog])
   f.close()
   
def duplicate_images(dPath):
   """
   Here is the place where the images file are duplicated, copied or moved.
   """
   i = 1
   nNbrImages = len(dPath.keys())
   if bMove:
      sMode = "Move"
   else:
      sMode = "Copy"
   for sOldPath in dPath.keys():
      sNewPath = dPath[sOldPath]
      if bNoClobber and os.path.exists(sNewPath):
         my_print ("File '%s' already exists and --no-clobber option activated. Skipping '%s'." \
                   % (sNewPath, sOldPath))
      else:
         my_print (sMode + " image %s/%s\r" % (i,nNbrImages))
         my_print ("\t %s --> %s" % (sOldPath, sNewPath))
         if bTest :
            my_print("----\n Test mode is activated: no operation is done")
         elif not bMove:
            shutil.copy2(sOldPath, sNewPath)
         else:
            shutil.movefile(sOldPath, sNewPath)
      my_print ("----")
      i = i + 1
   

def exif_rename_files(sInputDirectory, sOuputDirectory=None, bRecursiveInput=False, bCopyTree=False, \
                      bMove=False, bNoClubber=False, sLogPath=None, bTest=False):
   """
   Rename the files in sInputDirectory according to the EXIF information.
   Name of the file is of the form: YYYY-MM-DD_HHmm[_NN].jpg
   """

   # Get all the images path
   lPathImages = get_images_path(sInputDirectory, bRecursiveInput)

   # Extract the EXIF information for all images
   dExif = get_images_with_exif(lPathImages)

   # Create the path where the file will be copied
   dNewPathRaw = create_new_image_path(dExif, sInputDirectory, sOuputDirectory, bCopyTree)

   # Remove any possible collision by adding a suffix in the file name of image having the same Exif and destination
   dNewPathUnique = get_unique_path_for_images(dNewPathRaw)

   # If requested, copy the input tree in the output directory
   if bCopyTree:
      copytree(sInputDirectory, sOuputDirectory, ignore=ignore_files)

   # Duplicate files
   duplicate_images(dNewPathUnique)
         
   # Mettre le tout dans le log
   if sLogPath is not None:
      write_log(sLogPath)

############################################################
# exif_rename_files in Command line
#
#

import argparse

def get_command_line():
   """
   Parse the command line and perform all the checks.
   """

   parser = argparse.ArgumentParser(prog='PROG', prefix_chars='-')
   parser.add_argument("--input-directory", "-d", dest="InputDirectory", \
                     help="Directory where the jpg/JPG files will be searched for renaming",\
                       action="store", type=str, default=None, required=True)
   parser.add_argument("--output-directory", "-o", dest="OutputDirectory", \
                     help="Optionnal: Directory where the image files will be written",\
                     action="store", type=str, default=None)   
   parser.add_argument("--test", "-t", dest="Test", \
                     help="Perform the operation but do not move or copy the files, simply log the changes that would be done", action="store_true", default=False)
   parser.add_argument("--copy-directory-tree", "-C", dest="CopyTree",  \
                     help="Copy the directory tree in the output directory, to mimic the input sub-directories",\
                     action="store_true", default=False)
   parser.add_argument("--move", "-m", dest="Move", \
                     help="Move the files, instead of copying, into the EXIF format date",\
                     action="store_true", default=False)
   parser.add_argument("--no-clobber", "-n", dest="NoClobber", \
                     help=" Do not overwrite an  existing  file",\
                     action="store_true", default=False)
   parser.add_argument("--recursive", "-r",  dest="Recursive", \
                     help="Look for files in the directory and its subfolders.",\
                     action="store_true", default=False)
   parser.add_argument("--log", "-l", dest="LogFile", \
                     help="Write all the logging information in the identified file",\
                     action="store", type=str, default=None)
   parser.add_argument("--verbose", "-v", dest="Verbosity", \
                     help="Output is verbose.", action="store_true", default=False)
   parser.add_argument("--silent", "-s", dest="Silent", \
                     help="No output on terminal.", action="store_true", default=False)
   # Parse the args
   options = parser.parse_args()

   if options.CopyTree and options.OutputDirectory is None:
      print "Error: option '--copy-recursive-tree' should be used with '--output-directory'. Please provide an output directory or do not use this option. Exiting."
      exit (2)
   if options.OutputDirectory is not None and not os.path.isdir(options.OutputDirectory):
      print "Error: Directory '%s' provided in '--output-directory' does not exist or is not a directory. Please provide a valid output directory. Exiting." % (options.OutputDirectory)
      exit (3)

   # Check if the log file can be written
   if options.LogFile is not None:
      
      # Path is the current directory and a manipulation must be done to avoid an error while checking if the 
      # file can be written. Absolute path is then given instead of relative path in the working directory.
      sLogFile = options.LogFile
      if (os.path.dirname(options.LogFile)) == "":
         sLogFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), options.LogFile)
      
      # If the file exists
      if os.path.exists(sLogFile):
         if os.access(sLogFile, os.W_OK):
            print"Log file '%s' exists and will be overwritten" % (sLogFile)
         else:
            print "Error: Log path '%s' exists but can not be overwritten. Fix this error and retry. Exiting." \
               % (sLogFile)
            exit (4)
      # If the file does not exist
      elif os.access(os.path.dirname(sLogFile), os.W_OK):
         print "Log file will be written in '%s'"
      else:
         print "Error: Log path '%s' provided in '--log' and cannot be written. Please provide a valid file path. Exiting." % (sLogFile)
         exit (5)
      
      
   # Set the global verbosity
   global nGlobalVerbosity
   if options.Verbosity:
      nGlobalVerbosity = VERBOSE
      if options.Silent:
         my_print("Warning: Both '--verbose' and '--silent' mode are asked. Using '--verbose' mode.")
   elif options.Silent:
      nGlobalVerbosity = SILENT
   else:
      nGlobalVerbosity = NORMAL
   my_print("Verbosity level is set to: " + str(nGlobalVerbosity), nMessageVerbosity=VERBOSE)

   print (options.InputDirectory, options.OutputDirectory, options.Recursive, \
           options.CopyTree, options.Move, options.NoClobber, options.LogFile, options.Test)
      
   return (options.InputDirectory, options.OutputDirectory, options.Recursive, \
           options.CopyTree, options.Move, options.NoClobber, options.LogFile, options.Test)



if __name__ == "__main__":

   (sInputDirectory, sOutputDirectory, bRecursive, bCopyTree, bMove, bNoClobber,  sLogFile, bTest)\
      = get_command_line()

   exif_rename_files(sInputDirectory, sOutputDirectory, bRecursive, bCopyTree, bMove, bNoClobber, sLogFile, bTest)


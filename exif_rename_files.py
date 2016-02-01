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
VERBOSE = 1
lLog = []

def my_print(sMessage, bLog=False, bVerbose=1):
   """
   Use this method to write the message in the standart output and the log file, if requested.
   """

   if bVerbose == VERBOSE:
      print sMessage

   if bLog:
      lLog.append(sMessage)
   

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
   print "Looking for files in", FILETYPE
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
   print "%s images found" % (nNbrImages)
   print "----"
   print "Getting EXIF information from files"
   lPathImages.sort()
   dExifImage = {}
   i = 1
   for sImagePath in lPathImages:
      print ('Processing image %s/%s: %s\r' % \
             (i,nNbrImages, os.path.basename(sImagePath)))
      i = i + 1
      f = open(sImagePath, 'r')
      try:
         tags = exifread.process_file(f, strict=True)
         sExifDate = str(tags["EXIF DateTimeOriginal"])
         dExifImage[sImagePath] = sExifDate
      except (KeyError), inst:
         print "No EXIF information found in file '" + sImagePath + "'"
         print "Skipping."
      print "----"

   return dExifImage

def create_path_with_exif(sPath, sExif):
   """
   Create a file name with the exif date.
   """
   sExtension = os.path.splitext(sPath)[1]
   sNewFileName = sExif.replace(':',"-").replace(" ", "_")+ sExtension   
   sPathNew = os.path.join(os.path.dirname(sPath),sNewFileName)

   # Check if the file are not already been renamed correctly
   if sPathNew == sPath:
      print "Warning: File is already in the right format. Skipping '%s'" % (sPath)
      return None

   return sPathNew
   
def create_new_image_path(dExifImage, sInputDirectory, sOuputDirectory, bCopyTree):
   """
   Based on the input path, the Exif information and the options, create the new path for the images.
   """

   lPathOld = dExifImage.keys()
   lPathOld.sort()
   dOldNewPath = {}
   # If there is not destination, the images are copy/overwritten in the same directory than the input
   if sOuputDirectory is None or not bCopyTree:
      for sPathOld in lPathOld:
         sPathNew = create_path_with_exif(sPathOld,  dExifImage[sPathOld])
         if sPathNew is not None:
            dOldNewPath[sPathOld] = sPathNew
   else: # Recreate the same tree in the output
      sDirToRemove = os.path.dirname(sInputDirectory)
      for sPathOld in lPathOld:
         # "1" in "[1:]" is used to remove the first "/", so the path can be merged (see http://ur1.ca/ogdev)
         sSubDirectory = os.path.dirname(sPathOld).replace(sDirToRemove,"")[1:]
         sNewDirectory = os.path.join(sOuputDirectory, sSubDirectory)
         print "asdf", os.path.join(sNewDirectory, os.path.basename(sPathOld))
         sPathNew =  create_path_with_exif(os.path.join(sNewDirectory,os.path.basename(sPathOld)),\
                                           dExifImage[sPathOld])
         if sPathNew is not None:
            dOldNewPath[sPathOld] = sPathNew

   return dOldNewPath
         
def get_unique_path_for_images(dOldNewPathWithPossibleCollision):
   """
   Identifying the collision for new path being the same in the dictionnary dOldNewPathWithPossibleCollision
   To avoid the collision, add "_N" before the extension.
   """
   
   print "Checking uniqueness of output file name"
   dOldNewPathUnique = {}
   dNewOldPath = {}
   for k, v in dOldNewPathWithPossibleCollision.iteritems():
    dNewOldPath.setdefault(v, []).append(k)
    
   for sNewPath in dNewOldPath.keys():
      nNbrImageWithThisExif =  len(dNewOldPath[sNewPath])
      if nNbrImageWithThisExif == 1:
         # Ignore if origin and destination are the same
         if dNewOldPath[sNewPath][0] == sNewPath:
            print "File already has the right name and is in the destination directory.\n Ignoring '%s'" % (sNewPath)
            print "----"
         else: 
            dOldNewPathUnique[dNewOldPath[sNewPath][0]] = sNewPath
#            print "EXIF date is unique, renaming\n %s --> %s" % (dNewOldPath[key], key)
      else:
         print "File %s is not unique! There is %s occurences" % (sNewPath, nNbrImageWithThisExif)
         print "----"
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
               print "File already has the right name and is in the destination directory.\n Ignoring '%s'" %\
                  (sNewImagePathUnique)
               print "----"
            else:
               dOldNewPathUnique[sOldImagePathWithSameExif] = sNewImagePathUnique
            i = i + 1
#            print "Renaming\n %s --> %s" % (sOldImagePathWithSameExif,sNewImagePathUnique)

   return dOldNewPathUnique

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

      
def exif_rename_files(sInputDirectory, sOuputDirectory=None, bRecursiveInput=False, bCopyTree=False, \
                      bMove=False, bNoClubber=False):
   """
   Rename the files in sInputDirectory according to the EXIF information.
   Name of the file is of the form: YYYY-MM-DD_HHmm[_NN].jpg
   """

   # Get all the images path
   lPathImages = get_images_path(sInputDirectory, bRecursiveInput)

   # Extract the EXIF information for all images
   dExifImage = get_images_with_exif(lPathImages)

   # Create the path where the file will be copied
   dOldNewPath = create_new_image_path(dExifImage, sInputDirectory, sOuputDirectory, bCopyTree)

   # Remove any possible collision by adding a suffix in the file name of image having the same Exif and destination
   dOldNewPathUnique = get_unique_path_for_images(dOldNewPath)

   # If requested, copy the input tree in the output directory
   if bCopyTree:
      copytree(sInputDirectory, sOuputDirectory, ignore=ignore_files)
   # Rename files
   i = 1
   nNbrImages = len(dOldNewPathUnique.keys())
   if bMove:
      sMode = "Move"
   else:
      sMode = "Copy"
   for sOldPath in dOldNewPathUnique.keys():
      sNewPath = dOldNewPathUnique[sOldPath]
      if bNoClobber and os.path.exists(sNewPath):
         print "File %s already exists and --no-clobber option activated. Skipping %s." % (sNewPath, sOldPath)
      else:
         print sMode + " image %s/%s\r" % (i,nNbrImages)
         print "\t %s --> %s" % (sOldPath, sNewPath)
         if not bMove:
            shutil.copy2(sOldPath, sNewPath)
         else:
            shutil.movefile(sOldPath, sNewPath)
      print "----"
      i = i + 1
         

############################################################
# exif_rename_files in Command line
#
#

import optparse

def check_required (parser, opt):
   """
   Extention of class OptionParser for mandatory argument.
   Comes from
   http://www.python.org/doc/2.3.4/lib/optparse-extending-examples.html

   @type parser:  OptionParser
   @param parser: Parser containing the values in the command line
   @type opt: string
   @param opt: option to check if it is required.
   """
   option = parser.get_option(opt)
   # Assumes the option's 'default' is set to None!
   if getattr(parser.values, option.dest) is None:
      sError = "ERROR: " + opt +\
               " parameter is missing\n Please try " + \
               sys.argv[0] + " --help for all the options\n"
      sys.stderr.write(sError)
      sys.exit(1)

def get_command_line():
   """
   Parse the command line and perform all the checks.
   """
   # Parse the command line
   parser = optparse.OptionParser(usage="%prog --input-directory InputDirectory [--output-directory OutputDirectory [--copy-directory-tree]] [--test] [--move] [--no-clobber] [--recursive] [--log=log.txt]",\
                                  version="exif_rename_files version: " + str(VERSION))

   parser.add_option("--input-directory", "-d", dest="InputDirectory", \
                     help="Directory where the jpg/JPG files will be searched for renaming",\
                     action="store", type="string", default=None)
   parser.add_option("--output-directory", "-o", dest="OutputDirectory", \
                     help="Optionnal: Directory where the image files will be written",\
                     action="store", type="string", default=None)   
   parser.add_option("--test", "-t", dest="Test", \
                     help="Perform the operation but do not move or copy the files, simply log the changes that would be done",\
                     action="store_true", default=False)
   parser.add_option("--copy-directory-tree", "-C", dest="CopyTree", \
                     help="Copy the directory tree in the output directory, to mimic the input sub-directories",\
                     action="store_true", default=False)
   parser.add_option("--move", "-m", dest="Move", \
                     help="Move the files, instead of copying, into the EXIF format date",\
                     action="store_true", default=False)
   parser.add_option("--no-clobber", "-n", dest="NoClobber", \
                     help=" Do not overwrite an  existing  file",\
                     action="store_true", default=False)
   parser.add_option("--recursive", "-r", dest="Recursive", \
                     help="Look for files in the directory and its subfolders.",\
                     action="store_true", default=False)
   parser.add_option("--log", "-l", dest="/Log/file.txt", \
                     help="Write all the logging information in the identified file",\
                     action="store", type="string", default=None)
   # Parse the args
   (options, args) = parser.parse_args()


   # Check if all mandatory argument are here:
   for sOption in ["input-directory"]:
      sLongOption = "--" + sOption
      check_required(parser, sLongOption)

   if options.CopyTree and options.OutputDirectory is None:
      print "Error: option '--copy-recursive-tree' should be used with '--output-directory'. Please provide an output directory or do not use this option. Exiting."
      exit (2)
   if options.OutputDirectory is not None and not os.path.isdir(options.OutputDirectory):
      print "Error: Directory '%s' provided in '--output-directory' does not exist or is not a directory. Please provide a valid output directory. Exiting." % (options.OutputDirectory)
      exit (3)
      
      
   return (options.InputDirectory, options.OutputDirectory, options.Recursive, \
           options.CopyTree, options.Move, options.NoClobber)


def import_ExifRead():
   """
   Used to test check if a module is present.
   """

   try:
      sCode = "import exifread"
      exec sCode
   except (SyntaxError, ImportError, EOFError), inst:
      sMessage = "Fatal error! The python exif library must be installed. See how to install this library for your specific platform: https://pypi.python.org/pypi/ExifRead"
      print sMessage
      exit(1)

if __name__ == "__main__":

   (sInputDirectory, sOutputDirectory, bRecursive, bCopyTree, bMove, bNoClobber) = get_command_line()

   # Check if exif library is loaded
   import_ExifRead()   

   exif_rename_files(sInputDirectory, sOutputDirectory, bRecursive, bCopyTree, bMove, bNoClobber)


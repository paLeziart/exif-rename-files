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
FILETYPE= ["jpg", "JPG"]
# Verbose level:
## 1 Normal mode
## 2 Full debug
NORMAL= 1
VERBOSE= 2

nGlobalVerbosity = 1

def my_print(sMessage, nMessageVerbosity=NORMAL):
   """
   Use this method to write the message in the standart output 
   """

   if nMessageVerbosity == NORMAL:
      print sMessage
   elif nMessageVerbosity == VERBOSE and nGlobalVerbosity == VERBOSE:
      print sMessage
   

def get_images_path_directory(sDirectory, bRecursive):
   """
   Get the images path in target directory and stores it into a list.
   """
   lPathImages = []

   # Check if the directory exists
   if not os.path.exists(sDirectory):
      my_print("Directory '" + sDirectory + "' does not exists! Skipping.")

   # If the recursivity is not asked, simply list the files in the directory
   # Took the recipe here: http://ur1.ca/ogdez
   my_print("Looking for image files with extension in: " + str(FILETYPE), VERBOSE)
   if not bRecursive:
      for file in os.listdir(sDirectory):
         sExtension = os.path.splitext(file)[1][1:]
         if sExtension in FILETYPE:
            lPathImages.append(os.path.join(sDirectory, file))
   else: # Walk the directories
      for root, dirs, files in os.walk(sDirectory):
         for file in files:
            sExtension = os.path.splitext(file)[1]
            if sExtension in FILETYPE:
               lPathImages.append(os.path.join(root, file))

   return lPathImages


def get_images_path(tOptions):
   """
   Get the images path in directory and stores it into a list.
   """
   lPathImages = []
   dPathImage = {} # Key is the path, value is the original directory in the input
   # Check if the directory exists
   for sPath in tOptions.Input:
      # If input is a directory and it does not exist, we skip it
      if os.path.isdir(sPath):
	 lPathDirectory = get_images_path_directory(sPath, tOptions.Recursive)
	 for sImage in lPathDirectory:
	    dPathImage[sImage] = sPath
      elif os.path.isfile(sPath):
	 sExtension = os.path.splitext(sPath)[1]
         if sExtension in FILETYPE:
	    dPathImage[sPath] = sPath

   return dPathImage
 
def get_images_with_exif(lPathImages, bCpImageNoExif=False):
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
      my_print ('Extraction EXIF from %s/%s: %s\r' % \
                (i,nNbrImages, os.path.basename(sImagePath)))
      i = i + 1
      f = open(sImagePath, 'r')
      try:
         tags = exifread.process_file(f, strict=False)
         sExifDate = str(tags["EXIF DateTimeOriginal"])
         dExif[sImagePath] = sExifDate
      except (KeyError), inst:
         my_print ("No EXIF information found in file '" + sImagePath + "'", VERBOSE)
         if bCpImageNoExif:
            dExif[sImagePath] = None
         else:
            my_print ("Skipping.", VERBOSE)
      except MemoryError:
         my_print ("Unknown error reading EXIF of '" + sImagePath + "'", VERBOSE)
         my_print ("Using this image as no EXIF is present", VERBOSE)
         if bCpImageNoExif:
            dExif[sImagePath] = None
         else:
            my_print ("Skipping.", VERBOSE)

            
      my_print("----", VERBOSE)

   return dExif

def create_path_with_exif(sPath, sExif, bCpImageNoExif):
   """
   Create a file path with the exif date.
   
   sPath is the original image filename.
   sExif is the exif of the image.
   Returns the same directory as sPath, but with the filename replaced by the date values of the EXIF string.
   """
   sExtension = os.path.splitext(sPath)[1]
   if sExif is not None:
      sNewFileName = sExif.replace(':',"-").replace(" ", "_")+ sExtension   
      sPathNew = os.path.join(os.path.dirname(sPath),sNewFileName)
      # Check if the file are not already been renamed correctly
      if sPathNew == sPath:
         my_print ("Warning: File is already in the right format. Skipping '%s'" % (sPath), VERBOSE)
   elif bCpImageNoExif:
       sPathNew = sPath

   return sPathNew
   
def create_new_image_path(dExif, dInputDirectory, tOptions):
   """
   Based on the input path, the Exif information and the options, create the new path for the images.
   """

   lPathOld = dExif.keys()
   lPathOld.sort()
   dNewPathRaw = {}
   # If there is no destination, the images are copy/overwritten in the same directory than the input
   if tOptions.OutputDirectory is None:
      for sPathOld in lPathOld:
         sPathNew = create_path_with_exif(sPathOld, dExif[sPathOld], tOptions.CpNoExif)
         if sPathNew is not None:
            dNewPathRaw[sPathOld] = sPathNew
   elif tOptions.CopyTree: # Recreate the same tree in the output
      for sPathOld in lPathOld:
	 # Use the provided input directory stored in dInputDirectory for each image file. 
	 #  Remove this first part of the input directory, leaving only the part to be created.
	 sDirToRemove = os.path.dirname(dInputDirectory[sPathOld])
	  # "1" in "[1:]" is used to remove the first "/", so the path can be merged (see http://ur1.ca/ogdev)
         sSubDirectory = os.path.dirname(sPathOld).replace(sDirToRemove,"")[1:]
         sNewDirectory = os.path.join(tOptions.OutputDirectory, sSubDirectory)
         sPathNew =  create_path_with_exif(os.path.join(sNewDirectory,os.path.basename(sPathOld)),\
                                           dExif[sPathOld], tOptions.CpNoExif)
  	 dNewPathRaw[sPathOld] = sPathNew
   else: # Output directory given, all the files will be written there
      for sPathOld in lPathOld:
	 sFilepath = create_path_with_exif(sPathOld,  dExif[sPathOld], tOptions.CpNoExif)
	 sFileBasename = os.path.basename(sFilepath)
	 dNewPathRaw[sPathOld] = os.path.join(tOptions.OutputDirectory, sFileBasename)
 
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

   lNewPath = dNewOldPath.keys() 
   for sNewPath in lNewPath:
      nNbrImageWithThisExif =  len(dNewOldPath[sNewPath])
      if nNbrImageWithThisExif == 1:
         # Ignore if origin and destination are the same
         sOldPath = dNewOldPath[sNewPath][0]
         if sOldPath == sNewPath:
            my_print ("File already has the right name and is in the destination directory.\n Ignoring '%s'" \
                      % (sNewPath), VERBOSE)
            my_print ("----", VERBOSE)
         else: 
            dNewPathUnique[sOldPath] = sNewPath
            my_print ("EXIF date is unique, renaming\n %s --> %s" % (dNewOldPath[sNewPath], sNewPath), VERBOSE)
            my_print ("----", VERBOSE)
      else:
         my_print ("File %s is not unique! There is %s occurences" % (sNewPath, nNbrImageWithThisExif), VERBOSE)
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
                         (sNewImagePathUnique), VERBOSE)
               my_print ("----", VERBOSE)
            else:
               dNewPathUnique[sOldImagePathWithSameExif] = sNewImagePathUnique
            i = i + 1
            my_print ("Associating\n %s --> %s" % (sOldImagePathWithSameExif,sNewImagePathUnique), VERBOSE)
         my_print ("----", VERBOSE)

   return dNewPathUnique
      
def duplicate_images(dPath, tOptions):
   """
   Here is the place where the images file are duplicated, copied or moved.
   """
   
   # If requested, copy the input tree in the output directory
   if tOptions.CopyTree:	
      for sNewPath in dPath.values():
	 sDirectory = os.path.dirname(sNewPath)
	 if not os.path.exists(sDirectory):
	    os.makedirs(sDirectory)
	 

   i = 1
   nNbrImages = len(dPath.keys())
   if tOptions.Move:
      sMode = "Move"
   else:
      sMode = "Copy"
   for sOldPath in dPath.keys():
      sNewPath = dPath[sOldPath]
      if tOptions.NoClobber and os.path.exists(sNewPath):
         my_print ("File '%s' already exists and --no-clobber option activated. Skipping renaming of '%s'." \
                   % (sNewPath, sOldPath), VERBOSE)
      else:
         sProcessing = "----\nProcessing [%s/%s]:" % (i, nNbrImages)
         my_print(sProcessing + sMode +  " %s ---> %s" % (sOldPath, sNewPath))
         if tOptions.DryRun :
            my_print("Dry-run mode is activated: no operation is done")
         elif not tOptions.Move:
            shutil.copy2(sOldPath, sNewPath)
         else:
            shutil.move(sOldPath, sNewPath)
      my_print ("----", VERBOSE)
      i = i + 1
   
def exif_rename_files(tOptions):
   """
   Rename the files in sInputDirectory according to the EXIF information.
   Name of the file is of the form: YYYY-MM-DD_HHmm[_NN].jpg
   """

   # Get all the images path
   dInputPathImages = get_images_path(tOptions)

   if len(dInputPathImages.values()) == 0:
      my_print("No image file identified.")
      exit(0)
      
   # Extract the EXIF information for all images
   dExif = get_images_with_exif(dInputPathImages.keys(), tOptions.CpNoExif)

   # Create the path where the file will be copied
   dNewPathRaw = create_new_image_path(dExif, dInputPathImages, tOptions)

   # Remove any possible collision by adding a suffix in the file name of image having the same Exif and destination
   dNewPathUnique = get_unique_path_for_images(dNewPathRaw)

   # If requested, copy the input tree in the output directory
   if tOptions.CopyTree:	
      for sNewPath in dNewPathUnique.values():
	 sDirectory = os.path.dirname(sNewPath)
	 if not os.path.exists(sDirectory):
	    os.makedirs(sDirectory)
	 

   # Duplicate files
   duplicate_images(dNewPathUnique, tOptions)


############################################################
# exif_rename_files in Command line
#
#

import argparse

def get_command_line():
   """
   Parse the command line and perform all the checks.
   """

   parser = argparse.ArgumentParser(prog='PROG', prefix_chars='-',\
                                    description="Convert file name to date according to EXIF information")
   parser.add_argument("Input", metavar="Input", nargs="*", \
                     help="Directory or file(s) where the jpg/JPG files will be searched for renaming jpg files",\
                       action="store", type=str, default=None)
   parser.add_argument("--output-directory", "-o", dest="OutputDirectory", \
                     help="Directory where the image files will be written",\
                     action="store", type=str, default=None)   
   parser.add_argument("--dry-run", "-t", dest="DryRun", \
                     help="Execute the program, but do not move or copy the files",\
                       action="store_true", default=False)
   parser.add_argument("--copy-directory-tree", "-C", dest="CopyTree",  \
                     help="Copy the directory tree in the output directory, to mimic the input sub-directories",\
                     action="store_true", default=False)
   parser.add_argument("--move", "-m", dest="Move", \
                     help="Move the files, instead of copying",\
                     action="store_true", default=False)
   parser.add_argument("--no-clobber", "-n", dest="NoClobber", \
                     help=" Do not overwrite an  existing  file",\
                     action="store_true", default=False)
   parser.add_argument("--recursive", "-r",  dest="Recursive", \
                     help="Look for files in the directory and its subfolders",\
                     action="store_true", default=False)
   parser.add_argument("--verbose", "-v", dest="Verbosity", \
                     help="Explain what is being done", action="store_true", default=False)
   parser.add_argument("--include-file-with-no-exif", "-N", dest="CpNoExif", \
                       help="Copy or move files with no EXIF, using their original file name as destination",\
                       action="store_true", default=False)
   parser.add_argument("--version", "-V", dest="bVersion", \
                       help="Output version information and exit",\
                       action="store_true", default=False)               

   # Parse the args
   options = parser.parse_args()

   if options.bVersion:
      print "exif_rename.py version: " + VERSION
      print "Copyright (C) 2014 Free Software Foundation, Inc."
      print "License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>."
      print "This is free software: you are free to change and redistribute it."
      print "There is NO WARRANTY, to the extent permitted by law.\n"
      print "Written by Miguel Tremblay, http://ptaff.ca/miguel/"
      exit(0)
   
   # Verify is Copy Tree is provided but without any place to copy the output, or if the input is 
   #  files and not a directroy
   if options.CopyTree and options.OutputDirectory is None:
	 print "Error: option '--copy-recursive-tree' should be used with '--output-directory'. Please provide an output directory or do not use this option. Exiting."
	 exit (2)
   # Verify it the output is a directory
   if options.OutputDirectory is not None and not os.path.isdir(options.OutputDirectory):
      print "Error: Directory '%s' provided in '--output-directory' does not exist or is not a directory. Please provide a valid output directory. Exiting." % (options.OutputDirectory)
      exit (3)

   # Set the global verbosity
   global nGlobalVerbosity
   if options.Verbosity:
      nGlobalVerbosity = VERBOSE
   else:
      nGlobalVerbosity = NORMAL
      
   my_print("Verbosity level is set to: " + str(nGlobalVerbosity), nMessageVerbosity=VERBOSE)
   my_print("Arguments in command line are:\n " + str(sys.argv), nMessageVerbosity=VERBOSE)
   
   return options


if __name__ == "__main__":

   tOptions = get_command_line()
   exif_rename_files(tOptions)

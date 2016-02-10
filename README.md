EXIF rename
=============

Introduction
------------

The exif_rename_files.py is a python script used to rename, or copy, image files using the date in the EXIF information 
of the files. The input files must be in jpeg format, having an extension of the form ".jpg" or ".JPG". 

The file name has the form of "yyyy-mm-dd_HH-MM-SS.jpg".  If there is more than one file with the same date up to the second,
an extension of the form "_N" is added, giving "yyyy-mm-dd_HH-MM-SS_N.jpg". "N" has a fix number of digits. Hence, if there is 
10 files with the same second, the first will be labeled with "01", preserving the alphabetical order of the images.

This script is ideal if you have many image files coming from more than one device, for example when two person goes 
into vacation and take pictures of their trip. It is also perfect to give a meaningful file name to file like "DSC0000.JPG".

It works under GNU/Linux, Windows and Apple OS.

Requirements
------------

The python package ExifRead is a prerequesite for the usage of this file. Please install it for your operating system. See:  
  https://pypi.python.org/pypi/ExifRead

Download 
--------
The more recent package can be downloaded here:  
http://ptaff.ca/exif/exif_rename_files.py

git version can be accessed here:  
   git pull https://gitlab.com/MiguelTremblay/exif.git


Manual
--------
 
In a general way, this application should be called in command line like this:  
```bash
python exif_rename_files.py --input INPUT [--output-directory OUTPUTDIRECTORY] [--copy-directory-tree] [--move] [--no-clobber] [--recursive] [--log LOGFILE] [--verbose] [--silent] [--test] [--include-file-with-exif]
```


| Parameter        | Description   |
| ------------- |-------------| 
| `--version`     | Show program's version number and exit      | 
| `-h`, `--help` | Show help message and exit      | 
| `--input`     | Directory or files where the jpg/JPG files will be searched for renaming| 


Usage
-----

Copy files directly where the images are located:  
```bash
 python exif_rename_files.py --input  images/input
```

Copy files in the output directory, but do not overwrite is there is already a file with this name:   
```bash
python exif_rename_files.py --input  images/input --no-clobber --verbose --output-directory images/output/ --recursive --log log.txt --test
```

Bugs
----
Report bugs at:  
exif.miguel@ptaff.ca


Author
------
[Miguel Tremblay](http://ptaff.ca/miguel/)


License
-------

Copyright © 2016 Miguel Tremblay.

exif_rename_files.py is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.
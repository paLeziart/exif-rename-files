EXIF rename
=============

Introduction
------------

The exif_rename_files.py is a python script used to rename, or copy, image files using the date in the EXIF information 
of the files. The input files must be in jpeg format, having an extension of the form ".jpg" or ".JPG". 

The file name has the form of "yyyy-mm-dd_HH-MM-SS.jpg".  If there is more than one file with the same date up to the second,
an extension of the form "_N" is added, giving "yyyy-mm-dd_HH-MM-SS[_N].jpg". "N" has a flexible number of digits. Hence, if there is 10 files with the same second, the first will be labeled with "01", preserving the alphabetical order of the images.

This script is ideal if you have many image files coming from more than one device, for example when two person goes 
into vacation and take pictures of their trip. It is also perfect to give a meaningful file name to file like "DSC0000.JPG".

It works under GNU/Linux, Windows and Apple OS.
___

Requirements
------------

* [Python2] (https://www.python.org/downloads/)
* [Python ExifRead] (https://pypi.python.org/pypi/ExifRead)

___

Download 
--------
The more recent package can be downloaded here:  
http://ptaff.ca/exif/exif_rename_files.py

git version can be accessed here:  
 git clone https://gitlab.com/MiguelTremblay/exif_rename_files.git

Manual
--------
 
In a general way, this application should be called in command line like this:  
```bash
python exif_rename_files.py [OPTIONS] INPUT
```
<br />
where:   
* INPUT:Directory or file(s) where the jpg/JPG files will be searched for renaming jpg files.
* OPTIONS are described in the table below.

| Options        | Description   |
| ------------- |-------------| 
| `-h`, `--help` | Show help message and exit      | 
| `-o` `--output-directory`&nbsp;DIRECTORY   |Directory where the image files will be written      | 
|`-t`  `--dry-run`     |   Execute the program, but do not move or copy the files    | 
|`-C` `--copy-directory-tree`  |Copy the directory tree in the output directory, to mimic the input sub-directories |
|`-m` `--move`  |  Move the files, instead of copying |
| `-n` `--no-clobber` |Do not overwrite an existing file  |
| `-r` `--recursive`  | Look for files in the directory and its subfolders. |
|`-v` `--verbose`  | Explain what is being done |
|`-N` `--include-file-with-no-exif`  | Copy or move files with no EXIF, using their original  file name as destination |
|`-V` `--version`|Output version information and exit|

Usage
-----

Copy the image directly in the folder where it is located:  
```bash
 python exif_rename_files.py /home/miguel/photo/DSC0000.JPG
```
<br />
Copy all the images directly in the folder where they are located:  
```bash
 python exif_rename_files.py /home/miguel/photo/
```
<br />
Copy the images coming from two directories, in a target directory:  
```bash
 python exif_rename_files.py --output-directory /home/miguel/photo/output/2013/  /home/miguel/photo/2013/ /home/pauline/photo/2013/
```
<br />
Copy the all the images in the input directory, including those in subfolders, in the target directory, but do not overwrite is there is already an image with the target file name:   
```bash
python exif_rename_files.py --no-clobber --recursive --output-directory /home/miguel/output  /home/miguel/photo
```
<br />
Use find to fetch all the file name starting with "DSC" or "dsc" and rename them:
```bash
find /home/miguel/photo/ -iname "DSC*" -exec exif_rename_files.py --move {} +
```


Installation
-----

### GNU/Linux

Copy the file in '/usr/local/bin' directory and change its permission so it can be executed
```bash
wget http://ptaff.ca/exif/exif_rename_files.py
sudo mv exif_rename_files.py /usr/local/bin
sudo chmod a+rx /usr/local/bin/exif_rename_files.py
```

### Windows

### Mac OS X
First, you have to install the package `exifread` which is available via `pip`.
To install `pip`, install the [`python` `HomeBrew`](http://docs.python-guide.org/en/latest/starting/install/osx/) package with the command
```bash
brew install python
```
Then, install [`exifread`](https://pypi.python.org/pypi/ExifRead) with
```bash
pip install exifread
```

Once those steps are done, you can follow the same steps as on GNU/Linux:
```bash
wget http://ptaff.ca/exif/exif_rename_files.py
sudo mv exif_rename_files.py /usr/local/bin
sudo chmod a+rx /usr/local/bin/exif_rename_files.py
```


Bugs
----
Report bugs at:  
[exif.miguel@ptaff.ca](exif.miguel@ptaff.ca)

Author
------
[Miguel Tremblay](http://ptaff.ca/miguel/)


License
-------

Copyright © 2016 Miguel Tremblay.

exif_rename_files.py is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

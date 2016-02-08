 Rename or copy jpg files according to the information included in the EXIF information of the picture. File format is YYYY-MM-DD_HHmm[_NN].jpg
 
 The python package ExifRead is a prerequesite for the usage of this file. Please install it for your operating system. See:
  https://pypi.python.org/pypi/ExifRead
 
usage: PROG [-h] --input-directory INPUTDIRECTORY
            [--output-directory OUTPUTDIRECTORY] [--test]
            [--copy-directory-tree] [--move] [--no-clobber] [--recursive]
            [--log LOGFILE] [--verbose] [--silent]

optional arguments:
  -h, --help            show this help message and exit
  --input-directory INPUTDIRECTORY, -d INPUTDIRECTORY
                        Directory where the jpg/JPG files will be searched for
                        renaming
  --output-directory OUTPUTDIRECTORY, -o OUTPUTDIRECTORY
                        Optionnal: Directory where the image files will be
                        written
  --test, -t            Perform the operation but do not move or copy the
                        files, simply log the changes that would be done
  --copy-directory-tree, -C
                        Copy the directory tree in the output directory, to
                        mimic the input sub-directories
  --move, -m            Move the files, instead of copying, into the EXIF
                        format date
  --no-clobber, -n      Do not overwrite an existing file
  --recursive, -r       Look for files in the directory and its subfolders.
  --log LOGFILE, -l LOGFILE
                        Write all the logging information in the identified
                        file
  --verbose, -v         Output is verbose.
  --silent, -s          No output on terminal.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import shutil
import piexif

def rename_photo(src_path, dst_path, move=False, verbose=False):
    """Rename a photo file based on its EXIF data.

    Args:
        src_path (str): The source file path.
        dst_path (str): The destination file path.
        move (bool, optional): If True, move the file instead of copying it.
        verbose (bool, optional): If True, print verbose output.
    """
    if verbose:
        print(f"Processing file {src_path}")
    # Load EXIF data
    try:
        exif_data = piexif.load(src_path)
    except piexif.InvalidImageDataError:
        # EXIF data not found or invalid, skip the file
        return

    # Extract date and time from EXIF data
    date_time_original = exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal].decode()
    parts = date_time_original.split(" ")
    if len(parts) != 2:
        # Invalid date and time string, skip the file
        if verbose:
            print(f"Invalid date and time string {date_time_original} in {src_path}, skipping.")
        return
    date_parts = parts[0].split(":")
    time_parts = parts[1].split(":")
    if len(date_parts) != 3 or len(time_parts) != 3:
        # Invalid date and time string, skip the file
        if verbose:
            print(f"Invalid date and time string {date_time_original} in {src_path}, skipping.")
        return
    # Build the new file name
    year, month, day = date_parts
    hour, minute, second = time_parts
    new_filename = f"{year}-{month}-{day}_{hour}-{minute}-{second}.jpg"
    new_path = os.path.join(dst_path, new_filename)
    if os.path.exists(new_path):
        # Destination file already exists, skip the file
        if verbose:
            print(f"Destination file {new_path} already exists, skipping {src_path}")
        return
    if move:
        # Move the file
        if verbose:
            print(f"Moving {src_path} ---> {new_path}")
        os.rename(src_path, new_path)
    else:
        # Copy the file
        if verbose:
            print(f"Copying {src_path} ---> {new_path}")
        shutil.copy2(src_path, new_path)

def process_file(filepath, dst_path, move=False, verbose=False):
    """Process a single file.

    Args:
        filepath (str): The file path.
        dst_path (str): The destination path.
        move (bool, optional): If True, move the file instead of copying it.
        verbose (bool, optional): If True, print verbose output.
    """
    # Check if the file is a JPEG
    if filepath.lower().endswith(".jpg") or filepath.lower().endswith(".jpeg"):
        # Try to extract EXIF data from the file
        try:
            exif_data = piexif.load(filepath)
        except piexif.InvalidImageDataError:
            # EXIF data not found
            if verbose:
                print(f"EXIF data not found in {filepath}")
        else:
            # EXIF data found, rename the file
            rename_photo(filepath, dst_path, move=move, verbose=verbose)
    else:
        if verbose:
            print(f"{filepath} is not a JPEG file, skipping.")

def process_directory(dirpath, dst_path, recursive=False, move=False, verbose=False):
    """Process all files in a directory.

    Args:
        dirpath (str): The directory path.
        dst_path (str): The destination path.
recursive (bool, optional): If True, process subdirectories recursively.
        move (bool, optional): If True, move the files instead of copying them.
        verbose (bool, optional): If True, print verbose output.
    """
    # Loop through all files in the directory
    for filename in os.listdir(dirpath):
        filepath = os.path.join(dirpath, filename)
        # Check if the file is a regular file or a directory
        if os.path.isfile(filepath):
            # Process a single file
            process_file(filepath, dst_path, move=move, verbose=verbose)
        elif os.path.isdir(filepath) and recursive:
            # Process all files in a subdirectory
            process_directory(filepath, dst_path, recursive=True, move=move, verbose=verbose)

def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Rename photo files based on their EXIF data.")
    parser.add_argument("src", help="source file or directory")
    parser.add_argument("dst", help="destination directory")
    parser.add_argument("-r", "--recursive", action="store_true", help="process subdirectories recursively")
    parser.add_argument("-m", "--move", action="store_true", help="move files instead of copying them")
    parser.add_argument("-V", "--verbose", action="store_true", help="print verbose output")
    args = parser.parse_args()
    # Check if the source is a file or a directory
    if os.path.isfile(args.src):
        # Process a single file
        process_file(args.src, args.dst, move=args.move, verbose=args.verbose)
    elif os.path.isdir(args.src):
        # Process all files in a directory
        process_directory(args.src, args.dst, recursive=args.recursive, move=args.move, verbose=args.verbose)
    else:
        print(f"{args.src} is not a file or a directory.")

if __name__ == "__main__":
    main()

       


#!/usr/bin/bash

# USAGE
# You have a folder full of ready-to-being-stickers images, in PNG format. `cd` in this directory,
# and call this script (hint: you can also add the script in your $PATH). 
# This script will create a folder "converted", where it will drop your images with a white border.
#
# REQUIRES
# ImageMagick
#
# AUTHOR
# Romain Ricard https://github.com/romainricard
# Inspired by ondondil


mkdir converted
for filename in *.png;
do
    convert $filename -resize 300 -background none -bordercolor none -border 16x16 -write mpr:in -resize 200% -channel A -morphology dilate disk:10 +channel -fill white -colorize 100 -resize 50% mpr:in -composite converted/$filename
done

# -*- coding: utf-8 -*-
"""
Batch converts a folder (and sub-folders) of images into smaller thumbnails (like for a website) while preserving original folder structure
This code is licensed under the AGPLv3 license.
"""
from PIL import Image, ImageOps
import mimetypes
from pathlib import Path as paveway #3.4
from os import path as ospath, makedirs as osmakedirs, getcwd as osgetcwd
import shutil

#--- User Settings ---
base_folder = osgetcwd(); # Get the basename automatically (works if this file is next to the "fulls" folder)
# base_folder = r'C:\jlseidensticker.github.io\images'; # Folder which should have a `fulls` folder to convert to a `thumbs` folder
pixel_lim = 0.375; # MegaPixels, 1MP == 1000x1000 image (solid size for a thumbnail in a portfolio layout)


#--- Assemble all supported image/video/music file endings to inspect ---
supportedFormats_img = {'.jpg', '.png', '.jxl', '.jpeg', '.heic', '.webp', '.bmp', '.gif'}; #forced supported image formats
#based on https://stackoverflow.com/questions/4292029/how-to-get-a-list-of-file-extensions-for-a-general-file-type
mimetypes.init(); #fire whatever this is up
def get_extensions_for_type(general_type):
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext
        # END IF
    # END FOR ext
# END DEF
supportedFormats_img = supportedFormats_img.union(set(get_extensions_for_type('image'))); # Remove duplicates via sets


#--- Do folder work ---
input_folder = ospath.join(base_folder, 'fulls'); # Input folder for images, will check subfolders
if( not ospath.isdir(input_folder) ):
    raise Exception('ERROR: `input_folder` does not exist and must for this code to run. Consider setting base_folder to a static path in the User Settings.\nFolder missing: `'+input_folder+'`.');
# END IF
output_folder = ospath.join(base_folder, 'thumbs'); # Output folder for images, will preserve subfolders
if( not ospath.isdir(output_folder) ):
    osmakedirs(output_folder); # Make the folder if it does not exist
# END IF


#--- Get all files matching supportedFormats_img in input_folder ---
imgz = [pp.resolve() for pp in paveway(input_folder).rglob("**/*") if pp.suffix.lower() in supportedFormats_img]; # Get a list of files that match the supported image formats


#--- Convert megapixels to pixels ---
pixel_lim = pixel_lim*1E6; # For ease of use


#--- Make thumbnails of the images ---
for i in range(0, len(imgz)):
    img2img = Image.open(imgz[i]); # Get the image loaded in
    if( img2img.info.get('exif') is not None ):
        img2img = ImageOps.exif_transpose(img2img); # Rotate as exif data requests if it is there
    # END IF
    img2img_shape = img2img.size; # Get the size of the image
    dir4img = ospath.join(output_folder, imgz[i].parts[-2]); # Get the subfolder
    if( not ospath.isdir(dir4img) ):
        osmakedirs(dir4img); # Make the folder if it does not exist
    # END IF
    path4img = ospath.join(output_folder, *imgz[i].parts[-2:]); # Get the path
    if( img2img_shape[0]*img2img_shape[1] > pixel_lim ):
        # path4img = ospath.splitext(path4img)[0]+'.webp'; # Replace jpg with webp for conversion [not wanted b/c want to mirror all original file names]
        scalar = (pixel_lim/(img2img_shape[0]*img2img_shape[1]))**(1/2); # Calculate the scalar to scale it by to get to pixel_lim
        img2img_reshape = (round(img2img_shape[0]*scalar), round(img2img_shape[1]*scalar)); # Calculate the shape of the image at that pixel_lim
        if( ospath.splitext(path4img)[1].lower() in ['.jpg', '.jpeg'] ):
            img2img.resize((img2img_reshape[0], img2img_reshape[1]), Image.Resampling.LANCZOS).save(path4img, optimize=True, progressive=True); # Resize and save [for jpg]
        elif( ospath.splitext(path4img)[1].lower() == '.webp' ):
            img2img.resize((img2img_reshape[0], img2img_reshape[1]), Image.Resampling.LANCZOS).save(path4img, quality=65); # Resize and save [for webp]
        else:
            img2img.resize((img2img_reshape[0], img2img_reshape[1]), Image.Resampling.LANCZOS).save(path4img); # Catch-all
        # END IF
    else:
        shutil.copy(imgz[i], path4img); # Just copy it over, it's already thumbnail sized
    # END IF
# END FOR i
import argparse
import glob
import os
import pyexiv2
import shutil
import sys

# Say you've got a directory full of images, all with EXIF data, and
# you would like to organize them into folders based on date. This
# will do that.

def eachjpeg(rootdir):
    for f in os.listdir(rootdir):
        fullpath = os.path.join(rootdir, f)
        if os.path.isdir(fullpath):
            for j in eachjpeg(fullpath):
                yield j
        elif os.path.isfile(fullpath) and fullpath[-3:].lower() == 'jpg':
            yield fullpath

def main(argv):
    parser = argparse.ArgumentParser(description="Organize photos based on EXIF date",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('inputdir', help='Input directory')
    parser.add_argument('outputdir', help='Base output directory (date directories will be created under this)')
    args = parser.parse_args(argv)

    for jpgfile in eachjpeg(args.inputdir):
        metadata = pyexiv2.ImageMetadata(jpgfile)
        metadata.read()
        date = metadata['Exif.Image.DateTime']
        fmt = '%Y%m%d'
        d = date.value.strftime(fmt)
        newfiledir = os.path.join(args.outputdir, d)

        if not os.path.exists(newfiledir):
            print 'mkdir %s' % newfiledir
            os.makedirs(newfiledir)
        print 'cp %s %s' % (jpgfile, newfiledir)
        if not os.path.exists(os.path.join(newfiledir, os.path.basename(jpgfile))):
            shutil.copy(jpgfile, newfiledir)

if __name__ == "__main__":
    main(sys.argv[1:])

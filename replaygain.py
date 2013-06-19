import argparse
import os
import glob
import logging
import sys

from flac_embed import CmdInvoker, config_logging

def add_replaygain(directory):
    cmd = CmdInvoker()
    flacfiles = glob.glob(os.path.join(directory, '*.flac'))
    cmdline = tuple(['metaflac', '--add-replay-gain'] + flacfiles)
    logging.info("tagging files: %s" % ' '.join(cmdline))
    cmd.call(cmdline)

def each_subdir_containing_flacs(root_dir):
    for subfile in os.listdir(root_dir):
        if os.path.isdir(os.path.join(root_dir, subfile)):
            if glob.glob(os.path.join(root_dir, subfile, '*.flac')):
                yield os.path.join(root_dir, subfile)
            for subsubfile in os.listdir(os.path.join(root_dir, subfile)):
                if os.path.isdir(os.path.join(root_dir, subfile, subsubfile)):
                    subsubdir = os.path.join(root_dir, subfile, subsubfile)
                    if glob.glob(os.path.join(subsubdir, '*.flac')):
                        yield subsubdir

def main():
    fmt = argparse.ArgumentDefaultsHelpFormatter
    desc = "Tag all FLAC files with replaygain information"
    argparser = argparse.ArgumentParser(description=desc, formatter_class=fmt)
    argparser.add_argument('root', help='Root directory to search')
    args = argparser.parse_args(sys.argv[1:])
    config_logging()

    for directory in each_subdir_containing_flacs(args.root):
        add_replaygain(directory)

if __name__ == '__main__':
    main()

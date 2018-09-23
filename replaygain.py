import argparse
import os
import glob
import logging
import subprocess
import sys

from flac_embed import CmdInvoker, config_logging


def has_replaygain(filepath):
    cmd = CmdInvoker()
    cmdline = tuple(['metaflac', '--export-tags-to=-', filepath])
    output = cmd.call(cmdline)
    output_str = output.decode('utf-8')
    output_lines = output_str.split('\n')
    return any('REPLAYGAIN' in l for l in output_lines)


def add_replaygain(directory):
    blacklist = {'Opeth/Watershed', 'Blue Vein Blood', 'Terrifyer'}
    if any(d in directory for d in blacklist):
        return
    cmd = CmdInvoker()
    flacfiles = glob.glob(os.path.join(directory, '*.flac'))
    cmdline = tuple(['metaflac', '--add-replay-gain'] + flacfiles)
    has_rg = all(has_replaygain(f) for f in flacfiles)
    if not has_rg:
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
        flacs = glob.glob(os.path.join(directory, '*.flac'))
        tags_output = subprocess.check_output(['metaflac', '--export-tags-to=-', flacs[0]])
        if 'REPLAY' not in tags_output:
            add_replaygain(directory)



if __name__ == '__main__':
    main()

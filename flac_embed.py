import argparse
import logging
import os
import subprocess
import sys
from time import sleep


class CmdInvoker:
    def __init__(self):
        pass

    def call(self, tup):
        return subprocess.call(tup)


class EchoCmdInvoker:
    def __init__(self):
        pass

    def call(self, tup):
        logging.info('command to invoke: "%s"' % str(tup))
        return 0


def eachfile(rootdir, extension):
    for f in os.listdir(rootdir):
        fullpath = os.path.join(rootdir, f)
        if os.path.isdir(fullpath):
            for j in eachfile(fullpath, extension):
                yield j
        elif os.path.isfile(fullpath) and \
                fullpath[-len(extension):].lower() == extension:
            yield fullpath


def folder_art(filepath):
    artfile = os.path.join(os.path.dirname(filepath), 'folder.jpg')
    if os.path.exists(artfile):
        return artfile
    else:
        return None


def config_logging():
    formatstring = '%(asctime)s|%(module)s|%(levelname)s|%(message)s'
    formatter = logging.Formatter(formatstring)
    logging.basicConfig(level=logging.INFO, format=formatstring)
    stdouthandler = logging.StreamHandler(sys.stdout)
    stdouthandler.setLevel(logging.INFO)
    stdouthandler.setFormatter(formatter)
    rootlogger = logging.getLogger()
    for h in rootlogger.handlers:
        rootlogger.removeHandler(h)
    rootlogger.addHandler(stdouthandler)


def clear_art(filepath, cmd_invoker):
    cmdline = ('metaflac', '--remove', '--block-type=PICTURE', filepath)
    return cmd_invoker.call(cmdline)


def set_art(filepath, artpath, cmd_invoker):
    def spec():
        typ = 3
        mime = 'image/jpeg'
        descr = ''
        dims = ''  # leave to reader to determine from file
        return '%s|%s|%s|%s|%s' % (typ, mime, descr, dims, artpath)
    img_option = '--import-picture-from=%s' % spec()
    metaflac_cmdline = ('metaflac', img_option, filepath)
    retcode = cmd_invoker.call(metaflac_cmdline)
    return retcode


def main(argv):
    fmt = argparse.ArgumentDefaultsHelpFormatter
    desc = ""
    argparser = argparse.ArgumentParser(description=desc, formatter_class=fmt)
    argparser.add_argument('root', help='Root directory to search')
    argparser.add_argument('--dry', help='Dry run; only print actions',
                           action='store_const', const=True, default=False)
    argparser.add_argument('--pause', help='Pause after each file (2 seconds)',
                           action='store_const', const=True, default=False)
    args = argparser.parse_args(argv)

    config_logging()
    cmd_invoker = EchoCmdInvoker() if args.dry else CmdInvoker()

    for flacfile in eachfile(args.root, 'flac'):
        logging.info('FLAC|' + flacfile)
        artfile = folder_art(flacfile)
        if artfile:
            logging.info('JPEG|%s' % artfile)
            retcode = clear_art(flacfile, cmd_invoker)
            if retcode != 0:
                logging.error('FAILURE TO CLEAR ART: %s' % flacfile)
                continue
            retcode = set_art(flacfile, artfile, cmd_invoker)
            if retcode != 0:
                logging.error('FAILURE TO SET ART: %s' % flacfile)
        else:
            logging.info('no cover art')
        if args.pause:
            sleep(3)

if __name__ == '__main__':
    main(sys.argv[1:])

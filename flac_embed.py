import argparse
import logging
import os
import subprocess
import sys
from time import sleep


class Logger:
    def __init__(self, quiet):
        self._quiet = quiet

    def info(self, s):
        if self._quiet:
            return
        logging.info(s)


class CmdInvoker:
    def __init__(self, quiet):
        self._quiet = quiet

    def call(self, tup):
        return subprocess.check_output(tup)

    def is_quiet(self):
        return self._quiet


class EchoCmdInvoker:
    def __init__(self, quiet):
        self._quiet = quiet

    def call(self, tup):
        if not self._quiet:
            logging.info('command to invoke: "%s"' % str(tup))
        return 0

    def is_quiet(self):
        return self._quiet


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
    basenames = ['cover', 'folder']
    for b in basenames:
        artfile = os.path.join(os.path.dirname(filepath), '%s.jpg' % b)
        if os.path.exists(artfile):
            return artfile
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
    if not cmd_invoker.is_quiet():
        logging.info("%s %s %s" % metaflac_cmdline)
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
    argparser.add_argument('--quiet', help='Supress logging output',
                           action='store_const', const=True, default=False)
    args = argparser.parse_args(argv)

    config_logging()
    logger = Logger(args.quiet)
    cmd_invoker = EchoCmdInvoker(args.quiet) if args.dry else CmdInvoker(args.quiet)

    for flacfile in eachfile(args.root, 'flac'):
        #logger.info('FLAC|' + flacfile)
        artfile = folder_art(flacfile)
        if artfile:
            #logger.info('JPEG|%s' % artfile)
            retcode = clear_art(flacfile, cmd_invoker)
            retcode = set_art(flacfile, artfile, cmd_invoker)
        else:
            logger.info('no cover art')
        if args.pause:
            sleep(3)


if __name__ == '__main__':
    main(sys.argv[1:])

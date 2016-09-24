import argparse
import os
import re
import sys


def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('files', nargs='*')
    return p.parse_args(args)


def main(args):
    parsed_args = parse_args(args)

    if not parsed_args.files:
        exit(0)

    sorted_files = sorted(parsed_args.files)
    file_re = re.compile('^(\d+)(.*)$')

    def number_name(filepath):
        match = file_re.search(filepath)

        if match:
            return int(match.group(1)), match.group(2)
        else:
            return None, None

    offset = -1

    def make_name(prefix, n, rest):
        def zero_pad():
            if n <= 9:
                return '0%d' % n
            else:
                return str(n)
        return os.path.join(prefix, zero_pad() + rest)

    for f in sorted_files:
        file_only = f
        path_prefix = ''

        if os.sep in f:
            path_prefix = os.path.dirname(f)
            file_only = os.path.basename(f)

        num, rest = number_name(file_only)

        if offset == -1:
            offset = num - 1

        old_name = make_name(path_prefix, num, rest)
        new_name = make_name(path_prefix, num - offset, rest)

        print("%s -> %s" % (old_name, new_name))
        os.rename(old_name, new_name)

if __name__ == '__main__':
    main(sys.argv[1:])

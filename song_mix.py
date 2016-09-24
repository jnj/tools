__author__ = 'josh'

import argparse
import os
import random
import subprocess
import sys


def main(argv):
    fmt = argparse.ArgumentDefaultsHelpFormatter
    desc = ""
    argparser = argparse.ArgumentParser(description=desc, formatter_class=fmt)
    argparser.add_argument('sourcedir', help='Directory to find flac files in')
    argparser.add_argument('destdir', help='Directory to write files to')
    argparser.add_argument('--size', help='Use this much disk space, in MB', type=int)
    argparser.add_argument('--time', help='Use this many minutes (constrained by size parameter)', type=int)
    args = argparser.parse_args(argv)

    files = [os.path.join(path, filename)
             for path, dirs, files in os.walk(args.sourcedir)
             for filename in files if filename.endswith('.flac')]

    chosen_files = fill_time(args.time, files)
    print '\n'.join(chosen_files)


def fill_time(max_seconds, all_files):
    duration = 0
    tracks = []
    while duration <= max_seconds:
        path = choose_random_file(all_files)
        duration += get_play_time_seconds(path)
        tracks.append(path)
    return tracks

def choose_random_file(all_files):
    return random.choice(all_files)


def get_play_time_seconds(flac_path):
    output = subprocess.check_output(['metaflac', '--show-sample-rate', '--show-total-samples', flac_path])
    rate, samples = output.splitlines()
    rate = int(rate)
    samples = int(samples)
    return 1.0 * samples / rate


if __name__ == '__main__':
    main(sys.argv[1:])
import argparse
import os
import sys

from PIL import Image


def parse_args(args):
    p = argparse.ArgumentParser(description='Locates cover.jpg files that are too small')
    p.add_argument('--size', type=int, default=500, help='Max length for edge to be "small"')
    p.add_argument('rootpath')
    return p.parse_args(args)


def each_dir(root_path):
    if os.path.exists(root_path) and os.path.isdir(root_path):
        for subdir in os.listdir(root_path):
            abs_path = os.path.join(root_path, subdir)
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                yield abs_path


def check_album_art(album_dir, output, size):
    sq = (size, size)
    art_path = os.path.join(album_dir, 'cover.jpg')
    if os.path.exists(art_path) and os.path.isfile(art_path):
        with Image.open(art_path, 'r') as im:
            w, h = im.size
            if im.size < sq:
                output.append((art_path, w, h))


def main(args):
    parsed_args = parse_args(args)
    output = []
    for artist_path in each_dir(parsed_args.rootpath):
        for album_path in each_dir(artist_path):
            check_album_art(album_path, output, parsed_args.size)
    for result in sorted(output, key=lambda t: t[0]):
        print('%s %dx%d' % result)


if __name__ == '__main__':
    main(sys.argv[1:])

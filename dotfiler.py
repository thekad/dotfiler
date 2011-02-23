#!/usr/bin/env python
#
# Just a small script to bootstrap your dot files in your ~
#
# Copyright (c) 2010, Jorge A Gallegos <kad@blegh.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import argparse
import glob
import os
import sys


class DotFiler(object):

    def __init__(self, commit=False):
        self.commit = commit

    def run(self, source_dir, skip_files=[]):
        src = os.path.realpath(source_dir)
        skip = []
        for sk in skip_files:
            skip.extend(glob.glob(os.path.join(src, sk)))
        listing = os.listdir(src)
        maxlen = len(max(listing, key=len))
        for filename in listing:
            source = os.path.join(src, filename)
            if source in skip:
                print 'Skipping ~/.%s' % filename
            else:
                link = os.path.join('%s/.%s' % (os.path.expanduser('~'), filename))
                backup = os.path.join('%s/%s.dotfiler' % (os.path.expanduser('~'), filename))
                if os.path.exists(link):
                    if os.path.islink(link):
                        print 'Skipping ~/.%s (already a link)' % filename
                        continue
                    if self.commit:
                        print 'Moving   ~/.%s => ~/%s.dotfiler' % (filename.ljust(maxlen), filename)
                        try:
                            os.rename(link, backup)
                        except Exception as e:
                            print 'Skipping ~/.%s (Cannot create backup: %s)' % (filename, e)
                            continue
                print 'Linking  ~/.%s -> %s' % (filename.ljust(maxlen), os.path.join(src, filename))
                if self.commit:
                    try:
                        os.symlink(source, link)
                    except Exception as e:
                        print 'Skipping ~/.%s (Exception caught when creating link: %s)' % (filename, e)
                        continue
        if self.commit:
            print 'Done.'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--commit', '-c', action='store_true', default=False,
        help='By default, no changes will be written. Enable to write')
    ap.add_argument('--skip', '-k', action='append', default=[],
        help='Files you want to skip, use multiple times if you want')
    ap.add_argument('source', nargs=1, help='Path to the source directory')
    args = ap.parse_args()
    df = DotFiler(args.commit)
    return df.run(args.source[0], args.skip)

if __name__ == '__main__':
    sys.exit(main())


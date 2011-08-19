#!/usr/bin/env python
#
'''
Just a small script to bootstrap your dot files in your ~

The program will receive a "source" directory where to pull the files 
from, it will then try to link from within your HOME directory to 
the target file in the source directory (appending a dot at the start)
like this:
    The link ~/.something will point to /your/source/path/something
The program can also skip certain files based on a flag (glob expanded)
and will skip any file that is a symlink already. From those files that
will be linked, it will create a backup copy in your HOME dir in the
following manner:
    The file ~/.something will be moved to ~/something.dotfiler
If you want to later delete all those files just:
    rm -rf ~/*.dotfiler
The script will run in "dry run" mode unless you set the commit flag
'''

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

    def __init__(self, base, commit=False, backup=True):
        self.base = base
        self.commit = commit
        self.backup = backup

    def _norm(self, root, item):
        """Normalize paths"""

#       first-level items
        if not root:
            item = os.path.join(self.base, '.%s' % item)
        else:
            item = os.path.join(self.base, '.%s' % root, item)
        return item

    def handle_dirs(self, root, dirs):
        """Will create the proper directories"""

        for d in dirs:
            d = self._norm(root, d)
            if self.commit:
                try:
                    if os.path.exists(d):
                        print 'Skip creating %s (path already exists)' % d
                        continue
                    os.makedirs(d)
                except Exception as e:
                    print 'Skip %s (Exception caught: %s)' % (d, e)

    def handle_files(self, root, source, files):
        """Will handle the file linkin"""

        for f in files:
            target = os.path.join(source, root, f)
            link = self._norm(root, f)
            if os.path.exists(link):
                print 'Skip linking %s (already a link)' % link
                continue
            print 'Linking %s -> %s' % (link, target)
            if self.commit:
                try:
                    os.symlink(target, link)
                except Exception as e:
                    print 'Skip %s (Exception caught: %s)' % (link, e)

    def backup_root_dir(self, targets):
        """Makes backups out of the expected files"""

        for target in targets:
            link = os.path.join(self.base, '.%s' % target)
            backup = os.path.join(self.base, '%s.dotfiler' % target)
            target = os.path.join(self.base, target)
            if os.path.exists(link) and not os.path.islink(link):
                if not os.path.exists(backup):
                    print 'Moving %s => %s' % (link, backup)
                    if self.commit:
                        try:
                            os.rename(link, backup)
                        except Exception as e:
                            print 'Skip %s (Exception caught: %s)' % (link, e)

    def run(self, source_dir):
        """main loop"""

        source_dir = os.path.realpath(source_dir)
        for root, dirs, files in os.walk(source_dir):
            root = root.replace(source_dir, '')
            if not root and self.backup:
                self.backup_root_dir(dirs + files)
            if root.startswith('/'):
                root = root[1:]
            self.handle_dirs(root, dirs)
            self.handle_files(root, source_dir, files)
        print 'Done.'


def main():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('--commit', '-c', action='store_true', default=False,
        help='By default, no changes will be written. Enable to write')
    ap.add_argument('--no-backup', '-n', action='store_true', default=False,
        help='Do not backup stuff')
    ap.add_argument('--base-path', '-b', default=os.path.expanduser('~'),
        help='Base path to create the links')
    ap.add_argument('source', nargs=1, help='Path to the source directory')
    args = ap.parse_args()
    df = DotFiler(args.base_path, args.commit, not args.no_backup)
    return df.run(args.source[0])

if __name__ == '__main__':
    sys.exit(main())


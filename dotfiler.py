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
import os
import sys


class DotFiler(object):

    def __init__(self, base, commit=False, backup=True, force=False):
        self.base = base
        self.commit = commit
        self.backup = backup
        self.force = force

    def backup_file(self, target):
        """Backup individual file"""

        # Perfectly valid if you don't want to backup stuff
        if not self.backup:
            return
        stripped = target.replace('%s/.' % self.base, '')
        parts = os.path.split(stripped)
        # on root-level files, the first item is ''
        if parts[0]:
            topdir = parts[0]
            stripped = stripped.replace(topdir, '%s.dotfiler' % (topdir,))
            backup = os.path.join(self.base, stripped)
        else:
            backup = os.path.join(self.base, '%s.dotfiler' % (stripped,))
        print 'Backing up %s to %s' % (target, backup,)
        if self.commit and self.backup:
           if not os.path.isdir(os.path.dirname(backup)):
               os.makedirs(os.path.dirname(backup))
           os.rename(target, backup)
        else:
            pass

    def handle_files(self, root, source, files):
        """Will handle the file linking"""

        for f in files:
            target = os.path.join(source, root, f)
            if not root:
                link = os.path.join(self.base, '.%s' % f)
            else:
                link = os.path.join(self.base, '.%s' % root, f)
            if os.path.exists(link):
                if os.path.islink(link):
                    if self.force:
                        print 'Unlinking previous file/link %s' % link
                        if self.commit:
                            os.unlink(link)
                    else:
                        print 'Skip linking %s (already a link)' % link
                        continue
                else:
                    self.backup_file(link)

            print 'Linking %s -> %s' % (link, target)
            if self.commit:
                try:
                    if not os.path.isdir(os.path.dirname(link)):
                        os.makedirs(os.path.dirname(link))
                    os.symlink(target, link)
                except Exception as e:
                    print 'Skip %s (Exception caught: %s)' % (link, e)

    def run(self, source_dir):
        """main loop"""

        source_dir = os.path.realpath(source_dir)
        for root, dirs, files in os.walk(source_dir):
            root = root.replace(source_dir, '')
            if root.startswith('/'):
                root = root[1:]
            self.handle_files(root, source_dir, files)
        print 'Done.'


def main():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('--commit', '-c', action='store_true', default=False,
        help='By default, no changes will be written. Enable to write')
    ap.add_argument('--no-backup', '-n', action='store_true', default=False,
        help='Do not backup stuff')
    ap.add_argument('--force', '-f', action='store_true', default=False,
        help='Overwrite existing links')
    ap.add_argument('--base-path', '-b', default=os.path.expanduser('~'),
        help='Base path to create the links')
    ap.add_argument('source', nargs=1, help='Path to the source directory')
    args = ap.parse_args()
    df = DotFiler(args.base_path, args.commit, not args.no_backup, args.force)
    return df.run(args.source[0])

if __name__ == '__main__':
    sys.exit(main())


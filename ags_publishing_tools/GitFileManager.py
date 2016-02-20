import sys
from subprocess import check_output

__author__ = 'ifirkin'


def get_changed_files():
    return check_output(['git',  'diff', '--name-only',  'HEAD~1']).splitlines()


def get_changed_mxds(changed_files):
    return [f for (f) in changed_files if str(f).lower().endswith('mxd')]


def build_args():
    return ' '.join(['-i ' + f for f in get_changed_mxds(get_changed_files())])


def get_args():
    sys.stdout.write(build_args)
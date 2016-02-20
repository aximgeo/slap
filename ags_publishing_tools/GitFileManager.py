from subprocess import call

__author__ = 'ifirkin'


def get_changed_files():
    return call(['git',  'diff', '--name-only',  'HEAD~1'])


def get_changed_mxds(changed_files):
    return list({f for (f) in changed_files if str(f).lower().endswith('mxd')})

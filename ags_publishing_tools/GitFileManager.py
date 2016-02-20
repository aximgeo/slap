from subprocess import call

__author__ = 'ifirkin'


def get_changed_files():
    return call(['git',  'diff', '--name-only',  'HEAD~1'])


def get_changed_mxds(changed_files):
    return [f for (f) in changed_files if str(f).lower().endswith('mxd')]


def get_args():
    return ' '.join(['-i ' + f for f in get_changed_mxds(get_changed_files())])
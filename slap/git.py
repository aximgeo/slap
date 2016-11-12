import sys
from subprocess import check_output


def get_changed_files(sha='HEAD~1'):
    return check_output(['git', 'diff', '--name-only', 'HEAD', sha]).splitlines()


def get_changed_mxds(sha='HEAD~1'):
    return [f for (f) in get_changed_files(sha) if str(f).lower().endswith('mxd')]


def build_args():
    return ' '.join(['-i ' + f for f in get_changed_mxds()])


def get_args():
    sys.stdout.write(build_args())

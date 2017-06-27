from builtins import str
import sys
from subprocess import check_output


def get_changed_files(sha='HEAD~1'):
    return check_output(['git', 'diff', '--name-only', 'HEAD', sha]).splitlines()


def get_changed_mxds(sha='HEAD~1'):
    return [f for (f) in get_changed_files(sha) if str(f).lower().endswith('mxd')]

import os


def get_mxds(directories):
    mxds = []
    for directory in directories:
        mxds += [
            os.path.join(directory, f)
            for root, dirs, files in os.walk(directory)
            for f in files
            if f.lower().endswith('mxd')
        ]
    return mxds

import os
import subprocess


def line_number(path):
    if not (os.path.exists(path) and os.path.isfile(path)):
        raise IOError()
    p = subprocess.Popen(['wc', '-l', path],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])
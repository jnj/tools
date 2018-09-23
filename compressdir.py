import os
import tarfile


def compressify(entry):
    tarfilepath = os.path.join(os.path.abspath(entry), '%s.tar.gz' % entry)
    with tarfile.open(name=tarfilepath, mode='w:gz') as f:



entries = os.listdir('.')

for entry in entries:
    if os.path.isdir(entry):
        compressify(entry)




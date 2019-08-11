#!/usr/bin/env python3
import sys
if sys.version_info < (3, 7):
  sys.exit("Python %s.%s or later is required.\n" %(3, 7))

from setuptools import setup
from setuptools.command.install import install
import os, re, site


class OSInstall(install):
    """Allow OS installation"""
    def run(self):
        foundroot = 0
        install.run(self)
        for arg in sys.argv:
            if re.match("--root=.*", arg):
                rootdir = arg.split("=")[1]
                foundroot = 1
        if foundroot == 0:
            rootdir = ""
        lsbdir = rootdir + "/usr/lib/lsb"
        #bindir = rootdir + "/usr/bin"
        sitepkgdir = site.getsitepackages()[0]
        pkgdir = rootdir + sitepkgdir + "/lsbtools"
        if not os.path.exists(lsbdir):
            os.mkdir(lsbdir)
        #if not os.path.exists(bindir):
        #    os.mkdir(bindir)
        iid = pkgdir + "/install_initd.py"
        riid = sitepkgdir + "/lsbtools" + "/install_initd.py"
        did = lsbdir + "/install_initd"
        dtid = did + '.temp'
        ird = pkgdir + "/remove_initd.py"
        rird = sitepkgdir + "/lsbtools" + "/remove_initd.py"
        drd = lsbdir + "/remove_initd"
        dtrd = drd + '.temp'
        os.symlink(riid, dtid)
        os.rename(dtid, did)
        os.symlink(rird, dtrd)
        os.rename(dtrd, drd)
        os.chmod(iid, 0o755)
        os.chmod(ird, 0o755)

setup(
    cmdclass={
        'install': OSInstall,
    },
    name='LSB-Tools',
    version='0.2',
    packages=['lsbtools',],
    license='MIT',
    author='DJ Lucas',
    author_email='dj@linuxfromscratch.org',
    url='https://github.com/djlucas/LSB-Tools/',
    description='A distribution agnostic set of LSB scripts.',
    long_description=open('README').read(),
    python_requires='>3.7',
    platforms=['linux'],
    data_files = [('', ['LICENSE']),('', ['INSTALL'])]
)

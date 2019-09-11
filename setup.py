#!/usr/bin/env python3
import sys
if sys.version_info < (3, 7):
  sys.exit("Python %s.%s or later is required.\n" %(3, 7))

from setuptools import setup
from setuptools.command.install import install
import os, re, shutil, site


class OSInstall(install):
    """Allow OS installation"""
    def run(self):
        foundroot = 0
        for arg in sys.argv:
            if re.match("--root=.*", arg):
                rootdir = arg.split("=")[1]
                foundroot = 1
            if re.match("--home.*", arg):
                print("The '--home' argument is not supported.", file=sys.stderr)
                sys.exit(1)
            if re.match("--install.*", arg):
                print("The '--install-*' arguments are not supported.", file=sys.stderr)
                sys.exit(1)
            if re.match("--prefix.*", arg):
                print("The '--prefix' argument is not supported.", file=sys.stderr)
                sys.exit(1)
        if foundroot == 0:
            rootdir = ""
        install.run(self)
        lsbdir = rootdir + "/usr/lib/lsb"
        bindir = rootdir + "/usr/bin"
        man1dir = rootdir + "/usr/share/man/man1"
        man8dir = rootdir + "/usr/share/man/man8"
        sitepkgdir = site.getsitepackages()[0]
        pkgdir = rootdir + sitepkgdir + "/lsbtools"
        if not os.path.exists(lsbdir):
            os.mkdir(lsbdir)
        if not os.path.exists(bindir):
            os.mkdir(bindir)
        if not os.path.exists(man1dir):
            os.mkdir(man1dir)
        if not os.path.exists(man8dir):
            os.mkdir(man8dir)
        iid = pkgdir + "/install_initd.py"
        riid = sitepkgdir + "/lsbtools" + "/install_initd.py"
        did = lsbdir + "/install_initd"
        dtid = did + '.temp'
        ird = pkgdir + "/remove_initd.py"
        rird = sitepkgdir + "/lsbtools" + "/remove_initd.py"
        drd = lsbdir + "/remove_initd"
        dtrd = drd + '.temp'
        ilr = pkgdir + "/lsb_release.py"
        rilr = sitepkgdir + "/lsbtools" + "/lsb_release.py"
        dlr = bindir + "/lsb_release"
        dtlr = dlr + '.temp'
        os.symlink(riid, dtid)
        os.rename(dtid, did)
        os.symlink(rird, dtrd)
        os.rename(dtrd, drd)
        os.symlink(rilr, dtlr)
        shutil.copy2("man/lsb_release.1", man1dir)
        shutil.copy2("man/install_initd.8", man8dir)
        shutil.copy2("man/remove_initd.8", man8dir)
        os.rename(dtlr, dlr)
        os.chmod(iid, 0o755)
        os.chmod(ird, 0o755)
        os.chmod(ilr, 0o755)

setup(
    cmdclass={
        'install': OSInstall,
    },
    name='LSB-Tools',
    version='0.5',
    packages=['lsbtools',],
    license='MIT',
    author='DJ Lucas',
    author_email='dj@linuxfromscratch.org',
    url='https://github.com/djlucas/LSB-Tools/',
    description='A distribution agnostic set of LSB scripts.',
    long_description=open('README').read(),
    python_requires='>3.7',
    platforms=['linux'],
    data_files = [('', ['LICENSE']),
                  ('', ['INSTALL']),
                  ('', ['man/lsb_release.1']),
                  ('', ['man/install_initd.8']),
                  ('', ['man/remove_initd.8']),]
)

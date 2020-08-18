import sys

if sys.version_info < (3,7):
    sys.exit("Python %s.%s or later is required.\n" %(3, 7))

from setuptools import setup
from setuptools.command.install import install
import os, re, shutil, site

distversion = '0.7'

class OSInstall(install):
    """Allow OS installation"""
    def run(self):
        foundroot = 0
        for arg in sys.argv:
            if re.match("--root=.*", arg):
                rootdir = arg.split("=")[1]
                foundroot = 1
            if re.match("--home.*", arg):
                sys.stderr.write("The '--home' argument is not supported.")
                sys.exit(1)
            if re.match("--install.*", arg):
                sys.stderr.write("The '--install-*' arguments are not supported.")
                sys.exit(1)
            if re.match("--prefix.*", arg):
                sys.stderr.write("The '--prefix' argument is not supported.")
                sys.exit(1)
        if foundroot == 0:
            rootdir = ""
        install.run(self)
        lsbdir = rootdir + "/usr/lib/lsb"
        bindir = rootdir + "/usr/bin"
        sbindir = rootdir + "/usr/sbin"
        sitepkgdir = site.getsitepackages()[0]
        pkgdir = rootdir + sitepkgdir + "/lsbtools"
        if not os.path.exists(lsbdir):
            print("Creating: ", lsbdir)
            os.makedirs(lsbdir)
        if not os.path.exists(bindir):
            print("Creating: ", bindir)
            os.makedirs(bindir)
        if not os.path.exists(sbindir):
            print("Creating: ", sbindir)
            os.makedirs(sbindir)
        ipy = pkgdir + "/__init__.py"
        iid = pkgdir + "/install_initd.py"
        riid = sitepkgdir + "/lsbtools" + "/install_initd.py"
        did = lsbdir + "/install_initd"
        dtid = did + '.temp'
        sdid = sbindir + "/install_initd"
        sdtid = sdid + '.temp'
        ird = pkgdir + "/remove_initd.py"
        rird = sitepkgdir + "/lsbtools" + "/remove_initd.py"
        drd = lsbdir + "/remove_initd"
        dtrd = drd + '.temp'
        sdrd = sbindir + "/remove_initd"
        sdtrd = sdrd + '.temp'
        ilr = pkgdir + "/lsb_release.py"
        rilr = sitepkgdir + "/lsbtools" + "/lsb_release.py"
        dlr = bindir + "/lsb_release"
        dtlr = dlr + '.temp'
        ili = pkgdir + "/lsbinstall.py"
        rili = sitepkgdir + "/lsbtools" + "/lsbinstall.py"
        dli = bindir + "/lsbinstall.py"
        dtli = dli + '.temp'
        # setuptools depends on lsb_release
        # hardcode the interpreter for Python upgrades
        myshebang = "#!" + os.path.dirname(sys.executable) + "/" + os.readlink(sys.executable)
        with open(ipy, 'r') as original: data = original.read()
        with open(ipy, 'w') as modified: modified.write(myshebang + "\n" + data)
        with open(iid, 'r') as original: data = original.read()
        with open(iid, 'w') as modified: modified.write(myshebang + "\n" + data)
        with open(ird, 'r') as original: data = original.read()
        with open(ird, 'w') as modified: modified.write(myshebang + "\n" + data)
        with open(ilr, 'r') as original: data = original.read()
        with open(ilr, 'w') as modified: modified.write(myshebang + "\n" + data)
        with open(ili, 'r') as original: data = original.read()
        with open(ili, 'w') as modified: modified.write(myshebang + "\n" + data)
        os.symlink(riid, dtid)
        os.rename(dtid, did)
        os.symlink(riid, sdtid)
        os.rename(sdtid, sdid)
        os.symlink(rird, dtrd)
        os.rename(dtrd, drd)
        os.symlink(rird, sdtrd)
        os.rename(sdtrd, sdrd)
        os.symlink(rilr, dtlr)
        os.rename(dtlr, dlr)
        os.chmod(iid, 0o755)
        os.chmod(ird, 0o755)
        os.chmod(ilr, 0o755)

setup(
    cmdclass={
        'install': OSInstall,
    },
    name='LSB-Tools',
    version=distversion,
    packages=['lsbtools',],
    license='MIT',
    author='DJ Lucas',
    author_email='dj@linuxfromscratch.org',
    url='https://github.com/djlucas/LSB-Tools/',
    description='A distribution agnostic set of LSB scripts.',
    long_description=open('README').read(),
    python_requires='>3.7',
    platforms=['linux'],
    data_files = [('/usr/share/doc/LSB-Tools-' + distversion, ['LICENSE']),
                  ('/usr/share/doc/LSB-Tools-' + distversion, ['INSTALL']),
                  ('/usr/share/man/man1', ['man/lsb_release.1']),
                  ('/usr/share/man/man8', ['man/install_initd.8']),
                  ('/usr/share/man/man8', ['man/remove_initd.8']),]
)

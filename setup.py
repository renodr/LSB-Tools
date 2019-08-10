from setuptools import setup
from setuptools.command.install import install
import site, os

class OSInstall(install):
    """Allow OS installation"""
    def run(self):
        install.run(self)
        lsbdir = "/usr/lib/lsb"
        bindir = "/usr/bin"
        pkgdir = site.getsitepackages()[0]
        pkgdir = os.path.join(pkgdir, "lsbtools")
        iid = os.path.join(pkgdir, "install_initd.py")
        did = os.path.join(lsbdir, "install_initd")
        dtid = did + '.temp'
        ird = os.path.join(pkgdir, "remove_initd.py")
        drd = os.path.join(lsbdir, "remove_initd")
        dtrd = drd + '.temp'
        os.symlink(iid, dtid)
        os.rename(dtid, did)
        os.symlink(ird, dtrd)
        os.rename(dtrd, drd)
        os.chmod(iid, 0o755)
        os.chmod(ird, 0o755)

setup(
    cmdclass={
        'install': OSInstall,
    },
    name='LSB-Tools',
    version='0.1',
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

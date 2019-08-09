from distutils.core import setup

setup(
    name='LSB-Tools',
    version='0.1',
    packages=['lsbtools',],
    license='MIT',
    author='DJ Lucas',
    author_email='dj@linuxfromscratch.org',
    url='https://github.com/djlucas/python3-lsb-tools/',
    description='A distribution agnostic set of LSB scripts.',
    long_description=open('README').read(),
    scripts=['lsbtools/install_initd', 'lsbtools/remove_initd'],
    python_requires='>3.7',
    platforms=['linux'],
    data_files = [('', ['LICENSE']),('', ['INSTALL'])]
)

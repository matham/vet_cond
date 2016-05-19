from setuptools import setup, find_packages
import vet_cond

with open('README.rst') as fh:
    long_description = fh.read()

setup(
    name='VetCond',
    version=vet_cond.__version__,
    author='Matthew Einhorn',
    author_email='moiein2000@gmail.com',
    url='http://matham.github.io/vet_cond/',
    license='MIT',
    description='Vet school conditioning experiment.',
    long_description=long_description,
    classifiers=['License :: OSI Approved :: MIT License',
                 'Topic :: Scientific/Engineering',
                 'Topic :: System :: Hardware',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Operating System :: Microsoft :: Windows',
                 'Intended Audience :: Developers'],
    packages=find_packages(),
    install_requires=['moa', 'pybarst', 'ffpyplayer', 'cplcom'],
    setup_requires=['moa', 'pybarst', 'ffpyplayer', 'cplcom'],
    package_data={'vet_cond': ['data/*', '*.kv']},
    entry_points={'console_scripts': ['vet_cond=vet_cond.main:run_app']},
    )

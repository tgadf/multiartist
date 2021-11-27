from setuptools import setup
from setuptools.command.install import install
from sys import prefix

from masterMultiArtistDB import masterMultiArtistDB

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        mmadb = masterMultiArtistDB(install=True)

setup(
  name = 'multiartist',
  py_modules = ['multiArtist', 'masterMultiArtistDB'],
  version = '0.0.1',
  cmdclass={'install': PostInstallCommand},  
  description = 'A Python Wrapper To Parse Music Chart Data',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/multiartist',
  keywords = ['music'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  install_requires=['jupyter_contrib_nbextensions'],
  dependency_links=['git+ssh://git@github.com/tgadf/utils.git#egg=utils-0.0.1']
)
 

from distutils.core import setup
import setuptools
setup(
  name = 'borsh-python',
  packages = ['borsh', 'borsh.types'],
  version = '0.1.3',
  license='MIT',
  description = 'A Borsh library for Python 3.',
  author = 'whdev1',
  author_email = '',
  url = 'https://github.com/whdev1/borsh-python',
  download_url = 'https://github.com/whdev1/libborsh-py/archive/refs/tags/v0.1.3.tar.gz',
  keywords = ['Borsh', 'Binary', 'Stream'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
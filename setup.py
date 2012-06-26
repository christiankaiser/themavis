#!/usr/bin/env python

from distutils.core import setup

setup(name="themavis",
      version="0.0.1",
      description="Python Thematic Mapping and Information Visualisation Library",
      author="Christian Kaiser",
      author_email="christian@smarter-maps.org",
      url="http://www.smarter-maps.org/themavis",
      packages=['themavis'],
      package_dir={"themavis":"src/themavis"},
      package_data={'themavis': ['colormaps/*']},
      requires=['pysvg'],
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Multimedia :: Graphics',
          ],
     )

#!/usr/bin/env python

import os
from setuptools import setup, find_packages
description = "Turn HTML into a dict. Each function pulls a value from the document."
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
def get_version():
    from subprocess import Popen, PIPE
    try:
        from subprocess import DEVNULL # py3
    except ImportError:
        import os
        DEVNULL = open(os.devnull, 'wb')
    def run(*cmd):
        return (Popen(cmd, stderr=DEVNULL, stdout=PIPE)
                .communicate()[0].decode('utf8').strip())
    return(run('git', 'describe', '--tags').replace('-','.post',1).replace('-','+',1)
        or '0.0.0.post{}+g{}'.format(
            run('git', 'rev-list', '--count', 'HEAD'),
            run('git', 'rev-parse', '--short', 'HEAD')))
setup(
    name = "html_parser",
    version = get_version(),
    author = "Jonathan Knapp",
    author_email = "jaknapp8@gmail.com",
    description = description,
    license = "Unlicense",
    keywords = "html parse lxml",
    url = "http://github.com/thann/html_parser",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        # "License :: OSI Approved :: MIT License",
    ],
    py_modules=["html_parser"],
    # install_requires=[],
    entry_points={
        # 'gui_scripts': [
        #     'play-with-mpv=play_with_mpv:start',
        # ],
    },
    # setup_requires=[],
    # dependency_links=[],
)

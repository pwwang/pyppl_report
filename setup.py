
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='pyppl_report',
    version='0.5.0',
    description='A report generating system for PyPPL',
    python_requires='==3.*,>=3.6.0',
    project_urls={"homepage": "https://github.com/pwwang/pyppl_report", "repository": "https://github.com/pwwang/pyppl_report"},
    author='pwwang',
    author_email='pwwang@pwwang.com',
    license='MIT',
    entry_points={"pyppl": ["pyppl_report = pyppl_report"]},
    packages=['pyppl_report'],
    package_dir={"": "."},
    package_data={"pyppl_report": ["*.bak", "resources/templates/bootstrap/*.html", "resources/templates/bootstrap/static/*.css", "resources/templates/bootstrap/static/*.js"]},
    install_requires=['cmdy', 'panflute==1.11.*', 'pyppl', 'toml==0.*,>=0.10.0'],
    extras_require={"dev": ["pyparam", "pytest", "pytest-cov"]},
)

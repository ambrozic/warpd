# -*- coding: utf-8 -*-
"""
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import warpd

setup(
    name="warpd",
    version=".".join(str(i) for i in warpd.__version__),
    description="Cruise control",
    long_description="Cruise control",
    author=warpd.__author__,
    author_email="ambrozic@gmail.com",
    url=None,
    packages=None,
    package_data=None,
    package_dir={"warpd": "warpd"},
    include_package_data=True,
    install_requires=None,
    license=None,
    zip_safe=False,
)

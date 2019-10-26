#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name="mind your stonks",
      description="A library for keeping track of your bad investments (stonks).",
      author="Katleho Madisa",
      author_email="katleho.madisa47@gmail.com",
      packages=find_packages(),
      url='https://github.com/kmadisa/mind_your_stonks',
      license="BSD-2-Clause",
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      platforms=["OS Independent"],
      install_requires=[
          "gspread>=3.0.0",
          "gspread-formatting",
          "oauth2client",
          "loguru",
          "selenium",
          "aenum"],
      zip_safe=False,
      include_package_data=True,
      package_data={},
      scripts=[],
      entry_points={
          'console_scripts': []}
      )

import os

from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name                 = "TreNdis",
    description          = "Compute trending topics, powered by redis",
    long_description     = read("README.md"),
    author               = "Karthik Katooru",
    author_email         = "karthikkatooru@gmail.com",
    url                  = "https://github.com/k4rthik/trendis",
    license              = "MIT",
    install_requires     = ["redis", "twython"],
    py_modules           = ["trendis"],
    scripts              = ['trendis-cli'],
    classifiers          = [
        "Development Status :: 1 - Alpha",
        "License :: MIT",
        "Programming Language :: Python",
        "Topic :: Algorithm :: Database",
    ],
)


import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pyjags",
    version="0.0.1.dev0",
    author="Matthias Mittner",
    author_email="ihrke@github",
    description=(("Ugly, ugly hack to run jags from python using the rjags interface"
		  "via rpy2.")),
    license="BSD",
    keywords="jags bayes MCMC",
    url="http://github.com/ihrke/pyjags",
    py_modules=['pyjags'],
    data_files=[('R', ['R/rjags_coda_samples_dic.R'])],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)


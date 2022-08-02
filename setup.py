import os
from setuptools import setup, find_packages

BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, "requirements.txt")) as f:
    requirements = f.readlines()

setup(
    name="pybooth",
    version="0.0.0",
    description="Tiny photobooth project",
    url="",
    author="Morreski",
    author_email="contact@morreski.net",
    license="MIT",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={"console_scripts": ["pybooth=pybooth.main"]},
)

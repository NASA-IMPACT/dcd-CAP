import setuptools
from distutils.util import convert_path

version_path = convert_path('CAP/version.txt')
with open(version_path) as version_file:
    __version__ = version_file.read().strip()

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", "r", encoding="utf-8") as requirement_file:
    requirements = requirement_file.readlines()


setuptools.setup(
    name="CAP",
    version=__version__,
    author="NASA IMPACT",
    author_email="teamimpact@uah.edu",
    description="Description for the tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NASA-IMPACT/dcd-CAP",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache License, Version 2.0",
        "Operating System :: OS Independent",
    ],
    keywords='space separated keywords list',
    python_requires='>=3.8',
    install_requires=requirements,
    package_data={'CAP': ['Test/*']},
    include_package_data=True,
)

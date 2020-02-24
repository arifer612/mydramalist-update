import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mdl-update",
    version="0.1.8",
    author="arifer",
    author_email="arifer1995@gmail.com",
    description="A python package to update MyDramaList using information from Wikipedia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arifer612/mydramalist-update",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
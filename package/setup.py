import setuptools

with open("README.md", "r") as fh:
    readme_file = fh.read()

setuptools.setup(
    name="mdl-update",
    version="0.4.1",
    author="arifer",
    author_email="arifer1995@gmail.com",
    description="Python package to update Japanese shows on MDL by scraping information from ja.wikipedia.org",
    long_description=readme_file,
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
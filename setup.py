import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name='py_block_diagram',    # This is the name of your PyPI-package.
    version='0.9.3',
    url='https://github.com/ryanGT/py_block_diagram',
    author='Ryan Krauss',
    author_email='ryanwkrauss@gmail.com',
    description="package for  the backend of modeling controls block diagrams in python",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

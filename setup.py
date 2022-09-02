import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name='krauss_misc',    # This is the name of your PyPI-package.
    version='0.9.1',
    url='https://github.com/ryanGT/krauss_misc',
    author='Ryan Krauss',
    author_email='ryanwkrauss@gmail.com',
    description="package of misc code that supports other projects of mine",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    #packages=['basic_file_ops','rwkos','txt_mixin'], 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

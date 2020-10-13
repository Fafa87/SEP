import os

import setuptools

version = os.environ.get("RELEASE_VERSION", "0.0.0")

setuptools.setup(
    author="Filip Mroz",
    author_email="fafafft@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering"
    ],
    cmdclass={},
    include_package_data=True,
    keywords=["evaluation", "semantic", "segmentation", "benchmark"],
    license="BSD",
    long_description="",
    name="semevalplatform",
    description="Semantic Evaluation Platform",
    packages=setuptools.find_packages(exclude=[
        "tests", "examples"
    ]),
    install_requires=[
        "numpy",
        "fire",
        "imageio",
        "pathlib",
        "attrdict",
        "tqdm",
        "pandas",
        "matplotlib",
        "notebook",
        "jupyter_contrib_nbextensions",
        "scikit-image",
        "opencv-python",
        "pafy",
        "youtube_dl"
    ],
    url="https://github.com/Fafa87/SEP",
    version=version
)

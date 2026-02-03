"""
Setup configuration for GalacticNeighborsFinder package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="galactic-neighbors-finder",
    version="1.0.0",
    author="Deepak Deo",
    author_email="deepak.deo@example.com",
    description="Efficient neighbor identification in galaxy catalogs using k-d trees",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deepakdeo/GalacticNeighborsFinder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Astronomy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.0.0",
        "astropy>=4.0",
        "scipy>=1.5.0",
        "pyyaml>=5.3",
        "tqdm>=4.50.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=20.8b1",
            "flake8>=3.8",
            "isort>=5.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "gnf-finder=gnf.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

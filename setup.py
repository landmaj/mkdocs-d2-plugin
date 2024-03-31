from pathlib import Path

from setuptools import find_packages, setup

PROJ_DIR = Path(__file__).resolve().parent
with open(PROJ_DIR / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mkdocs-d2-plugin",
    version="1.3.0",
    description="MkDocs plugin for D2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs python markdown d2 diagram",
    url="https://github.com/landmaj/mkdocs-d2-plugin",
    author="Michał Wieluński",
    author_email="michal@wielunski.net",
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "mkdocs>=1.5.0",
        "pymdown-extensions>=9.0",
        "pydantic>=2.0",
        "packaging",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": ["d2 = d2.plugin:Plugin"],
        "markdown.extensions": ["d2_img = d2.img:D2ImgExtension"],
    },
)

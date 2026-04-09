from pathlib import Path

from setuptools import find_packages, setup

PROJ_DIR = Path(__file__).resolve().parent
with open(PROJ_DIR / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mkdocs-d2-plugin",
    version="1.7.0",
    description="MkDocs plugin for D2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs python markdown d2 diagram",
    url="https://github.com/landmaj/mkdocs-d2-plugin",
    author="Michał Wieluński",
    author_email="michal@wielunski.net",
    license="MIT",
    python_requires=">=3.10",
    install_requires=[
        "mkdocs~=1.6",
        "pymdown-extensions>=9.0",
        "pydantic>=2.0",
        "packaging",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: MkDocs",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: HTML",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
    ],
    packages=find_packages(),
    package_data={"d2.css": ["mkdocs_d2_plugin.css"]},
    include_package_data=True,
    entry_points={
        "mkdocs.plugins": ["d2 = d2.plugin:Plugin"],
        "markdown.extensions": ["d2_img = d2.img:D2ImgExtension"],
    },
)

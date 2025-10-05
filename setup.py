"""
Setup script for Modern PDF Splitter
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="modern-pdf-splitter",
    version="1.0.0",
    author="PDF Splitter Team",
    author_email="team@pdfsplitter.com",
    description="A modern, user-friendly PDF splitting application built with Kivy",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/modern-pdf-splitter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pdf-splitter=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.kv", "*.json", "*.md"],
    },
    keywords="pdf, splitter, kivy, gui, desktop, document, processing",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/modern-pdf-splitter/issues",
        "Source": "https://github.com/yourusername/modern-pdf-splitter",
        "Documentation": "https://github.com/yourusername/modern-pdf-splitter#readme",
    },
)
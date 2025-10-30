"""
Setup configuration for AUDIOANALYSISX1
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="audioanalysisx1",
    version="1.0.0",
    author="SWORD Intelligence",
    author_email="intel@swordintelligence.airforce",
    description="Forensic audio analysis system for detecting voice manipulation and AI-generated voices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SWORDIntel/AUDIOANALYSISX1",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'audioanalysisx1=audioanalysisx1.cli.simple:main',
            'audioanalysisx1-gui=scripts.start_gui:main',
            'audioanalysisx1-tui=audioanalysisx1.cli.interactive:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

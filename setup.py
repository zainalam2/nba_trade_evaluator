from setuptools import setup, find_packages

setup(
    name="nba-trade-evaluator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "nba_api>=1.2.1",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "pylint>=2.15.0",
        ],
    },
    python_requires=">=3.8",
) 
from setuptools import setup, find_packages

setup(
    name="debugagent",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai",
        "tqdm",
        "unidiff",
        "pytest",
        "PyQt5",
        "alpaca-trade-api",
        "matplotlib",
        "pandas",
        "psutil"
    ],
    entry_points={
        "console_scripts": [
            "debugagent-run=debugger.debugger_runner:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)

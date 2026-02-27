from setuptools import setup, find_packages

setup(
    name="predictor",
    version="0.1.0",
    description="基于GLM AI的未来预测系统",
    author="CTO",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "predictor=predictor.cli:main",
        ],
    },
    python_requires=">=3.8",
)

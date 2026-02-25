from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.readlines()
    requirements = [req.strip() for req in requirements]

setup(
    name="trading-system",
    version="2.0.0",
    author="Trading System Team",
    author_email="team@tradingsystem.com",
    description="Enterprise Algorithmic Trading Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/trading-system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
        ],
        "web": [
            "flask>=2.2.0",
            "flask-cors>=4.0.0",
            "plotly>=5.0.0",
            "dash>=2.0.0",
        ],
        "trading": [
            "alpaca-py>=0.8.0",
            "ccxt>=4.0.0",
            "ib_insync>=0.9.70",
        ],
    },
    entry_points={
        "console_scripts": [
            "trading-system=trading_system.cli:main",
            "trading-backtest=trading_system.backtesting.cli:main",
        ],
    },
)
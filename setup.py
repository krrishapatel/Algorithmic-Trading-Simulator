#!/usr/bin/env python3
"""
Setup script for AI Trading Simulator.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="ai-trading-simulator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Professional-Grade Multi-Asset Trading Platform with Real-Time AI Strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-trading-simulator",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ai-trading-simulator/issues",
        "Source": "https://github.com/yourusername/ai-trading-simulator",
        "Documentation": "https://github.com/yourusername/ai-trading-simulator#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-trading-sim=simple_demo:main",
            "ai-trading-dashboard=trading_dashboard:start_trading_dashboard",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "trading",
        "simulator",
        "ai",
        "algorithmic-trading",
        "financial",
        "investment",
        "portfolio",
        "risk-management",
        "vwap",
        "rsi",
        "bollinger-bands",
        "real-time",
        "dashboard",
        "web",
        "python",
    ],
)

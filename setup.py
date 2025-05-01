"""
Setup script for the AI Economic Research News Agent.
"""

from setuptools import setup, find_packages

setup(
    name="ai_econ_news_agent",
    version="0.1.0",
    description="An intelligent agent that discovers and curates economic research news about AI adoption",
    author="Lucas Hendrich",
    author_email="lucas.hendrich@fortegrp.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "python-dotenv>=1.0.0",
        "flask>=2.3.3",
        "flask-cors>=4.0.0",
        "loguru>=0.7.0",
    ],
    extras_require={
        "full": [
            "newspaper3k>=0.2.8",
            "feedparser>=6.0.10",
            "openai>=1.3.0",
            "pydantic>=2.5.0",
            "schedule>=1.2.0",
            "pandas>=2.1.1",
            "nltk>=3.8.1",
            "spacy>=3.7.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-econ-news=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)

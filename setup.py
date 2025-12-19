from setuptools import find_packages
from setuptools import setup


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="github-stats",
    version="1.0.0",
    description="Generate language statistics and visualizations from your GitHub repositories",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "github-stats=github_stats.main:main",
        ],
    },
    python_requires=">=3.10",
)

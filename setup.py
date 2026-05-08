from setuptools import setup, find_packages
from typing import List

def get_requirements(file_path: str) -> List[str]:
    try:
        with open(file_path, "r") as file:
                return [line.strip() for line in file if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. No dependencies will be installed.")
        return []

setup(
    name="NetworkSecurity",
    version="0.0.1",
    description="A network security project for ML Ops.",
    author="divya",
    author_email="",
    packages=find_packages(where="."),
    include_package_data=True,
    python_requires=">=3.13",
    install_requires=get_requirements("requirements.txt"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

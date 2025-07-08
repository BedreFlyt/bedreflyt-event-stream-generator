from setuptools import setup, find_packages

setup(
    name="SyntheticDataGenerator",
    author = "Buster Salomon Rasmussen",
    author_email = "buster.rasmussen@dscience.uio.no, bustersalomonrasmussen@gmail.com",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "numpy",
        "ipykernel",
    ],
)

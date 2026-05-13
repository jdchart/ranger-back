from setuptools import setup
from setuptools import find_packages

long_description= """
# rangerback
"""

required = [
    "fastapi",
    "uvicorn",
    "requests",
    "python-multipart",
    "sqlalchemy",
    "python-jose"
]

setup(
    name="rangerback",
    version="0.0.1",
    description="",
    long_description=long_description,
    author="Jacob Hart",
    author_email="jacob.dchart@gmail.com",
    url="https://github.com/jdchart/ranger-back",
    install_requires=required,
    packages=find_packages()
)
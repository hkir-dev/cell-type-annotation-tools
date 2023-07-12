import pathlib
from setuptools import setup


# The directory containing this file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="ctat",
    version="0.0.1.dev1",
    description="The aim of this project is to specify the Cell Type Annotation schema and related data standardization operations.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hkir-dev/cell-type-annotation-tools",
    author="",
    license="Apache-2.0 license",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={'': 'src'},
    packages=["ctat", "schema"],
    include_package_data=True,
    install_requires=["jsonschema", "ruamel.yaml", "dataclasses_json"],
    entry_points={
        "console_scripts": [
            "ctat=ctat.__main__:main",
        ]
    },
)

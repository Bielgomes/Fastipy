from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="fastipy",
    version="1.5.0",
    description="Fastipy is a fast and easy-to-use open source python library for developing RESTful APIs. It provides a clear and concise syntax for handling routes, requests, and responses, making the development of APIs faster and more efficient. With support for form parameters, body and route parameters, it is useful for handling different types of requests. Whether you are a beginner or an experienced developer, Fastipy is a simple and powerful choice for creating robust and scalable APIs.",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bielgomes/Fastipy",
    author="Bielgomes",
    author_email="bielgomesdasilva@hotmail.com",
    license="GNU Affero General Public License v3",
    project_urls={
        "Bug Tracker": "https://github.com/Bielgomes/Fastipy/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    install_requires=["watchdog >= 3.0.0"],
    python_requires=">=3.10",
)